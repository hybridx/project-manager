from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
from enum import Enum

def get_utc_now() -> datetime:
    """Get current UTC timestamp using timezone-aware datetime"""
    return datetime.now(timezone.utc)

class DocumentType(str, Enum):
    PRD = "prd"
    RFC = "rfc"
    REQUIREMENTS = "requirements"
    FEATURE_SPEC = "feature_spec"
    DESIGN_DOC = "design_doc"
    ARCHITECTURE_DOC = "architecture_doc"
    TECHNICAL_SPEC = "technical_spec"
    MARKDOWN = "markdown"
    TEXT = "text"
    UNKNOWN = "unknown"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class StoryPointValue(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FIVE = 5
    EIGHT = 8
    THIRTEEN = 13
    TWENTY_ONE = 21

class AcceptanceCriteria(BaseModel):
    scenario: str = Field(..., description="The scenario being tested")
    steps: List[str] = Field(..., description="Given-When-Then steps")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario": "User login validation",
                "steps": [
                    "Given a user with valid credentials",
                    "When they attempt to login",
                    "Then they should be successfully authenticated"
                ]
            }
        }
    )

class UserStory(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    title: str = Field(..., description="Story title")
    description: str = Field(..., description="Story description")
    role: str = Field(..., description="User role (As a...)")
    action: str = Field(..., description="Action to be performed (I want to...)")
    benefit: str = Field(..., description="Expected benefit (So that...)")
    acceptance_criteria: List[AcceptanceCriteria] = Field(default_factory=list)
    story_points: Optional[int] = Field(None, description="Estimated story points")
    priority: Priority = Field(default=Priority.MEDIUM)
    epic_id: Optional[str] = Field(None, description="Parent epic ID")
    labels: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "User Authentication",
                "description": "As a user, I want to authenticate securely",
                "role": "user",
                "action": "authenticate securely",
                "benefit": "I can access my account safely",
                "story_points": 5,
                "priority": "medium"
            }
        }
    )

class Epic(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    title: str = Field(..., description="Epic title")
    description: str = Field(..., description="Epic description")
    goal: str = Field(..., description="Business goal of the epic")
    user_stories: List[UserStory] = Field(default_factory=list)
    total_story_points: Optional[int] = Field(None, description="Sum of all story points")
    priority: Priority = Field(default=Priority.MEDIUM)
    labels: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "User Management System",
                "description": "Comprehensive user management capabilities",
                "goal": "Enable administrators to manage users effectively",
                "priority": "high"
            }
        }
    )

class ExtractedArtifacts(BaseModel):
    epics: List[Epic] = Field(default_factory=list)
    user_stories: List[UserStory] = Field(default_factory=list)
    contributors: List[str] = Field(default_factory=list)
    project_summary: str = Field(..., description="High-level project summary")
    estimated_duration: Optional[str] = Field(None, description="Estimated project duration")
    key_features: List[str] = Field(default_factory=list)
    technical_requirements: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_summary": "A project management system with AI capabilities",
                "estimated_duration": "3 months",
                "key_features": ["AI analysis", "Project tracking", "Team collaboration"]
            }
        }
    )

class DocumentProcessingRequest(BaseModel):
    content: str = Field(..., description="Document content to process")
    document_name: str = Field(..., description="Name of the document")
    document_type: DocumentType = Field(default=DocumentType.UNKNOWN)
    project_id: Optional[str] = Field(None, description="Associated project ID")
    additional_context: Optional[str] = Field(None, description="Additional context for processing")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "This is a project requirements document...",
                "document_name": "project_requirements.md",
                "document_type": "requirements"
            }
        }
    )

class DocumentProcessingResponse(BaseModel):
    success: bool = Field(..., description="Whether processing was successful")
    message: str = Field(..., description="Processing result message")
    document_id: str = Field(..., description="Generated document ID")
    artifacts: Optional[ExtractedArtifacts] = Field(None, description="Extracted project artifacts")
    processing_time: float = Field(..., description="Time taken to process (seconds)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Document processed successfully",
                "document_id": "doc_123",
                "processing_time": 2.5
            }
        }
    )

class StoryPointEstimate(BaseModel):
    story_points: int = Field(..., description="Estimated story points")
    confidence: float = Field(..., description="Confidence level (0-1)")
    reasoning: str = Field(..., description="Explanation for the estimate")
    complexity_factors: List[str] = Field(default_factory=list)
    similar_stories: List[str] = Field(default_factory=list, description="Similar stories used for estimation")
    
    @field_validator('story_points')
    @classmethod
    def validate_story_points(cls, v):
        valid_points = [1, 2, 3, 5, 8, 13, 21]
        if v not in valid_points:
            raise ValueError(f"Story points must be one of: {valid_points}")
        return v
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story_points": 5,
                "confidence": 0.85,
                "reasoning": "Medium complexity based on similar authentication features",
                "complexity_factors": ["Database integration", "Security requirements"]
            }
        }
    )

