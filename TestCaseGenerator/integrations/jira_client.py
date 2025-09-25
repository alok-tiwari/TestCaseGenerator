"""Jira REST API client for fetching user stories and acceptance criteria."""

import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Change the relative import
# Fix imports to use absolute paths
from config.settings import JiraConfig
from models.jira_models import JiraTicket, JiraIssue, JiraField
from parsers.user_story_parser import UserStoryParser


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
                raise ValueError(f"Ticket {ticket_id} not found. Use --mode local for testing with sample data.")
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
        """Generate dummy Jira ticket data for testing using local_user_story.txt."""
        
        # Try to read from local_user_story.txt, fallback to dummy_user_story.txt
        user_story_file = "local_user_story.txt"
        if not os.path.exists(user_story_file):
            user_story_file = "dummy_user_story.txt"
        
        try:
            with open(user_story_file, 'r') as f:
                user_story_content = f.read().strip()
        except FileNotFoundError:
            user_story_content = "As a user\nI want to perform an action\nSo that I can achieve a goal"
        
        # Generate random data
        priorities = ["Low", "Medium", "High", "Critical"]
        statuses = ["To Do", "In Progress", "In Review", "Done"]
        issue_types = ["Story", "Bug", "Task", "Epic"]
        
        # Create dummy issue
        issue = JiraIssue(
            issue_key=ticket_id,
            issue_id=str(random.randint(10000, 99999)),
            summary=f"Local ticket for {ticket_id}",
            description=f"This is a local ticket generated from {user_story_file}. It contains user story data for testing the test case generator functionality.\n\nUser Story:\n{user_story_content}",
            issue_type=random.choice(issue_types),
            status={"name": random.choice(statuses)},
            priority=random.choice(priorities),
            assignee=f"user{random.randint(1, 5)}",
            reporter="test.user",
            created=datetime.now() - timedelta(days=random.randint(1, 30)),
            updated=datetime.now() - timedelta(days=random.randint(0, 7)),
            fields={}
        )
        
        # Generate acceptance criteria based on user story
        acceptance_criteria = [
            f"Given a user from {user_story_file}, When they perform the specified action, Then they should achieve the expected goal",
            "Given the system is in a known state, When the user interacts with the system, Then the system should respond appropriately",
            "Given the user has valid permissions, When they access the feature, Then they should see the expected functionality"
        ]
        
        # Generate labels and components
        labels = ["local-test", "user-story", "test-generation"]
        components = ["test-framework", "user-interface"]
        
        return JiraTicket(
            issue=issue,
            acceptance_criteria=acceptance_criteria,
            user_story=user_story_content,
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
                from fetch_jira_tickets import jira_doc_to_text
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
                from fetch_jira_tickets import jira_doc_to_text
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
    
    def _extract_system_context(self, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract system context from JIRA fields for better LLM understanding."""
        
        context = {
            'tech_stack': [],
            'data_types': [],
            'constraints': [],
            'user_roles': [],
            'business_domain': None,
            'priority_level': None,
            'complexity': None
        }
        
        # Extract from description
        description = fields.get("description", "")
        if description:
            if isinstance(description, dict):
                from fetch_jira_tickets import jira_doc_to_text
                description = jira_doc_to_text(description)
            
            # Extract technical terms
            tech_terms = self._extract_technical_terms(description)
            context['tech_stack'].extend(tech_terms)
            
            # Extract business domain
            domain = self._extract_business_domain(description)
            if domain:
                context['business_domain'] = domain
        
        # Extract from labels
        labels = fields.get("labels", [])
        for label in labels:
            if any(tech in label.lower() for tech in ['api', 'ui', 'backend', 'frontend', 'database', 'microservice']):
                context['tech_stack'].append(label)
            elif any(role in label.lower() for role in ['admin', 'user', 'customer', 'developer', 'manager']):
                context['user_roles'].append(label)
        
        # Extract from components
        components = fields.get("components", [])
        for component in components:
            if isinstance(component, dict):
                component_name = component.get("name", "")
                if any(tech in component_name.lower() for tech in ['api', 'ui', 'backend', 'frontend', 'database']):
                    context['tech_stack'].append(component_name)
        
        # Extract priority
        priority = fields.get("priority", {})
        if isinstance(priority, dict):
            priority_name = priority.get("name", "")
            context['priority_level'] = priority_name.lower()
        
        # Extract story points for complexity
        story_points = fields.get("customfield_10016")  # Common story points field
        if story_points and isinstance(story_points, (int, float)):
            if story_points <= 3:
                context['complexity'] = 'low'
            elif story_points <= 8:
                context['complexity'] = 'medium'
            else:
                context['complexity'] = 'high'
        
        # Add default values if empty
        if not context['tech_stack']:
            context['tech_stack'] = ['web application']
        if not context['user_roles']:
            context['user_roles'] = ['user']
        
        return context
    
    def _extract_system_context_from_local_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract system context from local file content."""
        if not content:
            return None
        
        context = {
            'tech_stack': [],
            'data_types': [],
            'constraints': [],
            'user_roles': [],
            'business_domain': [],
            'priority_level': 'medium',
            'complexity': 'medium'
        }
        
        content_lower = content.lower()
        
        # Extract tech stack based on content
        if 'ipv4' in content_lower or 'ipv6' in content_lower:
            context['tech_stack'].extend(['IPv4', 'IPv6', 'Network Protocol'])
        if 'validation' in content_lower:
            context['tech_stack'].append('Input Validation')
        if 'configuration' in content_lower or 'settings' in content_lower:
            context['tech_stack'].append('Configuration Management')
        if 'diagnostics' in content_lower:
            context['tech_stack'].append('System Diagnostics')
        
        # Extract data types
        if 'ip address' in content_lower:
            context['data_types'].extend(['IP Address', 'String', 'Network Address'])
        if 'ipv4' in content_lower:
            context['data_types'].append('IPv4 Address')
        if 'ipv6' in content_lower:
            context['data_types'].append('IPv6 Address')
        
        # Extract constraints
        if 'spaces' in content_lower or 'special characters' in content_lower:
            context['constraints'].append('No spaces or special characters allowed')
        if 'blank' in content_lower or 'null' in content_lower:
            context['constraints'].append('Default value must be blank/null')
        if 'validation' in content_lower:
            context['constraints'].append('Must validate IP address format')
        
        # Extract user roles
        if 'user' in content_lower:
            context['user_roles'].append('End User')
        if 'configuration' in content_lower:
            context['user_roles'].append('System Administrator')
        
        # Extract business domain
        if 'ip address' in content_lower or 'network' in content_lower:
            context['business_domain'].append('Network Configuration')
        if 'device' in content_lower:
            context['business_domain'].append('Device Management')
        
        # Determine priority and complexity based on content
        if 'critical' in content_lower or 'offline' in content_lower:
            context['priority_level'] = 'high'
        if 'validation' in content_lower and 'ipv6' in content_lower:
            context['complexity'] = 'high'
        
        return context
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text."""
        import re
        
        tech_patterns = [
            r'\b(api|database|ui|ux|frontend|backend|microservice|container|kubernetes|docker|aws|azure|gcp)\b',
            r'\b(rest|graphql|json|xml|http|https|ssl|tls|oauth|jwt)\b',
            r'\b(react|angular|vue|node|python|java|go|rust|c#|php)\b',
            r'\b(mysql|postgresql|mongodb|redis|elasticsearch|kafka|rabbitmq)\b'
        ]
        
        terms = []
        text_lower = text.lower()
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower)
            terms.extend(matches)
        
        return list(set(terms))  # Remove duplicates
    
    def _extract_business_domain(self, text: str) -> Optional[str]:
        """Extract business domain from text."""
        import re
        
        domain_patterns = [
            r'\b(ecommerce|e-commerce|retail|finance|banking|healthcare|medical|education|learning|manufacturing|logistics|supply chain|hr|human resources|marketing|sales|crm|erp|analytics|reporting|monitoring|alerting|notification|communication|collaboration|project management|task management|workflow|automation|integration|migration|data processing|real-time|iot|sensor|hvac|energy|building management|facility management)\b'
        ]
        
        text_lower = text.lower()
        
        for pattern in domain_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                return matches[0]
        
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
