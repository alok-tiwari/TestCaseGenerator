"""Step-driven formatter for generating structured test cases with detailed steps and test data."""

import logging
from typing import List, Dict, Any, Optional

from models.test_models import TestCase, TestStep
from models.input_models import TestCaseRequest


logger = logging.getLogger(__name__)


class StepDrivenFormatter:
    """Formatter for generating step-driven test cases with detailed test data."""
    
    def __init__(self):
        """Initialize the step-driven formatter."""
        pass
    
    def format_test_cases(self, test_cases: List[TestCase], request: TestCaseRequest) -> str:
        """Format test cases into step-driven format."""
        
        if not test_cases:
            return "No test cases to format."
        
        formatted_cases = []
        
        for test_case in test_cases:
            formatted_case = self._format_single_test_case(test_case)
            formatted_cases.append(formatted_case)
        
        return "\n\n".join(formatted_cases)
    
    def _format_single_test_case(self, test_case: TestCase) -> str:
        """Format a single test case into step-driven format."""
        
        # Extract test data from steps
        test_data = self._extract_test_data(test_case.steps)
        
        # Format steps
        steps_text = self._format_steps(test_case.steps)
        
        # Create the formatted test case
        formatted = f"""Test Case ID: {test_case.test_id}
Test Case Name: {test_case.title}
Steps:
{steps_text}
Test Data: {test_data}
Expected Result: {self._extract_expected_result(test_case.steps)}
Actual Result:"""
        
        return formatted
    
    def _format_steps(self, steps: List[TestStep]) -> str:
        """Format test steps into numbered list."""
        
        if not steps:
            return "\t1.\tNo steps defined"
        
        formatted_steps = []
        for i, step in enumerate(steps, 1):
            # Combine action and expected result for step description
            step_desc = step.action
            if step.expected_result and step.expected_result != "Precondition satisfied" and step.expected_result != "Action completed" and step.expected_result != "Expected result achieved":
                step_desc += f" - {step.expected_result}"
            
            formatted_steps.append(f"\t{i}.\t{step_desc}")
        
        return "\n".join(formatted_steps)
    
    def _extract_test_data(self, steps: List[TestStep]) -> str:
        """Extract test data from steps."""
        
        test_data_items = []
        
        for step in steps:
            # Look for numeric values, inputs, or specific data in the action
            action = step.action.lower()
            
            # Extract common test data patterns
            if "gain" in action and "=" in action:
                # Extract gain value
                import re
                gain_match = re.search(r'gain\s*=\s*(\d+)', action, re.IGNORECASE)
                if gain_match:
                    test_data_items.append(f"Gain = {gain_match.group(1)}")
            
            if "offset" in action and "=" in action:
                # Extract offset value
                import re
                offset_match = re.search(r'offset\s*=\s*(\d+)', action, re.IGNORECASE)
                if offset_match:
                    test_data_items.append(f"Offset = {offset_match.group(1)}")
            
            if "raw" in action and "=" in action:
                # Extract raw value
                import re
                raw_match = re.search(r'raw\s*=\s*(\d+)', action, re.IGNORECASE)
                if raw_match:
                    test_data_items.append(f"Raw = {raw_match.group(1)}")
            
            if "value" in action and "=" in action:
                # Extract value
                import re
                value_match = re.search(r'value\s*=\s*(\d+)', action, re.IGNORECASE)
                if value_match:
                    test_data_items.append(f"Value = {value_match.group(1)}")
        
        # If no specific test data found, use generic values
        if not test_data_items:
            test_data_items = ["Input values as specified in steps"]
        
        return ", ".join(test_data_items)
    
    def _extract_expected_result(self, steps: List[TestStep]) -> str:
        """Extract expected result from the last step or calculate from test data."""
        
        if not steps:
            return "Test completes successfully"
        
        # Look for the last step with a meaningful expected result
        for step in reversed(steps):
            if step.expected_result and step.expected_result not in ["Precondition satisfied", "Action completed", "Expected result achieved"]:
                return step.expected_result
        
        # If no specific expected result, try to calculate from test data
        test_data = self._extract_test_data(steps)
        
        # Look for calculation patterns
        if "gain" in test_data.lower() and "offset" in test_data.lower() and "raw" in test_data.lower():
            # Extract values for calculation
            import re
            gain_match = re.search(r'gain\s*=\s*(\d+)', test_data, re.IGNORECASE)
            offset_match = re.search(r'offset\s*=\s*(\d+)', test_data, re.IGNORECASE)
            raw_match = re.search(r'raw\s*=\s*(\d+)', test_data, re.IGNORECASE)
            
            if gain_match and offset_match and raw_match:
                gain = int(gain_match.group(1))
                offset = int(offset_match.group(1))
                raw = int(raw_match.group(1))
                final_value = (raw * gain) + offset
                return f"Final Value = ({raw} × {gain}) + {offset} = {final_value}, displayed correctly"
        
        return "Expected result as specified in test steps"
