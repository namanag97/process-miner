#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Project Setup ===${NC}"

# 1. Backend Setup
echo -e "\n${BLUE}[1/2] Setting up Backend...${NC}"

# Check for Python 3.11+
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please install Python 3.11 or higher."
    exit 1
fi

cd backend

# Create .venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate venv and install requirements
echo "Installing backend dependencies..."
source .venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: backend/requirements.txt not found."
fi

# Check if .env exists, if not create from .env.example
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

cd ..

# 2. Frontend Setup
echo -e "\n${BLUE}[2/2] Setting up Frontend...${NC}"

# Install node modules
if [ -f "package.json" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "Error: package.json not found."
    exit 1
fi

echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
echo -e "You can now run:"
echo -e "  • Backend: ${BLUE}npm run dev:backend${NC}"
echo -e "  • Frontend: ${BLUE}npm run dev${NC}"
