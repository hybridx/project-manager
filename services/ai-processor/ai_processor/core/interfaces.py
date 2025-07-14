"""
Abstract interfaces for the AI processor service.
Following SOLID principles for better testability and maintainability.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from ..models.schemas import (
    Epic, UserStory, AcceptanceCriteria, StoryPointEstimate,
    ExtractedArtifacts, DocumentProcessingResponse
)


class AIClientProtocol(Protocol):
    """Protocol for AI client implementations"""
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Send a chat completion request"""
        ...
    
    async def get_structured_response(
        self,
        model: str,
        prompt: str,
        response_format: str = "json",
        **kwargs
    ) -> Dict[str, Any]:
        """Get structured response from AI model"""
        ...


class DocumentParserProtocol(Protocol):
    """Protocol for document parsing implementations"""
    
    async def extract_epics(self, content: str) -> List[Epic]:
        """Extract epics from document content"""
        ...
    
    async def extract_user_stories(self, content: str, epics: List[Epic]) -> List[UserStory]:
        """Extract user stories from document content"""
        ...
    
    async def extract_project_info(self, content: str) -> Dict[str, Any]:
        """Extract project information from document content"""
        ...


class StoryEnhancerProtocol(Protocol):
    """Protocol for story enhancement implementations"""
    
    async def generate_acceptance_criteria(self, story: UserStory) -> List[AcceptanceCriteria]:
        """Generate acceptance criteria for a user story"""
        ...
    
    async def estimate_story_points(
        self,
        story_title: str,
        story_description: str,
        acceptance_criteria: List[str]
    ) -> StoryPointEstimate:
        """Estimate story points for a user story"""
        ...


class DatabaseProtocol(Protocol):
    """Protocol for database implementations"""
    
    async def save_processing_result(
        self,
        document_id: str,
        document_name: str,
        document_type: str,
        content: str,
        artifacts: ExtractedArtifacts,
        project_id: Optional[str] = None
    ) -> None:
        """Save processing result to database"""
        ...


class DocumentProcessorProtocol(Protocol):
    """Protocol for document processor implementations"""
    
    async def process_document(
        self,
        content: str,
        document_name: str,
        document_type: str,
        project_id: Optional[str] = None
    ) -> DocumentProcessingResponse:
        """Process a document and extract artifacts"""
        ...


class ConfigurationManager(ABC):
    """Abstract configuration manager"""
    
    @abstractmethod
    def get_ai_model(self) -> str:
        """Get the AI model to use"""
        pass
    
    @abstractmethod
    def get_ollama_base_url(self) -> str:
        """Get Ollama base URL"""
        pass
    
    @abstractmethod
    def get_mongodb_uri(self) -> str:
        """Get MongoDB connection URI"""
        pass
    
    @abstractmethod
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration"""
        pass


class ErrorHandler(ABC):
    """Abstract error handler for consistent error management"""
    
    @abstractmethod
    async def handle_processing_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle processing errors"""
        pass
    
    @abstractmethod
    async def handle_ai_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle AI-related errors"""
        pass
    
    @abstractmethod
    async def handle_database_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle database errors"""
        pass 