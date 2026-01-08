# FE-BE CONNECTION FIX GUIDE

## The Connection Points

```
┌─────────────────────┐         ┌─────────────────────┐
│     FRONTEND        │         │      BACKEND        │
│   localhost:4200    │ ──────▶ │   localhost:8001    │
└─────────────────────┘  HTTP   └─────────────────────┘

Key Connection Points:
1. API Base URL configuration
2. CORS middleware
3. Auth token handling
4. Request/Response formats
```

---

## STEP 1: Verify Backend CORS

### Check current CORS config:
```bash
cd /Users/namanagarwal/system/backend
grep -A 20 "CORSMiddleware" src/api/main.py
```

### Required CORS setup in `src/api/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

# Add AFTER creating the app, BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:3000", 
        "http://127.0.0.1:4200",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # For file downloads
)
```

### Test CORS:
```bash
# This should return CORS headers
curl -I -X OPTIONS http://localhost:8001/api/v1/auth/login \
  -H "Origin: http://localhost:4200" \
  -H "Access-Control-Request-Method: POST"
```

**Expected headers:**
```
Access-Control-Allow-Origin: http://localhost:4200
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

---

## STEP 2: Verify Frontend API Config

### Find API configuration:
```bash
cd /Users/namanagarwal/system/frontend-new

# Check for env files
cat .env 2>/dev/null || echo "No .env file"
cat .env.local 2>/dev/null || echo "No .env.local"
cat .env.development 2>/dev/null || echo "No .env.development"

# Find API URL in code
grep -r "localhost:8001\|API_URL\|apiUrl\|baseURL" src/ --include="*.ts" --include="*.tsx" --include="*.js"
```

### Create/Update `.env`:
```bash
cd /Users/namanagarwal/system/frontend-new

# For Vite
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8001/api/v1
VITE_API_BASE=http://localhost:8001
EOF

# For Create React App
cat > .env << 'EOF'
REACT_APP_API_URL=http://localhost:8001/api/v1
REACT_APP_API_BASE=http://localhost:8001
EOF
```

### Standard API client setup:
```typescript
// src/services/api.ts
import axios from 'axios';

// Get base URL from environment or default
const getBaseUrl = () => {
  // Vite
  if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Create React App
  if (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // Default
  return 'http://localhost:8001/api/v1';
};

export const api = axios.create({
  baseURL: getBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## STEP 3: Test Connection from Browser

### Open browser console (F12) and run:
```javascript
// Test 1: Basic connectivity
fetch('http://localhost:8001/health/live')
  .then(r => r.json())
  .then(console.log)
  .catch(e => console.error('Connection failed:', e));

// Test 2: Auth endpoint
fetch('http://localhost:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    email: 'analyst@example.com', 
    password: 'TestPass123' 
  })
})
.then(r => r.json())
.then(data => {
  console.log('Login response:', data);
  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token);
    console.log('Token stored!');
  }
})
.catch(e => console.error('Login failed:', e));

