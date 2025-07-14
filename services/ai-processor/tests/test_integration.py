"""
Integration tests that verify service interactions work properly.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from ai_processor.services.document_orchestrator import DocumentOrchestrator
from ai_processor.services.document_parser import DocumentParser
from ai_processor.services.story_enhancer import StoryEnhancer
from ai_processor.services.ollama_client import OllamaClient
from ai_processor.services.nlp_pipeline import NLPPipeline
from ai_processor.database import MongoDB
from ai_processor.models.schemas import (
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    ExtractedArtifacts,
    Epic,
    UserStory,
    AcceptanceCriteria,
    StoryPointEstimate,
    DocumentType,
    Priority
)


class TestServiceIntegration:
    """Test integration between services"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_database = Mock()
        self.mock_ai_client = Mock()
        
        # Create service instances with mocked dependencies
        self.nlp_pipeline = NLPPipeline()
        self.document_parser = DocumentParser(
            ai_client=self.mock_ai_client,
            nlp_pipeline=self.nlp_pipeline
        )
        self.story_enhancer = StoryEnhancer(ai_client=self.mock_ai_client)
        self.orchestrator = DocumentOrchestrator(
            document_parser=self.document_parser,
            story_enhancer=self.story_enhancer,
            nlp_pipeline=self.nlp_pipeline,
            database=self.mock_database
        )
    
    @pytest.mark.asyncio
    async def test_document_processing_flow(self):
        """Test the complete document processing flow"""
        # Mock AI client responses
        mock_epic_response = {
            "epics": [
                {
                    "title": "User Management",
                    "description": "Handle user accounts and authentication",
                    "goal": "Provide secure user management"
                }
            ]
        }
        
        mock_story_response = {
            "user_stories": [
                {
                    "title": "User Registration",
                    "description": "As a new user, I want to create an account",
                    "role": "new user",
                    "action": "create an account",
                    "benefit": "access the system"
                }
            ]
        }
        
        mock_project_info = {
            "summary": "A comprehensive user management system",
            "features": ["Authentication", "User profiles", "Role management"],
            "technical_requirements": ["Database", "API", "Security"],
            "estimated_duration": "3 months"
        }
        
        # Configure mocks
        self.mock_ai_client.get_structured_response = AsyncMock(
            side_effect=[mock_epic_response, mock_story_response, mock_project_info]
        )
        self.mock_database.save_document_processing_result = AsyncMock(return_value="doc_123")
        
        # Test document processing
        result = await self.orchestrator.process_document(
            content="# User Management System\n\nWe need to build a comprehensive user management system...",
            document_name="user_management.md",
            document_type="markdown",
            project_id="proj_123"
        )
        
        # Verify result
        assert isinstance(result, DocumentProcessingResponse)
        assert result.success is True
        assert result.document_id == "doc_123"
        assert result.processing_time > 0
        assert len(result.artifacts.epics) == 1
        assert result.artifacts.epics[0].title == "User Management"
        assert len(result.artifacts.user_stories) == 1
        assert result.artifacts.user_stories[0].title == "User Registration"
        assert result.artifacts.project_summary == "A comprehensive user management system"
        
        # Verify service interactions
        assert self.mock_ai_client.get_structured_response.call_count == 3
        self.mock_database.save_document_processing_result.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_story_enhancement_flow(self):
        """Test the story enhancement flow"""
        # Create a basic user story
        story = UserStory(
            title="User Login",
            description="As a user, I want to login to the system",
            role="user",
            action="login to the system",
            benefit="access my account"
        )
        
        # Mock acceptance criteria response
        mock_criteria_response = {
            "acceptance_criteria": [
                {
                    "scenario": "Valid login",
                    "steps": [
                        "Given I have valid credentials",
                        "When I enter them on the login page",
                        "Then I should be redirected to the dashboard"
                    ]
                }
            ]
        }
        
        self.mock_ai_client.get_structured_response = AsyncMock(return_value=mock_criteria_response)
        
        # Test story enhancement
        enhanced_story = await self.story_enhancer.enhance_story(story)
        
        # Verify enhancement
        assert enhanced_story.title == "User Login"
        assert len(enhanced_story.acceptance_criteria) == 1
        assert enhanced_story.acceptance_criteria[0].scenario == "Valid login"
        assert len(enhanced_story.acceptance_criteria[0].steps) == 3
        
        # Verify service call
        self.mock_ai_client.get_structured_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_story_point_estimation(self):
        """Test story point estimation"""
        # Mock estimation response
        mock_estimate_response = {
            "story_points": 5,
            "confidence": 0.85,
            "reasoning": "Medium complexity with authentication and validation",
            "risks": ["Authentication", "Validation"],
            "assumptions": ["Database interaction"]
        }
        
        self.mock_ai_client.get_structured_response = AsyncMock(return_value=mock_estimate_response)
        
        # Test estimation
        estimate = await self.story_enhancer.estimate_story_points(
            story_title="User Login",
            story_description="As a user, I want to login to the system",
            acceptance_criteria=["Valid credentials", "Error handling"]
        )
        
        # Verify estimation
        assert estimate.story_points == 5
        assert estimate.confidence == 0.85
        assert estimate.reasoning == "Medium complexity with authentication and validation"
        assert len(estimate.complexity_factors) == 3
        
        # Verify service call
        self.mock_ai_client.get_structured_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_integration(self):
        """Test error handling across service integration"""
        # Mock AI client to raise an exception
        self.mock_ai_client.get_structured_response = AsyncMock(
            side_effect=Exception("AI service unavailable")
        )
        
        # Test that errors are properly handled
        with pytest.raises(Exception) as exc_info:
            await self.orchestrator.process_document(
                content="Test content",
                document_name="test.md",
                document_type="markdown"
            )
        
        # Verify error is propagated
        assert "AI service unavailable" in str(exc_info.value)
    
    def test_service_dependencies(self):
        """Test that services have proper dependencies"""
        # Verify orchestrator has required services
        assert hasattr(self.orchestrator, 'document_parser')
        assert hasattr(self.orchestrator, 'story_enhancer')
        assert hasattr(self.orchestrator, 'nlp_pipeline')
        assert hasattr(self.orchestrator, 'database')
        
        # Verify parser has required dependencies
        assert hasattr(self.document_parser, 'ai_client')
        assert hasattr(self.document_parser, 'nlp_pipeline')
        
        # Verify enhancer has required dependencies
        assert hasattr(self.story_enhancer, 'ai_client')
        
        # Verify configuration is loaded
        assert hasattr(self.document_parser, 'model')
        assert hasattr(self.story_enhancer, 'model')
    
    def test_service_configuration(self):
        """Test that services are properly configured"""
        # Check that services use configuration
        assert self.document_parser.model is not None
        assert self.story_enhancer.model is not None
        assert self.document_parser.temperature is not None
        assert self.story_enhancer.temperature is not None
        
        # Check story point scale configuration
        assert self.story_enhancer.story_point_scale is not None
        assert isinstance(self.story_enhancer.story_point_scale, list)


