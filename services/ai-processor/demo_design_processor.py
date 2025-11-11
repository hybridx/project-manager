#!/usr/bin/env python3
"""
Demo script for the Design Document Processor

This script demonstrates how to use the new design document processing
capabilities to break down design documents into actionable development issues.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the ai_processor module to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_processor.services.design_document_processor import DesignDocumentProcessor
from ai_processor.services.ollama_client import OllamaClient


# Sample design document for demonstration
SAMPLE_DESIGN_DOC = """
# E-commerce Platform Design Document

## Overview
This document outlines the design for a modern e-commerce platform that supports
multi-vendor marketplace functionality with real-time inventory management,
payment processing, and recommendation engine.

## System Components

### User Management Service
- User registration and authentication
- Profile management
- Role-based access control (Buyer, Seller, Admin)
- OAuth integration with Google/Facebook

### Product Catalog Service
- Product information management
- Category hierarchy
- Search and filtering capabilities
- Product recommendations using ML

### Inventory Management Service
- Real-time inventory tracking
- Stock alerts and notifications
- Automated reordering
- Multi-warehouse support

### Order Management Service
- Order processing workflow
- Order status tracking
- Return and refund management
- Invoice generation

### Payment Service
- Multiple payment gateway integration (Stripe, PayPal)
- Secure payment processing
- Subscription management
- Financial reporting

### Notification Service
- Email notifications
- SMS alerts
- Push notifications
- Event-driven messaging

## API Endpoints

### Authentication
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/register
- GET /api/auth/profile

### Products
- GET /api/products
- POST /api/products
- PUT /api/products/{id}
- DELETE /api/products/{id}
- GET /api/products/search

### Orders
- GET /api/orders
- POST /api/orders
- GET /api/orders/{id}
- PUT /api/orders/{id}/status

### Payments
- POST /api/payments/process
- GET /api/payments/history
- POST /api/payments/refund

## Data Models

### User
- id, email, password_hash, first_name, last_name, role, created_at, updated_at

### Product
- id, title, description, price, category_id, inventory_count, seller_id, created_at

### Order
- id, user_id, status, total_amount, shipping_address, created_at, updated_at

### Payment
- id, order_id, amount, payment_method, status, transaction_id, created_at

## Technical Requirements

### Performance
- 99.9% uptime requirement
- Response time < 200ms for API calls
- Support for 10,000 concurrent users
- Database queries < 100ms

### Security
- HTTPS encryption for all communications
- JWT-based authentication
- Input validation and sanitization
- SQL injection prevention
- CSRF protection

### Scalability
- Horizontal scaling capability
- Load balancer configuration
- Database sharding strategy
- CDN integration for static assets

## External Dependencies
- Stripe API for payment processing
- SendGrid for email notifications
- Redis for caching and session management
- Elasticsearch for product search
- AWS S3 for file storage

## Infrastructure Requirements
- Kubernetes deployment
- Docker containerization
- CI/CD pipeline with GitHub Actions
- Monitoring with Prometheus and Grafana
- Logging with ELK stack
"""


async def demo_design_processing():
    """Demonstrate design document processing"""
    
    print("🚀 Design Document Processing Demo")
    print("=" * 50)
    
    # Initialize Ollama client
    print("📡 Initializing Ollama client...")
    ollama_client = OllamaClient("http://localhost:11434")
    
    # Initialize design document processor
    print("🧠 Initializing Design Document Processor...")
    processor = DesignDocumentProcessor(ollama_client)
    
    try:
        print("📄 Processing sample design document...")
        result = await processor.process_design_document(
            content=SAMPLE_DESIGN_DOC,
            document_name="ecommerce_design.md",
            project_id="demo_project_123"
        )
        
        print("\n✅ Processing completed successfully!")
        print(f"📊 Results Summary:")
        print(f"   • Total Issues Generated: {result['total_issues']}")
        print(f"   • Functional Areas: {len(result['functional_areas'])}")
        print(f"   • Implementation Phases: {len(result['implementation_roadmap']['phases'])}")
        print(f"   • Estimated Total Hours: {result['metadata']['estimated_total_hours']}")
        
        # Display functional areas
        print(f"\n🏗️  Functional Areas:")
        for area in result['functional_areas']:
            print(f"   • {area['name']}: {area['description']}")
        
        # Display some sample issues
        print(f"\n📋 Sample Generated Issues:")
        for i, issue in enumerate(result['issues'][:5], 1):
            print(f"   {i}. [{issue['issue_type'].upper()}] {issue['title']}")
            print(f"      └─ {issue['estimated_hours']}h • {issue['priority']} priority • {issue['component']}")
        
        if len(result['issues']) > 5:
            print(f"   ... and {len(result['issues']) - 5} more issues")
        
        # Display implementation roadmap
        print(f"\n🗺️  Implementation Roadmap:")
        for phase in result['implementation_roadmap']['phases']:
            print(f"   • {phase['name']}: {phase['issues']} issues, {phase['estimated_hours']}h")
            print(f"     └─ {phase['description']}")
        
        # Save results to file
        output_file = Path("demo_results.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Full results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return None


async def demo_issue_validation(issues):
    """Demonstrate issue validation"""
    if not issues:
        return
    
    print("\n🔍 Issue Validation Demo")
    print("=" * 30)
    
    from ai_processor.models.schemas import DevelopmentIssue
    
    # Convert to DevelopmentIssue objects
    dev_issues = []
    for issue_data in issues['issues'][:10]:  # Validate first 10 issues
        try:
            issue = DevelopmentIssue(**issue_data)
            dev_issues.append(issue)
        except Exception as e:
            print(f"❌ Invalid issue format: {e}")
    
    if dev_issues:
        print(f"✅ Validated {len(dev_issues)} issues successfully")
        
        # Show validation details
        total_hours = sum(issue.estimated_hours for issue in dev_issues)
        issue_types = {}
        for issue in dev_issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        print(f"📊 Validation Summary:")
        print(f"   • Total Estimated Hours: {total_hours}")
        print(f"   • Issue Type Distribution:")
        for issue_type, count in issue_types.items():
            print(f"     └─ {issue_type}: {count} issues")


async def main():
    """Main demo function"""
    print("🎯 AI-Driven Project Management - Design Document Processing Demo")
    print("================================================================")
    
    try:
        # Test if Ollama is available
        ollama_client = OllamaClient("http://localhost:11434")
        models = await ollama_client.list_models()
        if not models:
            print("❌ No Ollama models available. Please install and pull a model:")
            print("   ollama pull llama3.2:3b")
            return
        
        print(f"✅ Ollama available with models: {', '.join(models)}")
        
        # Run design processing demo
        result = await demo_design_processing()
        
        # Run validation demo
        await demo_issue_validation(result)
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. 🌐 Start the AI processor service: poetry run ai-processor")
        print("2. 📡 Use the REST API endpoints to process your own design documents")
        print("3. 🔗 Integrate with Jira to create issues automatically")
        print("4. 🖥️  Use the frontend interface for a visual workflow")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Ensure a model is available: ollama pull llama3.2:3b")
        print("3. Check network connectivity to localhost:11434")


if __name__ == "__main__":
    asyncio.run(main())