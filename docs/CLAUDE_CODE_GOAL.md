# CLAUDE CODE MISSION: Polish MVP to Production Ready

## YOUR GOAL

Fix the Process Mining platform until a user can complete this flow WITHOUT ERRORS:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER FLOW (MUST WORK)                             │
│                                                                             │
│   1. Open http://localhost:4200                                             │
│   2. See login page → Enter credentials → Click login                       │
│   3. See workspace with projects → Click on a project                       │
│   4. Click "Upload" → Drag CSV file → See upload progress                   │
│   5. See column mapping → Select case_id, activity, timestamp → Submit      │
│   6. See processing indicator → Wait → See "Ready" status                   │
│   7. Click "View" or navigate to Explorer                                   │
│   8. SEE INTERACTIVE PROCESS MAP with nodes and edges                       │
│   9. Click on nodes → See activity details                                  │
│  10. Navigate to Analytics → See variants list and bottlenecks chart        │
│  11. Navigate to Discovery → Run Inductive Miner → See Petri net            │
│  12. No console errors throughout                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## SUCCESS CRITERIA

The MVP is DONE when:
- [ ] All 12 steps above work without errors
- [ ] Browser console (F12) shows no red errors
- [ ] Network tab shows all API calls return 200
- [ ] Visualization displays interactive graph with real data
- [ ] User can complete flow in under 5 minutes

---

## PHASE 1: ENVIRONMENT SETUP

### 1.1 Start Services

```bash
# Terminal 1: Backend
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Terminal 2: Frontend  
cd /Users/namanagarwal/system/frontend-new
npm install
npm run start

# Terminal 3: Testing
export TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')
echo "Token: $TOKEN"
```

### 1.2 Verify Infrastructure

```bash
# Backend health
curl -s http://localhost:8001/health/live | jq .status
# Expected: "healthy"

# Frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:4200
# Expected: 200

# Auth works
[ -n "$TOKEN" ] && echo "✓ Auth OK" || echo "✗ Auth BROKEN"
```

**STOP if any of these fail. Fix infrastructure first.**

---

## PHASE 2: FIX BACKEND API

### 2.1 Test Each Endpoint

Run these and fix any that fail:

```bash
BASE="http://localhost:8001/api/v1"

echo "=== AUTH ==="
curl -s "$BASE/auth/me" -H "Authorization: Bearer $TOKEN" | jq '.email // .detail'

echo "=== WORKSPACES ==="
curl -s "$BASE/workspaces" -H "Authorization: Bearer $TOKEN" | jq '.items | length // .detail'

echo "=== PROJECTS ==="
curl -s "$BASE/projects" -H "Authorization: Bearer $TOKEN" | jq '.items | length // .detail'

echo "=== DATASETS ==="
curl -s "$BASE/datasets/" -H "Authorization: Bearer $TOKEN" | jq '.items | length // .detail'

echo "=== DISCOVERY MINERS ==="
curl -s "$BASE/discovery/miners" -H "Authorization: Bearer $TOKEN" | jq 'length // .detail'
```

### 2.2 Test Data Pipeline

```bash
# Find or create a test dataset
DATASET_ID=$(curl -s "$BASE/datasets/" -H "Authorization: Bearer $TOKEN" | jq -r '.items[] | select(.status=="ready") | .id' | head -1)

if [ -z "$DATASET_ID" ]; then
  echo "No ready dataset. Creating one..."
  
  # Upload
  UPLOAD=$(curl -s -X POST "$BASE/datasets/" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
    -F "name=Test" \
    -F "project_id=mvp-proj-001")
  DATASET_ID=$(echo "$UPLOAD" | jq -r '.id')
  
  # Map columns
  curl -s -X POST "$BASE/datasets/$DATASET_ID/mapping" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}'
  
  # Ingest
  curl -s -X POST "$BASE/datasets/$DATASET_ID/ingest" -H "Authorization: Bearer $TOKEN"
  
  # Wait for ready
  for i in {1..30}; do
    STATUS=$(curl -s "$BASE/datasets/$DATASET_ID" -H "Authorization: Bearer $TOKEN" | jq -r '.status')
    echo "[$i] Status: $STATUS"
    [ "$STATUS" = "ready" ] && break
    [ "$STATUS" = "failed" ] && echo "FAILED!" && break
    sleep 2
  done
fi

echo "Using dataset: $DATASET_ID"
```

