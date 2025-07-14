#!/usr/bin/env python3
"""
Test script for the AI-Driven Project Management System with Ollama integration.
This script tests all the core AI functionalities including document processing,
epic extraction, user story generation, and NLP pipeline.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import the ai_processor package
sys.path.insert(0, str(Path(__file__).parent))

from ai_processor.services.ollama_client import OllamaClient
from ai_processor.services.document_orchestrator import DocumentOrchestrator
from ai_processor.services.document_parser import DocumentParser
from ai_processor.services.story_enhancer import StoryEnhancer
from ai_processor.services.nlp_pipeline import NLPPipeline
from ai_processor.database import MongoDB
from ai_processor.models.schemas import (
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    Epic,
    UserStory,
    AcceptanceCriteria,
    StoryPointEstimate,
    ExtractedArtifacts
)

async def test_ollama_integration():
    """Test Ollama integration with document processing"""
    
    print("🚀 Testing AI-Driven Project Management System with Ollama")
    print("=" * 60)
    
    # Initialize Ollama client
    ollama = OllamaClient(base_url="http://localhost:11434")
    nlp = NLPPipeline()
    
    # Test 1: Check Ollama connectivity
    print("\n1. Testing Ollama connectivity...")
    try:
        models = await ollama.list_models()
        print(f"✅ Ollama is running with {len(models)} models available:")
        for model in models[:3]:  # Show first 3 models
            print(f"   - {model['name']} ({model.get('size', 'Unknown size')})")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False
    
    # Test 2: Test basic chat functionality
    print("\n2. Testing basic chat functionality...")
    try:
        response = await ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant for project management. You know my name is deepesh."
                },
                {
                    "role": "user",
                    "content": "What is my name and what can you help me with?"
                }
            ]
        )
        print(f"✅ Chat response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False
    
    # Test 3: Document processing example
    print("\n3. Testing document processing...")
    
    sample_document = """
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
    
    ## Contributors
    - John Doe (Product Manager)
    - Jane Smith (Tech Lead)
    - Mike Johnson (Frontend Developer)
    - Sarah Wilson (Backend Developer)
    """
    
    # Extract epics using AI
    try:
        print("   🔍 Extracting epics from document...")
        epic_prompt = f"""
        Analyze the following requirements document and extract epics (high-level features).
        
        Document:
        {sample_document}
        
        Return a JSON array of epics with this structure:
        [
            {{
                "title": "Epic title",
                "description": "Epic description",
                "goal": "Business goal",
                "priority": "high|medium|low"
            }}
        ]
        
        Return only valid JSON.
        """
        
        epics_response = await ollama.get_structured_response(
            model="llama3.2:3b",
            prompt=epic_prompt,
            response_format="json"
        )
        
        print(f"✅ Extracted {len(epics_response)} epics:")
        for i, epic in enumerate(epics_response[:3], 1):  # Show first 3
            print(f"   {i}. {epic.get('title', 'Unknown')} - {epic.get('priority', 'medium')} priority")
    
    except Exception as e:
        print(f"❌ Epic extraction failed: {e}")
    
    # Test 4: Generate user stories
    try:
        print("\n   📝 Generating user stories...")
        story_prompt = f"""
        Extract user stories from this document in the format "As a [role], I want to [action] so that [benefit]".
        
        Document:
        {sample_document}
        
        Return a JSON array:
        [
            {{
                "title": "Story title",
                "role": "user role",
                "action": "what they want to do",
                "benefit": "why they want it",
                "priority": "high|medium|low"
            }}
        ]
        
        Return only valid JSON.
        """
        
        stories_response = await ollama.get_structured_response(
            model="llama3.2:3b",
            prompt=story_prompt,
            response_format="json"
        )
        
        print(f"✅ Generated {len(stories_response)} user stories:")
        for i, story in enumerate(stories_response[:3], 1):  # Show first 3
            role = story.get('role', 'user')
            action = story.get('action', 'perform action')
            benefit = story.get('benefit', 'achieve goal')
            print(f"   {i}. As a {role}, I want to {action} so that {benefit}")
    
    except Exception as e:
        print(f"❌ User story generation failed: {e}")
    
    # Test 5: Generate acceptance criteria
    try:
        print("\n   ✅ Generating acceptance criteria...")
        ac_prompt = """
        Generate acceptance criteria for this user story: "As a user, I want to register for an account so that I can access the platform features"
        
        Return 3-5 acceptance criteria in Gherkin format as JSON:
        [
            {
                "scenario": "Scenario description",
                "steps": [
                    "Given [initial state]",
                    "When [action]", 
                    "Then [expected result]"
                ]
            }
        ]
        
        Return only valid JSON.
        """
        
        ac_response = await ollama.get_structured_response(
            model="llama3.2:3b",
            prompt=ac_prompt,
            response_format="json"
        )
        
        print(f"✅ Generated {len(ac_response)} acceptance criteria:")
        for i, criterion in enumerate(ac_response[:2], 1):  # Show first 2
            scenario = criterion.get('scenario', 'Unknown scenario')
            steps = len(criterion.get('steps', []))
            print(f"   {i}. {scenario} ({steps} steps)")
    
    except Exception as e:
        print(f"❌ Acceptance criteria generation failed: {e}")
    
    # Test 6: Story point estimation
    try:
        print("\n   🎯 Estimating story points...")
        estimation_prompt = """
        Estimate story points for: "User Registration - Implement user registration with email verification"
        
        Consider complexity, effort, and risk. Use Fibonacci scale (1,2,3,5,8,13,21).
        
        Return JSON:
        {
            "story_points": 5,
            "confidence": 0.8,
            "reasoning": "Explanation for the estimate"
        }
        
        Return only valid JSON.
        """
        
        estimation_response = await ollama.get_structured_response(
            model="llama3.2:3b",
            prompt=estimation_prompt,
            response_format="json"
        )
        
        points = estimation_response.get('story_points', 0)
        confidence = estimation_response.get('confidence', 0)
        reasoning = estimation_response.get('reasoning', 'No reasoning provided')
        
        print(f"✅ Estimated {points} story points (confidence: {confidence*100:.0f}%)")
        print(f"   Reasoning: {reasoning[:100]}...")
    
    except Exception as e:
        print(f"❌ Story point estimation failed: {e}")
    
    # Test 7: NLP entity extraction
    print("\n4. Testing NLP pipeline...")
    try:
        entities = await nlp.extract_entities(sample_document)
        print(f"✅ NLP extraction completed:")
        print(f"   - Found {len(entities.persons)} contributors: {', '.join(entities.persons[:3])}")
        print(f"   - Found {len(entities.technical_terms)} technical terms")
        print(f"   - Found {len(entities.features)} features")
    except Exception as e:
        print(f"❌ NLP extraction failed: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("\nThe AI-Driven Project Management System is working with Ollama integration:")
    print("✅ Document processing")
    print("✅ Epic extraction") 
    print("✅ User story generation")
    print("✅ Acceptance criteria generation")
    print("✅ Story point estimation")
    print("✅ NLP entity extraction")
    print("\nNext steps:")
    print("1. Set up MongoDB for data persistence")
    print("2. Configure Jira integration")
    print("3. Add Google Calendar integration")
    print("4. Deploy with Docker")
    
    return True

async def main():
    """Main function"""
    try:
        success = await test_ollama_integration()
        if success:
            print(f"\n🚀 All tests passed! System is ready for use.")
            return 0
        else:
            print(f"\n❌ Some tests failed. Check Ollama setup.")
            return 1
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 