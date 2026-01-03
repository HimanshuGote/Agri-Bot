#!/bin/bash

# Agriculture Chatbot - Automated Setup Script
# This script sets up the entire project from scratch

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_color "$BLUE" "============================================"
    print_color "$BLUE" "$1"
    print_color "$BLUE" "============================================"
}

print_success() {
    print_color "$GREEN" "✓ $1"
}

print_error() {
    print_color "$RED" "✗ $1"
}

print_warning() {
    print_color "$YELLOW" "⚠ $1"
}

# Check if running on Unix-like system
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    print_error "This script is for Unix-like systems. For Windows, use setup.bat or manual setup."
    exit 1
fi

print_header "🌾 Agriculture Chatbot - Setup Script"

# Step 1: Check Python version
print_header "Step 1: Checking Python Version"
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    print_error "Python not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_success "Found Python $PYTHON_VERSION"

# Check if version is 3.9+
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 9 ]); then
    print_error "Python 3.9+ required. Found $PYTHON_VERSION"
    exit 1
fi

# Step 2: Create virtual environment
print_header "Step 2: Creating Virtual Environment"
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping..."
else
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Step 3: Activate virtual environment
print_header "Step 3: Activating Virtual Environment"
source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Upgrade pip
print_header "Step 4: Upgrading pip"
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Step 5: Install dependencies
print_header "Step 5: Installing Dependencies"
print_color "$YELLOW" "This may take 2-3 minutes..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Step 6: Check for PDF files
print_header "Step 6: Checking for PDF Files"
PDFS_FOUND=0

if [ -f "CitrusPlantPestsAndDiseases.pdf" ]; then
    print_success "Found CitrusPlantPestsAndDiseases.pdf"
    ((PDFS_FOUND++))
else
    print_error "CitrusPlantPestsAndDiseases.pdf not found!"
fi

if [ -f "GovernmentSchemes.pdf" ]; then
    print_success "Found GovernmentSchemes.pdf"
    ((PDFS_FOUND++))
else
    print_error "GovernmentSchemes.pdf not found!"
fi

if [ $PDFS_FOUND -ne 2 ]; then
    print_warning "Please place both PDF files in the project root directory."
    print_warning "The system will fail to start without them."
fi

# Step 7: Set up environment variables
print_header "Step 7: Setting up Environment Variables"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
        print_warning "IMPORTANT: Edit .env and add your OPENAI_API_KEY!"
        print_color "$YELLOW" "Run: nano .env  (or your preferred editor)"
    else
        print_error ".env.example not found!"
        print_warning "Create .env file manually with OPENAI_API_KEY"
    fi
else
    print_success ".env file already exists"
    
    # Check if API key is set
    if grep -q "your_openai_api_key_here" .env; then
        print_warning "Remember to update your OPENAI_API_KEY in .env!"
    else
        print_success "OPENAI_API_KEY appears to be set"
    fi
fi

# Step 8: Test imports
print_header "Step 8: Testing Imports"
$PYTHON_CMD -c "
import fastapi
import langchain
import langgraph
import chromadb
import openai
print('All imports successful!')
" 2>/dev/null && print_success "All required packages are importable" || print_error "Some packages failed to import"

# Step 9: Create necessary directories
print_header "Step 9: Creating Directory Structure"
mkdir -p chroma_db/citrus_diseases
mkdir -p chroma_db/government_schemes
mkdir -p logs
print_success "Directory structure created"

# Step 10: Summary
print_header "🎉 Setup Complete!"

echo ""
print_color "$GREEN" "✓ Python $PYTHON_VERSION configured"
print_color "$GREEN" "✓ Virtual environment ready"
print_color "$GREEN" "✓ Dependencies installed"
print_color "$GREEN" "✓ Directory structure created"

echo ""
print_header "📋 Next Steps:"
echo ""
echo "1. Ensure both PDF files are in the project root:"
echo "   - CitrusPlantPestsAndDiseases.pdf"
echo "   - GovernmentSchemes.pdf"
echo ""
echo "2. Configure your OpenAI API key in .env:"
print_color "$YELLOW" "   nano .env"
echo "   (Set OPENAI_API_KEY=your-actual-key)"
echo ""
echo "3. Start the application:"
print_color "$GREEN" "   python main.py"
echo "   or"
print_color "$GREEN" "   uvicorn main:app --reload"
echo ""
echo "4. Access the API:"
echo "   http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "5. Run tests:"
print_color "$GREEN" "   python test_queries.py"
echo ""

print_header "💡 Useful Commands:"
echo ""
echo "Activate virtual environment:"
print_color "$BLUE" "  source venv/bin/activate"
echo ""
echo "Deactivate virtual environment:"
print_color "$BLUE" "  deactivate"
echo ""
echo "Check health:"
print_color "$BLUE" "  curl http://localhost:8000/health"
echo ""
echo "Test query:"
print_color "$BLUE" '  curl -X POST http://localhost:8000/query \\'
print_color "$BLUE" '    -H "Content-Type: application/json" \\'
print_color "$BLUE" '    -d '"'"'{"question": "How do I prevent Citrus Canker?"}'"'"
echo ""

print_color "$GREEN" "Happy coding! 🚀"
echo ""
