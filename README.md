# AI-Driven Project Management System

A comprehensive AI-powered system that transforms natural language requirements documents into structured Jira backlogs, automating project setup and sprint management.

## 🚀 Features

### Core Capabilities
- **AI Document Processing**: Convert PRDs, RFCs, and feature specifications into structured agile artifacts
- **Automated Epic & Story Generation**: Extract epics and user stories from requirements documents
- **Intelligent Acceptance Criteria**: Generate comprehensive acceptance criteria using AI
- **Smart Story Point Estimation**: AI-powered story point estimation with confidence levels
- **Jira Integration**: Seamless two-way sync with Jira projects
- **Google Calendar Integration**: Automated scheduling of agile ceremonies
- **Real-time Dashboard**: Live project health monitoring and analytics

### AI-Powered Features
- **Ollama Integration**: Uses local Ollama API for private AI processing
- **Natural Language Processing**: Extract contributors, features, and technical requirements
- **Contextual Understanding**: Maintains project context across document processing
- **Intelligent Prioritization**: WSJF-based prioritization algorithms

## 🏗️ Architecture

### Microservices
- **Frontend Portal** (React) - Document upload and project management UI
- **API Gateway** (Node.js) - Authentication, routing, and real-time communication
- **AI Processor** (Python) - Document processing and Ollama integration
- **Jira Integration** (Node.js) - Jira API management and OAuth
- **Calendar Service** (Node.js) - Google Calendar integration
- **Database** (MongoDB) - Project data and processed artifacts

### Technology Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS, Socket.io
- **Backend**: Node.js, Express, Python FastAPI
- **AI**: Ollama (llama3.2:3b), Custom NLP pipeline
- **Database**: MongoDB, Redis
- **Infrastructure**: Docker, Docker Compose

## 🛠️ Quick Setup

### Prerequisites
- Python 3.11+
- Ollama running locally

### 1. Install and Start Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull the required model
ollama pull llama3.2:3b
```

### 2. One-Command Setup

```bash
# Clone the repository
git clone <repository-url>
cd project-manager

# Run the setup script
./setup.sh
```

That's it! The script will:
- ✅ Create virtual environment (`aivenv`)
- ✅ Install Poetry
- ✅ Install all dependencies
- ✅ Test the AI processor
- ✅ Verify Ollama connection

### 3. Start the Services

```bash
# AI Service
cd services/ai-processor
poetry run ai-processor

# Frontend (in another terminal)
cd services/frontend
npm install
npm run dev
```

**Access the Applications:**
- Frontend: http://localhost:3000
- AI Processor API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

### 4. Container Deployment

```bash
# Build and run with Podman
podman-compose -f podman-compose.yml up -d

# Or individual services
cd services/frontend && podman build -t ai-pm-frontend .
cd services/ai-processor && podman build -t ai-pm-ai-processor .
```

### 4. Development Commands

```bash
# Run tests
poetry run pytest

# Code formatting
poetry run black .
poetry run isort .

# Type checking
poetry run mypy ai_processor/

# Security scan
poetry run bandit -r ai_processor/

# Run all quality checks
poetry run pre-commit run --all-files
```

## 🏗️ Improved Architecture

The codebase now follows **SOLID principles** and **DRY patterns**:

### SOLID Principles Applied:
- **Single Responsibility**: Each service has one clear responsibility
  - `DocumentParser`: Only parses documents
  - `StoryEnhancer`: Only enhances stories with criteria and estimates
  - `ConfigurationManager`: Only manages configuration
  - `ErrorHandler`: Only handles errors

- **Open/Closed**: Services are open for extension, closed for modification via protocols

- **Dependency Inversion**: Services depend on abstractions (protocols) not concretions

### DRY Improvements:
- **Centralized Configuration**: All settings in one place
- **Unified Error Handling**: Consistent error management across services
- **Reusable Components**: Shared interfaces and protocols
- **Decorator Pattern**: Error handling decorator eliminates repetition

### Code Quality:
- **Poetry**: Professional dependency management
- **Type Hints**: Full type safety with mypy
- **Testing**: Comprehensive test coverage
- **Security**: Bandit security scanning
- **Formatting**: Black and isort for consistent style

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database
MONGODB_URI=mongodb://admin:password@localhost:27017/ai-pm?authSource=admin
REDIS_URL=redis://localhost:6379

# JWT Secrets
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
SESSION_SECRET=your-session-secret-change-this-in-production

# Services
AI_SERVICE_URL=http://localhost:8001
JIRA_SERVICE_URL=http://localhost:8002
CALENDAR_SERVICE_URL=http://localhost:8003

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
JIRA_CLIENT_ID=your-jira-client-id
JIRA_CLIENT_SECRET=your-jira-client-secret

# CORS
CORS_ORIGIN=http://localhost:3000,http://localhost:3001
```

### 4. Start the System

