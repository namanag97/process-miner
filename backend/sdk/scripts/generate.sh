#!/bin/bash
set -e

# Configuration
API_URL="${API_URL:-http://localhost:8001}"
OUTPUT_DIR="./src"

echo "Fetching OpenAPI spec from ${API_URL}/openapi.json..."
curl -s "${API_URL}/openapi.json" -o openapi.json

if [ ! -f openapi.json ]; then
    echo "Error: Failed to fetch OpenAPI spec"
    exit 1
fi

echo "Generating TypeScript client..."
npx openapi-typescript-codegen \
    --input openapi.json \
    --output "${OUTPUT_DIR}" \
    --client axios \
    --useOptions \
    --useUnionTypes \
    --exportCore true \
    --exportServices true \
    --exportModels true \
    --exportSchemas false

# Clean up
rm -f openapi.json

echo "SDK generated successfully in ${OUTPUT_DIR}/"
echo ""
echo "Generated structure:"
ls -la "${OUTPUT_DIR}/"
