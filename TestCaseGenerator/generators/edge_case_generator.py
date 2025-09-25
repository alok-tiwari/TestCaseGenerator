"""Edge case generator for boundary conditions, negative scenarios, and error cases."""

import logging
import re
from typing import List, Dict, Any, Optional

from .base_generator import BaseTestGenerator
from models.input_models import TestCaseRequest
from models.test_models import TestCase, TestStep, TestType, TestPriority


logger = logging.getLogger(__name__)


class EdgeCaseGenerator(BaseTestGenerator):
    """Generator for edge case test scenarios focusing on boundary conditions and error cases."""
    
    def __init__(self, llm_client):
        """Initialize the edge case generator."""
        super().__init__(llm_client)
        self.generator_type = "edge_case"
    
    async def generate(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate edge case test scenarios for the given request."""
        
        logger.info(f"Generating edge case test scenarios for request")
        
        try:
            # Generate test cases using LLM
            llm_response = await self._generate_with_llm(request, "edge_case_test")
            
            # Debug logging
            logger.info(f"LLM Response length: {len(llm_response)} characters")
            logger.debug(f"LLM Response: {llm_response[:500]}...")
            
            # Parse the response
            test_cases = self._parse_llm_response(llm_response, request)
            
            # If LLM parsing fails, generate fallback test cases
            if not test_cases:
                logger.warning("LLM parsing failed, generating fallback edge case test scenarios")
                test_cases = self._generate_fallback_edge_cases(request)
            
            # Enhance and validate test cases
            enhanced_cases = []
            for test_case in test_cases:
                enhanced_case = self._enhance_test_case(test_case, request)
                enhanced_case.test_type = TestType.EDGE  # Edge cases are edge tests
                enhanced_case.priority = self._determine_test_priority(request, "edge_case")
                enhanced_case.tags = self._generate_tags(request, "edge_case")
                
                # Validate the test case
                validation = self._validate_test_case(enhanced_case)
                if validation["is_valid"]:
                    enhanced_cases.append(enhanced_case)
                else:
                    logger.warning(f"Edge case test validation failed: {validation['errors']}")
            
            # Log generation statistics
            self._log_generation_stats(enhanced_cases, request)
            
            return enhanced_cases
            
        except Exception as e:
            logger.error(f"Error generating edge case test scenarios: {e}")
            # Return fallback test cases on error
            return self._generate_fallback_edge_cases(request)
    
    def _generate_fallback_edge_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate fallback edge case test scenarios when LLM generation fails."""
        
        test_cases = []
        
        # Generate generic edge cases based on acceptance criteria
        test_cases.extend(self._generate_generic_edge_cases(request))
        
        return test_cases
    
    
    def _generate_generic_edge_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate generic edge cases when not IP validation specific."""
        edge_cases = []
        
        # Generate boundary value test cases
        boundary_cases = self._generate_boundary_value_cases(request)
        edge_cases.extend(boundary_cases)
        
        # Generate negative scenario test cases
        negative_cases = self._generate_negative_scenario_cases(request)
        edge_cases.extend(negative_cases)
        
        # Generate error handling test cases
        error_cases = self._generate_error_handling_cases(request)
        edge_cases.extend(error_cases)
        
        # Generate data edge case test cases
        data_edge_cases = self._generate_data_edge_cases(request)
        edge_cases.extend(data_edge_cases)
        
        # Generate performance edge case test cases
        performance_cases = self._generate_performance_edge_cases(request)
        edge_cases.extend(performance_cases)
        
        return edge_cases
    
    def _generate_boundary_value_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate boundary value test cases."""
        
        boundary_cases = []
        
        # Extract numeric values from acceptance criteria
        numeric_values = self._extract_numeric_values(request.acceptance_criteria.criteria_list)
        
        for value_info in numeric_values:
            boundary_case = self._create_boundary_value_test_case(value_info, request)
            if boundary_case:
                boundary_cases.append(boundary_case)
        
        # Generate string length boundary cases
        string_boundary_cases = self._generate_string_boundary_cases(request)
        boundary_cases.extend(string_boundary_cases)
        
        return boundary_cases
    
    def _create_boundary_value_test_case(self, value_info: Dict[str, Any], 
                                       request: TestCaseRequest) -> Optional[TestCase]:
        """Create a boundary value test case."""
        
        value = value_info["value"]
        unit = value_info["unit"]
        context = value_info["context"]
        
        # Generate boundary values including edge cases
        boundary_values = [
            0,                    # Zero value
            value - 1,           # Just below boundary
            value,               # At boundary
            value + 1,           # Just above boundary
            value * 2,           # Double the boundary
            value * 10,          # 10x the boundary
            -1,                  # Negative value
            -value               # Negative boundary
        ]
        
        # Create test steps for boundary values
        steps = []
        step_number = 1
        
        for boundary_value in boundary_values:
            steps.append(self._create_test_step(
                step_number=step_number,
                action=f"Test with {boundary_value} {unit}",
                expected_result=f"System handles {boundary_value} {unit} appropriately",
                notes=f"Edge case testing for {context} - value: {boundary_value}"
            ))
            step_number += 1
        
        test_case = TestCase(
            test_id=self._generate_test_id("EDGE-BND"),
            title=f"Boundary Value Edge Case Test: {context}",
            description=f"Edge case test scenarios for boundary values around {context}",
            test_type=TestType.EDGE,
            priority=self._determine_test_priority(request, "edge_case"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "edge_case") + ["boundary-values", "edge-cases"],
            requirements=[f"Edge case testing for {context}"],
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
    
    def _generate_string_boundary_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate string length boundary test cases."""
        
        string_cases = []
        
        # Common string length boundaries
        string_boundaries = [
            {"name": "Empty String", "value": "", "description": "Zero length string"},
            {"name": "Single Character", "value": "a", "description": "One character string"},
            {"name": "Short String", "value": "test", "description": "Short string"},
            {"name": "Long String", "value": "a" * 1000, "description": "Very long string"},
            {"name": "Special Characters", "value": "!@#$%^&*()_+-=[]{}|;':\",./<>?", "description": "Special characters"},
            {"name": "Unicode Characters", "value": "🚀🌟🎉", "description": "Unicode characters"},
            {"name": "HTML Tags", "value": "<script>alert('test')</script>", "description": "HTML/script tags"},
            {"name": "SQL Injection", "value": "'; DROP TABLE users; --", "description": "SQL injection attempt"},
            {"name": "XSS Payload", "value": "<img src=x onerror=alert(1)>", "description": "XSS payload"},
            {"name": "Null Characters", "value": "test\0string", "description": "String with null characters"}
        ]
        
        for boundary in string_boundaries:
            steps = [
                self._create_test_step(
                    step_number=1,
                    action=f"Input string: {boundary['name']}",
                    expected_result=f"System handles {boundary['description']} appropriately",
                    notes=f"Edge case: {boundary['value'][:50]}..."
                )
            ]
            
            test_case = TestCase(
                test_id=self._generate_test_id("EDGE-STR"),
                title=f"String Edge Case: {boundary['name']}",
                description=f"Test system behavior with {boundary['description']}",
                test_type=TestType.EDGE,
                priority=self._determine_test_priority(request, "edge_case"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "edge_case") + ["string-edge-cases", "input-validation"],
                requirements=["String input edge case testing"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            string_cases.append(test_case)
        
        return string_cases
    
    def _generate_negative_scenario_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate negative scenario test cases."""
        
        negative_cases = []
        
        # Generate negative test cases for each acceptance criterion
        for i, criteria in enumerate(request.acceptance_criteria.criteria_list):
            negative_case = self._create_negative_scenario_case(criteria, request, i + 1)
            if negative_case:
                negative_cases.append(negative_case)
        
        # Generate common negative scenarios
        common_negative_cases = self._generate_common_negative_cases(request)
        negative_cases.extend(common_negative_cases)
        
        return negative_cases
    
    def _create_negative_scenario_case(self, criteria: str, request: TestCaseRequest, 
                                     criteria_index: int) -> Optional[TestCase]:
        """Create a negative scenario test case from acceptance criteria."""
        
        # Parse the acceptance criteria
        parsed_criteria = self.acceptance_parser.parse_criteria(criteria)
        
        if parsed_criteria:
            parsed = parsed_criteria[0]
            
            # Create negative test steps
            steps = [
                self._create_test_step(
                    step_number=1,
                    action=f"Ensure system is NOT in state: {parsed.given}",
                    expected_result="System is in a different state",
                    notes="Negative precondition setup"
                ),
                self._create_test_step(
                    step_number=2,
                    action=f"Attempt to {parsed.when}",
                    expected_result="System rejects the action appropriately",
                    notes="Negative action test"
                ),
                self._create_test_step(
                    step_number=3,
                    action="Verify error handling",
                    expected_result="System provides appropriate error message",
                    notes="Error handling verification"
                )
            ]
            
            test_case = TestCase(
                test_id=self._generate_test_id("EDGE-NEG"),
                title=f"Negative Scenario: {parsed.when} without proper preconditions",
                description=f"Negative test case for acceptance criteria {criteria_index}: {criteria}",
                test_type=TestType.EDGE,
                priority=self._determine_test_priority(request, "edge_case"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "edge_case") + ["negative-scenarios", "error-handling"],
                requirements=[f"AC-{criteria_index:02d}: {criteria}"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            return test_case
        
        return None
    
    def _generate_common_negative_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate common negative scenario test cases."""
        
        common_cases = []
        
        # Common negative scenarios
        negative_scenarios = [
            {
                "title": "Invalid Authentication",
                "description": "Test system behavior with invalid credentials",
                "steps": [
                    "Enter invalid username/password",
                    "Submit login form",
                    "Verify appropriate error message"
                ]
            },
            {
                "title": "Unauthorized Access",
                "description": "Test access control with insufficient permissions",
                "steps": [
                    "Login with limited user role",
                    "Attempt to access restricted functionality",
                    "Verify access is denied"
                ]
            },
            {
                "title": "Invalid Input Data",
                "description": "Test system behavior with invalid input data",
                "steps": [
                    "Enter invalid data in form fields",
                    "Submit the form",
                    "Verify validation errors are displayed"
                ]
            },
            {
                "title": "Network Failure",
                "description": "Test system behavior during network failures",
                "steps": [
                    "Simulate network disconnection",
                    "Attempt to perform operations",
                    "Verify graceful degradation"
                ]
            },
            {
                "title": "Concurrent Access",
                "description": "Test system behavior with concurrent users",
                "steps": [
                    "Simulate multiple users accessing same resource",
                    "Perform conflicting operations",
                    "Verify data consistency is maintained"
                ]
            }
        ]
        
        for scenario in negative_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="System handles the scenario appropriately",
                    notes=f"Negative scenario: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("EDGE-COM"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.EDGE,
                priority=self._determine_test_priority(request, "edge_case"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "edge_case") + ["common-negative", "system-resilience"],
                requirements=["Common negative scenario testing"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            common_cases.append(test_case)
        
        return common_cases
    
    def _generate_error_handling_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate error handling test cases."""
        
        error_cases = []
        
        # Common error scenarios
        error_scenarios = [
            {
                "title": "Database Connection Failure",
                "description": "Test system behavior when database is unavailable",
                "steps": [
                    "Simulate database connection failure",
                    "Attempt to perform database operations",
                    "Verify appropriate error handling"
                ]
            },
            {
                "title": "File Upload Errors",
                "description": "Test system behavior with invalid file uploads",
                "steps": [
                    "Attempt to upload invalid file types",
                    "Attempt to upload oversized files",
                    "Attempt to upload corrupted files",
                    "Verify appropriate error messages"
                ]
            },
            {
                "title": "API Rate Limiting",
                "description": "Test system behavior when API rate limits are exceeded",
                "steps": [
                    "Exceed API rate limits",
                    "Verify rate limiting is enforced",
                    "Verify appropriate error responses"
                ]
            },
            {
                "title": "Session Timeout",
                "description": "Test system behavior when user sessions expire",
                "steps": [
                    "Wait for session to expire",
                    "Attempt to perform operations",
                    "Verify user is redirected to login"
                ]
            }
        ]
        
        for scenario in error_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="System handles errors gracefully",
                    notes=f"Error handling: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("EDGE-ERR"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.EDGE,
                priority=self._determine_test_priority(request, "edge_case"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "edge_case") + ["error-handling", "system-reliability"],
                requirements=["Error handling verification"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            error_cases.append(test_case)
        
        return error_cases
    
    def _generate_data_edge_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate data edge case test scenarios."""
        
        data_cases = []
        
        # Data edge case scenarios
        data_scenarios = [
            {
                "title": "Empty Data Sets",
                "description": "Test system behavior with empty data",
                "steps": [
                    "Create empty data set",
                    "Perform operations on empty data",
                    "Verify appropriate handling"
                ]
            },
            {
                "title": "Large Data Sets",
                "description": "Test system behavior with very large data",
                "steps": [
                    "Create large data set",
                    "Perform operations on large data",
                    "Verify performance and memory usage"
                ]
            },
            {
                "title": "Special Characters in Data",
                "description": "Test system behavior with special characters",
                "steps": [
                    "Include special characters in data",
                    "Perform operations on data",
                    "Verify data integrity is maintained"
                ]
            },
            {
                "title": "Data Type Mismatches",
                "description": "Test system behavior with wrong data types",
                "steps": [
                    "Provide wrong data type for fields",
                    "Attempt to process data",
                    "Verify appropriate error handling"
                ]
            }
        ]
        
        for scenario in data_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="System handles data edge cases appropriately",
                    notes=f"Data edge case: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("EDGE-DATA"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.EDGE,
                priority=self._determine_test_priority(request, "edge_case"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "edge_case") + ["data-edge-cases", "data-integrity"],
                requirements=["Data edge case testing"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            data_cases.append(test_case)
        
        return data_cases
    
    def _generate_performance_edge_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate performance edge case test scenarios."""
        
        performance_cases = []
        
        # Performance edge case scenarios
        performance_scenarios = [
            {
                "title": "High Load Conditions",
                "description": "Test system behavior under high load",
                "steps": [
                    "Simulate high user load",
                    "Monitor system performance",
                    "Verify system remains responsive"
                ]
            },
            {
                "title": "Memory Pressure",
                "description": "Test system behavior under memory pressure",
                "steps": [
                    "Simulate low memory conditions",
                    "Perform memory-intensive operations",
                    "Verify graceful degradation"
                ]
            },
            {
                "title": "Slow Network Conditions",
                "description": "Test system behavior with slow network",
                "steps": [
                    "Simulate slow network conditions",
                    "Perform network operations",
                    "Verify timeout handling"
                ]
            },
            {
                "title": "Resource Exhaustion",
                "description": "Test system behavior when resources are exhausted",
                "steps": [
                    "Exhaust system resources",
                    "Attempt to perform operations",
                    "Verify appropriate error handling"
                ]
            }
        ]
        
        for scenario in performance_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="System handles performance edge cases appropriately",
                    notes=f"Performance edge case: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("EDGE-PERF"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.EDGE,
                priority=self._determine_test_priority(request, "edge_case"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "edge_case") + ["performance-edge-cases", "system-performance"],
                requirements=["Performance edge case testing"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            performance_cases.append(test_case)
        
        return performance_cases
    
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
            r'(\d+)\s+percent',  # "95 percent"
            r'(\d+)\s+times?',  # "3 times"
            r'(\d+)\s+attempts?',  # "5 attempts"
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
    
    def _parse_llm_response(self, response: str, request: TestCaseRequest) -> List[TestCase]:
        """Parse LLM response for edge case test scenarios."""
        
        test_cases = []
        
        try:
            logger.info("Starting edge case LLM response parsing")
            
            # Parse the simple TEST_CASE_X format (with optional quotes around title)
            test_case_pattern = r'TEST_CASE_(\d+):\s*"?([^"]+)"?\s*\nGIVEN\s+(.+?)\nWHEN\s+(.+?)\nTHEN\s+(.+?)(?=\n\nTEST_CASE_|\Z)'
            matches = re.findall(test_case_pattern, response, re.DOTALL)
            
            logger.info(f"First pattern found {len(matches)} matches")
            
            # If no matches, try a simpler pattern (without double newline before GIVEN)
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
            
            # If still no matches, try with more flexible pattern that handles the actual LLM output format
            if not matches:
                # Split by TEST_CASE_ and parse each section individually
                sections = re.split(r'TEST_CASE_(\d+):', response)
                if len(sections) > 1:
                    for i in range(1, len(sections), 2):
                        if i + 1 < len(sections):
                            case_num = sections[i]
                            content = sections[i + 1]
                            
                            # Try to extract title and GIVEN/WHEN/THEN
                            title_match = re.search(r'^"?([^"]+)"?\s*$', content.strip().split('\n')[0])
                            if title_match:
                                title = title_match.group(1).strip()
                                
                                # Look for GIVEN/WHEN/THEN pattern
                                given_match = re.search(r'GIVEN:\s*(.+?)(?=\nWHEN|\Z)', content, re.DOTALL)
                                when_match = re.search(r'WHEN:\s*(.+?)(?=\nTHEN|\Z)', content, re.DOTALL)
                                then_match = re.search(r'THEN:\s*(.+?)(?=\n\n|\Z)', content, re.DOTALL)
                                
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
                        test_id=self._generate_test_id("EDGE"),
                        title=title,
                        description=f"Edge case test generated from LLM: {title}",
                        test_type=TestType.EDGE,
                        priority=TestPriority.MEDIUM,
                        test_level=request.test_specification.test_level,
                        steps=steps,
                        tags=["llm-generated", "edge-case"],
                        requirements=[f"Generated from JIRA ticket: {request.jira_ticket_id}"] if request.jira_ticket_id else [],
                        jira_ticket_id=request.jira_ticket_id
                    )
                    test_cases.append(test_case)
            
            # If no test cases found with new format, try old format
            if not test_cases:
                logger.info("No matches with new format, trying old format")
                # Split response into test case sections
                sections = response.split('\n\n')
                
                for section in sections:
                    if not section.strip():
                        continue
                    
                    try:
                        test_case = self._parse_edge_case_test(section, request)
                        if test_case:
                            test_cases.append(test_case)
                    except Exception as e:
                        logger.warning(f"Failed to parse edge case test section: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error in edge case LLM response parsing: {e}")
        
        return test_cases
    
    def _parse_edge_case_test(self, section: str, request: TestCaseRequest) -> Optional[TestCase]:
        """Parse an edge case test from text."""
        
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
            test_id=self._generate_test_id("EDGE"),
            title=title,
            description=description,
            test_type=TestType.EDGE,
            priority=self._determine_test_priority(request, "edge_case"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "edge_case"),
            requirements=self._extract_requirements(request),
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