// Test 3: Authenticated request
const token = localStorage.getItem('access_token');
fetch('http://localhost:8001/api/v1/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

---

## STEP 4: Fix Common Issues

### Issue: CORS Error
```
Access to fetch at 'http://localhost:8001/...' from origin 
'http://localhost:4200' has been blocked by CORS policy
```

**Fix in backend** `src/api/main.py`:
```python
# Make sure CORS middleware is added FIRST
app = FastAPI(...)

# Add CORS immediately after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then add routes...
```

### Issue: 401 on Every Request

**Check 1:** Token stored correctly
```javascript
// In browser console
console.log('Token:', localStorage.getItem('access_token'));
```

**Check 2:** Token sent in header
```javascript
// Check network tab in DevTools
// Request headers should show: Authorization: Bearer <token>
```

**Fix in frontend** - auth service:
```typescript
// src/services/authService.ts
export const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password });
  const { access_token } = response.data;
  
  // Store token
  localStorage.setItem('access_token', access_token);
  
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
};

export const getToken = () => localStorage.getItem('access_token');

export const isAuthenticated = () => !!getToken();
```

### Issue: Network Error / ERR_CONNECTION_REFUSED

**Cause:** Backend not running

**Fix:**
```bash
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
```

### Issue: 404 Not Found

**Cause:** Wrong endpoint path

**Check backend routes:**
```bash
curl http://localhost:8001/openapi.json | jq '.paths | keys' | head -30
```

**Compare with frontend calls:**
```bash
grep -r "api.get\|api.post\|api.put\|api.delete" src/services/ --include="*.ts"
```

### Issue: 422 Unprocessable Entity

**Cause:** Request body doesn't match expected schema

**Check what backend expects:**
```bash
# Get schema for endpoint
curl http://localhost:8001/openapi.json | jq '.paths["/api/v1/auth/login"].post.requestBody'
```

**Fix frontend** to send correct format:
```typescript
// Wrong
api.post('/auth/login', { user: email, pass: password });

// Right
api.post('/auth/login', { email, password });
```

---

## STEP 5: Verify Each API Service

### Auth Service Test:
```typescript
// src/services/authService.ts
import api from './api';

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },
  
  me: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
  }
};
```

### Dataset Service Test:
```typescript
// src/services/datasetService.ts
import api from './api';

export const datasetService = {
  upload: async (file: File, projectId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);
    formData.append('project_id', projectId);
    
    const response = await api.post('/datasets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  getColumns: async (datasetId: string) => {
    const response = await api.get(`/datasets/${datasetId}/columns`);
    return response.data;
  },
  
  submitMapping: async (datasetId: string, mapping: object) => {
    const response = await api.post(`/datasets/${datasetId}/mapping`, mapping);
    return response.data;
  },
  
  ingest: async (datasetId: string) => {
    const response = await api.post(`/datasets/${datasetId}/ingest`);
    return response.data;
  },
  
  get: async (datasetId: string) => {
    const response = await api.get(`/datasets/${datasetId}`);
    return response.data;
  },
  
  list: async (projectId?: string) => {
    const params = projectId ? { project_id: projectId } : {};
    const response = await api.get('/datasets/', { params });
    return response.data;
  }
};
```

### Visualization Service Test:
```typescript
// src/services/visualizationService.ts
import api from './api';

export const visualizationService = {
  getDFG: async (datasetId: string) => {
    const response = await api.get(`/visualization/${datasetId}/dfg`);
    return response.data;
  },
  
  getDFGSvg: async (datasetId: string) => {
    const response = await api.get(`/visualization/${datasetId}/dfg/svg`);
    return response.data;
  },
  
  getPetriNet: async (modelId: string) => {
    const response = await api.get(`/visualization/models/${modelId}/petri`);
    return response.data;
  },
  
  getExplorerData: async (datasetId: string) => {
    const response = await api.get(`/visualization/${datasetId}/explorer-data`);
    return response.data;
  }
};
```

### Test from browser console:
```javascript
// After importing/defining services
const token = localStorage.getItem('access_token');

// Test dataset list
fetch('http://localhost:8001/api/v1/datasets/', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);

// Test visualization (replace with actual dataset ID)
fetch('http://localhost:8001/api/v1/visualization/mvp-dataset-001/dfg', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);
```

---

## CONNECTION CHECKLIST

- [ ] Backend running on port 8001
- [ ] Frontend running on port 4200
- [ ] CORS middleware configured with localhost:4200
- [ ] Frontend .env has correct API URL
- [ ] api.ts has correct baseURL
- [ ] Auth interceptor adds Bearer token
- [ ] Login stores token in localStorage
- [ ] No CORS errors in browser console
- [ ] No 401 errors after login
- [ ] Can fetch /auth/me with stored token
- [ ] Can fetch /datasets/ list
- [ ] Can fetch visualization data

**When all checked: FE-BE connection is working! ✅**