class ContributorInfo(BaseModel):
    name: str = Field(..., description="Contributor name")
    role: Optional[str] = Field(None, description="Role or title")
    email: Optional[str] = Field(None, description="Email address")
    confidence: float = Field(..., description="Confidence in identification")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "role": "Software Engineer",
                "email": "john.doe@example.com",
                "confidence": 0.9
            }
        }
    )

class JiraIssueMapping(BaseModel):
    """Mapping between extracted artifacts and Jira issue structure"""
    issue_type: str = Field(..., description="Jira issue type (Epic, Story, etc.)")
    project_key: str = Field(..., description="Jira project key")
    summary: str = Field(..., description="Issue summary")
    description: str = Field(..., description="Issue description")
    priority: str = Field(..., description="Issue priority")
    labels: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    fix_versions: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "issue_type": "Story",
                "project_key": "PROJ",
                "summary": "User Authentication Feature",
                "description": "Implement secure user authentication",
                "priority": "High"
            }
        }
    )

class ProcessingMetrics(BaseModel):
    """Metrics for document processing performance"""
    total_time: float = Field(..., description="Total processing time in seconds")
    ai_processing_time: float = Field(..., description="AI processing time in seconds")
    extraction_time: float = Field(..., description="Artifact extraction time in seconds")
    validation_time: float = Field(..., description="Validation time in seconds")
    word_count: int = Field(..., description="Document word count")
    epics_extracted: int = Field(..., description="Number of epics extracted")
    stories_extracted: int = Field(..., description="Number of stories extracted")
    model_used: str = Field(..., description="AI model used for processing")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_time": 5.2,
                "ai_processing_time": 3.8,
                "extraction_time": 1.0,
                "validation_time": 0.4,
                "word_count": 1500,
                "epics_extracted": 3,
                "stories_extracted": 12,
                "model_used": "llama3.2:3b"
            }
        }
    )

class ValidationResult(BaseModel):
    """Result of artifact validation"""
    is_valid: bool = Field(..., description="Whether the artifacts are valid")
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_valid": True,
                "errors": [],
                "warnings": ["Story points missing for 2 stories"],
                "suggestions": ["Consider adding acceptance criteria to all stories"]
            }
        }
    )

class ProjectConfiguration(BaseModel):
    """Configuration for project processing"""
    project_id: str = Field(..., description="Project identifier")
    project_name: str = Field(..., description="Project name")
    jira_project_key: str = Field(..., description="Jira project key")
    default_priority: Priority = Field(default=Priority.MEDIUM)
    auto_assign: bool = Field(default=False)
    team_members: List[str] = Field(default_factory=list)
    story_point_scale: List[int] = Field(default=[1, 2, 3, 5, 8, 13, 21])
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "proj_123",
                "project_name": "AI Project Manager",
                "jira_project_key": "AIPM",
                "default_priority": "medium",
                "team_members": ["alice@example.com", "bob@example.com"]
            }
        }
    )


# Design Document Processing Schemas

class IssueType(str, Enum):
    FEATURE = "feature"
    TASK = "task"
    BUG = "bug"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"


class ComplexityLevel(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class DevelopmentIssue(BaseModel):
    """Represents a granular development issue generated from design documents"""
    id: str = Field(..., description="Unique issue identifier")
    title: str = Field(..., description="Issue title (max 60 chars)")
    description: str = Field(..., description="Detailed issue description")
    issue_type: IssueType = Field(..., description="Type of issue")
    priority: Priority = Field(..., description="Issue priority")
    component: str = Field(..., description="Component or functional area")
    estimated_hours: float = Field(..., description="Estimated effort in hours")
    dependencies: List[str] = Field(default_factory=list, description="Issue IDs this depends on")
    labels: List[str] = Field(default_factory=list, description="Issue labels/tags")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    created_at: datetime = Field(default_factory=get_utc_now)
    
    @field_validator('estimated_hours')
    @classmethod
    def validate_estimated_hours(cls, v):
        if not 0.5 <= v <= 40:
            raise ValueError("Estimated hours must be between 0.5 and 40")
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title_length(cls, v):
        if len(v) > 60:
            raise ValueError("Title must be 60 characters or less")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "auth_setup_abc123",
                "title": "Implement user authentication service",
                "description": "Create JWT-based authentication service with login/logout",
                "issue_type": "feature",
                "priority": "high",
                "component": "Authentication",
                "estimated_hours": 6.0,
                "dependencies": ["security_config_xyz789"],
                "labels": ["authentication", "security", "backend"],
                "acceptance_criteria": [
                    "JWT token generation working",
                    "Login endpoint functional",
                    "Logout endpoint functional",
                    "Unit tests pass"
                ]
            }
        }
    )


