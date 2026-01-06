---
description: Debug API endpoints with curl commands and health checks
---
Quick debugging tools for API issues.

### 1. Health check
// turbo
```bash
curl -s http://localhost:8001/api/v1/health | python -m json.tool
```

### 2. List all endpoints
```bash
curl -s http://localhost:8001/openapi.json | python -c "import sys,json; [print(f'{m.upper():6} {p}') for p,v in json.load(sys.stdin)['paths'].items() for m in v.keys() if m in ['get','post','put','delete','patch']]"
```

### 3. Check specific endpoint
Replace `{endpoint}` with your path:
```bash
curl -s -X GET "http://localhost:8001/api/v1/{endpoint}" -H "Content-Type: application/json" | python -m json.tool
```

### 4. View recent server logs
```bash
cd backend && tail -50 server.log 2>/dev/null || echo "No server.log found"
```

### 5. Open API docs in browser
```bash
open http://localhost:8001/docs
```
