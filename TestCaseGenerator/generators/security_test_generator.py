"""Security test generator for authentication, authorization, and security vulnerabilities."""

import logging
import re
from typing import List, Dict, Any, Optional

from .base_generator import BaseTestGenerator
from models.input_models import TestCaseRequest
from models.test_models import TestCase, TestStep, TestType, TestPriority


logger = logging.getLogger(__name__)


class SecurityTestGenerator(BaseTestGenerator):
    """Generator for security test cases focusing on authentication, authorization, and vulnerabilities."""
    
    def __init__(self, llm_client):
        """Initialize the security test generator."""
        super().__init__(llm_client)
        self.generator_type = "security"
    
    async def generate(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate security test cases for the given request."""
        
        logger.info(f"Generating security test cases for request")
        
        try:
            # Generate test cases using LLM
            llm_response = await self._generate_with_llm(request, "security_test")
            
            # Parse the response
            test_cases = self._parse_llm_response(llm_response, request)
            
            # If LLM parsing fails, generate fallback test cases
            if not test_cases:
                logger.warning("LLM parsing failed, generating fallback security test cases")
                test_cases = self._generate_fallback_security_cases(request)
            
            # Enhance and validate test cases
            enhanced_cases = []
            for test_case in test_cases:
                enhanced_case = self._enhance_test_case(test_case, request)
                enhanced_case.test_type = TestType.SECURITY
                enhanced_case.priority = self._determine_test_priority(request, "security")
                enhanced_case.tags = self._generate_tags(request, "security")
                
                # Validate the test case
                validation = self._validate_test_case(enhanced_case)
                if validation["is_valid"]:
                    enhanced_cases.append(enhanced_case)
                else:
                    logger.warning(f"Security test validation failed: {validation['errors']}")
            
            # Log generation statistics
            self._log_generation_stats(enhanced_cases, request)
            
            return enhanced_cases
            
        except Exception as e:
            logger.error(f"Error generating security test cases: {e}")
            # Return fallback test cases on error
            return self._generate_fallback_security_cases(request)
    
    def _generate_fallback_security_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate fallback security test cases when LLM generation fails."""
        
        test_cases = []
        
        # Generate authentication test cases
        auth_cases = self._generate_authentication_cases(request)
        test_cases.extend(auth_cases)
        
        # Generate authorization test cases
        authz_cases = self._generate_authorization_cases(request)
        test_cases.extend(authz_cases)
        
        # Generate input validation test cases
        input_validation_cases = self._generate_input_validation_cases(request)
        test_cases.extend(input_validation_cases)
        
        # Generate session management test cases
        session_cases = self._generate_session_management_cases(request)
        test_cases.extend(session_cases)
        
        # Generate data protection test cases
        data_protection_cases = self._generate_data_protection_cases(request)
        test_cases.extend(data_protection_cases)
        
        # Generate API security test cases
        api_security_cases = self._generate_api_security_cases(request)
        test_cases.extend(api_security_cases)
        
        return test_cases
    
    def _generate_authentication_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate authentication test cases."""
        
        auth_cases = []
        
        # Basic authentication test cases
        basic_auth_scenarios = [
            {
                "title": "Valid Login Credentials",
                "description": "Test successful authentication with valid credentials",
                "steps": [
                    "Enter valid username and password",
                    "Submit login form",
                    "Verify successful authentication and redirect"
                ]
            },
            {
                "title": "Invalid Username",
                "description": "Test authentication failure with invalid username",
                "steps": [
                    "Enter invalid username with valid password",
                    "Submit login form",
                    "Verify authentication failure and error message"
                ]
            },
            {
                "title": "Invalid Password",
                "description": "Test authentication failure with invalid password",
                "steps": [
                    "Enter valid username with invalid password",
                    "Submit login form",
                    "Verify authentication failure and error message"
                ]
            },
            {
                "title": "Empty Credentials",
                "description": "Test authentication with empty username and password",
                "steps": [
                    "Leave username and password fields empty",
                    "Submit login form",
                    "Verify validation error messages"
                ]
            },
            {
                "title": "SQL Injection in Username",
                "description": "Test SQL injection protection in username field",
                "steps": [
                    "Enter SQL injection payload in username field",
                    "Submit login form",
                    "Verify system rejects the input safely"
                ]
            },
            {
                "title": "XSS in Username",
                "description": "Test XSS protection in username field",
                "steps": [
                    "Enter XSS payload in username field",
                    "Submit login form",
                    "Verify XSS payload is not executed"
                ]
            }
        ]
        
        for scenario in basic_auth_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="Authentication security is maintained",
                    notes=f"Authentication security: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-AUTH"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["authentication", "login-security"],
                requirements=["Authentication security verification"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            auth_cases.append(test_case)
        
        # Advanced authentication test cases
        advanced_auth_scenarios = [
            {
                "title": "Brute Force Protection",
                "description": "Test protection against brute force attacks",
                "steps": [
                    "Attempt multiple failed login attempts",
                    "Verify account lockout mechanism",
                    "Verify appropriate error messages"
                ]
            },
            {
                "title": "Password Complexity Requirements",
                "description": "Test password complexity validation",
                "steps": [
                    "Attempt to set weak passwords",
                    "Verify password complexity requirements are enforced",
                    "Verify appropriate error messages"
                ]
            },
            {
                "title": "Password Reset Security",
                "description": "Test password reset functionality security",
                "steps": [
                    "Request password reset",
                    "Verify secure reset link generation",
                    "Verify reset link expiration"
                ]
            }
        ]
        
        for scenario in advanced_auth_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="Advanced authentication security is maintained",
                    notes=f"Advanced authentication: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-AUTH-ADV"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["authentication", "advanced-security"],
                requirements=["Advanced authentication security"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            auth_cases.append(test_case)
        
        return auth_cases
    
    def _generate_authorization_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate authorization test cases."""
        
        authz_cases = []
        
        # Role-based access control test cases
        rbac_scenarios = [
            {
                "title": "Admin Role Access",
                "description": "Test admin role access to restricted functionality",
                "steps": [
                    "Login with admin user account",
                    "Access admin-only functionality",
                    "Verify access is granted"
                ]
            },
            {
                "title": "User Role Access Denial",
                "description": "Test user role access denial to restricted functionality",
                "steps": [
                    "Login with regular user account",
                    "Attempt to access admin functionality",
                    "Verify access is denied"
                ]
            },
            {
                "title": "Guest Role Restrictions",
                "description": "Test guest role access restrictions",
                "steps": [
                    "Access system as guest user",
                    "Attempt to access user functionality",
                    "Verify access is denied"
                ]
            },
            {
                "title": "Privilege Escalation Prevention",
                "description": "Test prevention of privilege escalation attacks",
                "steps": [
                    "Login with limited user account",
                    "Attempt to modify user role or permissions",
                    "Verify privilege escalation is prevented"
                ]
            }
        ]
        
        for scenario in rbac_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="Authorization controls are properly enforced",
                    notes=f"Authorization control: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-AUTHZ"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["authorization", "access-control"],
                requirements=["Authorization control verification"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            authz_cases.append(test_case)
        
        return authz_cases
    
    def _generate_input_validation_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate input validation security test cases."""
        
        input_validation_cases = []
        
        # SQL injection test cases
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; EXEC xp_cmdshell('dir'); --",
            "' OR 1=1--",
            "admin'--",
            "admin'/*",
            "admin'#"
        ]
        
        for payload in sql_injection_payloads:
            steps = [
                self._create_test_step(
                    step_number=1,
                    action=f"Enter SQL injection payload: {payload[:30]}...",
                    expected_result="System safely handles SQL injection attempt",
                    notes="SQL injection protection test"
                ),
                self._create_test_step(
                    step_number=2,
                    action="Submit the input",
                    expected_result="Input is rejected or sanitized",
                    notes="Input validation verification"
                )
            ]
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-SQL"),
                title=f"SQL Injection Protection: {payload[:20]}...",
                description=f"Test SQL injection protection with payload: {payload}",
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["sql-injection", "input-validation"],
                requirements=["SQL injection protection"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            input_validation_cases.append(test_case)
        
        # XSS test cases
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert('XSS')",
            "<svg onload=alert(1)>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert(1)>",
            "<body onload=alert(1)>",
            "<input onfocus=alert(1) autofocus>"
        ]
        
        for payload in xss_payloads:
            steps = [
                self._create_test_step(
                    step_number=1,
                    action=f"Enter XSS payload: {payload[:30]}...",
                    expected_result="System safely handles XSS attempt",
                    notes="XSS protection test"
                ),
                self._create_test_step(
                    step_number=2,
                    action="Submit the input",
                    expected_result="XSS payload is not executed",
                    notes="XSS protection verification"
                )
            ]
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-XSS"),
                title=f"XSS Protection: {payload[:20]}...",
                description=f"Test XSS protection with payload: {payload}",
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["xss", "input-validation"],
                requirements=["XSS protection"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            input_validation_cases.append(test_case)
        
        # Command injection test cases
        command_injection_payloads = [
            "; ls -la",
            "& dir",
            "| whoami",
            "`id`",
            "$(whoami)",
            "&& cat /etc/passwd",
            "|| echo 'injected'"
        ]
        
        for payload in command_injection_payloads:
            steps = [
                self._create_test_step(
                    step_number=1,
                    action=f"Enter command injection payload: {payload}",
                    expected_result="System safely handles command injection attempt",
                    notes="Command injection protection test"
                ),
                self._create_test_step(
                    step_number=2,
                    action="Submit the input",
                    expected_result="Command injection is prevented",
                    notes="Command injection protection verification"
                )
            ]
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-CMD"),
                title=f"Command Injection Protection: {payload}",
                description=f"Test command injection protection with payload: {payload}",
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["command-injection", "input-validation"],
                requirements=["Command injection protection"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            input_validation_cases.append(test_case)
        
        return input_validation_cases
    
    def _generate_session_management_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate session management security test cases."""
        
        session_cases = []
        
        # Session security scenarios
        session_scenarios = [
            {
                "title": "Session Timeout",
                "description": "Test session timeout functionality",
                "steps": [
                    "Login to the system",
                    "Wait for session to expire",
                    "Attempt to perform actions",
                    "Verify session timeout handling"
                ]
            },
            {
                "title": "Session Fixation Prevention",
                "description": "Test prevention of session fixation attacks",
                "steps": [
                    "Capture session ID before login",
                    "Complete login process",
                    "Verify session ID changes after login"
                ]
            },
            {
                "title": "Concurrent Session Handling",
                "description": "Test handling of concurrent sessions",
                "steps": [
                    "Login from multiple browsers/devices",
                    "Perform actions in different sessions",
                    "Verify session isolation"
                ]
            },
            {
                "title": "Logout Security",
                "description": "Test logout functionality security",
                "steps": [
                    "Login to the system",
                    "Perform logout",
                    "Attempt to access protected resources",
                    "Verify proper session termination"
                ]
            }
        ]
        
        for scenario in session_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="Session security is maintained",
                    notes=f"Session security: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-SESS"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["session-management", "session-security"],
                requirements=["Session security verification"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            session_cases.append(test_case)
        
        return session_cases
    
    def _generate_data_protection_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate data protection security test cases."""
        
        data_protection_cases = []
        
        # Data protection scenarios
        data_protection_scenarios = [
            {
                "title": "Sensitive Data Exposure",
                "description": "Test protection of sensitive data",
                "steps": [
                    "Access system with different user roles",
                    "Check for sensitive data exposure",
                    "Verify data is properly protected"
                ]
            },
            {
                "title": "Data Encryption",
                "description": "Test data encryption in transit and at rest",
                "steps": [
                    "Monitor network traffic during data transmission",
                    "Verify HTTPS/TLS encryption",
                    "Check database encryption"
                ]
            },
            {
                "title": "Data Sanitization",
                "description": "Test data sanitization in outputs",
                "steps": [
                    "Input potentially dangerous data",
                    "Check system outputs",
                    "Verify data is properly sanitized"
                ]
            }
        ]
        
        for scenario in data_protection_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="Data protection measures are effective",
                    notes=f"Data protection: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-DATA"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["data-protection", "encryption"],
                requirements=["Data protection verification"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            data_protection_cases.append(test_case)
        
        return data_protection_cases
    
    def _generate_api_security_cases(self, request: TestCaseRequest) -> List[TestCase]:
        """Generate API security test cases."""
        
        api_security_cases = []
        
        # API security scenarios
        api_security_scenarios = [
            {
                "title": "API Authentication",
                "description": "Test API authentication requirements",
                "steps": [
                    "Make API request without authentication",
                    "Verify authentication is required",
                    "Verify appropriate error response"
                ]
            },
            {
                "title": "API Rate Limiting",
                "description": "Test API rate limiting functionality",
                "steps": [
                    "Make multiple rapid API requests",
                    "Verify rate limiting is enforced",
                    "Verify appropriate error responses"
                ]
            },
            {
                "title": "API Input Validation",
                "description": "Test API input validation security",
                "steps": [
                    "Send malicious payloads to API endpoints",
                    "Verify input validation is effective",
                    "Verify appropriate error handling"
                ]
            },
            {
                "title": "API Authorization",
                "description": "Test API authorization controls",
                "steps": [
                    "Make API requests with different user roles",
                    "Verify proper authorization enforcement",
                    "Verify access control is maintained"
                ]
            }
        ]
        
        for scenario in api_security_scenarios:
            steps = []
            for i, step_desc in enumerate(scenario["steps"], 1):
                steps.append(self._create_test_step(
                    step_number=i,
                    action=step_desc,
                    expected_result="API security is maintained",
                    notes=f"API security: {scenario['title']}"
                ))
            
            test_case = TestCase(
                test_id=self._generate_test_id("SEC-API"),
                title=scenario["title"],
                description=scenario["description"],
                test_type=TestType.SECURITY,
                priority=self._determine_test_priority(request, "security"),
                test_level=request.test_specification.test_level,
                steps=steps,
                tags=self._generate_tags(request, "security") + ["api-security", "api-testing"],
                requirements=["API security verification"],
                jira_ticket_id=request.jira_ticket_id
            )
            
            api_security_cases.append(test_case)
        
        return api_security_cases
    
    def _parse_llm_response(self, response: str, request: TestCaseRequest) -> List[TestCase]:
        """Parse LLM response for security test cases."""
        
        test_cases = []
        
        # Split response into test case sections
        sections = response.split('\n\n')
        
        for section in sections:
            if not section.strip():
                continue
            
            try:
                test_case = self._parse_security_test_case(section, request)
                if test_case:
                    test_cases.append(test_case)
            except Exception as e:
                logger.warning(f"Failed to parse security test case section: {e}")
                continue
        
        return test_cases
    
    def _parse_security_test_case(self, section: str, request: TestCaseRequest) -> Optional[TestCase]:
        """Parse a security test case from text."""
        
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
            test_id=self._generate_test_id("SEC"),
            title=title,
            description=description,
            test_type=TestType.SECURITY,
            priority=self._determine_test_priority(request, "security"),
            test_level=request.test_specification.test_level,
            steps=steps,
            tags=self._generate_tags(request, "security"),
            requirements=self._extract_requirements(request),
            jira_ticket_id=request.jira_ticket_id
        )
        
        return test_case
