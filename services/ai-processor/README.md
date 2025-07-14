# AI Processor Service

Clean, SOLID-principles-based document processing service with Ollama integration.

## 🏗️ Architecture

### Clean Architecture Layers
- **Core**: Interfaces, configuration, error handling
- **Services**: Specialized, focused services following SRP
- **Models**: Data schemas and validation
- **API**: FastAPI endpoints and dependency injection

### Services
- **DocumentOrchestrator**: Facade coordinating all processing steps
- **DocumentParser**: Extracts epics and stories from documents  
- **StoryEnhancer**: Adds acceptance criteria and story point estimates
- **OllamaClient**: AI model communication
- **NLPPipeline**: Text preprocessing and entity extraction

## 🚀 Quick Start

```bash
# From project root
cd services/ai-processor

# Install dependencies  
poetry install

# Run tests
poetry run python test_ollama.py

# Start service
poetry run ai-processor
```

## 📡 API Endpoints

- `POST /process-document` - Full document processing
- `POST /upload-document` - Upload and process file
- `POST /generate-acceptance-criteria` - Generate criteria for story
- `POST /estimate-story-points` - Estimate story complexity
- `POST /extract-contributors` - Extract people from document
- `GET /models` - List available AI models
- `GET /health` - Health check

## 🧪 Testing

```bash
# Unit tests
poetry run pytest

# Integration test
poetry run python test_ollama.py

# Architecture validation
poetry run pytest tests/test_architecture.py
```

API documentation: http://localhost:8001/docs 