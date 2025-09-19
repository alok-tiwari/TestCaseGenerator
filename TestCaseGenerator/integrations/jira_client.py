"""Jira REST API client for fetching user stories and acceptance criteria."""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Change the relative import
# Fix imports to use absolute paths
from TestCaseGenerator.config.settings import JiraConfig
from TestCaseGenerator.models.jira_models import JiraTicket, JiraIssue, JiraField
from TestCaseGenerator.parsers.user_story_parser import UserStoryParser


logger = logging.getLogger(__name__)


class JiraClient:
    """Jira REST API client with authentication and error handling."""
    
    def __init__(self, config: JiraConfig):
        """Initialize Jira client with configuration."""
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.auth = (config.username, config.api_token)
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            timeout=config.timeout,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        
        # Cache for API responses
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Initialize user story parser with configurable format
        self.story_parser = UserStoryParser(story_format=config.user_story_format)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
    )
    async def fetch_ticket(self, ticket_id: str) -> JiraTicket:
        """Fetch a Jira ticket by ID."""
        
        # Check cache first
        cache_key = f"ticket_{ticket_id}"
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_ttl:
                logger.info(f"Returning cached ticket {ticket_id}")
                return cached_data
        
        try:
            logger.info(f"Fetching Jira ticket {ticket_id}")
            
            # Fetch issue details
            issue_response = await self.client.get(f"/rest/api/3/issue/{ticket_id}")
            issue_response.raise_for_status()
            issue_data = issue_response.json()
            
            # Fetch issue fields
            fields_response = await self.client.get(f"/rest/api/3/issue/{ticket_id}?expand=names,schema")
            fields_response.raise_for_status()
            fields_data = fields_response.json()
            
            # Parse the ticket
            ticket = self._parse_jira_ticket(issue_data, fields_data)
            
            # Cache the result
            self._cache[cache_key] = (ticket, datetime.now().timestamp())
            
            logger.info(f"Successfully fetched ticket {ticket_id}")
            return ticket
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Ticket {ticket_id} not found")
                raise ValueError(f"Ticket {ticket_id} not found")
            elif e.response.status_code == 401:
                logger.error(f"Authentication failed for ticket {ticket_id}")
                raise ValueError("Authentication failed - check Jira credentials")
            elif e.response.status_code == 403:
                logger.error(f"Access denied to ticket {ticket_id}")
                raise ValueError("Access denied - insufficient permissions")
            else:
                logger.error(f"HTTP error {e.response.status_code} fetching ticket {ticket_id}")
                raise
        except Exception as e:
            logger.error(f"Error fetching ticket {ticket_id}: {e}")
            raise
    
    async def fetch_tickets_by_jql(self, jql: str, max_results: int = 50) -> List[JiraTicket]:
        """Fetch multiple tickets using JQL query."""
        
        try:
            logger.info(f"Fetching tickets with JQL: {jql}")
            
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,description,issuetype,status,priority,assignee,reporter,created,updated,labels,components,customfield_10014,customfield_10015"  # Epic link and sprint
            }
            
            response = await self.client.get("/rest/api/3/search", params=params)
            response.raise_for_status()
            search_data = response.json()
            
            tickets = []
            for issue in search_data.get("issues", []):
                try:
                    # Fetch full issue details for each ticket
                    ticket = await self.fetch_ticket(issue["key"])
                    tickets.append(ticket)
                except Exception as e:
                    logger.warning(f"Failed to fetch ticket {issue['key']}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(tickets)} tickets")
            return tickets
            
        except Exception as e:
            logger.error(f"Error fetching tickets with JQL: {e}")
            raise
    
    async def fetch_user_stories(self, project_key: str, sprint: Optional[str] = None) -> List[JiraTicket]:
        """Fetch user stories from a specific project and optionally sprint."""
        
        jql_parts = [
            f"project = {project_key}",
            "issuetype = Story",
            "status != Closed"
        ]
        
        if sprint:
            jql_parts.append(f'sprint = "{sprint}"')
        
        jql = " AND ".join(jql_parts)
        return await self.fetch_tickets_by_jql(jql)
    
    async def fetch_epic_stories(self, epic_key: str) -> List[JiraTicket]:
        """Fetch all stories linked to an epic."""
        
        jql = f'issue in linkedIssues("{epic_key}") AND issuetype = Story'
        return await self.fetch_tickets_by_jql(jql)
    
    def generate_dummy_ticket(self, ticket_id: str) -> JiraTicket:
        """Generate dummy Jira ticket data for testing."""
        
        # Generate random data
        priorities = ["Low", "Medium", "High", "Critical"]
        statuses = ["To Do", "In Progress", "In Review", "Done"]
        issue_types = ["Story", "Bug", "Task", "Epic"]
        
        # Create dummy issue
        issue = JiraIssue(
            issue_key=ticket_id,
            issue_id=str(random.randint(10000, 99999)),
            summary=f"Dummy ticket for {ticket_id}",
            description="This is a dummy ticket generated for testing purposes. It contains sample data to demonstrate the test case generator functionality.",
            issue_type=random.choice(issue_types),
            status={"name": random.choice(statuses)},
            priority=random.choice(priorities),
            assignee=f"user{random.randint(1, 5)}",
            reporter="test.user",
            created=datetime.now() - timedelta(days=random.randint(1, 30)),
            updated=datetime.now() - timedelta(days=random.randint(0, 7)),
            fields={}
        )
        
        # Generate dummy acceptance criteria
        acceptance_criteria = [
            "Given a DUMMY user is logged into the system, When they navigate to the dashboard, Then they should see their personalized content",
            "Given a DUMMY user has completed a form, When they click the submit button, Then the data should be saved and a confirmation message displayed",
            "Given a DUMMY user is viewing a list of items, When they apply a filter, Then only matching items should be displayed"
        ]
        
        # Generate dummy user story
        user_story = "As a registered DUMMY user\nI want to access my personalized dashboard\nSo that I can view relevant information quickly"
        
        # Generate dummy labels and components
        labels = ["frontend", "user-experience", "dashboard"]
        components = ["web-interface", "user-management"]
        
        return JiraTicket(
            issue=issue,
            acceptance_criteria=acceptance_criteria,
            user_story=user_story,
            labels=labels,
            components=components,
            epic_link=f"EPIC-{random.randint(100, 999)}",
            sprint=f"Sprint {random.randint(1, 10)}",
            story_points=random.choice([1.0, 2.0, 3.0, 5.0, 8.0])
        )
    
    def _parse_jira_ticket(self, issue_data: Dict[str, Any], fields_data: Dict[str, Any]) -> JiraTicket:
        """Parse raw Jira API response into our domain model."""
        
        # Safely parse all fields with proper None handling
        fields = issue_data.get('fields', {})
        
        # Convert description to string if it's a rich-text document
        description = fields.get('description')
        if isinstance(description, dict):
            description = self._convert_jira_doc_to_text(description)
        elif description is None:
            description = ""
        elif not isinstance(description, str):
            try:
                description = str(description)
            except Exception:
                description = ""
            
        # Safely get nested field values with proper defaults
        issue = JiraIssue(
            issue_key=issue_data['key'],
            issue_id=issue_data['id'],
            summary=fields.get('summary', ''),
            description=description,
            issue_type=fields.get('issuetype', {}).get('name', ''),
            status=fields.get('status', {}).get('name', ''),
            priority=fields.get('priority', {}).get('name', ''),
            assignee=fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else None,
            reporter=fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else None,
            created=fields.get('created', ''),
            updated=fields.get('updated', ''),
            fields=fields
        )
        
        # Parse basic issue information
        issue = JiraIssue(
            issue_key=issue_data["key"],
            issue_id=issue_data["id"],
            summary=fields.get("summary", ""),
            description=description,
            issue_type=fields.get("issuetype", {}).get("name", "Unknown"),
            status=fields.get("status", {}).get("name", "Unknown"),
            priority=fields.get("priority", {}).get("name", "Medium"),
            assignee=fields.get("assignee", {}).get("accountId") if fields.get("assignee") else None,
            reporter=fields.get("reporter", {}).get("accountId", "Unknown"),
            created=datetime.fromisoformat(fields.get("created", "").replace("Z", "+00:00")),
            updated=datetime.fromisoformat(fields.get("updated", "").replace("Z", "+00:00")),
            fields=self._parse_custom_fields(fields)
        )
        
        # Extract acceptance criteria from description or custom fields
        acceptance_criteria = self._extract_acceptance_criteria(fields)
        
        # Extract user story from description or custom fields
        user_story = self._extract_user_story(fields)
        
        # Extract other metadata
        labels = fields.get("labels", [])
        components = [comp.get("name", "") for comp in fields.get("components", [])]
        
        # Extract epic link and sprint
        epic_link = None
        sprint = None
        
        # Try to find epic link in custom fields
        for field_name, field_value in fields.items():
            if "epic" in field_name.lower() and field_value:
                epic_link = field_value
                break
        
        # Try to find sprint information
        for field_name, field_value in fields.items():
            if "sprint" in field_name.lower() and field_value:
                if isinstance(field_value, list) and field_value:
                    sprint = field_value[0].get("name", "")
                elif isinstance(field_value, str):
                    sprint = field_value
                break
        
        # Extract story points if available
        story_points = None
        for field_name, field_value in fields.items():
            if "story point" in field_name.lower() or "storypoint" in field_name.lower():
                try:
                    story_points = float(field_value)
                    break
                except (ValueError, TypeError):
                    continue
        
        return JiraTicket(
            issue=issue,
            acceptance_criteria=acceptance_criteria,
            user_story=user_story,
            labels=labels,
            components=components,
            epic_link=epic_link,
            sprint=sprint,
            story_points=story_points
        )
    
    def _parse_custom_fields(self, fields: Dict[str, Any]) -> Dict[str, JiraField]:
        """Parse custom fields from Jira response."""
        custom_fields = {}
        
        for field_name, field_value in fields.items():
            if field_name.startswith("customfield_"):
                # Try to get field name from schema
                field_info = {
                    "field_id": field_name,
                    "field_name": field_name,  # Default to field ID if name not available
                    "field_value": field_value,
                    "field_type": type(field_value).__name__
                }
                custom_fields[field_name] = JiraField(**field_info)
        
        return custom_fields
    
    def _extract_acceptance_criteria(self, fields: Dict[str, Any]) -> List[str]:
        """Extract acceptance criteria from Jira fields."""
        acceptance_criteria = []
        
        # Try to find acceptance criteria in description
        description = fields.get("description", "")
        if description:
            # Convert rich text description to plain text if needed
            if isinstance(description, dict):
                from TestCaseGenerator.fetch_jira_tickets import jira_doc_to_text
                description = jira_doc_to_text(description)
            
            # Look for common acceptance criteria patterns
            lines = description.split('\n')
            in_ac_section = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if any(header in line.lower() for header in ["acceptance criteria", "acceptance", "criteria", "ac:"]):
                    in_ac_section = True
                    continue
                
                # Check for end of section
                if in_ac_section and any(header in line.lower() for header in ["test cases", "notes", "comments", "---"]):
                    break
                
                # If we're in AC section, add the line
                if in_ac_section and line:
                    # Clean up the line
                    line = line.lstrip('•*-').strip()
                    if line:
                        acceptance_criteria.append(line)
        
        # If no acceptance criteria found in description, try custom fields
        if not acceptance_criteria:
            for field_name, field_value in fields.items():
                if "acceptance" in field_name.lower() and field_value:
                    if isinstance(field_value, str):
                        # Split by common separators
                        criteria = [c.strip() for c in field_value.split('\n') if c.strip()]
                        acceptance_criteria.extend(criteria)
                    elif isinstance(field_value, list):
                        acceptance_criteria.extend([str(c) for c in field_value if c])
        
        return acceptance_criteria
    
    def _extract_user_story(self, fields: Dict[str, Any]) -> Optional[str]:
        """Extract user story from Jira fields using configurable format parsing."""
        
        # Try to find user story in description
        description = fields.get("description", "")
        if description:
            # Convert rich text description to plain text if needed
            if isinstance(description, dict):
                from TestCaseGenerator.fetch_jira_tickets import jira_doc_to_text
                description = jira_doc_to_text(description)
                
            # Use the configurable parser to extract user story
            parsed_story = self.story_parser.parse_user_story(description)
            if parsed_story:
                # Return the original text if parsing was successful
                return parsed_story.original_text
                
            # Fallback to original extraction logic if parser fails
            lines = description.split('\n')
            story_lines = []
            in_story_section = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if any(header in line.lower() for header in ["user story", "story:", "as a", "i want"]):
                    in_story_section = True
                    continue
                
                # Check for end of section
                if in_story_section and any(header in line.lower() for header in ["acceptance criteria", "notes", "comments", "---"]):
                    break
                
                # If we're in story section, add the line
                if in_story_section and line:
                    story_lines.append(line)
            
            if story_lines:
                return '\n'.join(story_lines)
        
        # If no user story found in description, try custom fields
        for field_name, field_value in fields.items():
            if "story" in field_name.lower() and field_value:
                if isinstance(field_value, str):
                    # Try parsing custom field value as well
                    parsed_story = self.story_parser.parse_user_story(field_value)
                    if parsed_story:
                        return parsed_story.original_text
                    return field_value
                elif isinstance(field_value, list) and field_value:
                    story_text = '\n'.join([str(s) for s in field_value])
                    parsed_story = self.story_parser.parse_user_story(story_text)
                    if parsed_story:
                        return parsed_story.original_text
                    return story_text
        
        return None
    
    async def test_connection(self) -> bool:
        """Test the Jira connection and authentication."""
        try:
            response = await self.client.get("/rest/api/3/myself")
            response.raise_for_status()
            user_data = response.json()
            logger.info(f"Successfully connected to Jira as {user_data.get('displayName', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            return False
    
    async def close(self):
        """Close the client and cleanup resources."""
        await self.client.aclose()
    
    def clear_cache(self):
        """Clear the response cache."""
        self._cache.clear()
        logger.info("Jira client cache cleared")


    def _convert_jira_doc_to_text(self, doc: Dict[str, Any]) -> str:
        """Convert Jira rich-text document to plain text."""
        if not doc:
            return ""
            
        lines = []
        for block in doc.get("content", []):
            block_type = block.get("type")
            if block_type == "paragraph":
                paragraph_text = "".join(
                    c.get("text", "") for c in block.get("content", []) if c.get("type") == "text"
                )
                lines.append(paragraph_text)
            elif block_type in ["orderedList", "bulletList"]:
                for li in block.get("content", []):
                    for c in li.get("content", []):
                        if c.get("type") == "paragraph":
                            text = "".join(
                                cc.get("text", "") for cc in c.get("content", []) if cc.get("type") == "text"
                            )
                            lines.append(f"- {text}")
        return "\n".join(lines)