### 2.3 Test Visualization Endpoint (CRITICAL)

```bash
echo "=== VISUALIZATION ==="
VIZ=$(curl -s "$BASE/visualization/$DATASET_ID/dfg" -H "Authorization: Bearer $TOKEN")
echo "$VIZ" | jq '{nodes: (.nodes | length), edges: (.edges | length), error: .detail}'
```

**Expected output:** `{"nodes": 5, "edges": 8, "error": null}`

**If nodes/edges are 0 or null:**
→ The visualization endpoint is broken
→ Fix `src/api/routes/visualization.py` (see Phase 2.4)

### 2.4 Fix Visualization Endpoint

**Check if endpoint exists:**
```bash
grep -r "dfg" /Users/namanagarwal/system/backend/src/api/routes/
```

**If missing or broken, create/fix it:**

```python
# File: src/api/routes/visualization.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import pm4py
import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.statistics.attributes.log.get import get_attribute_values

router = APIRouter(prefix="/visualization", tags=["visualization"])

@router.get("/{dataset_id}/dfg")
async def get_dfg(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Return DFG as JSON for frontend visualization."""
    
    # 1. Get dataset from database
    dataset = await dataset_repository.get_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    
    if dataset.status != "ready":
        raise HTTPException(status_code=400, detail=f"Dataset not ready: {dataset.status}")
    
    # 2. Load the processed data
    try:
        # Adjust path based on your storage
        df = pd.read_parquet(dataset.processed_path)
    except Exception as e:
        # Fallback to CSV if parquet doesn't exist
        df = pd.read_csv(dataset.file_path)
    
    # 3. Prepare for PM4Py
    df = df.rename(columns={
        dataset.case_column or "case_id": "case:concept:name",
        dataset.activity_column or "activity": "concept:name",
        dataset.timestamp_column or "timestamp": "time:timestamp"
    })
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    
    # 4. Convert to event log
    log = log_converter.apply(df, variant=log_converter.Variants.TO_EVENT_LOG)
    
    # 5. Discover DFG
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    
    # 6. Get activity frequencies
    activity_freq = get_attribute_values(log, "concept:name")
    
    # 7. Build response
    nodes = [
        {"id": activity, "label": activity, "frequency": freq}
        for activity, freq in activity_freq.items()
    ]
    
    edges = [
        {"source": source, "target": target, "value": count}
        for (source, target), count in dfg.items()
    ]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "start_activities": dict(start_activities),
        "end_activities": dict(end_activities)
    }
```

**Register the router in main.py:**
```python
# In src/api/main.py
from api.routes import visualization
app.include_router(visualization.router, prefix="/api/v1")
```

### 2.5 Test Analytics Endpoints

```bash
echo "=== VARIANTS ==="
curl -s "$BASE/analytics/datasets/$DATASET_ID/variants" -H "Authorization: Bearer $TOKEN" | jq '.variants | length // .detail'

echo "=== BOTTLENECKS ==="
curl -s "$BASE/analytics/datasets/$DATASET_ID/bottlenecks" -H "Authorization: Bearer $TOKEN" | jq '.bottlenecks | length // .detail'
```

### 2.6 Test Discovery Endpoints

```bash
echo "=== INDUCTIVE MINER ==="
DISCOVER=$(curl -s -X POST "$BASE/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"inductive\"}")
echo "$DISCOVER" | jq '{model_id: (.model_id // .id), error: .detail}'
```

---