class TestOllamaClientIntegration:
    """Test Ollama client integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = OllamaClient()
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.base_url == "http://localhost:11434"
        assert self.client.client is not None
    
    @pytest.mark.asyncio
    async def test_client_methods_exist(self):
        """Test that expected methods exist"""
        assert hasattr(self.client, 'chat')
        assert hasattr(self.client, 'generate')
        assert hasattr(self.client, 'list_models')
        assert hasattr(self.client, 'get_structured_response')
        assert hasattr(self.client, 'health_check')
    
    @pytest.mark.asyncio
    async def test_client_error_handling(self):
        """Test client error handling"""
        # This will test actual error handling when Ollama is not available
        with pytest.raises(Exception):
            await self.client.health_check()
    
    @pytest.mark.asyncio
    async def test_client_cleanup(self):
        """Test client cleanup"""
        await self.client.close()
        # After close, client should be closed
        assert self.client.client.is_closed


class TestDatabaseIntegration:
    """Test database integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.db = MongoDB()
    
    def test_database_initialization(self):
        """Test database initialization"""
        assert self.db.client is None  # Not connected yet
        assert self.db.database is None  # Not connected yet
        assert self.db.collection_name == "documents"
    
    def test_database_methods_exist(self):
        """Test that expected methods exist"""
        assert hasattr(self.db, 'connect')
        assert hasattr(self.db, 'disconnect')
        assert hasattr(self.db, 'save_document_processing_result')
        assert hasattr(self.db, 'get_document')
        assert hasattr(self.db, 'update_document')
        assert hasattr(self.db, 'delete_document')
    
    def test_object_id_validation(self):
        """Test ObjectId validation"""
        # Valid ObjectId
        assert self.db.validate_object_id("507f1f77bcf86cd799439011") is True
        
        # Invalid ObjectId
        assert self.db.validate_object_id("invalid_id") is False
        assert self.db.validate_object_id("") is False
        assert self.db.validate_object_id(None) is False


class TestNLPPipelineIntegration:
    """Test NLP pipeline integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = NLPPipeline()
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        assert self.pipeline is not None
    
    def test_pipeline_methods_exist(self):
        """Test that expected methods exist"""
        assert hasattr(self.pipeline, 'extract_entities')
        assert hasattr(self.pipeline, 'analyze_sentiment')
        assert hasattr(self.pipeline, 'extract_keywords')
        assert hasattr(self.pipeline, 'preprocess_text')
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self):
        """Test entity extraction functionality"""
        text = "Alice Smith and Bob Johnson are working on the authentication feature"
        
        result = await self.pipeline.extract_entities(text)
        
        # Result should be an EntityExtraction object
        assert hasattr(result, 'persons')
        assert hasattr(result, 'organizations')
        assert hasattr(result, 'features')
        assert hasattr(result, 'technical_terms')
        
        # Should find person names
        assert len(result.persons) >= 2
        assert 'Alice Smith' in result.persons
        assert 'Bob Johnson' in result.persons
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        positive_text = "This is a great feature that users will love"
        negative_text = "This feature is problematic and causes issues"
        
        positive_result = await self.pipeline.analyze_sentiment(positive_text)
        negative_result = await self.pipeline.analyze_sentiment(negative_text)
        
        # Should return sentiment classifications
        assert positive_result in ['positive', 'neutral', 'negative']
        assert negative_result in ['positive', 'neutral', 'negative']
    
    @pytest.mark.asyncio
    async def test_keyword_extraction(self):
        """Test keyword extraction"""
        text = "User authentication login security password database validation"
        
        result = await self.pipeline.extract_keywords(text)
        
        # Should return a list of keywords
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should contain relevant keywords
        keywords_text = ' '.join(result)
        assert any(keyword in keywords_text for keyword in ['authentication', 'login', 'security', 'password', 'database'])
    
    @pytest.mark.asyncio
    async def test_text_preprocessing(self):
        """Test text preprocessing"""
        text = "This is a TEST document with SPECIAL characters!@# and   extra   spaces"
        
        result = await self.pipeline.preprocess_text(text)
        
        # Should return cleaned text
        assert isinstance(result, str)
        assert result != text  # Should be different from original
        assert len(result) > 0
        
        # Should handle basic cleaning
        assert "test" in result.lower()
        assert "document" in result.lower()
        assert "special" in result.lower() 