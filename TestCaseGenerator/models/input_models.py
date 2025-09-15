"""Input data models for test case generation."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class AcceptanceCriteria(BaseModel):
    """Model for acceptance criteria data."""
    criteria_type: str = Field(
        default="gherkin",
        pattern="^(gherkin|plain|bullet)$",  # Using pattern instead of regex
        description="Type of acceptance criteria format"
    )
    criteria_list: List[str] = Field(
        default_factory=list,
        description="List of acceptance criteria statements"
    )
    
    @field_validator("criteria_list")
    def validate_criteria_list(cls, v):
        """Validate that criteria list contains non-empty strings."""
        if not all(criteria.strip() for criteria in v):
            raise ValueError("All acceptance criteria must be non-empty")
        return [criteria.strip() for criteria in v]


class UserStory(BaseModel):
    """Model for user story input."""
    
    persona: str = Field(
        ..., 
        min_length=1,
        description="User persona (e.g., 'As a customer')"
    )
    action: str = Field(
        ..., 
        min_length=1,
        description="Desired action (e.g., 'I want to reset my password')"
    )
    value: str = Field(
        ..., 
        min_length=1,
        description="Business value (e.g., 'So that I can access my account')"
    )
    
    @field_validator("persona")
    def validate_persona(cls, v):
        """Validate persona format."""
        if not v.lower().startswith("as a "):
            raise ValueError("Persona must start with 'As a '")
        return v
    
    @field_validator("action")
    def validate_action(cls, v):
        """Validate action format."""
        if not v.lower().startswith("i want to "):
            raise ValueError("Action must start with 'I want to '")
        return v
    
    @field_validator("value")
    def validate_value(cls, v):
        """Validate value format."""
        if not v.lower().startswith("so that "):
            raise ValueError("Value must start with 'So that '")
        return v


class SystemContext(BaseModel):
    """Model for system context information."""
    
    tech_stack: List[str] = Field(
        default_factory=list,
        description="List of technologies used in the system"
    )
    data_types: List[str] = Field(
        default_factory=list,
        description="Types of data handled by the system"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="System constraints and requirements"
    )
    user_roles: List[str] = Field(
        default_factory=list,
        description="User roles and permissions"
    )
    
    @field_validator("tech_stack", "data_types", "constraints", "user_roles")
    def validate_list_items(cls, v):
        """Validate that list items are non-empty strings."""
        return [item.strip() for item in v if item.strip()]


class TestSpecification(BaseModel):
    """Model for test specification requirements."""
    
    test_types: List[str] = Field(
        default=["functional"],
        description="Types of tests to generate"
    )
    test_level: str = Field(
        default="unit",
        pattern="^(unit|integration|system|acceptance)$",  # Changed from regex to pattern
        description="Level of the test"
    )
    output_format: str = Field(
        default="gherkin",
        pattern="^(gherkin|playwright|pytest|cypress|human)$",  # Changed from regex to pattern
        description="Desired output format for test cases"
    )
    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high|critical)$",  # Changed from regex to pattern
        description="Priority level for test cases"
    )
    
    @field_validator("test_types")
    def validate_test_types(cls, v):
        """Validate test types."""
        valid_types = ["functional", "api", "ui", "performance", "security", "accessibility"]
        for test_type in v:
            if test_type not in valid_types:
                raise ValueError(f"Invalid test type: {test_type}. Must be one of {valid_types}")
        return v


class TestCaseRequest(BaseModel):
    """Complete model for test case generation request."""
    
    acceptance_criteria: AcceptanceCriteria
    user_story: Optional[UserStory] = None
    system_context: Optional[SystemContext] = None
    test_specification: TestSpecification
    jira_ticket_id: Optional[str] = Field(None, description="Jira ticket ID for reference")
    additional_context: Optional[str] = Field(None, description="Additional context or notes")
    
    @field_validator("jira_ticket_id")
    def validate_jira_ticket_id(cls, v):
        """Validate Jira ticket ID format."""
        if v and not v.strip():
            return None
        return v.strip() if v else None
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "acceptance_criteria": {
                    "criteria_type": "given-when-then",
                    "criteria_list": [
                        "Given a user is logged in, When they click the logout button, Then they should be logged out",
                        "Given a user is not logged in, When they try to access a protected page, Then they should be redirected to login"
                    ]
                },
                "user_story": {
                    "persona": "As a registered user",
                    "action": "I want to log out of my account",
                    "value": "So that I can secure my account when using shared devices"
                },
                "system_context": {
                    "tech_stack": ["web app", "REST API", "React"],
                    "data_types": ["user credentials", "session data"],
                    "constraints": ["GDPR compliance", "session timeout"],
                    "user_roles": ["Admin", "User", "Guest"]
                },
                "test_specification": {
                    "test_types": ["functional", "security"],
                    "test_level": "integration",
                    "output_format": "gherkin",
                    "priority": "high"
                },
                "jira_ticket_id": "PROJ-123",
                "additional_context": "Focus on edge cases and security scenarios"
            }
        }
