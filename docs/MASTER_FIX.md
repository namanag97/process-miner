# 🚀 MASTER MVP FIX - START HERE

## Your Mission
Get the Process Mining platform working end-to-end in the browser UI.

```
┌─────────────────────────────────────────────────────────────────────┐
│  SUCCESS = User can do this in the browser:                        │
│                                                                     │
│  1. Login                                                           │
│  2. Upload CSV file                                                 │
│  3. Map columns (case_id, activity, timestamp)                      │
│  4. Wait for processing                                             │
│  5. SEE THE PROCESS MAP (interactive visualization!)                │
│  6. View bottlenecks and variants                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## STEP 0: START SERVERS

```bash
# Terminal 1: Backend
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Terminal 2: Frontend
cd /Users/namanagarwal/system/frontend-new
npm install  # if needed
npm run start

# Terminal 3: Verify
curl -s http://localhost:8001/health/live | jq .status
curl -s -o /dev/null -w "Frontend: %{http_code}\n" http://localhost:4200
```

**Both must be running before proceeding.**

---

## STEP 1: FIX BACKEND (15 min)

### Quick Test
```bash
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')

[ -z "$TOKEN" ] && echo "❌ AUTH BROKEN" || echo "✅ Auth works: $TOKEN"
```

### If auth fails:
1. Check database: `ls /Users/namanagarwal/system/backend/*.db`
2. Run migrations: `cd backend && .venv/bin/alembic upgrade head`
3. Check `src/api/routes/auth.py` for errors

### Test full backend flow:
```bash
# Upload
DATASET_ID=$(curl -s -X POST "http://localhost:8001/api/v1/datasets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
  -F "name=Test" -F "project_id=mvp-proj-001" | jq -r '.id')
echo "Dataset: $DATASET_ID"

# Map + Ingest
curl -s -X POST "http://localhost:8001/api/v1/datasets/$DATASET_ID/mapping" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}'

curl -s -X POST "http://localhost:8001/api/v1/datasets/$DATASET_ID/ingest" \
  -H "Authorization: Bearer $TOKEN"

# Wait for ready
for i in {1..20}; do
  STATUS=$(curl -s "http://localhost:8001/api/v1/datasets/$DATASET_ID" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  echo "[$i] $STATUS"
  [ "$STATUS" = "ready" ] && break
  sleep 2
done

# Test visualization
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq '{nodes: (.nodes | length), edges: (.edges | length)}'
```

**All should work. If not, see `MVP_COMPLETE_FIX.md`**

---

## STEP 2: FIX FE-BE CONNECTION (10 min)

### Check CORS in backend
```bash
grep -A 15 "CORSMiddleware" /Users/namanagarwal/system/backend/src/api/main.py
```

**Must include `http://localhost:4200` in `allow_origins`**

### Check API URL in frontend
```bash
cd /Users/namanagarwal/system/frontend-new
grep -r "localhost:8001\|API_URL\|baseURL" src/ --include="*.ts" | head -10
```

### Create/verify `.env`:
```bash
cd /Users/namanagarwal/system/frontend-new
echo "VITE_API_URL=http://localhost:8001/api/v1" > .env
# Or for CRA:
echo "REACT_APP_API_URL=http://localhost:8001/api/v1" > .env
```

### Test connection from browser
Open http://localhost:4200, then F12 → Console:
```javascript
fetch('http://localhost:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'analyst@example.com', password: 'TestPass123' })
}).then(r => r.json()).then(console.log).catch(console.error);
```

**Should return `{ access_token: "..." }`. If CORS error, fix backend.**

**See `FE_BE_CONNECTION.md` for detailed fixes.**

---

## STEP 3: FIX FRONTEND PAGES (20 min)

### Key pages to verify:

| Page | URL | Must Show |
|------|-----|-----------|
| Login | `/login` | Email/password form |
| Workspace | `/workspace` | Project list |
| Upload | `/workspace/{id}/upload` | File dropzone |
| Explorer | `/workspace/{id}/data/{id}/explorer` | **PROCESS MAP** |
| Analytics | `/workspace/{id}/data/{id}/analytics` | Charts |

### Check routing
```bash
cd /Users/namanagarwal/system/frontend-new
grep -r "Route\|path=" src/ --include="*.tsx" | head -20
```

### Check services exist
```bash
ls -la src/services/
# Should have: api.ts, authService.ts, datasetService.ts, visualizationService.ts
```

---

## STEP 4: FIX VISUALIZATION (15 min)

### Check if Cytoscape installed
```bash
cd /Users/namanagarwal/system/frontend-new
grep "cytoscape" package.json
```

### Install if missing
```bash
npm install cytoscape cytoscape-dagre @types/cytoscape
```

### Find visualization component
```bash
grep -r "cytoscape\|ProcessMap\|graph" src/ --include="*.tsx" | head -10
```

### Key: Explorer page must:
1. Fetch data from `/visualization/{datasetId}/dfg`
2. Pass nodes/edges to graph component
3. Render interactive graph

**See `UI_VISUALIZATION.md` for component code.**

---

## STEP 5: FULL UI TEST

### Manual test flow:
1. Open http://localhost:4200
2. Login: `analyst@example.com` / `TestPass123`
3. Click on a project
4. Upload: `backend/tests/data/insurance_small.csv`
5. Map columns:
   - Case ID → `case_id`
   - Activity → `activity`
   - Timestamp → `timestamp`
6. Wait for "Ready" status
7. Click "View" or navigate to Explorer
8. **See process map with nodes and edges**
9. Click Analytics → see variants, bottlenecks

### Check browser console (F12)
- ❌ No red errors
- ❌ No CORS errors
- ❌ No 401/403 errors
- ✅ Network requests returning 200

---

## QUICK FIX REFERENCE

| Problem | Fix |
|---------|-----|
| CORS error | Add `localhost:4200` to backend CORS |
| 401 Unauthorized | Token not stored or sent. Check localStorage and axios interceptor |
| 404 Not Found | Wrong API path. Check endpoint URL |
| 500 Server Error | Check backend terminal for Python traceback |
| Graph not rendering | Check container has height. Check data not empty |
| "Module not found" | Run `npm install` |
| Database errors | Run `alembic upgrade head` |

---

## FILES TO REFERENCE

| Topic | Document |
|-------|----------|
| Backend fixes | `MVP_COMPLETE_FIX.md` |
| FE-BE connection | `FE_BE_CONNECTION.md` |
| UI visualization | `UI_VISUALIZATION.md` |
| Full stack | `FULLSTACK_MVP_FIX.md` |

---

## DONE CHECKLIST

### Backend ✅
- [ ] Health endpoint works
- [ ] Login returns token
- [ ] Upload creates dataset
- [ ] Ingestion reaches "ready"
- [ ] Discovery creates model
- [ ] Visualization returns nodes/edges
- [ ] Analytics returns data

### Frontend ✅
- [ ] Pages load without errors
- [ ] Login stores token
- [ ] Upload wizard works
- [ ] Process map renders
- [ ] Analytics displays

### Integration ✅
- [ ] No CORS errors
- [ ] API calls succeed
- [ ] Full flow works in browser

---

## SUCCESS 🎉

When you can:
1. Open browser → Login → Upload CSV → See process map → View analytics

**The MVP is complete!**

Commit: `git add . && git commit -m "MVP: Full stack working end-to-end"`