class FunctionalArea(BaseModel):
    """Represents a functional area of the system that can be developed independently"""
    name: str = Field(..., description="Functional area name")
    description: str = Field(..., description="What this area is responsible for")
    components: List[str] = Field(default_factory=list, description="System components in this area")
    dependencies: List[str] = Field(default_factory=list, description="Other areas this depends on")
    priority: Priority = Field(default=Priority.MEDIUM, description="Development priority")
    complexity: ComplexityLevel = Field(default=ComplexityLevel.MEDIUM, description="Implementation complexity")
    estimated_issues: int = Field(default=0, description="Estimated number of issues")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "User Management",
                "description": "Handle user registration, authentication, and profile management",
                "components": ["UserService", "AuthController", "UserRepository"],
                "dependencies": ["Database Layer"],
                "priority": "high",
                "complexity": "medium",
                "estimated_issues": 8
            }
        }
    )


class DesignAnalysis(BaseModel):
    """Analysis results from processing a design document"""
    system_components: List[str] = Field(default_factory=list, description="Major system components")
    apis_interfaces: List[str] = Field(default_factory=list, description="APIs and interfaces")
    data_models: List[str] = Field(default_factory=list, description="Data structures and models")
    external_dependencies: List[str] = Field(default_factory=list, description="External dependencies")
    technical_requirements: List[str] = Field(default_factory=list, description="Non-functional requirements")
    user_interactions: List[str] = Field(default_factory=list, description="User flows and interactions")
    business_logic: List[str] = Field(default_factory=list, description="Core business rules")
    infrastructure_needs: List[str] = Field(default_factory=list, description="Infrastructure requirements")
    complexity_assessment: ComplexityLevel = Field(default=ComplexityLevel.MEDIUM, description="Overall complexity")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "system_components": ["UserService", "PaymentService", "NotificationService"],
                "apis_interfaces": ["GET /api/users", "POST /api/auth/login"],
                "data_models": ["User", "Payment", "Notification"],
                "external_dependencies": ["Stripe API", "SendGrid", "Redis"],
                "technical_requirements": ["99.9% uptime", "< 200ms response time"],
                "complexity_assessment": "medium"
            }
        }
    )


class ImplementationRoadmap(BaseModel):
    """Implementation roadmap with phases and timelines"""
    phases: List[Dict[str, Any]] = Field(default_factory=list, description="Development phases")
    total_estimated_hours: float = Field(..., description="Total estimated effort")
    total_issues: int = Field(..., description="Total number of issues")
    estimated_duration_weeks: Optional[int] = Field(None, description="Estimated duration in weeks")
    critical_path: List[str] = Field(default_factory=list, description="Critical path issue IDs")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phases": [
                    {
                        "name": "Phase 1: Foundation",
                        "description": "Setup infrastructure and core services",
                        "issues": 5,
                        "estimated_hours": 40.0,
                        "issue_ids": ["infra_setup_abc123", "db_setup_def456"]
                    }
                ],
                "total_estimated_hours": 120.0,
                "total_issues": 25,
                "estimated_duration_weeks": 6
            }
        }
    )


class DesignDocumentProcessingRequest(BaseModel):
    """Request for processing a design document into issues"""
    content: str = Field(..., description="Design document content")
    document_name: str = Field(..., description="Document name")
    document_type: DocumentType = Field(default=DocumentType.DESIGN_DOC, description="Type of design document")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    processing_options: Dict[str, Any] = Field(default_factory=dict, description="Processing configuration")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "# E-commerce Platform Design\n\nThis document outlines...",
                "document_name": "ecommerce_design.md",
                "document_type": "design_doc",
                "project_id": "ecom_proj_123",
                "processing_options": {
                    "max_issues_per_area": 8,
                    "include_cross_cutting": True,
                    "generate_roadmap": True
                }
            }
        }
    )


class DesignDocumentProcessingResponse(BaseModel):
    """Response from design document processing"""
    success: bool = Field(..., description="Whether processing was successful")
    document_name: str = Field(..., description="Processed document name")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    total_issues: int = Field(..., description="Total number of issues generated")
    design_analysis: DesignAnalysis = Field(..., description="Analysis of the design document")
    functional_areas: List[FunctionalArea] = Field(..., description="Identified functional areas")
    issues: List[DevelopmentIssue] = Field(..., description="Generated development issues")
    implementation_roadmap: ImplementationRoadmap = Field(..., description="Implementation roadmap")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "document_name": "ecommerce_design.md",
                "project_id": "ecom_proj_123",
                "total_issues": 32,
                "metadata": {
                    "processing_timestamp": "2024-01-15T10:30:00Z",
                    "document_complexity": "medium",
                    "estimated_total_hours": 240.0
                },
                "processing_time": 15.3
            }
        }
    )


class IssueValidationResult(BaseModel):
    """Result of validating generated issues"""
    is_valid: bool = Field(..., description="Whether all issues are valid")
    total_issues: int = Field(..., description="Total number of issues validated")
    valid_issues: int = Field(..., description="Number of valid issues")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    validation_warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_valid": True,
                "total_issues": 25,
                "valid_issues": 23,
                "validation_errors": [],
                "validation_warnings": ["2 issues missing acceptance criteria"],
                "suggestions": ["Consider adding more detailed descriptions"]
            }
        }
    ) 