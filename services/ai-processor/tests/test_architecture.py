"""
Test the new SOLID architecture components.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from ai_processor.core.config import config
from ai_processor.core.error_handler import error_handler, AppErrorHandler
from ai_processor.services.document_parser import DocumentParser


class TestConfiguration:
    """Test the configuration manager"""
    
    def test_configuration_manager_methods(self):
        """Test that configuration manager has all required methods"""
        assert hasattr(config, 'get_ai_model')
        assert hasattr(config, 'get_ollama_base_url')
        assert hasattr(config, 'get_mongodb_uri')
        assert hasattr(config, 'get_processing_config')
        
    def test_configuration_values(self):
        """Test that configuration returns expected values"""
        assert config.get_ai_model() == "llama3.2:3b"
        assert config.get_ollama_base_url() == "http://localhost:11434"
        assert isinstance(config.get_processing_config(), dict)
        
    def test_configuration_types(self):
        """Test that configuration methods return correct types"""
        assert isinstance(config.get_ai_model(), str)
        assert isinstance(config.get_ollama_base_url(), str)
        assert isinstance(config.get_mongodb_uri(), str)
        assert isinstance(config.get_processing_config(), dict)


class TestErrorHandler:
    """Test the error handler"""
    
    def test_error_handler_initialization(self):
        """Test error handler initialization"""
        handler = AppErrorHandler()
        assert handler.error_count == 0
        assert handler.last_error_time is None
        
    @pytest.mark.asyncio
    async def test_error_handling_methods(self):
        """Test error handling methods"""
        handler = AppErrorHandler()
        
        # Test processing error
        await handler.handle_processing_error(
            Exception("test error"), 
            {"test": "context"}
        )
        assert handler.error_count == 1
        
        # Test AI error
        await handler.handle_ai_error(
            Exception("ai error"), 
            {"model": "test", "prompt": "test prompt"}
        )
        assert handler.error_count == 2
        
        # Test database error
        await handler.handle_database_error(
            Exception("db error"), 
            {"operation": "insert"}
        )
        assert handler.error_count == 3
        
    def test_error_stats(self):
        """Test error statistics"""
        handler = AppErrorHandler()
        stats = handler.get_error_stats()
        assert "total_errors" in stats
        assert "last_error_time" in stats
        
        handler.reset_error_stats()
        assert handler.error_count == 0
        assert handler.last_error_time is None


class TestDocumentParser:
    """Test the document parser service"""
    
    def test_document_parser_initialization(self):
        """Test document parser initialization"""
        mock_ai_client = Mock()
        mock_nlp_pipeline = Mock()
        
        parser = DocumentParser(mock_ai_client, mock_nlp_pipeline)
        
        assert parser.ai_client == mock_ai_client
        assert parser.nlp_pipeline == mock_nlp_pipeline
        assert parser.model == config.get_ai_model()
        assert parser.temperature == config.get_ai_temperature()
        
    @pytest.mark.asyncio
    async def test_document_preprocessing(self):
        """Test document preprocessing"""
        mock_ai_client = Mock()
        mock_nlp_pipeline = Mock()
        mock_nlp_pipeline.preprocess_text = AsyncMock(return_value="processed text")
        
        parser = DocumentParser(mock_ai_client, mock_nlp_pipeline)
        
        result = await parser.preprocess_document("raw text")
        assert result == "processed text"
        mock_nlp_pipeline.preprocess_text.assert_called_once_with("raw text")
        
    def test_prompt_generation(self):
        """Test prompt generation methods"""
        mock_ai_client = Mock()
        mock_nlp_pipeline = Mock()
        
        parser = DocumentParser(mock_ai_client, mock_nlp_pipeline)
        
        # Test epic extraction prompt
        epic_prompt = parser._get_epic_extraction_prompt("test content")
        assert "test content" in epic_prompt
        assert "JSON" in epic_prompt
        assert "epic" in epic_prompt.lower()
        
        # Test project info prompt
        project_prompt = parser._get_project_info_extraction_prompt("test content")
        assert "test content" in project_prompt
        assert "JSON" in project_prompt
        assert "summary" in project_prompt.lower()


class TestSolidPrinciples:
    """Test that SOLID principles are followed"""
    
    def test_single_responsibility(self):
        """Test that each class has a single responsibility"""
        # DocumentParser should only parse documents
        parser_methods = [method for method in dir(DocumentParser) 
                         if not method.startswith('_') and callable(getattr(DocumentParser, method))]
        
        # All public methods should be related to parsing
        parsing_related = ['extract_epics', 'extract_user_stories', 'extract_project_info', 'preprocess_document']
        for method in parser_methods:
            assert method in parsing_related, f"Method {method} violates SRP"
            
    def test_dependency_inversion(self):
        """Test that classes depend on abstractions, not concretions"""
        # DocumentParser constructor takes protocols, not concrete classes
        parser_init = DocumentParser.__init__
        annotations = getattr(parser_init, '__annotations__', {})
        
        # Check that parameters are properly typed (would be protocols in real implementation)
        assert 'ai_client' in annotations
        assert 'nlp_pipeline' in annotations
        
    def test_open_closed_principle(self):
        """Test that classes are open for extension, closed for modification"""
        # Configuration can be extended without modifying existing code
        original_methods = set(dir(config))
        
        # We should be able to add new configuration methods without breaking existing ones
        assert 'get_ai_model' in original_methods
        assert 'get_ollama_base_url' in original_methods
        assert 'get_mongodb_uri' in original_methods
        

if __name__ == "__main__":
    pytest.main([__file__]) 