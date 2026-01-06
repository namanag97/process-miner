#!/bin/bash
# Development server restart script
# Usage: ./dev.sh [port]

set -e

PORT=${1:-8001}
VENV_PATH=".venv/bin/activate"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Restarting backend server on port $PORT...${NC}"

# Kill any process using the port
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}⚡ Killing process on port $PORT...${NC}"
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Double-check port is free
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo -e "${RED}❌ Failed to free port $PORT${NC}"
    echo -e "${YELLOW}Process still running:${NC}"
    lsof -i:$PORT
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment found at $VENV_PATH${NC}"
fi

# Start server
echo -e "${GREEN}🚀 Starting uvicorn on port $PORT...${NC}"
echo ""
python -m uvicorn src.api.main:app --reload --reload-dir src --port $PORT
