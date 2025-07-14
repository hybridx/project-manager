#!/bin/bash
set -e

echo "🚀 Setting up AI-Driven Project Management System..."

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "📍 Found Python version: $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv aivenv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source aivenv/bin/activate

# Install Poetry
echo "📦 Installing Poetry..."
pip install poetry

# Navigate to AI processor directory
echo "📁 Navigating to AI processor directory..."
cd services/ai-processor

# Install dependencies
echo "📚 Installing dependencies..."
poetry install

# Check if Ollama is running
echo "🤖 Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Please start Ollama first:"
    echo "   1. Install Ollama: https://ollama.ai"
    echo "   2. Run: ollama serve"
    echo "   3. Pull model: ollama pull llama3.2:3b"
    echo ""
    echo "🔄 After starting Ollama, run the test:"
    echo "   poetry run python test_ollama.py"
else
    echo "✅ Ollama is running"
    
    # Run tests
    echo "🧪 Running tests..."
    poetry run python test_ollama.py
fi

echo ""
echo "🎉 Setup complete! To start the AI processor:"
echo "   cd services/ai-processor"
echo "   poetry run ai-processor"
echo ""
echo "📖 API documentation will be available at: http://localhost:8001/docs"
echo ""
echo "🐳 To run with Podman containers:"
echo "   podman-compose -f podman-compose.yml up -d"
echo ""
echo "📝 Note: Make sure Ollama is running on the host system for AI processing" 