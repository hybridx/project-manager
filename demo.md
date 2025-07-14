# AI-Driven Project Management System Demo

This demo shows how to use the AI-powered project management system to transform requirements documents into structured Jira backlogs using Ollama.

## Prerequisites

Before running the demo, ensure you have:

1. **Ollama installed and running**:
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   
   # Pull the model
   ollama pull llama3.2:3b
   ```

2. **System started**:
   ```bash
   # Start MongoDB services
   cd services/database
   podman-compose up -d
   
   # Or use the management script
   ./manage.sh start
   
   # Verify services are running
   podman-compose ps
   ```

## Demo Workflow

### 1. Test Ollama Integration

First, let's test the Ollama integration directly:

```bash
# Test Ollama health
curl -X GET http://localhost:11434/api/tags

# Test chat completion
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant for project management. Return only valid JSON."
      },
      {
        "role": "user",
        "content": "Extract user stories from this text: \"Users need to be able to login and logout of the system.\""
      }
    ],
    "stream": false
  }'
```

### 2. Sample Requirements Document

Create a sample requirements document (`sample_requirements.md`):

```markdown
# E-Commerce Platform Requirements

## Project Overview
Build a modern e-commerce platform that allows users to browse products, manage shopping carts, and complete purchases.

## Key Features

### User Management
- User registration and authentication
- User profile management
- Password reset functionality
- Email verification

### Product Management
- Product catalog with categories
- Product search and filtering
- Product reviews and ratings
- Inventory management

### Shopping Cart
- Add/remove items from cart
- Update quantities
- Save cart for later
- Apply discount codes

### Order Management
- Checkout process
- Payment integration
- Order history
- Order tracking

## Technical Requirements
- RESTful API architecture
- JWT authentication
- MongoDB database
- React frontend
- Node.js backend
- Payment gateway integration

## Contributors
- John Doe (Product Manager)
- Jane Smith (Tech Lead)
- Mike Johnson (Frontend Developer)
- Sarah Wilson (Backend Developer)

## Timeline
The project should be completed in 3-4 months with the following phases:
1. Phase 1: User authentication and basic UI (4 weeks)
2. Phase 2: Product catalog and search (4 weeks)
3. Phase 3: Shopping cart and checkout (4 weeks)
4. Phase 4: Order management and admin features (4 weeks)
```

### 3. Process Document with AI

Now let's process this document using the AI service:

```bash
# Process the document
curl -X POST http://localhost:8001/process-document \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# E-Commerce Platform Requirements\n\n## Project Overview\nBuild a modern e-commerce platform that allows users to browse products, manage shopping carts, and complete purchases.\n\n## Key Features\n\n### User Management\n- User registration and authentication\n- User profile management\n- Password reset functionality\n- Email verification\n\n### Product Management\n- Product catalog with categories\n- Product search and filtering\n- Product reviews and ratings\n- Inventory management\n\n### Shopping Cart\n- Add/remove items from cart\n- Update quantities\n- Save cart for later\n- Apply discount codes\n\n### Order Management\n- Checkout process\n- Payment integration\n- Order history\n- Order tracking\n\n## Technical Requirements\n- RESTful API architecture\n- JWT authentication\n- MongoDB database\n- React frontend\n- Node.js backend\n- Payment gateway integration\n\n## Contributors\n- John Doe (Product Manager)\n- Jane Smith (Tech Lead)\n- Mike Johnson (Frontend Developer)\n- Sarah Wilson (Backend Developer)",
    "document_name": "E-commerce Requirements",
    "document_type": "requirements",
    "project_id": "ecommerce-demo"
  }'
