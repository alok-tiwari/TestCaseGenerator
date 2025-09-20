"""Gherkin formatter for generating BDD-style test scenarios."""

import logging
from typing import List, Dict, Any, Optional

from models.test_models import TestCase, TestStep
from models.input_models import TestCaseRequest


logger = logging.getLogger(__name__)


class GherkinFormatter:
    """Formatter for generating Gherkin (BDD) test scenarios."""
    
    def __init__(self):
        """Initialize the Gherkin formatter."""
        self.feature_template = """Feature: {feature_name}
  As a {user_role}
  I want to {user_action}
  So that {user_value}

  Background:
    Given the system is in a known state

{scenarios}"""

        self.scenario_template = """
  Scenario: {scenario_title}
    {steps}"""

        self.scenario_outline_template = """
  Scenario Outline: {scenario_title}
    {steps}
    
    Examples:
      {examples_header}
      {examples_data}"""

        self.step_template = "    {keyword} {step_description}"
    
    def format_test_cases(self, test_cases: List[TestCase], request: TestCaseRequest) -> str:
        """Format test cases into Gherkin feature file format."""
        
        if not test_cases:
            return "# No test cases to format"
        
        try:
            # Extract feature information from the first test case or request
            feature_info = self._extract_feature_info(test_cases[0], request)
            
            # Generate scenarios
            scenarios = []
            for test_case in test_cases:
                scenario = self._format_scenario(test_case)
                if scenario:
                    scenarios.append(scenario)
            
            # Combine into feature file
            feature_content = self.feature_template.format(
                feature_name=feature_info["name"],
                user_role=feature_info["user_role"],
                user_action=feature_info["user_action"],
                user_value=feature_info["user_value"],
                scenarios="\n".join(scenarios)
            )
            
            return feature_content
            
        except Exception as e:
            logger.error(f"Error formatting test cases to Gherkin: {e}")
            return f"# Error formatting test cases: {e}"
    
    def _extract_feature_info(self, test_case: TestCase, request: TestCaseRequest) -> Dict[str, str]:
        """Extract feature information from test case and request."""
        
        # Try to extract from user story first
        if request.user_story:
            return {
                "name": f"{request.user_story.action}",
                "user_role": request.user_story.persona.replace("As a ", ""),
                "user_action": request.user_story.action.replace("I want to ", ""),
                "user_value": request.user_story.value.replace("So that ", "")
            }
        
        # Fallback to test case information
        if test_case.requirements:
            # Try to extract from requirements
            for req in test_case.requirements:
                if req.startswith("US:"):
                    # Parse user story from requirements
                    us_parts = req.replace("US: ", "").split(" - ")
                    if len(us_parts) >= 2:
                        return {
                            "name": us_parts[1],
                            "user_role": us_parts[0].replace("As a ", ""),
                            "user_action": us_parts[1].replace("I want to ", ""),
                            "user_value": "achieve the desired functionality"
                        }
        
        # Default feature information
        return {
            "name": test_case.title or "Test Feature",
            "user_role": "user",
            "user_action": "perform the required actions",
            "user_value": "achieve the desired functionality"
        }
    
    def _format_scenario(self, test_case: TestCase) -> Optional[str]:
        """Format a single test case into a Gherkin scenario."""
        
        try:
            # Check if this should be a scenario outline
            if self._should_be_scenario_outline(test_case):
                return self._format_scenario_outline(test_case)
            
            # Regular scenario
            steps = self._format_scenario_steps(test_case.steps)
            
            scenario_content = self.scenario_template.format(
                scenario_title=test_case.title,
                steps="\n".join(steps)
            )
            
            return scenario_content
            
        except Exception as e:
            logger.warning(f"Failed to format scenario {test_case.test_id}: {e}")
            return None
    
    def _should_be_scenario_outline(self, test_case: TestCase) -> bool:
        """Determine if a test case should be formatted as a scenario outline."""
        
        # Check if test case has multiple similar steps with different data
        if len(test_case.steps) < 2:
            return False
        
        # Look for patterns that suggest scenario outline
        step_actions = [step.action.lower() for step in test_case.steps]
        
        # Check for data-driven patterns
        data_patterns = [
            "test with", "verify with", "input", "enter", "select",
            "different", "various", "multiple", "range"
        ]
        
        for pattern in data_patterns:
            if any(pattern in action for action in step_actions):
                return True
        
        return False
    
    def _format_scenario_outline(self, test_case: TestCase) -> str:
        """Format a test case as a scenario outline."""
        
        # Extract data variations from test steps
        data_variations = self._extract_data_variations(test_case.steps)
        
        # Format steps with placeholders
        steps = self._format_scenario_outline_steps(test_case.steps)
        
        # Generate examples table
        examples_header, examples_data = self._generate_examples_table(data_variations)
        
        scenario_content = self.scenario_outline_template.format(
            scenario_title=test_case.title,
            steps="\n".join(steps),
            examples_header=examples_header,
            examples_data=examples_data
        )
        
        return scenario_content
    
    def _extract_data_variations(self, steps: List[TestStep]) -> List[Dict[str, str]]:
        """Extract data variations from test steps."""
        
        variations = []
        
        # Look for test data in steps
        for step in steps:
            if step.test_data:
                # Parse test data for variations
                data_parts = step.test_data.split(",")
                for i, part in enumerate(data_parts):
                    if i < len(variations):
                        variations[i][f"data_{len(variations[i])}"] = part.strip()
                    else:
                        variations.append({f"data_{len(variations)}": part.strip()})
        
        # If no variations found, create default ones
        if not variations:
            variations = [
                {"data_1": "valid data", "data_2": "expected result 1"},
                {"data_1": "invalid data", "data_2": "expected result 2"},
                {"data_1": "boundary data", "data_2": "expected result 3"}
            ]
        
        return variations
    
    def _format_scenario_outline_steps(self, steps: List[TestStep]) -> List[str]:
        """Format steps for scenario outline with placeholders."""
        
        formatted_steps = []
        
        for step in steps:
            # Replace specific data with placeholders
            step_text = step.action
            
            # Replace common data patterns with placeholders
            if step.test_data:
                step_text = step_text.replace(step.test_data, "<data_1>")
            
            # Add expected result placeholder if needed
            if "verify" in step.action.lower() or "check" in step.action.lower():
                step_text = f"{step_text} <data_2>"
            
            # Format the step
            keyword = self._get_step_keyword(step)
            formatted_step = self.step_template.format(
                keyword=keyword,
                step_description=step_text
            )
            
            formatted_steps.append(formatted_step)
        
        return formatted_steps
    
    def _generate_examples_table(self, data_variations: List[Dict[str, str]]) -> tuple:
        """Generate examples table for scenario outline."""
        
        if not data_variations:
            return "| data_1 | data_2 |", "| valid | expected |"
        
        # Get all unique keys
        all_keys = set()
        for variation in data_variations:
            all_keys.update(variation.keys())
        
        keys = sorted(list(all_keys))
        
        # Generate header
        header = "| " + " | ".join(keys) + " |"
        
        # Generate data rows
        data_rows = []
        for variation in data_variations:
            row_data = [variation.get(key, "") for key in keys]
            data_rows.append("| " + " | ".join(row_data) + " |")
        
        return header, "\n      ".join(data_rows)
    
    def _format_scenario_steps(self, steps: List[TestStep]) -> List[str]:
        """Format regular scenario steps."""
        
        formatted_steps = []
        
        for step in steps:
            keyword = self._get_step_keyword(step)
            
            # Format step description
            step_description = step.action
            
            # Add test data if available
            if step.test_data:
                step_description += f" with {step.test_data}"
            
            # Add expected result for verification steps
            if keyword == "Then" and step.expected_result:
                step_description += f" and {step.expected_result}"
            
            # Format the step
            formatted_step = self.step_template.format(
                keyword=keyword,
                step_description=step_description
            )
            
            formatted_steps.append(formatted_step)
        
        return formatted_steps
    
    def _get_step_keyword(self, step: TestStep) -> str:
        """Determine the appropriate Gherkin keyword for a step."""
        
        action_lower = step.action.lower()
        
        # Given steps (preconditions)
        given_keywords = [
            "ensure", "verify", "check", "confirm", "setup", "prepare",
            "create", "have", "exist", "available", "logged in"
        ]
        
        # When steps (actions)
        when_keywords = [
            "click", "enter", "select", "submit", "navigate", "perform",
            "execute", "run", "start", "initiate", "trigger", "send"
        ]
        
        # Then steps (verifications)
        then_keywords = [
            "should", "will", "must", "verify", "confirm", "check",
            "see", "display", "show", "appear", "receive", "get"
        ]
        
        # Determine step type based on action content
        if any(keyword in action_lower for keyword in given_keywords):
            return "Given"
        elif any(keyword in action_lower for keyword in when_keywords):
            return "When"
        elif any(keyword in action_lower for keyword in then_keywords):
            return "Then"
        else:
            # Default based on step number or content analysis
            if "verify" in action_lower or "check" in action_lower:
                return "Then"
            elif "ensure" in action_lower or "setup" in action_lower:
                return "Given"
            else:
                return "When"
    
    def format_single_test_case(self, test_case: TestCase) -> str:
        """Format a single test case as a standalone Gherkin scenario."""
        
        try:
            # Create a minimal feature for single test case
            feature_name = test_case.title or "Test Scenario"
            
            # Format the scenario
            scenario = self._format_scenario(test_case)
            if not scenario:
                return f"# Failed to format test case: {test_case.test_id}"
            
            # Create minimal feature
            feature_content = f"""Feature: {feature_name}

  Background:
    Given the system is in a known state

{scenario}"""
            
            return feature_content
            
        except Exception as e:
            logger.error(f"Error formatting single test case: {e}")
            return f"# Error formatting test case: {e}"
    
    def format_test_cases_by_type(self, test_cases: List[TestCase], request: TestCaseRequest) -> Dict[str, str]:
        """Format test cases grouped by type into separate feature files."""
        
        grouped_cases = {}
        
        # Group test cases by type
        for test_case in test_cases:
            test_type = test_case.test_type.value
            if test_type not in grouped_cases:
                grouped_cases[test_type] = []
            grouped_cases[test_type].append(test_case)
        
        # Format each group
        formatted_features = {}
        for test_type, cases in grouped_cases.items():
            feature_name = f"{test_type.title()} Test Cases"
            
            # Create a modified request for this group
            group_request = self._create_group_request(request, test_type)
            
            # Format the group
            formatted_content = self.format_test_cases(cases, group_request)
            
            # Add feature name header
            formatted_content = f"# {feature_name}\n\n{formatted_content}"
            
            formatted_features[test_type] = formatted_content
        
        return formatted_features
    
    def _create_group_request(self, original_request: TestCaseRequest, test_type: str) -> TestCaseRequest:
        """Create a modified request for a specific test type group."""
        
        # Create a copy of the original request with modified test specification
        from copy import deepcopy
        
        group_request = deepcopy(original_request)
        
        # Update test specification for the group
        group_request.test_specification.test_types = [test_type]
        group_request.test_specification.output_format = "gherkin"
        
        return group_request
    
    def add_gherkin_metadata(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add metadata comments to Gherkin content."""
        
        metadata_comments = []
        
        # Add basic metadata
        if "jira_ticket" in metadata:
            metadata_comments.append(f"# JIRA Ticket: {metadata['jira_ticket']}")
        
        if "test_level" in metadata:
            metadata_comments.append(f"# Test Level: {metadata['test_level']}")
        
        if "priority" in metadata:
            metadata_comments.append(f"# Priority: {metadata['priority']}")
        
        if "tags" in metadata:
            metadata_comments.append(f"# Tags: {', '.join(metadata['tags'])}")
        
        if "generated_at" in metadata:
            metadata_comments.append(f"# Generated: {metadata['generated_at']}")
        
        if "requirements" in metadata:
            metadata_comments.append(f"# Requirements: {', '.join(metadata['requirements'])}")
        
        # Add metadata to content
        if metadata_comments:
            metadata_header = "\n".join(metadata_comments)
            content = f"{metadata_header}\n\n{content}"
        
        return content
