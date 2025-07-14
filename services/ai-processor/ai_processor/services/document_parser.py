"""
Document parser service following Single Responsibility Principle.
Only responsible for parsing documents and extracting basic information.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from ..core.interfaces import DocumentParserProtocol, AIClientProtocol
from ..core.config import config
from ..core.error_handler import handle_errors, AIError
from ..models.schemas import Epic, UserStory, Priority
from ..services.nlp_pipeline import NLPPipeline

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Document parser service that extracts structured information from documents.
    Follows Single Responsibility Principle - only handles document parsing.
    """
    
    def __init__(self, ai_client: AIClientProtocol, nlp_pipeline: NLPPipeline):
        self.ai_client = ai_client
        self.nlp_pipeline = nlp_pipeline
        self.model = config.get_ai_model()
        self.temperature = config.get_ai_temperature()
    
    @handle_errors("ai")
    async def extract_epics(self, content: str) -> List[Epic]:
        """Extract epics from document content"""
        logger.info("Extracting epics from document")
        
        prompt = self._get_epic_extraction_prompt(content)
        
        try:
            response = await self.ai_client.get_structured_response(
                model=self.model,
                prompt=prompt,
                response_format="json",
                temperature=self.temperature
            )
            
            return self._parse_epics_response(response)
        
        except Exception as e:
            raise AIError(f"Failed to extract epics: {str(e)}", self.model, {"content_length": len(content)})
    
    @handle_errors("ai")
    async def extract_user_stories(self, content: str, epics: List[Epic]) -> List[UserStory]:
        """Extract user stories from document content"""
        logger.info(f"Extracting user stories for {len(epics)} epics")
        
        prompt = self._get_user_stories_extraction_prompt(content, epics)
        
        try:
            response = await self.ai_client.get_structured_response(
                model=self.model,
                prompt=prompt,
                response_format="json",
                temperature=self.temperature
            )
            
            return self._parse_user_stories_response(response, epics)
        
        except Exception as e:
            raise AIError(f"Failed to extract user stories: {str(e)}", self.model, {"epic_count": len(epics)})
    
    @handle_errors("ai")
    async def extract_project_info(self, content: str) -> Dict[str, Any]:
        """Extract project information from document content"""
        logger.info("Extracting project information")
        
        prompt = self._get_project_info_extraction_prompt(content)
        
        try:
            response = await self.ai_client.get_structured_response(
                model=self.model,
                prompt=prompt,
                response_format="json",
                temperature=self.temperature
            )
            
            return self._parse_project_info_response(response)
        
        except Exception as e:
            raise AIError(f"Failed to extract project info: {str(e)}", self.model, {"content_length": len(content)})
    
    async def preprocess_document(self, content: str) -> str:
        """Preprocess document content for better parsing"""
        return await self.nlp_pipeline.preprocess_text(content)
    
    def _get_epic_extraction_prompt(self, content: str) -> str:
        """Get prompt for epic extraction"""
        return f"""
        You are a skilled product manager. Analyze the following document and extract epics.
        
        Document:
        {content}
        
        Extract epics that represent large bodies of work. Return a JSON array of objects with:
        - title: Epic title
        - description: Epic description
        - priority: "high", "medium", or "low"
        - acceptance_criteria: Brief criteria for epic completion
        
        Focus on:
        - Major features or capabilities
        - Distinct functional areas
        - User-facing value propositions
        
        Return only valid JSON array of epic objects.
        """
    
    def _get_user_stories_extraction_prompt(self, content: str, epics: List[Epic]) -> str:
        """Get prompt for user story extraction"""
        epic_titles = [epic.title for epic in epics]
        return f"""
        You are a skilled product manager. Extract user stories from the document.
        
        Document:
        {content}
        
        Available Epics: {epic_titles}
        
        Extract user stories following this format:
        - title: Clear, concise title
        - description: "As a [user], I want [goal] so that [benefit]"
        - priority: "high", "medium", or "low"
        - estimated_effort: "small", "medium", or "large"
        
        Return a JSON array of user story objects.
        Each story should be actionable and testable.
        """
    
    def _get_project_info_extraction_prompt(self, content: str) -> str:
        """Get prompt for project info extraction"""
        return f"""
        Analyze the following document and extract high-level project information.
        
        Document:
        {content}
        
        Extract and return a JSON object with:
        {{
            "summary": "Brief project summary (1-2 sentences)",
            "duration": "Estimated project duration",
            "features": ["List of key features"],
            "tech_requirements": ["List of technical requirements"],
            "risks": ["List of potential risks"],
            "dependencies": ["List of dependencies"],
            "success_criteria": ["List of success criteria"]
        }}
        
        Return only valid JSON.
        """
    
    def _parse_epics_response(self, response: Dict[str, Any]) -> List[Epic]:
        """Parse AI response into Epic objects"""
        epics = []
        
        if isinstance(response, list):
            epic_data = response
        else:
            epic_data = response.get("epics", [])
        
        for item in epic_data:
            try:
                epic = Epic(
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    priority=Priority(item.get("priority", "medium")),
                    acceptance_criteria=item.get("acceptance_criteria", ""),
                    estimated_story_points=0,  # Will be calculated later
                    user_stories=[]  # Will be populated later
                )
                epics.append(epic)
            except Exception as e:
                logger.warning(f"Failed to parse epic: {item}, error: {e}")
                continue
        
        return epics
    
    def _parse_user_stories_response(self, response: Dict[str, Any], epics: List[Epic]) -> List[UserStory]:
        """Parse AI response into UserStory objects"""
        user_stories = []
        
        if isinstance(response, list):
            story_data = response
        else:
            story_data = response.get("user_stories", [])
        
        for item in story_data:
            try:
                user_story = UserStory(
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    priority=Priority(item.get("priority", "medium")),
                    story_points=0,  # Will be estimated later
                    acceptance_criteria=[],  # Will be generated later
                    epic_id=None,  # Will be linked later
                    status="backlog",
                    estimated_effort=item.get("estimated_effort", "medium")
                )
                user_stories.append(user_story)
            except Exception as e:
                logger.warning(f"Failed to parse user story: {item}, error: {e}")
                continue
        
        return user_stories
    
    def _parse_project_info_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into project info dictionary"""
        default_info = {
            "summary": "Project information could not be extracted",
            "duration": None,
            "features": [],
            "tech_requirements": [],
            "risks": [],
            "dependencies": [],
            "success_criteria": []
        }
        
        if not isinstance(response, dict):
            return default_info
        
        return {
            "summary": response.get("summary", default_info["summary"]),
            "duration": response.get("duration", default_info["duration"]),
            "features": response.get("features", default_info["features"]),
            "tech_requirements": response.get("tech_requirements", default_info["tech_requirements"]),
            "risks": response.get("risks", default_info["risks"]),
            "dependencies": response.get("dependencies", default_info["dependencies"]),
            "success_criteria": response.get("success_criteria", default_info["success_criteria"])
        } 