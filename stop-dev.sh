#!/bin/bash
# Stop development servers

echo "🛑 Stopping development servers..."

# Kill by PID files if they exist
if [ -f /tmp/dev-backend.pid ]; then
  BACKEND_PID=$(cat /tmp/dev-backend.pid)
  kill $BACKEND_PID 2>/dev/null && echo "✓ Stopped backend (PID: $BACKEND_PID)"
  rm /tmp/dev-backend.pid
fi

if [ -f /tmp/dev-frontend.pid ]; then
  FRONTEND_PID=$(cat /tmp/dev-frontend.pid)
  kill $FRONTEND_PID 2>/dev/null && echo "✓ Stopped frontend (PID: $FRONTEND_PID)"
  rm /tmp/dev-frontend.pid
fi

# Fallback: kill by process name
pkill -f "uvicorn" 2>/dev/null && echo "✓ Killed uvicorn processes"
pkill -f "nx serve" 2>/dev/null && echo "✓ Killed nx serve processes"

echo "✅ All servers stopped"
