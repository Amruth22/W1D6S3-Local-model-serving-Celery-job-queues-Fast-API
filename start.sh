#!/bin/bash

# Local RAG FastAPI + Celery Startup Script

echo "=========================================="
echo "Local RAG FastAPI + Celery System"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed or not in PATH"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo "✓ pip found: $(pip --version)"

# Install requirements if needed
if [ ! -f "requirements_installed.flag" ]; then
    echo ""
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch requirements_installed.flag
        echo "✓ Requirements installed successfully"
    else
        echo "❌ Failed to install requirements"
        exit 1
    fi
else
    echo "✓ Requirements already installed"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/documents
mkdir -p data/cache
mkdir -p data/celery_results
mkdir -p embeddings
echo "✓ Directories created"

# Start the application
echo ""
echo "🚀 Starting Local RAG System..."
echo "   - FastAPI server will be available at: http://localhost:8080"
echo "   - API documentation: http://localhost:8080/docs"
echo "   - Health check: http://localhost:8080/system/health"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

python3 main.py