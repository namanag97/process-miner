#!/usr/bin/env bash
# Generate TypeScript SDK from OpenAPI spec
# Usage: ./scripts/generate-sdk.sh

set -e

API_URL="${API_URL:-http://localhost:8001}"
OUTPUT_DIR="${OUTPUT_DIR:-../frontend-new/src/api/generated}"

echo "🔄 Generating TypeScript SDK from OpenAPI spec..."
echo "   API: $API_URL"
echo "   Output: $OUTPUT_DIR"

# Check if server is running
if ! curl -s "$API_URL/openapi.json" > /dev/null 2>&1; then
    echo "❌ Backend server not running at $API_URL"
    echo "   Start with: cd backend && python -m src.api.main"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate SDK using openapi-typescript-codegen
npx -y openapi-typescript-codegen \
    --input "$API_URL/openapi.json" \
    --output "$OUTPUT_DIR" \
    --client axios \
    --useOptions \
    --useUnionTypes

echo "✅ SDK generated successfully!"
echo ""
echo "Usage in frontend:"
echo "  import { DatasetsService } from '@/api/generated';"
echo "  const datasets = await DatasetsService.listDatasets();"
