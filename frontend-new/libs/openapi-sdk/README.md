# OpenAPI SDK - Auto-Generated

This library contains auto-generated TypeScript types and API clients from the FastAPI backend's OpenAPI specification.

## Usage

```typescript
import { DFGNode, DFGEdge, ProjectResponse } from '@frontend-new/openapi-sdk';
import { DatasetsService, DiscoveryService } from '@frontend-new/openapi-sdk';
```

## Regenerating

Requires the backend to be running:

```bash
# Start backend
cd backend && source .venv/bin/activate && uvicorn src.api.main:app --port 8001

# Generate SDK (from frontend-new directory)
nx run @frontend-new/openapi-sdk:generate

# Or directly
cd libs/openapi-sdk && npm run generate
```

## Important

**DO NOT manually edit files in `src/`** — they are auto-generated and will be overwritten.

For custom types or extensions, create them in the consuming feature modules.
