"""Code skeleton formatter for generating test code templates in various frameworks."""

import logging
from typing import List, Dict, Any, Optional

from ..models.test_models import TestCase, TestStep
from ..models.input_models import TestCaseRequest


logger = logging.getLogger(__name__)


class CodeSkeletonFormatter:
    """Formatter for generating test code skeletons in various frameworks."""
    
    def __init__(self):
        """Initialize the code skeleton formatter."""
        self.framework_templates = {
            "playwright": self._get_playwright_template(),
            "pytest": self._get_pytest_template(),
            "cypress": self._get_cypress_template(),
            "selenium": self._get_selenium_template(),
            "junit": self._get_junit_template()
        }
    
    def format_test_cases(self, test_cases: List[TestCase], request: TestCaseRequest, 
                         framework: str = "playwright") -> str:
        """Format test cases into code skeleton for the specified framework."""
        
        if not test_cases:
            return f"# No test cases to format for {framework}"
        
        if framework not in self.framework_templates:
            return f"# Unsupported framework: {framework}"
        
        try:
            template = self.framework_templates[framework]
            
            # Generate code for each test case
            test_methods = []
            for test_case in test_cases:
                method_code = self._format_test_case(test_case, framework)
                if method_code:
                    test_methods.append(method_code)
            
            # Combine into complete test file
            complete_code = template.format(
                class_name=self._generate_class_name(request, framework),
                test_methods="\n\n".join(test_methods),
                imports=self._get_framework_imports(framework),
                setup_methods=self._get_setup_methods(framework)
            )
            
            return complete_code
            
        except Exception as e:
            logger.error(f"Error formatting test cases to {framework}: {e}")
            return f"# Error formatting test cases: {e}"
    
    def _format_test_case(self, test_case: TestCase, framework: str) -> Optional[str]:
        """Format a single test case into code for the specified framework."""
        
        try:
            if framework == "playwright":
                return self._format_playwright_test(test_case)
            elif framework == "pytest":
                return self._format_pytest_test(test_case)
            elif framework == "cypress":
                return self._format_cypress_test(test_case)
            elif framework == "selenium":
                return self._format_selenium_test(test_case)
            elif framework == "junit":
                return self._format_junit_test(test_case)
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Failed to format test case {test_case.test_id} for {framework}: {e}")
            return None
    
    def _format_playwright_test(self, test_case: TestCase) -> str:
        """Format test case for Playwright."""
        
        # Generate test method name
        method_name = self._generate_method_name(test_case.title)
        
        # Generate test steps
        steps_code = []
        for step in test_case.steps:
            step_code = self._format_playwright_step(step)
            if step_code:
                steps_code.append(step_code)
        
        # Add assertions
        if test_case.steps:
            last_step = test_case.steps[-1]
            if last_step.expected_result:
                assertion = self._generate_playwright_assertion(last_step.expected_result)
                if assertion:
                    steps_code.append(assertion)
        
        test_code = f"""    def test_{method_name}(self, page):
        \"\"\"
        {test_case.description}
        
        Test ID: {test_case.test_id}
        Priority: {test_case.priority.value}
        Tags: {', '.join(test_case.tags)}
        \"\"\"
        
        # Test steps
{chr(10).join(steps_code)}
        
        # Additional verifications
        # TODO: Add specific assertions based on requirements"""
        
        return test_code
    
    def _format_playwright_step(self, step: TestStep) -> str:
        """Format a test step for Playwright."""
        
        action_lower = step.action.lower()
        
        if "click" in action_lower:
            return f"        # {step.action}\n        page.click('selector')  # TODO: Update selector"
        elif "enter" in action_lower or "input" in action_lower:
            return f"        # {step.action}\n        page.fill('selector', 'value')  # TODO: Update selector and value"
        elif "select" in action_lower:
            return f"        # {step.action}\n        page.select_option('selector', 'value')  # TODO: Update selector and value"
        elif "navigate" in action_lower or "go to" in action_lower:
            return f"        # {step.action}\n        page.goto('url')  # TODO: Update URL"
        elif "submit" in action_lower:
            return f"        # {step.action}\n        page.click('button[type=\"submit\"]')  # TODO: Update selector"
        elif "verify" in action_lower or "check" in action_lower:
            return f"        # {step.action}\n        expect(page.locator('selector')).to_be_visible()  # TODO: Update selector"
        else:
            return f"        # {step.action}\n        # TODO: Implement step: {step.action}"
    
    def _generate_playwright_assertion(self, expected_result: str) -> str:
        """Generate Playwright assertion based on expected result."""
        
        expected_lower = expected_result.lower()
        
        if "visible" in expected_lower or "display" in expected_lower:
            return "        expect(page.locator('selector')).to_be_visible()  # TODO: Update selector"
        elif "text" in expected_lower:
            return "        expect(page.locator('selector')).to_contain_text('expected text')  # TODO: Update selector and text"
        elif "redirect" in expected_lower:
            return "        expect(page).to_have_url('expected_url')  # TODO: Update expected URL"
        elif "enabled" in expected_lower:
            return "        expect(page.locator('selector')).to_be_enabled()  # TODO: Update selector"
        else:
            return "        # TODO: Add assertion for: " + expected_result
    
    def _format_pytest_test(self, test_case: TestCase) -> str:
        """Format test case for Pytest."""
        
        method_name = self._generate_method_name(test_case.title)
        
        # Generate test steps
        steps_code = []
        for step in test_case.steps:
            step_code = self._format_pytest_step(step)
            if step_code:
                steps_code.append(step_code)
        
        test_code = f"""    def test_{method_name}(self):
        \"\"\"
        {test_case.description}
        
        Test ID: {test_case.test_id}
        Priority: {test_case.priority.value}
        Tags: {', '.join(test_case.tags)}
        \"\"\"
        
        # Test steps
{chr(10).join(steps_code)}
        
        # Assertions
        # TODO: Add specific assertions based on requirements"""
        
        return test_code
    
    def _format_pytest_step(self, step: TestStep) -> str:
        """Format a test step for Pytest."""
        
        action_lower = step.action.lower()
        
        if "click" in action_lower:
            return f"        # {step.action}\n        # TODO: Implement click action"
        elif "enter" in action_lower or "input" in action_lower:
            return f"        # {step.action}\n        # TODO: Implement input action"
        elif "verify" in action_lower or "check" in action_lower:
            return f"        # {step.action}\n        assert True  # TODO: Implement verification"
        else:
            return f"        # {step.action}\n        # TODO: Implement step: {step.action}"
    
    def _format_cypress_test(self, test_case: TestCase) -> str:
        """Format test case for Cypress."""
        
        method_name = self._generate_method_name(test_case.title)
        
        # Generate test steps
        steps_code = []
        for step in test_case.steps:
            step_code = self._format_cypress_step(step)
            if step_code:
                steps_code.append(step_code)
        
        test_code = f"""    it('{test_case.title}', () => {{
        // {test_case.description}
        // Test ID: {test_case.test_id}
        // Priority: {test_case.priority.value}
        // Tags: {', '.join(test_case.tags)}
        
        // Test steps
{chr(10).join(steps_code)}
        
        // Additional verifications
        // TODO: Add specific assertions based on requirements
    }});"""
        
        return test_code
    
    def _format_cypress_step(self, step: TestStep) -> str:
        """Format a test step for Cypress."""
        
        action_lower = step.action.lower()
        
        if "click" in action_lower:
            return f"        // {step.action}\n        cy.get('selector').click()  // TODO: Update selector"
        elif "enter" in action_lower or "input" in action_lower:
            return f"        // {step.action}\n        cy.get('selector').type('value')  // TODO: Update selector and value"
        elif "navigate" in action_lower or "go to" in action_lower:
            return f"        // {step.action}\n        cy.visit('url')  // TODO: Update URL"
        elif "verify" in action_lower or "check" in action_lower:
            return f"        // {step.action}\n        cy.get('selector').should('be.visible')  // TODO: Update selector"
        else:
            return f"        // {step.action}\n        // TODO: Implement step: {step.action}"
    
    def _format_selenium_test(self, test_case: TestCase) -> str:
        """Format test case for Selenium."""
        
        method_name = self._generate_method_name(test_case.title)
        
        # Generate test steps
        steps_code = []
        for step in test_case.steps:
            step_code = self._format_selenium_step(step)
            if step_code:
                steps_code.append(step_code)
        
        test_code = f"""    def test_{method_name}(self):
        \"\"\"
        {test_case.description}
        
        Test ID: {test_case.test_id}
        Priority: {test_case.priority.value}
        Tags: {', '.join(test_case.tags)}
        \"\"\"
        
        # Test steps
{chr(10).join(steps_code)}
        
        # Assertions
        # TODO: Add specific assertions based on requirements"""
        
        return test_code
    
    def _format_selenium_step(self, step: TestStep) -> str:
        """Format a test step for Selenium."""
        
        action_lower = step.action.lower()
        
        if "click" in action_lower:
            return f"        # {step.action}\n        self.driver.find_element(By.CSS_SELECTOR, 'selector').click()  # TODO: Update selector"
        elif "enter" in action_lower or "input" in action_lower:
            return f"        # {step.action}\n        element = self.driver.find_element(By.CSS_SELECTOR, 'selector')\n        element.clear()\n        element.send_keys('value')  # TODO: Update selector and value"
        elif "navigate" in action_lower or "go to" in action_lower:
            return f"        # {step.action}\n        self.driver.get('url')  # TODO: Update URL"
        elif "verify" in action_lower or "check" in action_lower:
            return f"        # {step.action}\n        # TODO: Implement verification"
        else:
            return f"        # {step.action}\n        # TODO: Implement step: {step.action}"
    
    def _format_junit_test(self, test_case: TestCase) -> str:
        """Format test case for JUnit."""
        
        method_name = self._generate_method_name(test_case.title)
        
        # Generate test steps
        steps_code = []
        for step in test_case.steps:
            step_code = self._format_junit_step(step)
            if step_code:
                steps_code.append(step_code)
        
        test_code = f"""    @Test
    public void test{method_name}() {{
        // {test_case.description}
        // Test ID: {test_case.test_id}
        // Priority: {test_case.priority.value}
        // Tags: {', '.join(test_case.tags)}
        
        // Test steps
{chr(10).join(steps_code)}
        
        // Assertions
        // TODO: Add specific assertions based on requirements
    }}"""
        
        return test_code
    
    def _format_junit_step(self, step: TestStep) -> str:
        """Format a test step for JUnit."""
        
        action_lower = step.action.lower()
        
        if "click" in action_lower:
            return f"        // {step.action}\n        // TODO: Implement click action"
        elif "enter" in action_lower or "input" in action_lower:
            return f"        // {step.action}\n        // TODO: Implement input action"
        elif "verify" in action_lower or "check" in action_lower:
            return f"        // {step.action}\n        assertTrue(true);  // TODO: Implement verification"
        else:
            return f"        // {step.action}\n        // TODO: Implement step: {step.action}"
    
    def _generate_method_name(self, title: str) -> str:
        """Generate a valid method name from test case title."""
        
        # Remove special characters and convert to camelCase
        import re
        
        # Clean the title
        clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        
        # Split into words and capitalize
        words = clean_title.split()
        if not words:
            return "testCase"
        
        # Convert to camelCase
        method_name = words[0].lower()
        for word in words[1:]:
            method_name += word.capitalize()
        
        # Ensure it starts with a letter
        if not method_name[0].isalpha():
            method_name = "test" + method_name
        
        return method_name
    
    def _generate_class_name(self, request: TestCaseRequest, framework: str) -> str:
        """Generate a class name for the test class."""
        
        if request.user_story:
            # Extract action from user story
            action = request.user_story.action.replace("I want to ", "").replace("I want ", "")
            words = action.split()[:3]  # Take first 3 words
            class_name = "".join(word.capitalize() for word in words)
        else:
            # Use test level and type
            test_level = request.test_specification.test_level.capitalize()
            test_type = request.test_specification.test_types[0].capitalize() if request.test_specification.test_types else "Test"
            class_name = f"{test_level}{test_type}"
        
        # Add framework suffix
        framework_suffix = framework.capitalize()
        if framework == "pytest":
            framework_suffix = "Test"
        elif framework == "junit":
            framework_suffix = "Test"
        
        return f"{class_name}{framework_suffix}"
    
    def _get_framework_imports(self, framework: str) -> str:
        """Get framework-specific imports."""
        
        imports = {
            "playwright": """from playwright.sync_api import expect
import pytest""",
            "pytest": """import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By""",
            "cypress": """// Cypress imports are handled automatically""",
            "selenium": """from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC""",
            "junit": """import org.junit.Test;
import static org.junit.Assert.*;"""
        }
        
        return imports.get(framework, "")
    
    def _get_setup_methods(self, framework: str) -> str:
        """Get framework-specific setup methods."""
        
        setup_methods = {
            "playwright": """    def setup_method(self, method):
        \"\"\"Setup method for each test.\"\"\"
        # TODO: Add any setup logic needed before each test
        pass
    
    def teardown_method(self, method):
        \"\"\"Teardown method for each test.\"\"\"
        # TODO: Add any cleanup logic needed after each test
        pass""",
            "pytest": """    def setup_method(self, method):
        \"\"\"Setup method for each test.\"\"\"
        # TODO: Initialize WebDriver or other test dependencies
        pass
    
    def teardown_method(self, method):
        \"\"\"Teardown method for each test.\"\"\"
        # TODO: Clean up WebDriver or other test dependencies
        pass""",
            "cypress": """    beforeEach(() => {{
        // Setup before each test
        // TODO: Add any setup logic
    }});
    
    afterEach(() => {{
        // Cleanup after each test
        // TODO: Add any cleanup logic
    }});""",
            "selenium": """    def setup_method(self, method):
        \"\"\"Setup method for each test.\"\"\"
        # TODO: Initialize WebDriver
        # self.driver = webdriver.Chrome()
        pass
    
    def teardown_method(self, method):
        \"\"\"Teardown method for each test.\"\"\"
        # TODO: Clean up WebDriver
        # if hasattr(self, 'driver'):
        #     self.driver.quit()
        pass""",
            "junit": """    @Before
    public void setUp() {{
        // Setup before each test
        // TODO: Add any setup logic
    }}
    
    @After
    public void tearDown() {{
        // Cleanup after each test
        // TODO: Add any cleanup logic
    }}"""
        }
        
        return setup_methods.get(framework, "")
    
    def _get_playwright_template(self) -> str:
        """Get Playwright test class template."""
        return """import pytest
from playwright.sync_api import expect

class {class_name}:
    \"\"\"Test class for Playwright tests.\"\"\"
    
{setup_methods}
    
{test_methods}"""
    
    def _get_pytest_template(self) -> str:
        """Get Pytest test class template."""
        return """import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

class {class_name}:
    \"\"\"Test class for Pytest tests.\"\"\"
    
{setup_methods}
    
{test_methods}"""
    
    def _get_cypress_template(self) -> str:
        """Get Cypress test template."""
        return """describe('{class_name}', () => {{
    \"\"\"Test suite for Cypress tests.\"\"\"
    
{setup_methods}
    
{test_methods}}
);"""
    
    def _get_selenium_template(self) -> str:
        """Get Selenium test class template."""
        return """from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class {class_name}:
    \"\"\"Test class for Selenium tests.\"\"\"
    
{setup_methods}
    
{test_methods}"""
    
    def _get_junit_template(self) -> str:
        """Get JUnit test class template."""
        return """import org.junit.Test;
import org.junit.Before;
import org.junit.After;
import static org.junit.Assert.*;

public class {class_name} {{
    \"\"\"Test class for JUnit tests.\"\"\"
    
{setup_methods}
    
{test_methods}
}}"""
    
    def format_single_test_case(self, test_case: TestCase, framework: str = "playwright") -> str:
        """Format a single test case as standalone code."""
        
        try:
            # Create a minimal test class with just this test case
            template = self.framework_templates.get(framework, self._get_playwright_template())
            
            # Format the test case
            test_method = self._format_test_case(test_case, framework)
            if not test_method:
                return f"# Failed to format test case: {test_case.test_id}"
            
            # Create minimal class
            class_name = f"Test{self._generate_method_name(test_case.title)}"
            
            complete_code = template.format(
                class_name=class_name,
                test_methods=test_method,
                imports=self._get_framework_imports(framework),
                setup_methods=self._get_setup_methods(framework)
            )
            
            return complete_code
            
        except Exception as e:
            logger.error(f"Error formatting single test case: {e}")
            return f"# Error formatting test case: {e}"
    
    def get_supported_frameworks(self) -> List[str]:
        """Get list of supported frameworks."""
        return list(self.framework_templates.keys())
    
    def add_code_metadata(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add metadata comments to code content."""
        
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