## PHASE 3: FIX FRONTEND-BACKEND CONNECTION

### 3.1 Check CORS

**File:** `src/api/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

# Add IMMEDIATELY after app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:3000",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3.2 Check Frontend API Config

**Find the API client:**
```bash
cd /Users/namanagarwal/system/frontend-new
grep -r "baseURL\|API_URL\|localhost:8001" src/ --include="*.ts" --include="*.tsx" | head -5
```

**Ensure it points to correct URL:**
```typescript
// src/services/api.ts (or wherever your API client is)
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
});

// Auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 3.3 Create/Check .env File

```bash
cd /Users/namanagarwal/system/frontend-new

# For Vite
echo "VITE_API_URL=http://localhost:8001/api/v1" > .env

# Restart frontend after creating .env
npm run start
```

### 3.4 Test Connection from Browser

Open http://localhost:4200, press F12, go to Console, run:

```javascript
// Test API connection
fetch('http://localhost:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'analyst@example.com', password: 'TestPass123' })
})
.then(r => r.json())
.then(d => console.log('Login:', d.access_token ? 'SUCCESS' : 'FAILED', d))
.catch(e => console.error('CORS/Network error:', e));
```

---

## PHASE 4: FIX FRONTEND PAGES

### 4.1 Audit Existing Pages

```bash
cd /Users/namanagarwal/system/frontend-new

# List all page components
find src -type d -name "[Pp]ages" -o -name "[Vv]iews" | xargs -I {} find {} -name "*.tsx" | head -20

# Check for key pages
ls -la src/pages/ 2>/dev/null || ls -la src/views/ 2>/dev/null
```

**Required pages:**
- Login
- Workspace/Dashboard
- Upload (wizard)
- Explorer (process map)
- Analytics
- Discovery

### 4.2 Fix Login Page

**Ensure login stores token:**
```typescript
// src/pages/Login/Login.tsx (or similar)
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await api.post('/auth/login', { email, password });
    const { access_token } = response.data;
    
    // CRITICAL: Store the token
    localStorage.setItem('access_token', access_token);
    
    // Redirect to workspace
    navigate('/workspace');
  } catch (error) {
    setError('Login failed');
  }
};
```

### 4.3 Fix Explorer Page (Process Map)

**This is the most critical page. It MUST:**
1. Get datasetId from URL
2. Fetch DFG from backend
3. Pass data to graph component
4. Render interactive graph

```typescript
// src/pages/Explorer/Explorer.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';
import ProcessMap from '../../components/ProcessMap/ProcessMap';

interface DFGData {
  nodes: Array<{ id: string; label: string; frequency: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
}

const Explorer: React.FC = () => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [data, setData] = useState<DFGData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) {
      setError('No dataset selected');
      setLoading(false);
      return;
    }

    const fetchVisualization = async () => {
      try {
        const response = await api.get(`/visualization/${datasetId}/dfg`);
        setData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load visualization');
      } finally {
        setLoading(false);
      }
    };

    fetchVisualization();
  }, [datasetId]);

  if (loading) {
    return <div className="loading">Loading process map...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!data || !data.nodes.length) {
    return <div className="empty">No process data available</div>;
  }

  return (
    <div className="explorer-page">
      <header>
        <h1>Process Explorer</h1>
        <span>{data.nodes.length} activities · {data.edges.length} transitions</span>
      </header>
      <main>
        <ProcessMap nodes={data.nodes} edges={data.edges} />
      </main>
    </div>
  );
};

export default Explorer;
```

### 4.4 Fix ProcessMap Component

```bash
# Install Cytoscape if missing
cd /Users/namanagarwal/system/frontend-new
npm install cytoscape cytoscape-dagre @types/cytoscape
```