```

### 4. Expected AI Response

The AI processor should return structured artifacts like:

```json
{
  "success": true,
  "message": "Document processed successfully. Extracted 4 epics and 16 user stories.",
  "document_id": "doc_12345",
  "artifacts": {
    "epics": [
      {
        "id": "epic_1",
        "title": "User Management System",
        "description": "Complete user authentication and profile management",
        "goal": "Enable users to securely access and manage their accounts",
        "priority": "high",
        "labels": ["authentication", "user-management"]
      },
      {
        "id": "epic_2",
        "title": "Product Catalog",
        "description": "Product browsing, search, and management functionality",
        "goal": "Allow users to discover and view products",
        "priority": "high",
        "labels": ["products", "catalog"]
      },
      {
        "id": "epic_3",
        "title": "Shopping Cart",
        "description": "Cart management and checkout process",
        "goal": "Enable users to purchase products",
        "priority": "medium",
        "labels": ["cart", "checkout"]
      },
      {
        "id": "epic_4",
        "title": "Order Management",
        "description": "Order processing and tracking",
        "goal": "Provide order history and tracking capabilities",
        "priority": "medium",
        "labels": ["orders", "tracking"]
      }
    ],
    "user_stories": [
      {
        "id": "story_1",
        "title": "User Registration",
        "description": "New users can create accounts",
        "role": "new user",
        "action": "register for an account",
        "benefit": "I can access the platform features",
        "epic_id": "epic_1",
        "story_points": 5,
        "priority": "high",
        "acceptance_criteria": [
          {
            "scenario": "Successful registration",
            "steps": [
              "Given user is on registration page",
              "When user enters valid details",
              "Then account is created successfully"
            ]
          }
        ]
      }
    ],
    "contributors": ["John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson"],
    "project_summary": "Build a modern e-commerce platform with user management, product catalog, shopping cart, and order management",
    "estimated_duration": "3-4 months",
    "key_features": [
      "User authentication",
      "Product catalog",
      "Shopping cart",
      "Order management"
    ],
    "technical_requirements": [
      "RESTful API architecture",
      "JWT authentication",
      "MongoDB database",
      "React frontend",
      "Node.js backend"
    ]
  },
  "processing_time": 15.2,
  "metadata": {
    "word_count": 180,
    "model_used": "llama3.2:3b"
  }
}
```

### 5. Generate Acceptance Criteria

Generate detailed acceptance criteria for a user story:

```bash
curl -X POST http://localhost:8001/generate-acceptance-criteria \
  -H "Content-Type: application/json" \
  -d '{
    "story_title": "User Registration",
    "story_description": "As a new user, I want to register for an account so that I can access the platform features"
  }'
```

Expected response:
```json
[
  {
    "scenario": "Successful registration with valid data",
    "steps": [
      "Given user is on the registration page",
      "When user enters valid email, password, and personal information",
      "Then account is created successfully",
      "And user receives confirmation email",
      "And user is redirected to login page"
    ]
  },
  {
    "scenario": "Registration with invalid email",
    "steps": [
      "Given user is on the registration page",
      "When user enters invalid email format",
      "Then error message is displayed",
      "And registration form remains visible"
    ]
  },
  {
    "scenario": "Registration with duplicate email",
    "steps": [
      "Given user is on the registration page",
      "When user enters email that already exists",
      "Then error message shows 'Email already registered'",
      "And option to login or reset password is provided"
    ]
  }
]
```

### 6. Story Point Estimation

Estimate story points for a user story:

```bash
curl -X POST http://localhost:8001/estimate-story-points \
  -H "Content-Type: application/json" \
  -d '{
    "story_title": "User Registration",
    "story_description": "Implement user registration with email verification and validation",
    "acceptance_criteria": [
      "User can register with email/password",
      "Email validation is performed",
      "Confirmation email is sent",
      "Duplicate email prevention"
    ]
  }'
```

Expected response:
```json
{
  "story_points": 5,
  "confidence": 0.8,
  "reasoning": "Medium complexity story requiring database operations, email service integration, validation logic, and error handling. Comparable to other authentication-related stories.",
  "complexity_factors": [
    "Database schema design",
    "Email service integration",
    "Input validation",
    "Error handling",
    "Security considerations"
  ]
}
```

### 7. Extract Contributors

Extract team members from document:

```bash
curl -X POST http://localhost:8001/extract-contributors \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The team includes John Doe as Product Manager, Jane Smith as Tech Lead, and Mike Johnson as Frontend Developer. Sarah Wilson will handle backend development."
  }'
