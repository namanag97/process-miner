# RALPH LOOP: MVP to Polished State

## THE GOAL

User completes this flow in browser WITHOUT ERRORS:

```
Login → Upload CSV → Map Columns → Wait → SEE PROCESS MAP → View Analytics
```

---

## THE LOOP

```
┌─────────────────────────────────────────┐
│  1. TEST the user flow in browser       │
│              ↓                          │
│  2. FIND where it breaks                │
│              ↓                          │
│  3. FIX that specific issue             │
│              ↓                          │
│  4. VERIFY the fix works                │
│              ↓                          │
│  REPEAT until all 12 steps work         │
└─────────────────────────────────────────┘
```

---

## 12 STEPS TO VERIFY

Open http://localhost:4200 and test each:

| # | Action | Pass Criteria |
|---|--------|---------------|
| 1 | Open app | Login page shows |
| 2 | Enter creds, click login | Redirects to workspace |
| 3 | Click on project | Project opens |
| 4 | Click Upload | Dropzone appears |
| 5 | Drop CSV file | Upload completes |
| 6 | See column mapping | Dropdowns populated |
| 7 | Select columns, submit | Processing starts |
| 8 | Wait | Status = "Ready" |
| 9 | Navigate to Explorer | **GRAPH SHOWS** |
| 10 | Interact with graph | Zoom/click works |
| 11 | Go to Analytics | Data displays |
| 12 | Check console | No red errors |

---

## QUICK FIXES

### Step 2 fails (Login)
```typescript
// After login, store token:
localStorage.setItem('access_token', response.data.access_token);
```

### Step 5 fails (Upload)
```bash
# Check backend
curl -X POST "http://localhost:8001/api/v1/datasets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.csv" -F "name=Test" -F "project_id=mvp-proj-001"
```

### Step 9 fails (No Graph)
1. Check `/visualization/{id}/dfg` returns data
2. Check Cytoscape installed: `npm install cytoscape cytoscape-dagre`
3. Check container has height: `style={{ height: '500px' }}`

### CORS Error
```python
# In backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 401 Error
```typescript
// Check token is sent
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

---

## TEST COMMANDS

```bash
# Backend health
curl http://localhost:8001/health/live

# Auth
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')

# Visualization (CRITICAL)
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq '{nodes: (.nodes|length), edges: (.edges|length)}'
```

---

## KEY FILES

| Issue | File to Fix |
|-------|-------------|
| CORS | `backend/src/api/main.py` |
| Auth | `backend/src/api/routes/auth.py` |
| Visualization API | `backend/src/api/routes/visualization.py` |
| API client | `frontend/src/services/api.ts` |
| Login page | `frontend/src/pages/Login/` |
| Explorer page | `frontend/src/pages/Explorer/` |
| Process map | `frontend/src/components/ProcessMap/` |

---

## DONE WHEN

All 12 steps work. User can:
1. ✅ Login
2. ✅ Upload file
3. ✅ Map columns
4. ✅ See processing complete
5. ✅ **View interactive process map**
6. ✅ View analytics
7. ✅ No console errors

Then commit:
```bash
git add . && git commit -m "MVP: Polished end-to-end user flow"
```
