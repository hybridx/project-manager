from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import json
import os
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timezone

from .models.schemas import (
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    ExtractedArtifacts,
    Epic,
    UserStory,
    AcceptanceCriteria,
    StoryPointEstimate
)
from .services.document_orchestrator import DocumentOrchestrator
from .services.document_parser import DocumentParser
from .services.story_enhancer import StoryEnhancer
from .services.ollama_client import OllamaClient
from .services.nlp_pipeline import NLPPipeline
from .database import MongoDB
from .core.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
document_orchestrator = None
ollama_client = None
nlp_pipeline = None
mongodb = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global document_orchestrator, ollama_client, nlp_pipeline, mongodb
    
    logger.info("Starting AI Processor Service...")
    
    # Initialize MongoDB connection
    mongodb = MongoDB()
    await mongodb.connect()
    
    # Initialize Ollama client
    ollama_client = OllamaClient(
        base_url=config.get_ollama_base_url()
    )
    
    # Initialize NLP pipeline
    nlp_pipeline = NLPPipeline()
    
    # Initialize specialized services
    document_parser = DocumentParser(ollama_client, nlp_pipeline)
    story_enhancer = StoryEnhancer(ollama_client)
    
    # Initialize document orchestrator (Facade)
    document_orchestrator = DocumentOrchestrator(
        document_parser=document_parser,
        story_enhancer=story_enhancer,
        nlp_pipeline=nlp_pipeline,
        database=mongodb
    )
    
    logger.info("AI Processor Service started successfully with clean architecture")
    yield
    
    # Shutdown
    logger.info("Shutting down AI Processor Service...")
    await mongodb.disconnect()

app = FastAPI(
    title="AI Processor Service",
    description="AI-driven document processing and artifact extraction service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_document_orchestrator():
    if document_orchestrator is None:
        raise HTTPException(status_code=500, detail="Document orchestrator not initialized")
    return document_orchestrator

def get_ollama_client():
    if ollama_client is None:
        raise HTTPException(status_code=500, detail="Ollama client not initialized")
    return ollama_client

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ai-processor"
    }

@app.post("/process-document", response_model=DocumentProcessingResponse)
async def process_document(
    request: DocumentProcessingRequest,
    orchestrator: DocumentOrchestrator = Depends(get_document_orchestrator)
):
    """Process a document and extract project artifacts"""
    try:
        logger.info(f"Processing document: {request.document_name}")
        
        # Process the document using orchestrator
        result = await orchestrator.process_document(
            content=request.content,
            document_name=request.document_name,
            document_type=request.document_type,
            project_id=request.project_id
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-document", response_model=DocumentProcessingResponse)
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = None,
    orchestrator: DocumentOrchestrator = Depends(get_document_orchestrator)
):
    """Upload and process a document file"""
    try:
        # Read file content
        content = await file.read()
        
        # Determine document type from filename
        document_type = "unknown"
        if file.filename:
            if file.filename.endswith(('.pdf', '.doc', '.docx')):
                document_type = "requirements"
            elif file.filename.endswith('.md'):
                document_type = "markdown"
            elif file.filename.endswith('.txt'):
                document_type = "text"
        
        # Process the document using orchestrator
        result = await orchestrator.process_document(
            content=content.decode('utf-8') if isinstance(content, bytes) else content,
            document_name=file.filename,
            document_type=document_type,
            project_id=project_id
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-acceptance-criteria", response_model=List[AcceptanceCriteria])
async def generate_acceptance_criteria(
    story_title: str,
    story_description: str,
    orchestrator: DocumentOrchestrator = Depends(get_document_orchestrator)
):
    """Generate acceptance criteria for a user story"""
    try:
        logger.info(f"Generating acceptance criteria for story: {story_title}")
        
        # Create a temporary user story object
        from .models.schemas import UserStory, Priority
        temp_story = UserStory(
            title=story_title,
            description=story_description,
            priority=Priority.MEDIUM,
            story_points=0,
            acceptance_criteria=[],
            epic_id=None,
            status="draft"
        )
        
        # Generate acceptance criteria using story enhancer
        criteria = await orchestrator.story_enhancer.generate_acceptance_criteria(temp_story)
        
        return criteria
    
    except Exception as e:
        logger.error(f"Error generating acceptance criteria: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/estimate-story-points", response_model=StoryPointEstimate)
async def estimate_story_points(
    story_title: str,
    story_description: str,
    acceptance_criteria: List[str] = None,
    orchestrator: DocumentOrchestrator = Depends(get_document_orchestrator)
):
    """Estimate story points for a user story"""
    try:
        logger.info(f"Estimating story points for: {story_title}")
        
        estimate = await orchestrator.story_enhancer.estimate_story_points(
            story_title=story_title,
            story_description=story_description,
            acceptance_criteria=acceptance_criteria or []
        )
        
        return estimate
    
    except Exception as e:
        logger.error(f"Error estimating story points: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-contributors")
async def extract_contributors(
    content: str,
    orchestrator: DocumentOrchestrator = Depends(get_document_orchestrator)
):
    """Extract potential team contributors from document content"""
    try:
        contributors = await orchestrator._extract_contributors(content)
        return {"contributors": contributors}
    
    except Exception as e:
        logger.error(f"Error extracting contributors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_available_models(
    ollama: OllamaClient = Depends(get_ollama_client)
):
    """Get available Ollama models"""
    try:
        models = await ollama.list_models()
        return {"models": models}
    
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Main entry point for the AI processor service"""
    import uvicorn
    uvicorn.run(
        "ai_processor.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 

if __name__ == "__main__":
    main() 