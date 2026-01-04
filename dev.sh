#!/bin/bash
# Development server startup script
# Starts both backend and frontend in parallel

set -e

echo "🚀 Starting development servers..."

# Kill any existing servers
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "nx serve" 2>/dev/null || true
sleep 1

# Start backend
echo "📦 Starting backend on http://localhost:8001..."
cd backend
source .venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend..."
for i in {1..10}; do
  if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✓ Backend ready"
    break
  fi
  sleep 1
done

# Start frontend
echo "⚛️  Starting frontend on http://localhost:4200..."
cd frontend-new
npm start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd ..

# Save PIDs for cleanup
echo "$BACKEND_PID" > /tmp/dev-backend.pid
echo "$FRONTEND_PID" > /tmp/dev-frontend.pid

echo ""
echo "✅ Development servers started!"
echo ""
echo "   Backend:  http://localhost:8001  (PID: $BACKEND_PID)"
echo "   Frontend: http://localhost:4200  (PID: $FRONTEND_PID)"
echo ""
echo "   Logs:"
echo "   - Backend:  tail -f /tmp/backend.log"
echo "   - Frontend: tail -f /tmp/frontend.log"
echo ""
echo "   To stop servers: ./stop-dev.sh"
echo ""

# Wait for user to Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