```typescript
// src/components/ProcessMap/ProcessMap.tsx
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register layout plugin once
cytoscape.use(dagre);

interface Props {
  nodes: Array<{ id: string; label: string; frequency?: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
}

const ProcessMap: React.FC<Props> = ({ nodes, edges }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || !nodes.length) return;

    // Destroy previous instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Calculate max values for scaling
    const maxFreq = Math.max(...nodes.map(n => n.frequency || 1));
    const maxEdge = Math.max(...edges.map(e => e.value));

    // Create Cytoscape instance
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map(n => ({
          data: { 
            id: n.id, 
            label: `${n.label}\n(${n.frequency || 0})`,
            frequency: n.frequency || 1
          }
        })),
        ...edges.map(e => ({
          data: {
            id: `${e.source}→${e.target}`,
            source: e.source,
            target: e.target,
            value: e.value,
            label: String(e.value)
          }
        }))
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#4A90D9',
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#fff',
            'text-outline-width': 2,
            'text-outline-color': '#4A90D9',
            'font-size': '11px',
            'text-wrap': 'wrap',
            'width': `mapData(frequency, 1, ${maxFreq}, 50, 100)`,
            'height': `mapData(frequency, 1, ${maxFreq}, 50, 100)`,
            'shape': 'roundrectangle'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': `mapData(value, 1, ${maxEdge}, 1, 6)`,
            'line-color': '#7f8c8d',
            'target-arrow-color': '#7f8c8d',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '9px',
            'text-background-color': '#fff',
            'text-background-opacity': 0.8
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 3,
            'border-color': '#e74c3c'
          }
        }
      ],
      layout: {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 60,
        rankSep: 100,
        padding: 30
      },
      minZoom: 0.3,
      maxZoom: 3
    });

    // Fit view
    cyRef.current.fit(undefined, 30);

    return () => {
      cyRef.current?.destroy();
    };
  }, [nodes, edges]);

  return (
    <div 
      ref={containerRef}
      style={{
        width: '100%',
        height: '600px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        background: '#fafafa'
      }}
    />
  );
};

export default ProcessMap;
```

### 4.5 Check Routes Configuration

```typescript
// src/App.tsx or src/routes/index.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Workspace from './pages/Workspace';
import Upload from './pages/Upload';
import Explorer from './pages/Explorer';
import Analytics from './pages/Analytics';
import Discovery from './pages/Discovery';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/workspace" element={<Workspace />} />
        <Route path="/workspace/:workspaceId/upload" element={<Upload />} />
        <Route path="/workspace/:workspaceId/data/:datasetId/explorer" element={<Explorer />} />
        <Route path="/workspace/:workspaceId/data/:datasetId/analytics" element={<Analytics />} />
        <Route path="/workspace/:workspaceId/data/:datasetId/discovery" element={<Discovery />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## PHASE 5: FIX UPLOAD WIZARD

### 5.1 Upload Flow Components

The upload wizard needs:
1. File dropzone
2. Column detection display
3. Column mapping form
4. Progress indicator
5. Success/error states

```typescript
// src/pages/Upload/Upload.tsx
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

type Step = 'upload' | 'mapping' | 'processing' | 'complete';

