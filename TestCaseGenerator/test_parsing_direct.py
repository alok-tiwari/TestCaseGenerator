#!/usr/bin/env python3
"""Test parsing directly."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators.base_generator import BaseTestGenerator
from models.input_models import TestCaseRequest, AcceptanceCriteria, UserStory, SystemContext, TestSpecification

class TestGenerator(BaseTestGenerator):
    def generate(self, request):
        pass

def test_parsing():
    """Test the parsing method directly."""
    
    # Create test request
    request = TestCaseRequest(
        acceptance_criteria=AcceptanceCriteria(criteria_type='bullet', criteria_list=['test']),
        user_story=UserStory(persona='As a user', action='I want to test', value='So that I can verify'),
        system_context=SystemContext(tech_stack=[], user_roles=[], data_types=[], constraints=[]),
        test_specification=TestSpecification(test_types=['functional'], test_level='integration', output_format='gherkin', priority='medium'),
        jira_ticket_id='TEST'
    )
    
    # Test response
    response = """Here are 7 comprehensive functional test cases for the given requirements:

**Test Case 1: Happy Path - Real-time Sensor Data Analysis**

```gherkin
Feature: Analyze real-time sensor data from HVAC, lighting, and energy systems

Scenario Outline: Facility Manager Monitors Equipment Performance in Real-Time

Given the system is configured with real-time sensor data from HVAC, lighting, and energy systems
And the facility manager has logged in to the system as an authorized user
When the 10-minute update interval has passed since the last data update
Then the system should display real-time performance metrics for each equipment type
```"""
    
    # Create generator and test parsing
    generator = TestGenerator(None)
    
    print("Testing Gherkin parsing...")
    print("=" * 50)
    
    test_cases = generator._parse_gherkin_response(response, request)
    
    print(f"Parsed {len(test_cases)} test cases")
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}:")
        print(f"  Title: {test_case.title}")
        print(f"  Description: {test_case.description}")
        print(f"  Steps: {len(test_case.steps)}")
        for j, step in enumerate(test_case.steps):
            print(f"    {j+1}. {step.action}")

if __name__ == "__main__":
    test_parsing()