```bash
# Start MongoDB database with Podman Compose
cd services/database
podman-compose up -d

# Or use the management script (recommended)
./manage.sh start

# Check service status
podman-compose ps

# View logs
podman-compose logs -f
```

### 5. Development Setup (Optional)

For development, you can run services locally:

```bash
# Install dependencies
npm install

# Start development servers
npm run dev

# Or start individual services
npm run dev:gateway
npm run dev:ai
npm run dev:frontend
```

## 📚 Usage Guide

### 1. Document Processing

**Upload a Requirements Document:**

```bash
curl -X POST http://localhost:8000/api/ai/upload-document \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@requirements.md" \
  -F "projectId=project123"
```

**Process Text Content:**

```bash
curl -X POST http://localhost:8000/api/ai/process-document \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# User Management System\n\nWe need to build a user authentication system...",
    "documentName": "User Auth Requirements",
    "documentType": "requirements",
    "projectId": "project123"
  }'
```

### 2. AI-Powered Features

**Generate Acceptance Criteria:**

```bash
curl -X POST http://localhost:8000/api/ai/generate-acceptance-criteria \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "storyTitle": "User Login",
    "storyDescription": "As a user, I want to log into the system so that I can access my dashboard"
  }'
```

**Estimate Story Points:**

```bash
curl -X POST http://localhost:8000/api/ai/estimate-story-points \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "storyTitle": "User Login",
    "storyDescription": "Implement user authentication with JWT tokens",
    "acceptanceCriteria": ["User can login with email/password", "Invalid credentials show error"]
  }'
```

### 3. Frontend Usage

Navigate to `http://localhost:3000` to access the web interface:

1. **Upload Documents**: Drag and drop requirement documents
2. **Review Artifacts**: Review AI-generated epics and stories
3. **Edit and Refine**: Modify generated content before Jira sync
4. **Project Dashboard**: Monitor project health and progress
5. **Real-time Updates**: See processing status in real-time

### 4. Jira Integration

**Create Project in Jira:**

```bash
curl -X POST http://localhost:8000/api/jira/projects \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Project Management",
    "key": "AIP",
    "description": "AI-generated project from requirements"
  }'
```

**Sync Artifacts to Jira:**

```bash
curl -X POST http://localhost:8000/api/jira/sync-artifacts \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "jiraProjectKey": "AIP",
    "createSprint": true
  }'
```

## 🔧 Configuration

### AI Model Configuration

The system uses Ollama with llama3.2:3b by default. You can configure different models:

```python
# In services/ai-processor/main.py
MODEL = "llama3.2:3b"  # Change to your preferred model

# Available models
ollama pull llama3.2:1b    # Smaller, faster
ollama pull llama3.2:7b    # Larger, more accurate
ollama pull codellama:7b   # Code-focused
```

### Database Configuration

```yaml
# services/database/podman-compose.yml
mongodb:
  build:
    context: .
    dockerfile: Containerfile
  container_name: project-manager-mongodb
  environment:
    - MONGO_INITDB_ROOT_USERNAME=admin
    - MONGO_INITDB_ROOT_PASSWORD=projectmanager123
    - MONGO_INITDB_DATABASE=project_manager
  volumes:
    - mongodb_data:/data/db
    - mongodb_logs:/var/log/mongodb
```

### Service Configuration

Each service can be configured via environment variables:

```env
# AI Processor
AI_SERVICE_TIMEOUT=300000  # 5 minutes for processing
AI_SERVICE_RETRIES=3

# Rate Limiting
RATE_LIMIT_WINDOW=900000   # 15 minutes
RATE_LIMIT_MAX=100         # 100 requests per window

# File Upload
MAX_FILE_SIZE=10485760     # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,md
```

## 📊 Monitoring and Analytics

### Health Checks

```bash
# Gateway health
curl http://localhost:8000/health

# AI service health
curl http://localhost:8000/api/ai/health

# Jira service health
curl http://localhost:8002/health
```

### Metrics and Logging

- **Application Logs**: Available via `podman-compose logs` or `./manage.sh logs`
- **Processing Metrics**: Stored in MongoDB for analysis
- **Real-time Dashboard**: Available at `http://localhost:3000/dashboard`

### Performance Monitoring

```bash
# Monitor container resources
docker stats

# Check processing times
curl http://localhost:8000/api/dashboard/metrics

# View recent documents
curl http://localhost:8000/api/documents/recent
```

## 🚢 Deployment

### Production Deployment

1. **Configure Environment Variables**:
```env
NODE_ENV=production
JWT_SECRET=your-production-secret
MONGODB_URI=mongodb://production-host:27017/ai-pm
REDIS_URL=redis://production-redis:6379
```

2. **Build and Deploy**:
```bash
# Build production images
cd services/database
podman-compose build

# Deploy to production
podman-compose up -d
```

3. **SSL Configuration**:
```