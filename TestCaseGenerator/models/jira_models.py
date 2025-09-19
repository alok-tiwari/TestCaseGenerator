"""Jira integration models for representing Jira tickets and data structures."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import field_validator


class JiraField(BaseModel):
    """Model for Jira field values."""
    
    field_id: Optional[str] = Field(None, description="Jira field identifier")
    field_name: Optional[str] = Field(None, description="Human-readable field name")
    field_value: Any = Field(None, description="Field value")
    field_type: Optional[str] = Field(None, description="Jira field type")
    
    @classmethod
    def from_raw_value(cls, field_id: str, value: Any):
        """Create a JiraField from a raw value."""
        return cls(
            field_id=field_id,
            field_name=field_id,
            field_value=value,
            field_type=type(value).__name__
        )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "field_id": "summary",
                "field_name": "Summary",
                "field_value": "Implement user logout functionality",
                "field_type": "string"
            }
        }


class JiraIssue(BaseModel):
    """Model for Jira issue data."""
    
    issue_key: str = Field(..., description="Jira issue key (e.g., PROJ-123)")
    issue_id: str = Field(..., description="Jira issue ID")
    summary: str = Field(..., description="Issue summary/title")
    description: Optional[str] = Field(None, description="Issue description")
    issue_type: str = Field(..., description="Issue type (Story, Bug, Task, etc.)")
    status: Dict[str, Any] | str = Field(..., description="Current issue status (can be string or dictionary)")
    
    @field_validator("status")
    def normalize_status(cls, v):
        """Normalize status to always be a dictionary."""
        if isinstance(v, str):
            return {"name": v}
        return v
    priority: str = Field(..., description="Issue priority")
    assignee: Optional[str] = Field(None, description="Assigned user")
    reporter: str = Field(..., description="Issue reporter")
    created: datetime = Field(..., description="Creation timestamp")
    updated: datetime = Field(..., description="Last update timestamp")
    fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Jira fields. Can contain JiraField objects or raw values"
    )
    
    @field_validator("issue_key")
    def validate_issue_key(cls, v):
        """Validate Jira issue key format."""
        if not v or "-" not in v:
            raise ValueError("Jira issue key must contain a hyphen (e.g., PROJ-123)")
        return v.upper()
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "issue_key": "PROJ-123",
                "issue_id": "12345",
                "summary": "Implement user logout functionality",
                "description": "Users should be able to log out of the system securely",
                "issue_type": "Story",
                "status": "To Do",
                "priority": "High",
                "assignee": "john.doe",
                "reporter": "jane.smith",
                "created": "2024-01-15T10:00:00Z",
                "updated": "2024-01-15T14:30:00Z"
            }
        }


class JiraTicket(BaseModel):
    """Complete model for a Jira ticket with acceptance criteria."""
    
    issue: JiraIssue
    acceptance_criteria: List[str] = Field(
        default_factory=list,
        description="List of acceptance criteria"
    )
    user_story: Optional[str] = Field(None, description="User story in As a... I want to... So that... format")
    labels: List[str] = Field(
        default_factory=list,
        description="Jira labels/tags"
    )
    components: List[str] = Field(
        default_factory=list,
        description="Jira components"
    )
    epic_link: Optional[str] = Field(None, description="Linked epic issue key")
    sprint: Optional[str] = Field(None, description="Sprint information")
    story_points: Optional[float] = Field(None, ge=0, description="Story points estimate")
    
    @field_validator("acceptance_criteria")
    def validate_acceptance_criteria(cls, v):
        """Validate acceptance criteria are non-empty strings."""
        return [criteria.strip() for criteria in v if criteria.strip()]
    
    @field_validator("labels", "components")
    def validate_list_items(cls, v):
        """Validate list items are non-empty strings."""
        return [item.strip() for item in v if item.strip()]
    
    def extract_user_story_parts(self) -> Optional[Dict[str, str]]:
        """Extract user story parts if available."""
        if not self.user_story:
            return None
            
        story_parts = {}
        lines = self.user_story.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('as a '):
                story_parts['persona'] = line
            elif line.lower().startswith('i want to '):
                story_parts['action'] = line
            elif line.lower().startswith('so that '):
                story_parts['value'] = line
                
        return story_parts if len(story_parts) == 3 else None
    
    def get_acceptance_criteria_type(self) -> str:
        """Determine the type of acceptance criteria format."""
        if not self.acceptance_criteria:
            return "bullet"
            
        # Check if any criteria follow Given-When-Then format
        gwt_patterns = ["given", "when", "then"]
        for criteria in self.acceptance_criteria:
            if any(pattern in criteria.lower() for pattern in gwt_patterns):
                return "gherkin"
        
        return "bullet"
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "issue": {
                    "issue_key": "PROJ-123",
                    "issue_id": "12345",
                    "summary": "Implement user logout functionality",
                    "description": "Users should be able to log out of the system securely",
                    "issue_type": "Story",
                    "status": "To Do",
                    "priority": "High",
                    "assignee": "john.doe",
                    "reporter": "jane.smith",
                    "created": "2024-01-15T10:00:00Z",
                    "updated": "2024-01-15T14:30:00Z"
                },
                "acceptance_criteria": [
                    "Given a user is logged in, When they click the logout button, Then they should be logged out",
                    "Given a user is not logged in, When they try to access a protected page, Then they should be redirected to login"
                ],
                "user_story": "As a registered user\nI want to log out of my account\nSo that I can secure my account when using shared devices",
                "labels": ["authentication", "security", "user-management"],
                "components": ["frontend", "backend"],
                "epic_link": "PROJ-100",
                "sprint": "Sprint 5",
                "story_points": 3.0
            }
        }
