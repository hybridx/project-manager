"""
Document orchestrator service following Facade pattern.
Coordinates multiple specialized services to process documents end-to-end.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ..core.interfaces import DocumentProcessorProtocol, DatabaseProtocol
from ..core.config import config
from ..core.error_handler import handle_errors, ProcessingError
from ..models.schemas import (
    DocumentProcessingResponse, ExtractedArtifacts, ValidationResult, 
    ProcessingMetrics
)
from .document_parser import DocumentParser
from .story_enhancer import StoryEnhancer
from ..services.nlp_pipeline import NLPPipeline

logger = logging.getLogger(__name__)


class DocumentOrchestrator:
    """
    Document orchestrator that coordinates multiple services to process documents.
    Follows Facade pattern to provide a simple interface to complex operations.
    """
    
    def __init__(
        self,
        document_parser: DocumentParser,
        story_enhancer: StoryEnhancer,
        nlp_pipeline: NLPPipeline,
        database: DatabaseProtocol
    ):
        self.document_parser = document_parser
        self.story_enhancer = story_enhancer
        self.nlp_pipeline = nlp_pipeline
        self.database = database
        self.processing_timeout = config.get_processing_timeout()
    
    @handle_errors("processing")
    async def process_document(
        self,
        content: str,
        document_name: str,
        document_type: str,
        project_id: Optional[str] = None
    ) -> DocumentProcessingResponse:
        """
        Process a document end-to-end using coordinated services
        
        Args:
            content: Document content
            document_name: Name of the document
            document_type: Type of document
            project_id: Associated project ID
            
        Returns:
            DocumentProcessingResponse with processed artifacts
        """
        start_time = time.time()
        document_id = str(uuid.uuid4())
        
        logger.info(f"Starting document processing: {document_name}")
        
        try:
            # Step 1: Preprocess document
            processed_content = await self._preprocess_document(content)
            logger.info("Document preprocessing completed")
            
            # Step 2: Extract basic information
            project_info = await self._extract_project_information(processed_content)
            logger.info("Project information extracted")
            
            # Step 3: Extract epics and user stories
            epics = await self.document_parser.extract_epics(processed_content)
            user_stories = await self.document_parser.extract_user_stories(processed_content, epics)
            logger.info(f"Extracted {len(epics)} epics and {len(user_stories)} user stories")
            
            # Step 4: Enhance stories with acceptance criteria and estimates
            enhanced_stories = await self.story_enhancer.enhance_multiple_stories(user_stories)
            logger.info("Stories enhanced with acceptance criteria and estimates")
            
            # Step 5: Link stories to epics and calculate epic estimates
            self._link_stories_to_epics(enhanced_stories, epics)
            self._calculate_epic_estimates(epics)
            logger.info("Stories linked to epics and estimates calculated")
            
            # Step 6: Extract contributors and additional metadata
            contributors = await self._extract_contributors(content)
            logger.info(f"Extracted {len(contributors)} contributors")
            
            # Step 7: Create artifacts bundle
            artifacts = self._create_extracted_artifacts(
                epics, enhanced_stories, contributors, project_info
            )
            
            # Step 8: Validate artifacts
            validation = await self._validate_artifacts(artifacts)
            logger.info(f"Artifacts validation: {validation.is_valid}")
            
            # Step 9: Save to database
            await self._save_processing_result(
                document_id, document_name, document_type, 
                content, artifacts, project_id
            )
            logger.info("Processing result saved to database")
            
            processing_time = time.time() - start_time
            
            response = DocumentProcessingResponse(
                success=True,
                message=f"Document processed successfully. Extracted {len(epics)} epics and {len(enhanced_stories)} user stories.",
                document_id=document_id,
                artifacts=artifacts,
                processing_time=processing_time,
                metadata={
                    "word_count": len(content.split()),
                    "model_used": config.get_ai_model(),
                    "validation_result": validation.dict(),
                    "project_id": project_id,
                    "processing_steps": [
                        "preprocessing", "project_info", "epics", "stories", 
                        "enhancement", "linking", "contributors", "validation", "storage"
                    ]
                }
            )
            
            logger.info(f"Document processing completed in {processing_time:.2f} seconds")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Document processing failed after {processing_time:.2f} seconds: {e}")
            
            return DocumentProcessingResponse(
                success=False,
                message=f"Document processing failed: {str(e)}",
                document_id=document_id,
                artifacts=None,
                processing_time=processing_time,
                metadata={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "project_id": project_id
                }
            )
    
    async def _preprocess_document(self, content: str) -> str:
        """Preprocess document content"""
        return await self.document_parser.preprocess_document(content)
    
    async def _extract_project_information(self, content: str) -> Dict[str, Any]:
        """Extract high-level project information"""
        return await self.document_parser.extract_project_info(content)
    
    async def _extract_contributors(self, content: str) -> list:
        """Extract contributors from document content"""
        entities = await self.nlp_pipeline.extract_entities(content)
        return entities.persons
    
    def _link_stories_to_epics(self, stories, epics) -> None:
        """Link user stories to their corresponding epics"""
        if not epics:
            return
            
        # Simple heuristic: link based on title similarity
        for story in stories:
            best_match_epic = None
            best_similarity = 0
            
            for epic in epics:
                # Simple word overlap similarity
                story_words = set(story.title.lower().split())
                epic_words = set(epic.title.lower().split())
                similarity = len(story_words & epic_words) / max(len(story_words | epic_words), 1)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_epic = epic
            
            # Link to best matching epic if similarity is reasonable
            if best_match_epic and best_similarity > 0.1:
                story.epic_id = best_match_epic.title
                best_match_epic.user_stories.append(story)
    
    def _calculate_epic_estimates(self, epics) -> None:
        """Calculate story point estimates for epics based on their stories"""
        for epic in epics:
            total_points = sum(story.story_points for story in epic.user_stories)
            epic.estimated_story_points = total_points
    
    def _create_extracted_artifacts(self, epics, stories, contributors, project_info) -> ExtractedArtifacts:
        """Create the extracted artifacts bundle"""
        return ExtractedArtifacts(
            epics=epics,
            user_stories=stories,
            contributors=contributors,
            project_summary=project_info.get("summary", ""),
            estimated_duration=project_info.get("duration", None),
            key_features=project_info.get("features", []),
            technical_requirements=project_info.get("tech_requirements", []),
            risks=project_info.get("risks", []),
            dependencies=project_info.get("dependencies", [])
        )
    
    async def _validate_artifacts(self, artifacts: ExtractedArtifacts) -> ValidationResult:
        """Validate the extracted artifacts"""
        errors = []
        warnings = []
        
        # Validate epics
        if not artifacts.epics:
            warnings.append("No epics were extracted from the document")
        
        for epic in artifacts.epics:
            if not epic.title:
                errors.append("Epic found without title")
            if not epic.description:
                warnings.append(f"Epic '{epic.title}' has no description")
        
        # Validate user stories
        if not artifacts.user_stories:
            warnings.append("No user stories were extracted from the document")
        
        for story in artifacts.user_stories:
            if not story.title:
                errors.append("User story found without title")
            if not story.description:
                warnings.append(f"User story '{story.title}' has no description")
            if story.story_points <= 0:
                warnings.append(f"User story '{story.title}' has no story point estimate")
            if not story.acceptance_criteria:
                warnings.append(f"User story '{story.title}' has no acceptance criteria")
        
        # Validate project information
        if not artifacts.project_summary:
            warnings.append("No project summary was extracted")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_timestamp=datetime.now(timezone.utc)
        )
    
    async def _save_processing_result(
        self,
        document_id: str,
        document_name: str,
        document_type: str,
        content: str,
        artifacts: ExtractedArtifacts,
        project_id: Optional[str]
    ) -> None:
        """Save processing result to database"""
        await self.database.save_processing_result(
            document_id, document_name, document_type, 
            content, artifacts, project_id
        ) 