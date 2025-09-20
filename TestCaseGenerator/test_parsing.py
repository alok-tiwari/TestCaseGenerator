#!/usr/bin/env python3
"""Test the Gherkin parsing directly."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators.base_generator import BaseTestGenerator
from models.input_models import TestCaseRequest, AcceptanceCriteria, UserStory, SystemContext, TestSpecification
from models.test_models import TestType, TestPriority

class TestGenerator(BaseTestGenerator):
    def generate(self, request):
        pass

def test_parsing():
    """Test Gherkin parsing with sample data."""
    
    # Create test request
    acceptance_criteria = AcceptanceCriteria(
        criteria_type="bullet",
        criteria_list=[
            "The system analyzes real-time sensor data from HVAC, lighting, and energy systems",
            "Users receive alerts when equipment performance deviates from normal operational thresholds"
        ]
    )
    
    user_story = UserStory(
        persona="As a facility manager",
        action="I want to monitor equipment performance in real-time",
        value="So that I can prevent equipment failures and optimize energy usage"
    )
    
    system_context = SystemContext(
        tech_stack=["REST API", "MongoDB"],
        user_roles=["facility manager"],
        data_types=["sensor data"],
        constraints=["10-minute update intervals"]
    )
    
    test_spec = TestSpecification(
        test_types=["functional"],
        test_level="integration",
        output_format="gherkin",
        priority="medium"
    )
    
    request = TestCaseRequest(
        acceptance_criteria=acceptance_criteria,
        user_story=user_story,
        system_context=system_context,
        test_specification=test_spec,
        jira_ticket_id="SJP-2"
    )
    
    # Sample LLM response
    sample_response = """Here are 8 comprehensive functional test cases for the given requirements:

**Test Case 1: Receive Maintenance Alert with Recommended Action**

```gherkin
Feature: Maintenance Alerts
  As a user, I want to receive maintenance alerts when equipment performance deviates from normal operational thresholds.

Scenario: User Receives Maintenance Alert
  Given I am logged into the EcoStruxure platform
  When the system detects abnormal behavior in a piece of HVAC equipment (e.g. temperature exceeds 80°F)
  Then I should receive a maintenance alert with recommended action
  And I should be able to view historical alerts and trends for that equipment
```

**Test Case 2: Real-time Sensor Data Analysis**

```gherkin
Feature: Real-time Sensor Data Analysis
  As a facility manager, I want to monitor equipment performance in real-time.

Scenario: Analyze HVAC Sensor Data
  Given I am logged into the EcoStruxure platform
  When the system receives sensor data from HVAC equipment
  Then the system should analyze the data and display performance metrics
  And the system should update the dashboard every 10 minutes
```
"""
    
    # Create generator and test parsing
    generator = TestGenerator(None)
    
    print("Testing Gherkin parsing...")
    print("=" * 50)
    
    test_cases = generator._parse_gherkin_response(sample_response, request)
    
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
