"""LLM client for test case generation with support for multiple providers."""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Change these imports
from config.settings import LLMProviderConfig
from models.input_models import TestCaseRequest


logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response from the LLM provider."""
        pass
    
    @abstractmethod
    def _build_request_payload(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build the request payload for the provider."""
        pass
    
    @abstractmethod
    def _parse_response(self, response: httpx.Response) -> str:
        """Parse the response from the provider."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=config.timeout
        )
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response using OpenAI API."""
        payload = self._build_request_payload(prompt, context)
        
        response = await self.client.post(
            "/chat/completions",
            json=payload
        )
        response.raise_for_status()
        
        return self._parse_response(response)
    
    def _build_request_payload(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build OpenAI API request payload."""
        return {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert test engineer with deep knowledge of software testing methodologies, test case design, and quality assurance practices. Your role is to generate comprehensive, well-structured test cases based on the provided requirements and context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False
        }
    
    def _parse_response(self, response: httpx.Response) -> str:
        """Parse OpenAI API response."""
        data = response.json()
        return data["choices"][0]["message"]["content"]


class AnthropicProvider(LLMProvider):
    """Anthropic API provider implementation."""
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "x-api-key": config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            timeout=config.timeout
        )
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response using Anthropic API."""
        payload = self._build_request_payload(prompt, context)
        
        response = await self.client.post(
            "/v1/messages",
            json=payload
        )
        response.raise_for_status()
        
        return self._parse_response(response)
    
    def _build_request_payload(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build Anthropic API request payload."""
        return {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "system": "You are an expert test engineer with deep knowledge of software testing methodologies, test case design, and quality assurance practices. Your role is to generate comprehensive, well-structured test cases based on the provided requirements and context."
        }
    
    def _parse_response(self, response: httpx.Response) -> str:
        """Parse Anthropic API response."""
        data = response.json()
        return data["content"][0]["text"]


class OllamaProvider(LLMProvider):
    """Ollama local provider implementation."""
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout
        )
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response using Ollama API."""
        payload = self._build_request_payload(prompt, context)
        
        response = await self.client.post(
            "/api/generate",
            json=payload
        )
        response.raise_for_status()
        
        return self._parse_response(response)
    
    def _build_request_payload(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build Ollama API request payload."""
        return {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
    
    def _parse_response(self, response: httpx.Response) -> str:
        """Parse Ollama API response."""
        data = response.json()
        return data["response"]


class CustomProvider(LLMProvider):
    """Custom API provider implementation."""
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}" if config.api_key else None,
                "Content-Type": "application/json"
            },
            timeout=config.timeout
        )
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response using custom API."""
        payload = self._build_request_payload(prompt, context)
        
        response = await self.client.post(
            "/generate",  # Adjust endpoint as needed
            json=payload
        )
        response.raise_for_status()
        
        return self._parse_response(response)
    
    def _build_request_payload(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build custom API request payload."""
        return {
            "prompt": prompt,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "context": context
        }
    
    def _parse_response(self, response: httpx.Response) -> str:
        """Parse custom API response."""
        data = response.json()
        # Adjust based on your custom API response format
        return data.get("response", data.get("text", data.get("content", str(data))))


class LLMClient:
    """Main LLM client with support for multiple providers."""
    
    def __init__(self, config: LLMProviderConfig):
        """Initialize LLM client with configuration."""
        self.config = config
        self.provider = self._create_provider()
        self.rate_limiter = RateLimiter()
        
        # Prompt templates
        self.prompt_templates = {
            "functional_test": self._get_functional_test_template(),
            "edge_case_test": self._get_edge_case_template(),
            "security_test": self._get_security_test_template(),
            "api_test": self._get_api_test_template(),
            "ui_test": self._get_ui_test_template()
        }
    
    def _create_provider(self) -> LLMProvider:
        """Create the appropriate provider based on configuration."""
        base_url = self.config.base_url.lower()
        
        if "openai" in base_url or "api.openai.com" in base_url:
            return OpenAIProvider(self.config)
        elif "anthropic" in base_url or "api.anthropic.com" in base_url:
            return AnthropicProvider(self.config)
        elif "ollama" in base_url or "localhost" in base_url:
            return OllamaProvider(self.config)
        else:
            return CustomProvider(self.config)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
    )
    async def generate_test_cases(self, request: TestCaseRequest, 
                                test_type: str = "functional") -> str:
        """Generate test cases using the LLM provider."""
        
        # Apply rate limiting
        await self.rate_limiter.wait_if_needed()
        
        # Build prompt
        prompt = self._build_prompt(test_type, request)
        
        # Prepare context
        context = self._prepare_context(request)
        
        try:
            logger.info(f"Generating {test_type} test cases using {self.config.model}")
            start_time = time.time()
            
            response = await self.provider.generate(prompt, context)
            
            generation_time = time.time() - start_time
            logger.info(f"Generated test cases in {generation_time:.2f} seconds")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating test cases: {e}")
            raise
    
    def _build_prompt(self, test_type: str, request: TestCaseRequest) -> str:
        """Build the prompt for test case generation."""
        
        # Get base template
        template = self.prompt_templates.get(test_type, self.prompt_templates["functional_test"])
        
        # Prepare context data
        context_data = {
            "acceptance_criteria": request.acceptance_criteria.criteria_list,
            "criteria_type": request.acceptance_criteria.criteria_type,
            "user_story": self._format_user_story(request.user_story) if request.user_story else None,
            "system_context": self._format_system_context(request.system_context) if request.system_context else None,
            "test_specification": request.test_specification,
            "output_format": request.test_specification.output_format,
            "test_level": request.test_specification.test_level,
            "priority": request.test_specification.priority
        }
        
        # Format the prompt
        prompt = template.format(**context_data)
        
        # Add specific instructions based on test type
        if test_type == "edge_case_test":
            prompt += "\n\nFocus on boundary conditions, negative scenarios, and edge cases."
        elif test_type == "security_test":
            prompt += "\n\nFocus on security vulnerabilities, authentication, authorization, and data protection."
        elif test_type == "api_test":
            prompt += "\n\nFocus on API endpoints, request/response validation, and error handling."
        elif test_type == "ui_test":
            prompt += "\n\nFocus on user interface elements, user interactions, and visual validation."
        
        return prompt
    
    def _prepare_context(self, request: TestCaseRequest) -> Dict[str, Any]:
        """Prepare context data for the LLM."""
        context = {
            "acceptance_criteria": request.acceptance_criteria.dict(),
            "test_specification": request.test_specification.dict()
        }
        
        if request.user_story:
            context["user_story"] = request.user_story.dict()
        
        if request.system_context:
            context["system_context"] = request.system_context.dict()
        
        if request.jira_ticket_id:
            context["jira_ticket_id"] = request.jira_ticket_id
        
        if request.additional_context:
            context["additional_context"] = request.additional_context
        
        return context
    
    def _format_user_story(self, user_story) -> str:
        """Format user story for prompt inclusion."""
        if not user_story:
            return "No user story provided"
        
        return f"""
User Story:
- Persona: {user_story.persona}
- Action: {user_story.action}
- Value: {user_story.value}
"""
    
    def _format_system_context(self, system_context) -> str:
        """Format system context for prompt inclusion."""
        if not system_context:
            return "No system context provided"
        
        context_parts = []
        
        if system_context.tech_stack:
            context_parts.append(f"Technology Stack: {', '.join(system_context.tech_stack)}")
        
        if system_context.data_types:
            context_parts.append(f"Data Types: {', '.join(system_context.data_types)}")
        
        if system_context.constraints:
            context_parts.append(f"Constraints: {', '.join(system_context.constraints)}")
        
        if system_context.user_roles:
            context_parts.append(f"User Roles: {', '.join(system_context.user_roles)}")
        
        return "\n".join(context_parts) if context_parts else "No system context details provided"
    
    def _get_functional_test_template(self) -> str:
        """Get template for functional test generation."""
        return """Generate comprehensive functional test cases for the following requirements:

Acceptance Criteria:
{acceptance_criteria}

{user_story}

System Context:
{system_context}

Test Requirements:
- Test Level: {test_level}
- Output Format: {output_format}
- Priority: {priority}

Please generate test cases that:
1. Cover all acceptance criteria
2. Include positive and negative scenarios
3. Test boundary conditions
4. Are specific and actionable
5. Follow the specified output format: {output_format}

Generate at least 3-5 test cases with clear test steps, expected results, and test data requirements."""

    def _get_edge_case_template(self) -> str:
        """Get template for edge case test generation."""
        return """Generate edge case test scenarios for the following requirements:

Acceptance Criteria:
{acceptance_criteria}

{user_story}

System Context:
{system_context}

Focus on:
1. Boundary conditions
2. Invalid inputs
3. Error scenarios
4. Performance edge cases
5. Security edge cases
6. Data edge cases

Generate test cases that explore the limits and failure modes of the system."""

    def _get_security_test_template(self) -> str:
        """Get template for security test generation."""
        return """Generate security test cases for the following requirements:

Acceptance Criteria:
{acceptance_criteria}

{user_story}

System Context:
{system_context}

Focus on:
1. Authentication bypass attempts
2. Authorization violations
3. Input validation attacks
4. Data exposure scenarios
5. Session management issues
6. API security vulnerabilities

Generate test cases that identify potential security weaknesses."""

    def _get_api_test_template(self) -> str:
        """Get template for API test generation."""
        return """Generate API test cases for the following requirements:

Acceptance Criteria:
{acceptance_criteria}

{user_story}

System Context:
{system_context}

Focus on:
1. HTTP method validation
2. Request/response validation
3. Error handling
4. Authentication/authorization
5. Rate limiting
6. Data validation

Generate test cases that thoroughly test the API endpoints."""

    def _get_ui_test_template(self) -> str:
        """Get template for UI test generation."""
        return """Generate UI test cases for the following requirements:

Acceptance Criteria:
{acceptance_criteria}

{user_story}

System Context:
{system_context}

Focus on:
1. User interactions
2. Visual elements
3. Responsive design
4. Accessibility
5. Cross-browser compatibility
6. User experience

Generate test cases that validate the user interface functionality."""

    async def close(self):
        """Close the client and cleanup resources."""
        await self.provider.client.aclose()


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_times = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        async with self.lock:
            now = time.time()
            
            # Remove calls older than 1 minute
            self.call_times = [t for t in self.call_times if now - t < 60]
            
            # If we've made too many calls, wait
            if len(self.call_times) >= self.calls_per_minute:
                wait_time = 60 - (now - self.call_times[0])
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
            
            # Record this call
            self.call_times.append(now)
