"""Functional test generator for happy path and basic functionality testing."""

import logging
import re
from typing import List, Dict, Any, Optional

from .base_generator import BaseTestGenerator
from models.input_models import TestCaseRequest
from models.test_models import TestCase, TestStep, TestType, TestPriority


logger = logging.getLogger(__name__)


class FunctionalTestGenerator(BaseTestGenerator):
    """Generator for functional test cases focusing on happy path scenarios."""
    
    def __init__(self, llm_client):
        """Initialize the functional test generator."""
        super().__init__(llm_client)
        self.generator_type = "functional"
    
    async def generate(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate functional test cases for the given request."""
        
        logger.info(f"Generating functional test cases for request")
        
        try:
            # Generate test cases using LLM
            llm_response = await self._generate_with_llm(request, "functional_test")
            
            # Parse the response
            logger.info(f"LLM Response length: {len(llm_response)} characters")
            logger.debug(f"LLM Response: {llm_response[:500]}...")  # Log first 500 chars for debugging
            logger.debug(f"Full LLM Response: {llm_response}")  # Log full response for debugging
            
            test_cases = self._parse_llm_response(llm_response, request)
            logger.info(f"Parsed {len(test_cases)} test cases from LLM response")
            
            # If LLM parsing fails, generate fallback test cases
            if not test_cases:
                logger.warning("LLM parsing failed, generating fallback test cases")
                test_cases = self._generate_fallback_test_cases(request)
            
            # Enhance and validate test cases
            enhanced_cases = []
            for test_case in test_cases:
                enhanced_case = self._enhance_test_case(test_case, request)
                enhanced_case.test_type = TestType.FUNCTIONAL
                enhanced_case.priority = self._determine_test_priority(request, "functional")
                enhanced_case.tags = self._generate_tags(request, "functional")
                
                # Validate the test case
                validation = self._validate_test_case(enhanced_case)
                if validation["is_valid"]:
                    enhanced_cases.append(enhanced_case)
                else:
                    logger.warning(f"Test case validation failed: {validation['errors']}")
            
            # Log generation statistics
            self._log_generation_stats(enhanced_cases, request)
            
            return enhanced_cases
            
        except Exception as e:
            logger.error(f"Error generating functional test cases: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            # Return fallback test cases on error
            return self._generate_fallback_test_cases(request)
    
    def _generate_fallback_test_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate fallback test cases when LLM generation fails."""
        
        test_cases = []
        
        # Generate generic functional test cases based on acceptance criteria
        test_cases.extend(self._generate_generic_functional_cases(request))
        
        return test_cases
    
    
    def _generate_generic_functional_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate generic functional test cases when not IP validation specific."""
        test_cases = []
        
        # Generate test case for each acceptance criterion
        for i, criteria in enumerate(request.acceptance_criteria.criteria_list):
            test_case = self._create_functional_test_case(
                criteria, request, i + 1
            )
            test_cases.append(test_case)
        
        # Generate additional positive scenario test cases
        additional_cases = self._generate_additional_positive_cases(request)
        test_cases.extend(additional_cases)
        
        return test_cases
    
    def _create_functional_test_case(self, criteria: str, request: TestCaseRequest, 
                                   criteria_index: int) -> TestCase:
        """Create a functional test case from acceptance criteria."""
        
        # Parse the acceptance criteria
        parsed_criteria = self.acceptance_parser.parse_criteria(criteria)
        
        if parsed_criteria:
            # Use parsed criteria
            parsed = parsed_criteria[0]  # Take the first parsed result
            
            # Create test steps
            steps = []
            step_number = 1
            
            # Given step
            if parsed.given and parsed.given != "the system is in a known state":
                steps.append(self._create_test_step(
                    step_number=step_number,
                    action=f"Ensure {parsed.given}",
                    expected_result="System is in the required state",
                    notes="Precondition setup"
                ))
                step_number += 1
            
            # When step
            steps.append(self._create_test_step(
                step_number=step_number,
                action=parsed.when,
                expected_result=parsed.then,
                notes="Main test action"
            ))
            
            # Create test case
            test_case = TestCase(
                test_id=self._generate_test_id("FUNC"),
                title=f"Verify {parsed.when} - {parsed.then}",
                description=f"Test case for acceptance criteria {criteria_index}: {criteria}",
                test_type=TestType.FUNCTIONAL,
                priority=self._determine_test_priority(request, "functional"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "functional"),
                requirements=[f"AC-{criteria_index:02d}: {criteria}"],
                jira_ticket_id=request.jira_ticket_id
            )
            
        else:
            # Fallback: create simple test case
            steps = [
                self._create_test_step(
                    step_number=1,
                    action=f"Execute the requirement: {criteria}",
                    expected_result="Requirement is satisfied successfully",
                    notes="Basic functional verification"
                )
            ]
            
            test_case = TestCase(
                test_id=self._generate_test_id("FUNC"),
                title=f"Functional Test for Criteria {criteria_index}",
                description=f"Basic functional test for: {criteria}",
                test_type=TestType.FUNCTIONAL,
                priority=self._determine_test_priority(request, "functional"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "functional"),
                requirements=[f"AC-{criteria_index:02d}: {criteria}"],
                jira_ticket_id=request.jira_ticket_id
            )
        
        return test_case
    
    def _generate_additional_positive_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate additional positive scenario test cases."""
        
        additional_cases = []
        
        # Generate test case for user story if available
        if request.user_story:
            user_story_case = self._create_user_story_test_case(request)
            additional_cases.append(user_story_case)
        
        # Generate test case for system context if available
        if request.system_context:
            context_case = self._create_system_context_test_case(request)
            additional_cases.append(context_case)
        
        # Generate boundary value test cases
        boundary_cases = self._generate_boundary_value_cases(request)
        additional_cases.extend(boundary_cases)
        
        return additional_cases
    
    def _create_user_story_test_case(self, request: TestCaseRequest) -> TestCase:
        """Create a test case based on the user story."""
        
        user_story = request.user_story
        
        # Create test steps based on user story
        steps = [
            self._create_test_step(
                step_number=1,
                action=f"Verify user persona: {user_story.persona}",
                expected_result="User has the correct role and permissions",
                notes="User setup verification"
            ),
            self._create_test_step(
                step_number=2,
                action=f"Execute action: {user_story.action}",
                expected_result="Action completes successfully",
                notes="Main functionality test"
            ),
            self._create_test_step(
                step_number=3,
                action=f"Verify business value: {user_story.value}",
                expected_result="Business value is achieved",
                notes="Value verification"
            )
        ]
        
        test_case = TestCase(
            test_id=self._generate_test_id("US"),
            title=f"User Story Test: {user_story.action}",
            description=f"Test case covering the complete user story: {user_story.persona} - {user_story.action} - {user_story.value}",
            test_type=TestType.FUNCTIONAL,
            priority=self._determine_test_priority(request, "functional"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "functional") + ["user-story"],
            requirements=[f"US: {user_story.persona} - {user_story.action}"],
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
    
    def _create_system_context_test_case(self, request: TestCaseRequest) -> TestCase:
        """Create a test case based on system context."""
        
        system_context = request.system_context
        
        # Create test steps based on system context
        steps = []
        step_number = 1
        
        if system_context.tech_stack:
            steps.append(self._create_test_step(
                step_number=step_number,
                action="Verify technology stack compatibility",
                expected_result=f"System works with: {', '.join(system_context.tech_stack[:3])}",
                notes="Technology compatibility check"
            ))
            step_number += 1
        
        if system_context.user_roles:
            steps.append(self._create_test_step(
                step_number=step_number,
                action="Verify user role functionality",
                expected_result=f"All user roles work correctly: {', '.join(system_context.user_roles[:3])}",
                notes="Role-based functionality verification"
            ))
            step_number += 1
        
        if system_context.constraints:
            steps.append(self._create_test_step(
                step_number=step_number,
                action="Verify system constraints",
                expected_result=f"System meets constraints: {', '.join(system_context.constraints[:3])}",
                notes="Constraint compliance check"
            ))
        
        if not steps:
            # Fallback step
            steps = [
                self._create_test_step(
                    step_number=1,
                    action="Verify system context requirements",
                    expected_result="System context requirements are satisfied",
                    notes="System context verification"
                )
            ]
        
        test_case = TestCase(
            test_id=self._generate_test_id("CTX"),
            title="System Context Verification Test",
            description="Test case covering system context requirements and constraints",
            test_type=TestType.FUNCTIONAL,
            priority=self._determine_test_priority(request, "functional"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "functional") + ["system-context"],
            requirements=["System context requirements"],
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
    
    def _generate_boundary_value_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate boundary value test cases."""
        
        boundary_cases = []
        
        # Extract numeric values from acceptance criteria
        numeric_values = self._extract_numeric_values(request.acceptance_criteria.criteria_list)
        
        for value_info in numeric_values:
            boundary_case = self._create_boundary_value_test_case(value_info, request)
            if boundary_case:
                boundary_cases.append(boundary_case)
        
        return boundary_cases
    
    def _extract_numeric_values(self, criteria_list: List[str]) -> List[Dict[str, Any]]:
        """Extract numeric values from acceptance criteria."""
        
        numeric_values = []
        
        # Patterns for numeric values
        patterns = [
            r'(\d+)\s+users?',  # "100 users"
            r'(\d+)\s+characters?',  # "50 characters"
            r'(\d+)\s+items?',  # "25 items"
            r'(\d+)\s+seconds?',  # "30 seconds"
            r'(\d+)\s+minutes?',  # "5 minutes"
            r'(\d+)\s+hours?',  # "2 hours"
            r'(\d+)\s+days?',  # "7 days"
            r'(\d+)\s+bytes?',  # "1024 bytes"
            r'(\d+)\s+MB',  # "100 MB"
            r'(\d+)\s+GB',  # "1 GB"
        ]
        
        for criteria in criteria_list:
            for pattern in patterns:
                matches = re.finditer(pattern, criteria, re.IGNORECASE)
                for match in matches:
                    value = int(match.group(1))
                    unit = match.group(0).split()[1] if len(match.group(0).split()) > 1 else "units"
                    
                    numeric_values.append({
                        "value": value,
                        "unit": unit,
                        "criteria": criteria,
                        "context": match.group(0)
                    })
        
        return numeric_values
    
    def _create_boundary_value_test_case(self, value_info: Dict[str, Any], 
                                       request: TestCaseRequest) -> Optional[TestCase]:
        """Create a boundary value test case."""
        
        value = value_info["value"]
        unit = value_info["unit"]
        context = value_info["context"]
        
        # Generate boundary values
        boundary_values = [
            value - 1,  # Just below boundary
            value,      # At boundary
            value + 1   # Just above boundary
        ]
        
        # Create test steps for boundary values
        steps = []
        step_number = 1
        
        for boundary_value in boundary_values:
            if boundary_value >= 0:  # Avoid negative values for most contexts
                steps.append(self._create_test_step(
                    step_number=step_number,
                    action=f"Test with {boundary_value} {unit}",
                    expected_result=f"System handles {boundary_value} {unit} correctly",
                    notes=f"Boundary value testing for {context}"
                ))
                step_number += 1
        
        if not steps:
            return None
        
        test_case = TestCase(
            test_id=self._generate_test_id("BND"),
            title=f"Boundary Value Test: {context}",
            description=f"Test case for boundary values around {context}",
            test_type=TestType.FUNCTIONAL,
            priority=self._determine_test_priority(request, "functional"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "functional") + ["boundary-values"],
            requirements=[f"Boundary testing for {context}"],
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
    
    def _parse_llm_response(self, response: str, request: TestCaseRequest) -> List[TestCase]:
        """Parse LLM response for functional test cases."""
        
        test_cases = []
        
        try:
            logger.info("Starting functional LLM response parsing")
            
            # Parse the simple TEST_CASE_X format (with optional quotes around title)
            test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\n\nTEST_CASE_|\Z)'
            matches = re.findall(test_case_pattern, response, re.DOTALL)
            
            logger.info(f"First pattern found {len(matches)} matches")
            
            # If no matches, try with single newline between title and GIVEN
            if not matches:
                test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\nTEST_CASE_|\Z)'
                matches = re.findall(test_case_pattern, response, re.DOTALL)
                logger.info(f"First-b pattern found {len(matches)} matches")
            
            # If no matches, try a simpler pattern
            if not matches:
                test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\nTEST_CASE_|\Z)'
                matches = re.findall(test_case_pattern, response, re.DOTALL)
                logger.info(f"Second pattern found {len(matches)} matches")
            
            # If still no matches, try with no newline between title and GIVEN
            if not matches:
                test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*GIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\nTEST_CASE_|\Z)'
                matches = re.findall(test_case_pattern, response, re.DOTALL)
                logger.info(f"Third pattern found {len(matches)} matches")
            
            # If still no matches, try with double newline between title and GIVEN
            if not matches:
                test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*\n\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\n\nTEST_CASE_|\Z)'
                matches = re.findall(test_case_pattern, response, re.DOTALL)
                logger.info(f"Fourth pattern found {len(matches)} matches")
            
            # If still no matches, try with exact format from LLM (double newline, space after GIVEN)
            if not matches:
                test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*\n\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\n\nTEST_CASE_|\Z)'
                matches = re.findall(test_case_pattern, response, re.DOTALL)
                logger.info(f"Fifth pattern found {len(matches)} matches")
            
            # If still no matches, try with simpler lookahead
            if not matches:
                test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*\n\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\n\n|\Z)'
                matches = re.findall(test_case_pattern, response, re.DOTALL)
                logger.info(f"Sixth pattern found {len(matches)} matches")
            
            # If still no matches, try with more flexible pattern that handles mixed formats
            if not matches:
                # Split by TEST_CASE_ and parse each section individually
                sections = re.split(r'TEST_CASE_(\d+):', response)
                if len(sections) > 1:
                    for i in range(1, len(sections), 2):
                        if i + 1 < len(sections):
                            case_num = sections[i]
                            content = sections[i + 1]
                            
                            # Try to extract title and GIVEN/WHEN/THEN
                            title_match = re.search(r'^([^\n]+)', content.strip())
                            if title_match:
                                title = title_match.group(1).strip()
                                
                                # Look for GIVEN/WHEN/THEN pattern
                                given_match = re.search(r'GIVEN\s+(.+?)(?=\nWHEN|\Z)', content, re.DOTALL)
                                when_match = re.search(r'WHEN\s+(.+?)(?=\nTHEN|\Z)', content, re.DOTALL)
                                then_match = re.search(r'THEN\s+(.+?)(?=\n\n|\Z)', content, re.DOTALL)
                                
                                if given_match and when_match and then_match:
                                    given = given_match.group(1).strip()
                                    when = when_match.group(1).strip()
                                    then = then_match.group(1).strip()
                                    matches.append((case_num, title, given, when, then))
                
                logger.info(f"Flexible pattern found {len(matches)} matches")
            
            
            logger.info(f"Total matches found: {len(matches)}")
            
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
                logger.info("No matches with new format, trying old format")
                sections = response.split('\n\n')
                
                for section in sections:
                    if not section.strip():
                        continue
                    
                    try:
                        test_case = self._parse_functional_test_case(section, request)
                        if test_case:
                            test_cases.append(test_case)
                    except Exception as e:
                        logger.warning(f"Failed to parse functional test case section: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error in functional LLM response parsing: {e}")
        
        return test_cases
    
    def _parse_functional_test_case(self, section: str, request: TestCaseRequest) -> Optional[TestCase]:
        """Parse a functional test case from text."""
        
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
            test_id=self._generate_test_id("FUNC"),
            title=title,
            description=description,
            test_type=TestType.FUNCTIONAL,
            priority=self._determine_test_priority(request, "functional"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "functional"),
            requirements=self._extract_requirements(request),
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
