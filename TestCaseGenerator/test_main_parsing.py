#!/usr/bin/env python3
"""Test parsing in the main system context."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators.functional_test_generator import FunctionalTestGenerator
from integrations.llm_client import LLMClient
from config.settings import get_llm_config
from models.input_models import TestCaseRequest, AcceptanceCriteria, UserStory, SystemContext, TestSpecification

async def test_main_parsing():
    """Test parsing in the main system context."""
    
    # Create a test request
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
    
    # Get LLM client
    llm_config = get_llm_config("ollama")
    llm_client = LLMClient(llm_config)
    
    try:
        # Create functional test generator
        generator = FunctionalTestGenerator(llm_client)
        
        # Generate test cases
        test_cases = await generator.generate(request)
        
        print(f"Generated {len(test_cases)} test cases")
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest Case {i+1}:")
            print(f"  Title: {test_case.title}")
            print(f"  Description: {test_case.description}")
            print(f"  Steps: {len(test_case.steps)}")
            for j, step in enumerate(test_case.steps):
                print(f"    {j+1}. {step.action}")
        
    finally:
        await llm_client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_main_parsing())