const Upload: React.FC = () => {
  const { workspaceId } = useParams();
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>('upload');
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [mapping, setMapping] = useState({
    case_id_column: '',
    activity_column: '',
    timestamp_column: ''
  });
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  // Step 1: Upload file
  const handleFileUpload = async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', file.name);
      formData.append('project_id', 'mvp-proj-001'); // Or get from context

      const response = await api.post('/datasets/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => setProgress(Math.round((e.loaded * 100) / (e.total || 1)))
      });

      setDatasetId(response.data.id);

      // Get detected columns
      const colResponse = await api.get(`/datasets/${response.data.id}/columns`);
      setColumns(colResponse.data.columns || []);
      setStep('mapping');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    }
  };

  // Step 2: Submit mapping
  const handleMappingSubmit = async () => {
    if (!datasetId) return;

    try {
      await api.post(`/datasets/${datasetId}/mapping`, mapping);
      await api.post(`/datasets/${datasetId}/ingest`);
      setStep('processing');

      // Poll for completion
      const pollStatus = async () => {
        const response = await api.get(`/datasets/${datasetId}`);
        if (response.data.status === 'ready') {
          setStep('complete');
        } else if (response.data.status === 'failed') {
          setError('Processing failed');
        } else {
          setTimeout(pollStatus, 2000);
        }
      };
      pollStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Processing failed');
    }
  };

  // Render based on step
  return (
    <div className="upload-page">
      <h1>Upload Event Log</h1>

      {error && <div className="error-banner">{error}</div>}

      {step === 'upload' && (
        <div className="upload-dropzone">
          <input 
            type="file" 
            accept=".csv,.xes"
            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
          />
          <p>Drop CSV or XES file here</p>
          {progress > 0 && <progress value={progress} max={100} />}
        </div>
      )}

      {step === 'mapping' && (
        <div className="column-mapping">
          <h2>Map Your Columns</h2>
          <div className="form-group">
            <label>Case ID *</label>
            <select 
              value={mapping.case_id_column}
              onChange={(e) => setMapping({...mapping, case_id_column: e.target.value})}
            >
              <option value="">Select...</option>
              {columns.map(col => <option key={col} value={col}>{col}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Activity *</label>
            <select 
              value={mapping.activity_column}
              onChange={(e) => setMapping({...mapping, activity_column: e.target.value})}
            >
              <option value="">Select...</option>
              {columns.map(col => <option key={col} value={col}>{col}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Timestamp *</label>
            <select 
              value={mapping.timestamp_column}
              onChange={(e) => setMapping({...mapping, timestamp_column: e.target.value})}
            >
              <option value="">Select...</option>
              {columns.map(col => <option key={col} value={col}>{col}</option>)}
            </select>
          </div>
          <button 
            onClick={handleMappingSubmit}
            disabled={!mapping.case_id_column || !mapping.activity_column || !mapping.timestamp_column}
          >
            Start Processing
          </button>
        </div>
      )}

      {step === 'processing' && (
        <div className="processing">
          <div className="spinner" />
          <p>Processing your data...</p>
        </div>
      )}

      {step === 'complete' && datasetId && (
        <div className="complete">
          <h2>✓ Upload Complete!</h2>
          <button onClick={() => navigate(`/workspace/${workspaceId}/data/${datasetId}/explorer`)}>
            View Process Map
          </button>
        </div>
      )}
    </div>
  );
};

export default Upload;
```

---

## PHASE 6: VERIFICATION

### 6.1 Automated Verification Script

```bash
#!/bin/bash
# Save as verify_mvp.sh and run

BASE="http://localhost:8001/api/v1"
PASS=0; FAIL=0

check() {
  if [ "$1" = "true" ]; then
    echo "✓ $2"; PASS=$((PASS+1))
  else
    echo "✗ $2"; FAIL=$((FAIL+1))
  fi
}

echo "=== MVP VERIFICATION ==="

# Auth
TOKEN=$(curl -s -X POST "$BASE/auth/login" -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token // empty')
check "[ -n \"$TOKEN\" ]" "Auth login"

# Upload
DS=$(curl -s -X POST "$BASE/datasets/" -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
  -F "name=Verify" -F "project_id=mvp-proj-001" | jq -r '.id // empty')
check "[ -n \"$DS\" ]" "Dataset upload (ID: $DS)"

# Columns
COLS=$(curl -s "$BASE/datasets/$DS/columns" -H "Authorization: Bearer $TOKEN" | jq '.columns | length')
check "[ \"$COLS\" -gt 0 ]" "Column detection ($COLS columns)"

# Mapping
curl -s -X POST "$BASE/datasets/$DS/mapping" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}' > /dev/null
check "true" "Column mapping"

# Ingest
curl -s -X POST "$BASE/datasets/$DS/ingest" -H "Authorization: Bearer $TOKEN" > /dev/null
for i in {1..30}; do
  STATUS=$(curl -s "$BASE/datasets/$DS" -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  [ "$STATUS" = "ready" ] && break
  sleep 1
done
check "[ \"$STATUS\" = \"ready\" ]" "Ingestion (status: $STATUS)"

# Visualization
NODES=$(curl -s "$BASE/visualization/$DS/dfg" -H "Authorization: Bearer $TOKEN" | jq '.nodes | length // 0')
check "[ \"$NODES\" -gt 0 ]" "DFG visualization ($NODES nodes)"

# Analytics
VARS=$(curl -s "$BASE/analytics/datasets/$DS/variants" -H "Authorization: Bearer $TOKEN" | jq '.variants | length // 0')
check "[ \"$VARS\" -gt 0 ]" "Variants ($VARS found)"

# Discovery
MODEL=$(curl -s -X POST "$BASE/discovery/discover" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DS\",\"algorithm\":\"inductive\"}" | jq -r '.model_id // .id // empty')
check "[ -n \"$MODEL\" ]" "Inductive Miner (model: $MODEL)"

echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && echo "🎉 MVP BACKEND COMPLETE!" || echo "⚠️ Fix failing checks"
```

### 6.2 Manual UI Verification

Open http://localhost:4200 and verify each step:

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Go to /login | See login form |
| 2 | Enter analyst@example.com / TestPass123 | Redirects to workspace |
| 3 | Click on a project | See project details |
| 4 | Click Upload | See file dropzone |
| 5 | Drop insurance_small.csv | See upload progress, then column list |
| 6 | Select case_id, activity, timestamp | Dropdowns work |
| 7 | Click Start Processing | See spinner |
| 8 | Wait for completion | See "Complete" message |
| 9 | Click View Process Map | **See graph with nodes and edges** |
| 10 | Click on a node | See highlight or details |
| 11 | Go to Analytics | See variants and bottlenecks |
| 12 | Check console (F12) | No red errors |

---

## PHASE 7: POLISH

### 7.1 Add Loading States

Every page that fetches data should have:
```typescript
if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error} />;
if (!data) return <EmptyState />;
```

### 7.2 Add Error Handling

```typescript
try {
  const response = await api.get(...);
} catch (err) {
  if (err.response?.status === 401) {
    navigate('/login');
  } else if (err.response?.status === 404) {
    setError('Resource not found');
  } else {
    setError('Something went wrong');
  }
}
```

### 7.3 Add Navigation

Ensure users can navigate between pages:
- Header with nav links
- Back buttons
- Breadcrumbs

### 7.4 Style Consistency

- Use consistent colors
- Add hover states to buttons
- Make interactive elements obvious

---

## COMPLETION CHECKLIST

### Backend ✅
- [ ] Auth endpoints work
- [ ] Dataset upload works
- [ ] Column detection works
- [ ] Column mapping saves
- [ ] Ingestion completes to "ready"
- [ ] Visualization returns nodes/edges
- [ ] Analytics returns variants/bottlenecks
- [ ] Discovery returns model

### Frontend ✅
- [ ] Login page works, stores token
- [ ] Workspace shows projects
- [ ] Upload wizard complete flow
- [ ] Explorer shows interactive graph
- [ ] Analytics displays data
- [ ] Discovery runs algorithms
- [ ] No console errors
- [ ] Responsive and usable

### Integration ✅
- [ ] No CORS errors
- [ ] All API calls authenticated
- [ ] Error states handled gracefully
- [ ] Loading states present
- [ ] Navigation works

---

## WHEN COMPLETE

```bash
git add .
git commit -m "feat: MVP complete - polished end-to-end user flow

- Backend: All API endpoints working
- Frontend: Complete user flow from login to visualization
- Integration: CORS, auth, error handling
- Polish: Loading states, navigation, styling"
```

**The MVP is DONE when a user can complete the 12-step flow without seeing any errors.**
