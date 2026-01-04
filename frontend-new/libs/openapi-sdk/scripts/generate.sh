#!/bin/bash
set -e

# Configuration
API_URL="${API_URL:-http://localhost:8001}"
OUTPUT_DIR="./src"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDK_DIR="$(dirname "$SCRIPT_DIR")"

cd "$SDK_DIR"

echo "🔍 Fetching OpenAPI spec from ${API_URL}/openapi.json..."
curl -s "${API_URL}/openapi.json" -o openapi.json

if [ ! -f openapi.json ] || [ ! -s openapi.json ]; then
    echo "❌ Error: Failed to fetch OpenAPI spec. Is the backend running?"
    echo "   Start it with: cd backend && source .venv/bin/activate && uvicorn src.api.main:app --port 8001"
    exit 1
fi

echo "📦 Generating TypeScript SDK..."
npx openapi-typescript-codegen \
    --input openapi.json \
    --output "${OUTPUT_DIR}" \
    --client fetch \
    --useOptions \
    --useUnionTypes \
    --exportCore true \
    --exportServices true \
    --exportModels true \
    --exportSchemas false

# Clean up temp file
rm -f openapi.json

echo "✅ SDK generated successfully!"
echo ""
echo "Generated files:"
ls -la "${OUTPUT_DIR}/"
echo ""
echo "Models: $(ls -1 "${OUTPUT_DIR}/models/" 2>/dev/null | wc -l | tr -d ' ') files"
echo "Services: $(ls -1 "${OUTPUT_DIR}/services/" 2>/dev/null | wc -l | tr -d ' ') files"
