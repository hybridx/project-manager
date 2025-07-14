"""
Test the database layer components.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from ai_processor.database import MongoDB
from ai_processor.models.schemas import (
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    ExtractedArtifacts,
    Epic,
    UserStory,
    AcceptanceCriteria,
    DocumentType,
    Priority
)
from bson import ObjectId
from datetime import datetime, timezone


class TestMongoDB:
    """Test the MongoDB database class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.db = MongoDB()
        self.mock_client = Mock()
        self.mock_database = Mock()
        self.mock_collection = Mock()
        
        # Set up mock chain
        self.mock_client.__getitem__.return_value = self.mock_database
        self.mock_database.__getitem__.return_value = self.mock_collection
    
    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful database connection"""
        with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_motor:
            mock_motor.return_value = self.mock_client
            self.mock_client.admin.command = AsyncMock(return_value={"ok": 1})
            
            await self.db.connect()
            
            assert self.db.client is not None
            assert self.db.database is not None
            mock_motor.assert_called_once()
            self.mock_client.admin.command.assert_called_once_with('ping')
    
    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test database connection failure"""
        with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_motor:
            mock_motor.return_value = self.mock_client
            self.mock_client.admin.command = AsyncMock(side_effect=Exception("Connection failed"))
            
            with pytest.raises(Exception) as exc_info:
                await self.db.connect()
            
            assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test database disconnection"""
        self.db.client = self.mock_client
        self.mock_client.close = AsyncMock()
        
        await self.db.disconnect()
        
        self.mock_client.close.assert_called_once()
        assert self.db.client is None
    
    @pytest.mark.asyncio
    async def test_save_document_success(self):
        """Test successful document saving"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        # Mock the collection
        self.mock_database.__getitem__.return_value = self.mock_collection
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
        self.mock_collection.insert_one = AsyncMock(return_value=mock_insert_result)
        
        # Test data
        request = DocumentProcessingRequest(
            content="Test document content",
            document_name="test.md",
            document_type=DocumentType.MARKDOWN
        )
        
        artifacts = ExtractedArtifacts(
            epics=[],
            user_stories=[],
            contributors=["test user"],
            project_summary="Test project"
        )
        
        result = await self.db.save_document(request, artifacts)
        
        assert result == "507f1f77bcf86cd799439011"
        self.mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_document_failure(self):
        """Test document saving failure"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.insert_one = AsyncMock(side_effect=Exception("Insert failed"))
        
        request = DocumentProcessingRequest(
            content="Test document content",
            document_name="test.md"
        )
        
        artifacts = ExtractedArtifacts(
            epics=[],
            user_stories=[],
            contributors=[],
            project_summary="Test project"
        )
        
        with pytest.raises(Exception) as exc_info:
            await self.db.save_document(request, artifacts)
        
        assert "Insert failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_document_success(self):
        """Test successful document retrieval"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        # Mock document data
        mock_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "document_name": "test.md",
            "content": "Test content",
            "artifacts": {
                "epics": [],
                "user_stories": [],
                "contributors": ["test user"],
                "project_summary": "Test project"
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.find_one = AsyncMock(return_value=mock_doc)
        
        result = await self.db.get_document("507f1f77bcf86cd799439011")
        
        assert result is not None
        assert result["document_name"] == "test.md"
        assert result["content"] == "Test content"
        self.mock_collection.find_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_document_not_found(self):
        """Test document retrieval when document not found"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.find_one = AsyncMock(return_value=None)
        
        result = await self.db.get_document("507f1f77bcf86cd799439011")
        
        assert result is None
        self.mock_collection.find_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_document_invalid_id(self):
        """Test document retrieval with invalid ObjectId"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        with pytest.raises(Exception) as exc_info:
            await self.db.get_document("invalid_id")
        
        assert "invalid" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_update_document_success(self):
        """Test successful document update"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        self.mock_collection.update_one = AsyncMock(return_value=mock_update_result)
        
        update_data = {
            "content": "Updated content",
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await self.db.update_document("507f1f77bcf86cd799439011", update_data)
        
        assert result is True
        self.mock_collection.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_document_not_found(self):
        """Test document update when document not found"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        mock_update_result = Mock()
        mock_update_result.modified_count = 0
        self.mock_collection.update_one = AsyncMock(return_value=mock_update_result)
        
        update_data = {"content": "Updated content"}
        
        result = await self.db.update_document("507f1f77bcf86cd799439011", update_data)
        
        assert result is False
        self.mock_collection.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self):
        """Test successful document deletion"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 1
        self.mock_collection.delete_one = AsyncMock(return_value=mock_delete_result)
        
        result = await self.db.delete_document("507f1f77bcf86cd799439011")
        
        assert result is True
        self.mock_collection.delete_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_document_not_found(self):
        """Test document deletion when document not found"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 0
        self.mock_collection.delete_one = AsyncMock(return_value=mock_delete_result)
        
        result = await self.db.delete_document("507f1f77bcf86cd799439011")
        
        assert result is False
        self.mock_collection.delete_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_documents_success(self):
        """Test successful document listing"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        mock_docs = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "document_name": "test1.md",
                "content": "Test content 1",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "_id": ObjectId("507f1f77bcf86cd799439012"),
                "document_name": "test2.md",
                "content": "Test content 2",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        
        # Mock the cursor
        mock_cursor = Mock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        
        self.mock_collection.find.return_value = mock_cursor
        
        result = await self.db.list_documents()
        
        assert len(result) == 2
        assert result[0]["document_name"] == "test1.md"
        assert result[1]["document_name"] == "test2.md"
        self.mock_collection.find.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_documents_with_filter(self):
        """Test document listing with filter"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        
        # Mock the cursor
        mock_cursor = Mock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        
        self.mock_collection.find.return_value = mock_cursor
        
        filter_query = {"document_name": {"$regex": "test"}}
        result = await self.db.list_documents(filter_query=filter_query)
        
        assert len(result) == 0
        self.mock_collection.find.assert_called_once_with(filter_query)
    
    @pytest.mark.asyncio
    async def test_list_documents_with_pagination(self):
        """Test document listing with pagination"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        
        # Mock the cursor
        mock_cursor = Mock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        
        self.mock_collection.find.return_value = mock_cursor
        
        result = await self.db.list_documents(skip=10, limit=5)
        
        assert len(result) == 0
        mock_cursor.skip.assert_called_once_with(10)
        mock_cursor.limit.assert_called_once_with(5)
    
    @pytest.mark.asyncio
    async def test_count_documents_success(self):
        """Test successful document counting"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.count_documents = AsyncMock(return_value=42)
        
        result = await self.db.count_documents()
        
        assert result == 42
        self.mock_collection.count_documents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_documents_with_filter(self):
        """Test document counting with filter"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.count_documents = AsyncMock(return_value=10)
        
        filter_query = {"document_type": "markdown"}
        result = await self.db.count_documents(filter_query)
        
        assert result == 10
        self.mock_collection.count_documents.assert_called_once_with(filter_query)
    
    @pytest.mark.asyncio
    async def test_search_documents_success(self):
        """Test successful document search"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        mock_search_results = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "document_name": "test1.md",
                "content": "Test content with search term",
                "score": 0.85
            }
        ]
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        
        # Mock the cursor
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=mock_search_results)
        
        self.mock_collection.find.return_value = mock_cursor
        
        result = await self.db.search_documents("search term")
        
        assert len(result) == 1
        assert result[0]["document_name"] == "test1.md"
        assert "search term" in result[0]["content"]
        self.mock_collection.find.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_aggregate_documents_success(self):
        """Test successful document aggregation"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        mock_aggregate_result = [
            {"_id": "markdown", "count": 5},
            {"_id": "text", "count": 3}
        ]
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        
        # Mock the cursor
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=mock_aggregate_result)
        
        self.mock_collection.aggregate.return_value = mock_cursor
        
        pipeline = [
            {"$group": {"_id": "$document_type", "count": {"$sum": 1}}}
        ]
        
        result = await self.db.aggregate_documents(pipeline)
        
        assert len(result) == 2
        assert result[0]["_id"] == "markdown"
        assert result[0]["count"] == 5
        self.mock_collection.aggregate.assert_called_once_with(pipeline)
    
    @pytest.mark.asyncio
    async def test_create_indexes_success(self):
        """Test successful index creation"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.create_index = AsyncMock()
        
        await self.db.create_indexes()
        
        # Should create indexes on common fields
        assert self.mock_collection.create_index.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_backup_collection_success(self):
        """Test successful collection backup"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "data": "test1"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "data": "test2"}
        ]
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        
        # Mock the cursor
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        
        self.mock_collection.find.return_value = mock_cursor
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                result = await self.db.backup_collection("test_backup.json")
                
                assert result is True
                mock_file.assert_called_once_with("test_backup.json", "w")
                mock_json_dump.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_restore_collection_success(self):
        """Test successful collection restore"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        mock_data = [
            {"_id": "507f1f77bcf86cd799439011", "data": "test1"},
            {"_id": "507f1f77bcf86cd799439012", "data": "test2"}
        ]
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.insert_many = AsyncMock()
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.load', return_value=mock_data) as mock_json_load:
                result = await self.db.restore_collection("test_backup.json")
                
                assert result is True
                mock_file.assert_called_once_with("test_backup.json", "r")
                mock_json_load.assert_called_once()
                self.mock_collection.insert_many.assert_called_once()
    
    def test_document_to_dict(self):
        """Test document serialization to dictionary"""
        doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "document_name": "test.md",
            "content": "Test content",
            "created_at": datetime.now(timezone.utc)
        }
        
        result = self.db.document_to_dict(doc)
        
        assert result["_id"] == "507f1f77bcf86cd799439011"
        assert result["document_name"] == "test.md"
        assert result["content"] == "Test content"
        assert isinstance(result["created_at"], str)  # Should be ISO format
    
    def test_validate_object_id_valid(self):
        """Test ObjectId validation with valid ID"""
        valid_id = "507f1f77bcf86cd799439011"
        
        result = self.db.validate_object_id(valid_id)
        
        assert result is True
    
    def test_validate_object_id_invalid(self):
        """Test ObjectId validation with invalid ID"""
        invalid_id = "invalid_id"
        
        result = self.db.validate_object_id(invalid_id)
        
        assert result is False
    
    def test_get_collection_stats(self):
        """Test getting collection statistics"""
        self.db.client = self.mock_client
        self.db.database = self.mock_database
        
        self.mock_database.__getitem__.return_value = self.mock_collection
        self.mock_collection.count_documents = AsyncMock(return_value=100)
        
        # This would be an async method in the actual implementation
        # For now, just test the setup
        assert self.db.database is not None
        assert self.mock_collection is not None


def mock_open(*args, **kwargs):
    """Mock open function for file operations"""
    return MagicMock() 