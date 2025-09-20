"""Base test generator with common functionality."""

import logging
import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional

from integrations.llm_client import LLMClient
from models.input_models import TestCaseRequest
from models.test_models import TestCase, TestStep, TestData, TestType, TestPriority, TestStatus
from parsers.acceptance_criteria_parser import AcceptanceCriteriaParser


logger = logging.getLogger(__name__)


class BaseTestGenerator(ABC):
    """Abstract base class for test case generators."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize the base generator."""
        self.llm_client = llm_client
        self.acceptance_parser = AcceptanceCriteriaParser()
        
        # Test case counter for generating unique IDs
        self._test_counter = 0
    
    @abstractmethod
    async def generate(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate test cases for the given request."""
        pass
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for test case generation."""
        if not text:
            return []
        
        # Extract technical terms, actions, and objects
        words = re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b', text)
        
        # Filter out common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'can', 'may', 'might', 'must', 'shall', 'given', 'when', 'then',
            'user', 'system', 'should', 'will', 'must', 'can', 'able', 'to', 'that'
        }
        
        keywords = []
        for word in words:
            word_lower = word.lower()
            if (word_lower not in common_words and 
                len(word) > 2 and 
                not word.isdigit() and
                word_lower not in keywords):
                keywords.append(word_lower)
        
        return keywords[:20]  # Limit to top 20 keywords
    
    def _identify_edge_cases(self, criteria: List[str]) -> List[str]:
        """Identify potential edge cases from acceptance criteria."""
        edge_cases = []
        
        edge_case_patterns = [
            r'\b(empty|null|none|zero)\b',
            r'\b(maximum|minimum|limit|boundary)\b',
            r'\b(invalid|invalid|wrong|incorrect)\b',
            r'\b(timeout|expired|stale)\b',
            r'\b(concurrent|simultaneous|parallel)\b',
            r'\b(offline|disconnected|unavailable)\b',
            r'\b(permission|access|authorization)\b',
            r'\b(performance|slow|fast|response time)\b',
            r'\b(negative|error|exception)\b',
            r'\b(boundary|edge|corner)\b'
        ]
        
        for criterion in criteria:
            for pattern in edge_case_patterns:
                if re.search(pattern, criterion, re.IGNORECASE):
                    edge_cases.append(criterion)
                    break
        
        return edge_cases
    
    def _generate_test_id(self, prefix: str = "TC") -> str:
        """Generate a unique test case ID."""
        self._test_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{prefix}-{timestamp}-{self._test_counter:03d}"
    
    def _create_test_step(self, step_number: int, action: str, expected_result: str, 
                         test_data: Optional[str] = None, notes: Optional[str] = None) -> TestStep:
        """Create a test step with the given parameters."""
        return TestStep(
            step_number=step_number,
            action=action,
            expected_result=expected_result,
            test_data=test_data,
            notes=notes
        )
    
    def _create_test_data(self, input_data: Dict[str, Any] = None, 
                         expected_output: Dict[str, Any] = None,
                         preconditions: List[str] = None,
                         test_environment: Dict[str, str] = None) -> TestData:
        """Create test data requirements."""
        return TestData(
            input_data=input_data or {},
            expected_output=expected_output or {},
            preconditions=preconditions or [],
            test_environment=test_environment or {}
        )
    
    def _determine_test_priority(self, request: TestCaseRequest, test_type: str) -> TestPriority:
        """Determine the priority for a test case."""
        # Map request priority to test priority
        priority_mapping = {
            "low": TestPriority.LOW,
            "medium": TestPriority.MEDIUM,
            "high": TestPriority.HIGH,
            "critical": TestPriority.CRITICAL
        }
        
        base_priority = priority_mapping.get(request.test_specification.priority, TestPriority.MEDIUM)
        
        # Adjust priority based on test type
        if test_type == "security":
            # Security tests are typically high priority
            if base_priority == TestPriority.LOW:
                return TestPriority.MEDIUM
            elif base_priority == TestPriority.MEDIUM:
                return TestPriority.HIGH
        
        return base_priority
    
    def _determine_test_type(self, request: TestCaseRequest, test_category: str) -> TestType:
        """Determine the test type based on request and category."""
        # Map test categories to test types
        type_mapping = {
            "functional": TestType.FUNCTIONAL,
            "api": TestType.API,
            "ui": TestType.UI,
            "performance": TestType.PERFORMANCE,
            "security": TestType.SECURITY,
            "accessibility": TestType.ACCESSIBILITY,
            "integration": TestType.INTEGRATION,
            "unit": TestType.UNIT,
            "e2e": TestType.E2E
        }
        
        # Check if the category is in the request's test types
        if test_category in request.test_specification.test_types:
            return type_mapping.get(test_category, TestType.FUNCTIONAL)
        
        # Default to functional if category not specified
        return TestType.FUNCTIONAL
    
    def _extract_requirements(self, request: TestCaseRequest) -> List[str]:
        """Extract requirements from the test case request."""
        requirements = []
        
        # Add acceptance criteria as requirements
        for i, criteria in enumerate(request.acceptance_criteria.criteria_list):
            requirements.append(f"AC-{i+1:02d}: {criteria}")
        
        # Add user story if available
        if request.user_story:
            requirements.append(f"US: {request.user_story.persona} - {request.user_story.action}")
        
        # Add Jira ticket if available
        if request.jira_ticket_id:
            requirements.append(f"JIRA: {request.jira_ticket_id}")
        
        return requirements
    
    def _generate_tags(self, request: TestCaseRequest, test_category: str) -> List[str]:
        """Generate tags for the test case."""
        tags = [test_category]
        
        # Add tags based on test level
        tags.append(request.test_specification.test_level)
        
        # Add tags based on priority
        tags.append(request.test_specification.priority)
        
        # Add tags based on output format
        tags.append(request.test_specification.output_format)
        
        # Add tags from system context if available
        if request.system_context:
            if request.system_context.tech_stack:
                tags.extend([tech.lower().replace(" ", "-") for tech in request.system_context.tech_stack[:3]])
            
            if request.system_context.user_roles:
                tags.extend([role.lower() for role in request.system_context.user_roles[:2]])
        
        # Add tags from acceptance criteria keywords
        keywords = self._extract_keywords(" ".join(request.acceptance_criteria.criteria_list))
        tags.extend(keywords[:5])  # Add top 5 keywords as tags
        
        return list(set(tags))  # Remove duplicates
    
    def _validate_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """Validate a generated test case."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check basic requirements
        if not test_case.title or len(test_case.title.strip()) < 5:
            validation_result["errors"].append("Test case title is too short")
            validation_result["is_valid"] = False
        
        if not test_case.description or len(test_case.description.strip()) < 10:
            validation_result["warnings"].append("Test case description could be more detailed")
        
        if not test_case.steps:
            validation_result["errors"].append("Test case has no steps")
            validation_result["is_valid"] = False
        
        # Check step quality
        for i, step in enumerate(test_case.steps):
            if not step.action or len(step.action.strip()) < 5:
                validation_result["warnings"].append(f"Step {i+1} action could be more specific")
            
            if not step.expected_result or len(step.expected_result.strip()) < 5:
                validation_result["warnings"].append(f"Step {i+1} expected result could be more specific")
        
        # Check for missing critical information
        if not test_case.tags:
            validation_result["suggestions"].append("Consider adding tags for better categorization")
        
        if not test_case.requirements:
            validation_result["suggestions"].append("Consider linking to specific requirements")
        
        return validation_result
    
    def _enhance_test_case(self, test_case: TestCase, request: TestCaseRequest) -> TestCase:
        """Enhance a test case with additional information."""
        
        # Add source information
        test_case.source_request = str(uuid.uuid4())
        test_case.jira_ticket_id = request.jira_ticket_id
        test_case.generated_at = datetime.now().isoformat()
        
        # Enhance test data if not provided
        if not test_case.test_data:
            test_case.test_data = self._create_test_data(
                preconditions=["System is in a known state"],
                test_environment={"browser": "Chrome", "os": "Windows"}
            )
        
        # Enhance steps if they seem incomplete
        if test_case.steps:
            for step in test_case.steps:
                if not step.notes and len(step.action) > 50:
                    step.notes = "Verify the action completes successfully"
        
        return test_case
    
    def _log_generation_stats(self, test_cases: List[TestCase], request: TestCaseRequest):
        """Log statistics about the generated test cases."""
        if not test_cases:
            logger.warning("No test cases were generated")
            return
        
        total_steps = sum(len(tc.steps) for tc in test_cases)
        avg_steps = total_steps / len(test_cases)
        
        logger.info(f"Generated {len(test_cases)} test cases with {total_steps} total steps")
        logger.info(f"Average steps per test case: {avg_steps:.1f}")
        logger.info(f"Output format: {request.test_specification.output_format}")
        logger.info(f"Test level: {request.test_specification.test_level}")
        
        # Log test case types
        type_counts = {}
        for tc in test_cases:
            tc_type = tc.test_type.value
            type_counts[tc_type] = type_counts.get(tc_type, 0) + 1
        
        for tc_type, count in type_counts.items():
            logger.info(f"  {tc_type}: {count} test cases")
    
    async def _generate_with_llm(self, request: TestCaseRequest, test_type: str) -> str:
        """Generate test cases using the LLM client."""
        try:
            return await self.llm_client.generate_test_cases(request, test_type)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str, request: TestCaseRequest) -> List[TestCase]:
        """Parse LLM response into structured test cases."""
        test_cases = []
        
        try:
            logger.info("Starting LLM response parsing")
            
            # Parse the simple TEST_CASE_X format
            test_case_pattern = r'TEST_CASE_(\d+):\s*(.+?)\n\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\n\nTEST_CASE_|\Z)'
            matches = re.findall(test_case_pattern, response, re.DOTALL)
            
            logger.info(f"First pattern found {len(matches)} matches")
            
            # If no matches, try a simpler pattern
            if not matches:
                test_case_pattern = r'TEST_CASE_(\d+):\s*(.+?)\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\nTEST_CASE_|\Z)'
                matches = re.findall(test_case_pattern, response, re.DOTALL)
                logger.info(f"Second pattern found {len(matches)} matches")
            
            logger.info(f"Total matches found: {len(matches)}")
            
        except Exception as e:
            logger.error(f"Error in pattern matching: {e}")
            matches = []
        
        for match in matches:
            case_num, title, given, when, then = match
            
            # Clean up the title
            title = title.strip()
            
            # Create test steps
            steps = []
            step_number = 1
            
            # Add GIVEN step
            if given.strip():
                steps.append(self._create_test_step(
                    step_number=step_number,
                    action=given.strip(),
                    expected_result="Precondition satisfied",
                    notes="Given step"
                ))
                step_number += 1
            
            # Add WHEN step
            if when.strip():
                steps.append(self._create_test_step(
                    step_number=step_number,
                    action=when.strip(),
                    expected_result="Action completed",
                    notes="When step"
                ))
                step_number += 1
            
            # Add THEN step
            if then.strip():
                steps.append(self._create_test_step(
                    step_number=step_number,
                    action=then.strip(),
                    expected_result="Expected result achieved",
                    notes="Then step"
                ))
                step_number += 1
            
            if steps:
                test_case = TestCase(
                    test_id=self._generate_test_id("TC"),
                    title=title,
                    description=f"Test case generated from LLM: {title}",
                    test_type=TestType.FUNCTIONAL,
                    priority=TestPriority.MEDIUM,
                    test_level=request.test_specification.test_level,
                    steps=steps,
                    tags=["llm-generated", "functional"],
                    requirements=[f"Generated from JIRA ticket: {request.jira_ticket_id}"] if request.jira_ticket_id else [],
                    jira_ticket_id=request.jira_ticket_id
                )
                test_cases.append(test_case)
        
        # If no test cases found with new format, try old format
        if not test_cases:
            # Try old format parsing
            sections = re.split(r'\*\*Test Case \d+:', response)
            
            if len(sections) > 1:
                for i, section in enumerate(sections[1:], 1):
                    if not section.strip():
                        continue
                    
                    lines = section.strip().split('\n')
                    title = lines[0].strip() if lines else f"Test Case {i}"
                    title = re.sub(r'\*\*', '', title).strip()
                    
                    steps = []
                    step_number = 1
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith(("Given ", "When ", "Then ", "And ")):
                            keyword = line.split()[0]
                            action = line[len(keyword)+1:].strip()
                            
                            step = self._create_test_step(
                                step_number=step_number,
                                action=action,
                                expected_result="Step completed successfully" if keyword in ["Then", "And"] else "Precondition satisfied",
                                notes=f"{keyword} step"
                            )
                            steps.append(step)
                            step_number += 1
                    
                    if steps:
                        test_case = TestCase(
                            test_id=self._generate_test_id("TC"),
                            title=title,
                            description=f"Test case generated from LLM: {title}",
                            test_type=TestType.FUNCTIONAL,
                            priority=TestPriority.MEDIUM,
                            test_level=request.test_specification.test_level,
                            steps=steps,
                            tags=["llm-generated", "functional"],
                            requirements=[f"Generated from JIRA ticket: {request.jira_ticket_id}"] if request.jira_ticket_id else [],
                            jira_ticket_id=request.jira_ticket_id
                        )
                        test_cases.append(test_case)
        
        return test_cases
    
    def _parse_gherkin_response(self, response: str, request: TestCaseRequest) -> List[TestCase]:
        """Parse Gherkin format response from LLM."""
        test_cases = []
        
        # Remove markdown code blocks
        response = re.sub(r'```gherkin\n?', '', response)
        response = re.sub(r'```\n?', '', response)
        
        # Remove explanatory text before Gherkin content
        # Look for the first occurrence of "Feature:" or "Scenario:"
        feature_match = re.search(r'Feature:', response)
        scenario_match = re.search(r'Scenario:', response)
        
        if feature_match:
            response = response[feature_match.start():]
        elif scenario_match:
            response = response[scenario_match.start():]
        
        # Split by test case sections (look for **Test Case X:** patterns)
        test_case_sections = re.split(r'\*\*Test Case \d+:\s*', response)
        
        if len(test_case_sections) > 1:
            # Parse each test case section
            for i, section in enumerate(test_case_sections[1:], 1):  # Skip first empty section
                if not section.strip():
                    continue
                
                try:
                    test_case = self._parse_test_case_section(section, request, i)
                    if test_case:
                        test_cases.append(test_case)
                except Exception as e:
                    logger.warning(f"Failed to parse test case section {i}: {e}")
                    continue
        else:
            # Fallback to scenario-based parsing
            scenarios = re.split(r'\n\s*Scenario(?:\s+Outline)?:', response)
            
            # Also try splitting by "Scenario Outline:" specifically
            if len(scenarios) == 1 and "Scenario Outline:" in response:
                scenarios = re.split(r'\n\s*Scenario\s+Outline:', response)
            
            logger.debug(f"Found {len(scenarios)} scenario sections")
            
            for i, scenario in enumerate(scenarios):
                if not scenario.strip():
                    continue
                
                # Add "Scenario:" back if it was removed by split
                if i > 0:
                    scenario = "Scenario:" + scenario
                
                logger.debug(f"Processing scenario {i}: {scenario[:100]}...")
                
                try:
                    test_case = self._parse_gherkin_scenario(scenario, request)
                    if test_case:
                        test_cases.append(test_case)
                        logger.debug(f"Successfully parsed scenario {i}")
                    else:
                        logger.debug(f"Failed to parse scenario {i} - no test case returned")
                except Exception as e:
                    logger.warning(f"Failed to parse Gherkin scenario: {e}")
                    continue
        
        return test_cases
    
    def _parse_test_case_section(self, section: str, request: TestCaseRequest, case_number: int) -> Optional[TestCase]:
        """Parse a test case section from LLM response."""
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Extract title from first line, clean it up
        title = lines[0].strip()
        # Remove any markdown formatting
        title = re.sub(r'\*\*', '', title)
        title = re.sub(r'^#+\s*', '', title)
        title = title.strip()
        
        # Look for Gherkin content in the section
        gherkin_content = ""
        in_gherkin = False
        
        for line in lines:
            if "```gherkin" in line or "Feature:" in line:
                in_gherkin = True
                continue
            elif "```" in line and in_gherkin:
                break
            elif in_gherkin:
                gherkin_content += line + "\n"
        
        if not gherkin_content:
            return None
        
        # Parse the Gherkin content
        test_case = self._parse_gherkin_scenario(gherkin_content, request)
        if test_case:
            test_case.title = title
            test_case.description = f"Test case {case_number}: {title}"
        
        return test_case
    
    def _parse_gherkin_scenario(self, scenario: str, request: TestCaseRequest) -> Optional[TestCase]:
        """Parse a single Gherkin scenario into a TestCase."""
        lines = [line.strip() for line in scenario.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Extract scenario title - look for the first meaningful line
        title = "Test Scenario"
        for line in lines:
            if line and not line.startswith(("Given", "When", "Then", "And", "Examples:", "|", "Background:", "Feature:")):
                title = line
                break
        
        # Extract steps
        steps = []
        step_number = 1
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Skip Examples, Background, and other non-step lines
            if (line.startswith("Examples:") or line.startswith("|") or 
                line.startswith("Background:") or line.startswith("Feature:") or
                line.startswith("- ") or line.startswith("Reading:") or 
                line.startswith("Threshold:") or line.startswith("Sensor type:")):
                continue
            
            # Parse Given/When/Then/And steps
            if line.startswith(("Given ", "When ", "Then ", "And ")):
                keyword = line.split()[0]
                action = line[len(keyword)+1:].strip()  # Remove keyword and space
                
                # Handle "And" steps by using the previous keyword context
                if keyword == "And":
                    if steps:
                        keyword = "And"  # Keep as "And" for clarity
                    else:
                        keyword = "Given"  # Default to Given if no previous context
                
                step = self._create_test_step(
                    step_number=step_number,
                    action=action,
                    expected_result="Step completed successfully" if keyword in ["Then", "And"] else "Precondition satisfied",
                    notes=f"{keyword} step"
                )
                steps.append(step)
                step_number += 1
        
        if not steps:
            return None
        
        # Create test case
        test_case = TestCase(
            test_id=self._generate_test_id("TC"),
            title=title,
            description=f"Test case generated from LLM: {title}",
            test_type=TestType.FUNCTIONAL,
            priority=TestPriority.MEDIUM,
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=["llm-generated", "functional"],
            requirements=[f"Generated from JIRA ticket: {request.jira_ticket_id}"] if request.jira_ticket_id else [],
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
    
    def _parse_single_test_case(self, section: str, request: TestCaseRequest) -> Optional[TestCase]:
        """Parse a single test case from text."""
        # Basic parsing - specific generators should override this
        lines = section.strip().split('\n')
        
        if len(lines) < 3:  # Need at least title, description, and one step
            return None
        
        # Extract title (first line)
        title = lines[0].strip()
        if not title or title.startswith('#'):
            return None
        
        # Extract description (second line)
        description = lines[1].strip()
        
        # Extract steps (remaining lines)
        steps = []
        step_number = 1
        
        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue
            
            # Look for step patterns
            if re.match(r'^\d+\.', line) or re.match(r'^[-*•]', line):
                # Extract action and expected result
                parts = line.split(':', 1)
                if len(parts) == 2:
                    action = parts[0].lstrip('1234567890.-*• ').strip()
                    expected_result = parts[1].strip()
                    
                    steps.append(self._create_test_step(
                        step_number=step_number,
                        action=action,
                        expected_result=expected_result
                    ))
                    step_number += 1
        
        if not steps:
            return None
        
        # Create test case
        test_case = TestCase(
            test_id=self._generate_test_id(),
            title=title,
            description=description,
            test_type=self._determine_test_type(request, "functional"),
            priority=self._determine_test_priority(request, "functional"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "functional"),
            requirements=self._extract_requirements(request),
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