```

Expected response:
```json
{
  "contributors": ["John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson"]
}
```

### 8. Available Models

Check available Ollama models:

```bash
curl -X GET http://localhost:8001/models
```

Expected response:
```json
{
  "models": [
    {
      "name": "llama3.2:3b",
      "size": "2.0GB",
      "modified_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Performance Monitoring

### Health Checks

```bash
# Check AI service health
curl -X GET http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "ai-processor"
}
```

### Processing Metrics

Monitor processing performance:

```bash
# Get recent processing metrics
curl -X GET http://localhost:8001/metrics

# Expected response:
{
  "recent_documents": [
    {
      "document_id": "doc_12345",
      "processing_time": 15.2,
      "word_count": 180,
      "epics_extracted": 4,
      "stories_extracted": 16,
      "model_used": "llama3.2:3b"
    }
  ],
  "average_processing_time": 12.5,
  "total_documents_processed": 25
}
```

## Advanced Features Demo

### 1. Batch Processing

Process multiple documents:

```bash
# Process multiple documents in sequence
for file in requirements1.md requirements2.md requirements3.md; do
  curl -X POST http://localhost:8001/upload-document \
    -F "file=@$file" \
    -F "project_id=batch-demo"
done
```

### 2. Custom Model Configuration

Switch to a different model:

```bash
# Pull a different model
ollama pull llama3.2:7b

# The system will automatically use the new model
# You can configure the default model in services/ai-processor/main.py
```

### 3. Contextual Processing

Process related documents with context:

```bash
curl -X POST http://localhost:8001/process-document \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Additional requirements for the shopping cart feature...",
    "document_name": "Cart Requirements Update",
    "document_type": "requirements",
    "project_id": "ecommerce-demo",
    "additional_context": "This is an update to the existing e-commerce platform requirements"
  }'
```

## Troubleshooting

### Common Issues

1. **Ollama not responding**:
   ```bash
   # Check if Ollama is running
   ps aux | grep ollama
   
   # Restart Ollama
   ollama serve
   ```

2. **Model not found**:
   ```bash
   # List available models
   ollama list
   
   # Pull required model
   ollama pull llama3.2:3b
   ```

3. **Connection refused**:
   ```bash
   # Check service logs
   cd services/database
   podman-compose logs mongodb
   
   # Or use management script
   ./manage.sh logs
   
   # Restart services
   podman-compose restart
   
   # Or use management script
   ./manage.sh restart
   ```

### Performance Optimization

1. **Use smaller models for faster processing**:
   ```bash
   ollama pull llama3.2:1b  # Faster, less accurate
   ```

2. **Increase processing timeout**:
   ```env
   AI_SERVICE_TIMEOUT=600000  # 10 minutes
   ```

3. **Monitor database performance**:
   ```bash
   # Check MongoDB stats
   cd services/database
   ./manage.sh monitor
   
   # View database health
   ./manage.sh health
   ```

## Integration with Frontend

The frontend can integrate with these APIs:

```javascript
// Example React component
import { useState, useEffect } from 'react';

function DocumentProcessor() {
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);

  const processDocument = async (content) => {
    setProcessing(true);
    try {
      const response = await fetch('/api/ai/process-document', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content,
          documentName: 'Requirements',
          documentType: 'requirements'
        })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Processing failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div>
      {processing ? (
        <div>Processing document...</div>
      ) : (
        <div>
          {results && (
            <div>
              <h3>Extracted {results.artifacts.epics.length} epics</h3>
              <h3>Generated {results.artifacts.user_stories.length} user stories</h3>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

## Next Steps

1. **Set up Jira integration** for syncing artifacts
2. **Configure Google Calendar** for automated ceremonies
3. **Add team members** and assign roles
4. **Create custom workflows** for your organization
5. **Set up monitoring** and alerts

This completes the comprehensive demo of the AI-driven project management system using Ollama for local AI processing! 