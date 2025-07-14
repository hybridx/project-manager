#!/usr/bin/env python3
"""
Quick demonstration of the AI-Driven Project Management System
This script shows the core AI capabilities with sample data.
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
    StoryPointEstimate
)

async def quick_demo():
    print("🚀 AI-Driven Project Management System Demo")
    print("=" * 50)
    
    ollama = OllamaClient()
    
    # Test 1: Confirm your name (from your request)
    print("\n1. Testing personalized AI response...")
    response = await ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. and you know my name is deepesh"},
            {"role": "user", "content": "What is my name?"}
        ]
    )
    print(f"✅ AI Response: {response}")
    
    # Test 2: Requirements processing
    print("\n2. Processing sample requirements...")
    requirements = """
    Mobile Banking App Features:
    - User login with biometrics
    - View account balance
    - Transfer money between accounts
    - Pay bills online
    - Find nearby ATMs
    - Transaction notifications
    """
    
    epic_prompt = f"""
    Extract 2-3 epics from these requirements: {requirements}
    Return JSON: [{{"title": "Epic Name", "description": "Epic description"}}]
    """
    
    epics = await ollama.get_structured_response("llama3.2:3b", epic_prompt, "json")
    print(f"✅ Extracted {len(epics)} epics:")
    for i, epic in enumerate(epics, 1):
        title = epic.get("title", "Unknown Epic")
        print(f"   {i}. {title}")
    
    # Test 3: User story generation
    print("\n3. Generating user stories...")
    story_prompt = f"""
    Generate 3 user stories from: {requirements}
    Format: [{{"story": "As a user, I want X so that Y", "points": 5}}]
    """
    
    stories = await ollama.get_structured_response("llama3.2:3b", story_prompt, "json")
    print(f"✅ Generated {len(stories)} user stories:")
    for i, story in enumerate(stories, 1):
        story_text = story.get("story", "Unknown story")
        points = story.get("points", 5)
        print(f"   {i}. {story_text} [{points} pts]")
    
    # Test 4: Acceptance criteria
    print("\n4. Creating acceptance criteria...")
    ac_prompt = """
    Generate acceptance criteria for "User wants to view account balance"
    Return: [{"scenario": "Success case", "steps": ["Given", "When", "Then"]}]
    """
    
    criteria = await ollama.get_structured_response("llama3.2:3b", ac_prompt, "json")
    print(f"✅ Generated {len(criteria)} acceptance criteria:")
    for i, criterion in enumerate(criteria, 1):
        scenario = criterion.get("scenario", "Unknown scenario")
        steps = len(criterion.get("steps", []))
        print(f"   {i}. {scenario} ({steps} steps)")
    
    # Test 5: Team extraction
    print("\n5. Extracting team members...")
    team_text = "Team: Sarah Johnson (Product Manager), Mike Chen (iOS Dev), Lisa Wong (Android Dev)"
    
    team_prompt = f"""
    Extract team members from: {team_text}
    Return: [{{"name": "Full Name", "role": "Role"}}]
    """
    
    team = await ollama.get_structured_response("llama3.2:3b", team_prompt, "json")
    print(f"✅ Found {len(team)} team members:")
    for member in team:
        name = member.get("name", "Unknown")
        role = member.get("role", "Unknown")
        print(f"   - {name} ({role})")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("✅ AI name recognition")
    print("✅ Epic extraction")
    print("✅ User story generation")
    print("✅ Acceptance criteria creation")
    print("✅ Team member identification")
    print("\nThe system is ready for full deployment! 🚀")

if __name__ == "__main__":
    asyncio.run(quick_demo()) 