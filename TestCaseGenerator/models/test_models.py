"""Test case data models for representing generated test cases."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from pydantic import field_validator


class TestStatus(str, Enum):
    """Test case status enumeration."""
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TestPriority(str, Enum):
    """Test case priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestType(str, Enum):
    """Test case type enumeration."""
    FUNCTIONAL = "functional"
    API = "api"
    UI = "ui"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    INTEGRATION = "integration"
    UNIT = "unit"
    E2E = "e2e"


class TestStep(BaseModel):
    """Model for individual test steps."""
    
    step_number: int = Field(..., gt=0, description="Step number in sequence")
    action: str = Field(..., min_length=1, description="Action to perform")
    expected_result: str = Field("Expected result not specified", min_length=1, description="Expected outcome")
    test_data: Optional[str] = Field(None, description="Test data required for this step")
    notes: Optional[str] = Field(None, description="Additional notes or instructions")
    
    @field_validator("action", "expected_result")
    def validate_non_empty(cls, v):
        """Validate that strings are not empty after stripping."""
        if not v.strip():
            raise ValueError("Action and expected result must not be empty")
        return v.strip()


class TestData(BaseModel):
    """Model for test data requirements."""
    
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for the test case"
    )
    expected_output: Dict[str, Any] = Field(
        default_factory=dict,
        description="Expected output data"
    )
    preconditions: List[str] = Field(
        default_factory=list,
        description="Preconditions that must be met"
    )
    test_environment: Dict[str, str] = Field(
        default_factory=dict,
        description="Test environment requirements"
    )
    
    @field_validator("preconditions")
    def validate_preconditions(cls, v):
        """Validate preconditions are non-empty strings."""
        return [precondition.strip() for precondition in v if precondition.strip()]


class TestResult(BaseModel):
    """Model for test execution results."""
    
    status: TestStatus = Field(TestStatus.DRAFT, description="Current test status")
    execution_time: Optional[float] = Field(None, ge=0, description="Execution time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if test failed")
    screenshots: List[str] = Field(
        default_factory=list,
        description="List of screenshot file paths"
    )
    logs: List[str] = Field(
        default_factory=list,
        description="List of log entries"
    )
    executed_by: Optional[str] = Field(None, description="User who executed the test")
    executed_at: Optional[str] = Field(None, description="Timestamp of execution")


class TestCase(BaseModel):
    """Complete model for a test case."""
    
    # Basic Information
    test_id: str = Field(..., description="Unique test case identifier")
    title: str = Field(..., min_length=1, description="Test case title")
    description: str = Field(..., min_length=1, description="Test case description")
    
    # Classification
    test_type: TestType = Field(..., description="Type of test case")
    priority: TestPriority = Field(TestPriority.MEDIUM, description="Test case priority")
    test_level: str = Field(..., description="Testing level (unit, integration, e2e)")
    
    # Test Content
    steps: List[TestStep] = Field(..., min_items=1, description="Test execution steps")
    test_data: Optional[TestData] = Field(None, description="Test data requirements")
    
    # Metadata
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing the test case"
    )
    requirements: List[str] = Field(
        default_factory=list,
        description="Requirements covered by this test case"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Dependencies on other test cases or systems"
    )
    
    # Results and Status
    result: TestResult = Field(
        default_factory=lambda: TestResult(),
        description="Test execution results"
    )
    
    # Source Information
    source_request: Optional[str] = Field(None, description="Source test case request ID")
    jira_ticket_id: Optional[str] = Field(None, description="Associated Jira ticket")
    generated_at: Optional[str] = Field(None, description="Timestamp when test case was generated")
    
    @field_validator("steps")
    def validate_steps(cls, v):
        """Validate that steps have sequential numbering."""
        step_numbers = [step.step_number for step in v]
        if len(step_numbers) != len(set(step_numbers)):
            raise ValueError("Step numbers must be unique")
        if step_numbers != sorted(step_numbers):
            raise ValueError("Steps must be in sequential order")
        return v
    
    @field_validator("tags")
    def validate_tags(cls, v):
        """Validate tags are non-empty strings."""
        return [tag.strip() for tag in v if tag.strip()]
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "test_id": "TC-001",
                "title": "User Logout Functionality",
                "description": "Verify that users can successfully log out of the system",
                "test_type": "functional",
                "priority": "high",
                "test_level": "integration",
                "steps": [
                    {
                        "step_number": 1,
                        "action": "Navigate to the application homepage",
                        "expected_result": "Homepage loads successfully",
                        "test_data": "Valid user credentials"
                    },
                    {
                        "step_number": 2,
                        "action": "Click on the logout button",
                        "expected_result": "User is logged out and redirected to login page"
                    }
                ],
                "tags": ["authentication", "logout", "user-management"],
                "requirements": ["REQ-001", "REQ-002"],
                "jira_ticket_id": "PROJ-123"
            }
        }
