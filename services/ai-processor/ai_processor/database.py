import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
import os

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB database layer for AI processor service"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ai-pm")
        
    async def connect(self):
        """Connect to MongoDB database"""
        try:
            logger.info(f"Connecting to MongoDB: {self.uri}")
            
            # Parse URI to get database name
            if "?" in self.uri:
                db_part = self.uri.split("/")[-1].split("?")[0]
            else:
                db_part = self.uri.split("/")[-1]
            
            db_name = db_part if db_part else "ai-pm"
            
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[db_name]
            
            # Test connection
            await self.client.server_info()
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes
            await self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Documents collection indexes
            await self.db.documents.create_index([("project_id", 1)])
            await self.db.documents.create_index([("processed_at", -1)])
            await self.db.documents.create_index([("type", 1)])
            await self.db.documents.create_index([("name", 1)])
            
            # Projects collection indexes
            await self.db.projects.create_index([("jira_project_key", 1)], unique=True)
            await self.db.projects.create_index([("created_at", -1)])
            
            # Artifacts collection indexes
            await self.db.artifacts.create_index([("project_id", 1)])
            await self.db.artifacts.create_index([("document_id", 1)])
            await self.db.artifacts.create_index([("type", 1)])
            await self.db.artifacts.create_index([("created_at", -1)])
            
            # Processing metrics indexes
            await self.db.processing_metrics.create_index([("document_id", 1)])
            await self.db.processing_metrics.create_index([("created_at", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    async def save_document(self, document_data: Dict[str, Any]) -> str:
        """
        Save processed document to database
        
        Args:
            document_data: Document data to save
            
        Returns:
            Document ID
        """
        try:
            # Add timestamp if not present
            if "processed_at" not in document_data:
                document_data["processed_at"] = datetime.utcnow()
            
            # Insert document
            result = await self.db.documents.insert_one(document_data)
            document_id = str(result.inserted_id)
            
            logger.info(f"Document saved with ID: {document_id}")
            return document_id
            
        except DuplicateKeyError:
            # Update existing document
            document_id = document_data.get("_id")
            await self.db.documents.update_one(
                {"_id": document_id},
                {"$set": document_data}
            )
            logger.info(f"Document updated with ID: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID
        
        Args:
            document_id: Document ID to retrieve
            
        Returns:
            Document data or None if not found
        """
        try:
            document = await self.db.documents.find_one({"_id": document_id})
            return document
            
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    async def get_documents_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all documents for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            List of documents
        """
        try:
            cursor = self.db.documents.find({"project_id": project_id})
            documents = await cursor.to_list(length=None)
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents for project {project_id}: {e}")
            return []
    
    async def save_project(self, project_data: Dict[str, Any]) -> str:
        """
        Save project configuration
        
        Args:
            project_data: Project data to save
            
        Returns:
            Project ID
        """
        try:
            # Add timestamp if not present
            if "created_at" not in project_data:
                project_data["created_at"] = datetime.utcnow()
            
            # Insert project
            result = await self.db.projects.insert_one(project_data)
            project_id = str(result.inserted_id)
            
            logger.info(f"Project saved with ID: {project_id}")
            return project_id
            
        except DuplicateKeyError:
            # Update existing project
            project_id = project_data.get("_id")
            await self.db.projects.update_one(
                {"_id": project_id},
                {"$set": project_data}
            )
            logger.info(f"Project updated with ID: {project_id}")
            return project_id
            
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project by ID
        
        Args:
            project_id: Project ID to retrieve
            
        Returns:
            Project data or None if not found
        """
        try:
            project = await self.db.projects.find_one({"_id": project_id})
            return project
            
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            return None
    
    async def get_project_by_jira_key(self, jira_key: str) -> Optional[Dict[str, Any]]:
        """
        Get project by Jira project key
        
        Args:
            jira_key: Jira project key
            
        Returns:
            Project data or None if not found
        """
        try:
            project = await self.db.projects.find_one({"jira_project_key": jira_key})
            return project
            
        except Exception as e:
            logger.error(f"Error getting project by Jira key {jira_key}: {e}")
            return None
    
    async def save_artifacts(self, artifacts_data: Dict[str, Any]) -> str:
        """
        Save extracted artifacts
        
        Args:
            artifacts_data: Artifacts data to save
            
        Returns:
            Artifacts ID
        """
        try:
            # Add timestamp if not present
            if "created_at" not in artifacts_data:
                artifacts_data["created_at"] = datetime.utcnow()
            
            # Insert artifacts
            result = await self.db.artifacts.insert_one(artifacts_data)
            artifacts_id = str(result.inserted_id)
            
            logger.info(f"Artifacts saved with ID: {artifacts_id}")
            return artifacts_id
            
        except Exception as e:
            logger.error(f"Error saving artifacts: {e}")
            raise
    
    async def get_artifacts_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get artifacts by document ID
        
        Args:
            document_id: Document ID
            
        Returns:
            List of artifacts
        """
        try:
            cursor = self.db.artifacts.find({"document_id": document_id})
            artifacts = await cursor.to_list(length=None)
            return artifacts
            
        except Exception as e:
            logger.error(f"Error getting artifacts for document {document_id}: {e}")
            return []
    
    async def save_processing_metrics(self, metrics_data: Dict[str, Any]) -> str:
        """
        Save processing metrics
        
        Args:
            metrics_data: Metrics data to save
            
        Returns:
            Metrics ID
        """
        try:
            # Add timestamp if not present
            if "created_at" not in metrics_data:
                metrics_data["created_at"] = datetime.utcnow()
            
            # Insert metrics
            result = await self.db.processing_metrics.insert_one(metrics_data)
            metrics_id = str(result.inserted_id)
            
            logger.info(f"Processing metrics saved with ID: {metrics_id}")
            return metrics_id
            
        except Exception as e:
            logger.error(f"Error saving processing metrics: {e}")
            raise
    
    async def get_processing_metrics(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processing metrics by document ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Metrics data or None if not found
        """
        try:
            metrics = await self.db.processing_metrics.find_one({"document_id": document_id})
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting processing metrics for document {document_id}: {e}")
            return None
    
    async def get_recent_documents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently processed documents
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of recent documents
        """
        try:
            cursor = self.db.documents.find().sort("processed_at", -1).limit(limit)
            documents = await cursor.to_list(length=None)
            return documents
            
        except Exception as e:
            logger.error(f"Error getting recent documents: {e}")
            return []
    
    async def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        Get project statistics
        
        Args:
            project_id: Project ID
            
        Returns:
            Project statistics
        """
        try:
            # Count documents
            doc_count = await self.db.documents.count_documents({"project_id": project_id})
            
            # Count artifacts
            artifact_count = await self.db.artifacts.count_documents({"project_id": project_id})
            
            # Get processing metrics
            metrics_cursor = self.db.processing_metrics.find({"project_id": project_id})
            metrics_list = await metrics_cursor.to_list(length=None)
            
            total_processing_time = sum(m.get("total_time", 0) for m in metrics_list)
            avg_processing_time = total_processing_time / len(metrics_list) if metrics_list else 0
            
            return {
                "project_id": project_id,
                "document_count": doc_count,
                "artifact_count": artifact_count,
                "total_processing_time": total_processing_time,
                "average_processing_time": avg_processing_time,
                "metrics_count": len(metrics_list)
            }
            
        except Exception as e:
            logger.error(f"Error getting project statistics for {project_id}: {e}")
            return {}
    
    async def search_documents(self, query: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search documents by text
        
        Args:
            query: Search query
            project_id: Optional project ID to filter by
            
        Returns:
            List of matching documents
        """
        try:
            # Build search filter
            search_filter = {"$text": {"$search": query}}
            
            if project_id:
                search_filter["project_id"] = project_id
            
            # Execute search
            cursor = self.db.documents.find(search_filter)
            documents = await cursor.to_list(length=None)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document and related data
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete document
            doc_result = await self.db.documents.delete_one({"_id": document_id})
            
            # Delete related artifacts
            await self.db.artifacts.delete_many({"document_id": document_id})
            
            # Delete related metrics
            await self.db.processing_metrics.delete_many({"document_id": document_id})
            
            success = doc_result.deleted_count > 0
            if success:
                logger.info(f"Document {document_id} and related data deleted successfully")
            else:
                logger.warning(f"Document {document_id} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def cleanup_old_data(self, days_old: int = 30) -> int:
        """
        Clean up old data
        
        Args:
            days_old: Number of days to keep data
            
        Returns:
            Number of documents cleaned up
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Find old documents
            cursor = self.db.documents.find({"processed_at": {"$lt": cutoff_date}})
            old_documents = await cursor.to_list(length=None)
            
            # Delete old documents and related data
            deleted_count = 0
            for doc in old_documents:
                if await self.delete_document(doc["_id"]):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old documents")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    async def health_check(self) -> bool:
        """
        Check database health
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Ping the database
            await self.client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False 