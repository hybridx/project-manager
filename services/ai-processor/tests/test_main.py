"""
Test the main FastAPI application endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from ai_processor.main import app, get_document_orchestrator, get_ollama_client
from ai_processor.models.schemas import (
    DocumentProcessingRequest, 
    DocumentProcessingResponse,
    ExtractedArtifacts,
    AcceptanceCriteria,
    StoryPointEstimate
)


class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check(self):
        """Test that health check returns success"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-processor"
        assert "timestamp" in data


class TestDocumentProcessingEndpoint:
    """Test the document processing endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.mock_orchestrator = Mock()
        self.mock_artifacts = ExtractedArtifacts(
            epics=[],
            user_stories=[],
            contributors=["test user"],
            project_summary="Test project",
            key_features=["feature1", "feature2"]
        )
        self.mock_response = DocumentProcessingResponse(
            success=True,
            message="Document processed successfully",
            document_id="test_doc_123",
            artifacts=self.mock_artifacts,
            processing_time=2.5,
            metadata={"word_count": 100}
        )
    
    def test_process_document_success(self):
        """Test successful document processing"""
        self.mock_orchestrator.process_document = AsyncMock(return_value=self.mock_response)
        
        with patch.object(app, 'dependency_overrides', {get_document_orchestrator: lambda: self.mock_orchestrator}):
            response = self.client.post("/process-document", json={
                "content": "Test document content",
                "document_name": "test.md",
                "document_type": "markdown"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Document processed successfully"
        assert data["document_id"] == "test_doc_123"
        assert data["processing_time"] == 2.5
    
    def test_process_document_validation_error(self):
        """Test document processing with validation error"""
        response = self.client.post("/process-document", json={
            "content": "",  # Empty content should fail validation
            "document_name": "test.md"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_process_document_processing_error(self):
        """Test document processing with processing error"""
        self.mock_orchestrator.process_document = AsyncMock(side_effect=Exception("Processing failed"))
        
        with patch.object(app, 'dependency_overrides', {get_document_orchestrator: lambda: self.mock_orchestrator}):
            response = self.client.post("/process-document", json={
                "content": "Test document content",
                "document_name": "test.md"
            })
        
        assert response.status_code == 500


class TestFileUploadEndpoint:
    """Test the file upload endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.mock_orchestrator = Mock()
        self.mock_artifacts = ExtractedArtifacts(
            epics=[],
            user_stories=[],
            contributors=["test user"],
            project_summary="Test project",
            key_features=["feature1", "feature2"]
        )
        self.mock_response = DocumentProcessingResponse(
            success=True,
            message="File processed successfully",
            document_id="test_file_123",
            artifacts=self.mock_artifacts,
            processing_time=3.0,
            metadata={"file_size": 500}
        )
    
    def test_upload_document_success(self):
        """Test successful file upload and processing"""
        self.mock_orchestrator.process_document = AsyncMock(return_value=self.mock_response)
        
        with patch.object(app, 'dependency_overrides', {get_document_orchestrator: lambda: self.mock_orchestrator}):
            response = self.client.post(
                "/upload-document",
                files={"file": ("test.md", b"Test file content", "text/markdown")},
                data={"project_id": "proj_123"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File processed successfully"
        assert data["document_id"] == "test_file_123"
    
    def test_upload_document_no_file(self):
        """Test file upload without file"""
        response = self.client.post("/upload-document")
        
        assert response.status_code == 422  # Validation error


class TestAcceptanceCriteriaEndpoint:
    """Test the acceptance criteria generation endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.mock_orchestrator = Mock()
        self.mock_criteria = [
            AcceptanceCriteria(
                scenario="User login",
                steps=["Given user credentials", "When user logs in", "Then user is authenticated"]
            )
        ]
    
    def test_generate_acceptance_criteria_success(self):
        """Test successful acceptance criteria generation"""
        self.mock_orchestrator.generate_acceptance_criteria = AsyncMock(return_value=self.mock_criteria)
        
        with patch.object(app, 'dependency_overrides', {get_document_orchestrator: lambda: self.mock_orchestrator}):
            response = self.client.post("/generate-acceptance-criteria", params={
                "story_title": "User Authentication",
                "story_description": "As a user, I want to login securely"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["scenario"] == "User login"
        assert len(data[0]["steps"]) == 3
    
    def test_generate_acceptance_criteria_missing_params(self):
        """Test acceptance criteria generation with missing parameters"""
        response = self.client.post("/generate-acceptance-criteria")
        
        assert response.status_code == 422  # Validation error


class TestStoryPointEstimationEndpoint:
    """Test the story point estimation endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.mock_orchestrator = Mock()
        self.mock_estimate = StoryPointEstimate(
            story_points=5,
            confidence=0.8,
            reasoning="Medium complexity feature",
            complexity_factors=["Database integration", "Authentication"]
        )
    
    def test_estimate_story_points_success(self):
        """Test successful story point estimation"""
        self.mock_orchestrator.estimate_story_points = AsyncMock(return_value=self.mock_estimate)
        
        with patch.object(app, 'dependency_overrides', {get_document_orchestrator: lambda: self.mock_orchestrator}):
            response = self.client.post("/estimate-story-points", params={
                "story_title": "User Authentication",
                "story_description": "As a user, I want to login securely"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["story_points"] == 5
        assert data["confidence"] == 0.8
        assert data["reasoning"] == "Medium complexity feature"
        assert len(data["complexity_factors"]) == 2
    
    def test_estimate_story_points_with_acceptance_criteria(self):
        """Test story point estimation with acceptance criteria"""
        self.mock_orchestrator.estimate_story_points = AsyncMock(return_value=self.mock_estimate)
        
        with patch.object(app, 'dependency_overrides', {get_document_orchestrator: lambda: self.mock_orchestrator}):
            response = self.client.post("/estimate-story-points", params={
                "story_title": "User Authentication",
                "story_description": "As a user, I want to login securely",
                "acceptance_criteria": ["Given valid credentials", "When user logs in"]
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["story_points"] == 5


class TestContributorExtractionEndpoint:
    """Test the contributor extraction endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.mock_orchestrator = Mock()
        self.mock_contributors = ["alice@example.com", "bob@example.com"]
    
    def test_extract_contributors_success(self):
        """Test successful contributor extraction"""
        self.mock_orchestrator.extract_contributors = AsyncMock(return_value=self.mock_contributors)
        
        with patch.object(app, 'dependency_overrides', {get_document_orchestrator: lambda: self.mock_orchestrator}):
            response = self.client.post("/extract-contributors", params={
                "content": "Project authored by Alice and Bob"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["contributors"] == self.mock_contributors
        assert len(data["contributors"]) == 2
    
    def test_extract_contributors_missing_content(self):
        """Test contributor extraction with missing content"""
        response = self.client.post("/extract-contributors")
        
        assert response.status_code == 422  # Validation error


class TestModelsEndpoint:
    """Test the models endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.mock_ollama_client = Mock()
        self.mock_models = ["llama3.2:3b", "llama3.2:1b", "codellama:7b"]
    
    def test_get_available_models_success(self):
        """Test successful model listing"""
        self.mock_ollama_client.get_available_models = AsyncMock(return_value=self.mock_models)
        
        with patch.object(app, 'dependency_overrides', {get_ollama_client: lambda: self.mock_ollama_client}):
            response = self.client.get("/models")
        
        assert response.status_code == 200
        data = response.json()
        assert data["models"] == self.mock_models
        assert len(data["models"]) == 3
    
    def test_get_available_models_error(self):
        """Test model listing with error"""
        self.mock_ollama_client.get_available_models = AsyncMock(side_effect=Exception("Ollama service unavailable"))
        
        with patch.object(app, 'dependency_overrides', {get_ollama_client: lambda: self.mock_ollama_client}):
            response = self.client.get("/models")
        
        assert response.status_code == 500


class TestDependencyInjection:
    """Test dependency injection functions"""
    
    def test_get_document_orchestrator(self):
        """Test document orchestrator dependency"""
        orchestrator = get_document_orchestrator()
        assert orchestrator is not None
        # In a real app, this would be initialized during lifespan
        # For now, we just check it returns something
    
    def test_get_ollama_client(self):
        """Test Ollama client dependency"""
        client = get_ollama_client()
        assert client is not None
        # In a real app, this would be initialized during lifespan
        # For now, we just check it returns something 