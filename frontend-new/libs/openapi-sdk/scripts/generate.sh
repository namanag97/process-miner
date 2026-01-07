#!/bin/bash

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

# Backend OpenAPI spec location
OPENAPI_SPEC="../../../backend/docs/openapi.json"

if [ ! -f "$OPENAPI_SPEC" ]; then
    echo "Error: OpenAPI spec not found at $OPENAPI_SPEC"
    exit 1
fi

echo "Found OpenAPI spec at $OPENAPI_SPEC"

# Generate Client using Node.js tool (no Java required)
npx openapi-typescript-codegen \
    --input "$OPENAPI_SPEC" \
    --output src \
    --client axios \
    --name OpenAPI

echo "SDK Generated successfully in libs/openapi-sdk/src"
