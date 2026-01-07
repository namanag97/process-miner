# Backend API CLAUDE.md

## Overview
FastAPI application entry point and route aggregation. This is the presentation layer that handles HTTP requests.

## Key Files

### main.py
FastAPI application factory:
- App initialization
- Middleware configuration
- Exception handlers
- Router registration

## API Structure

Routes are registered from feature modules:
```python
from src.features.process_mining.analytics.router import router as analytics_router
from src.features.process_mining.discovery.router import router as discovery_router

app.include_router(analytics_router, prefix="/api/v1/analytics")
app.include_router(discovery_router, prefix="/api/v1/discovery")
```

## Middleware Stack

1. CORS - Cross-origin requests
2. Request ID - Unique request tracking
3. Error handling - Consistent error responses
4. Authentication - JWT validation

## Error Response Format

RFC 7807 Problem Details:
```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Dataset with id xyz not found",
  "instance": "/api/v1/datasets/xyz"
}
```

## Authentication

Bearer token authentication:
```
Authorization: Bearer <jwt_token>
```

Endpoints marked with `Depends(get_current_user)` require authentication.

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json
