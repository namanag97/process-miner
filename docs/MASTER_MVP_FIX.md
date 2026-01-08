# 🚀 COMPLETE MVP FIX - MASTER GUIDE

## Mission
Fix the Process Mining platform so it works end-to-end in the browser:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER JOURNEY (MUST WORK)                         │
│                                                                         │
│   Browser: Login → Upload CSV → Map Columns → See Process Map →         │
│            → View Bottlenecks → View Variants → Discover with           │
│            Different Algorithms → See Petri Net / BPMN                  │
│                                                                         │
│   Algorithms: DFG, Alpha, Heuristic, Inductive (all must work)          │
│   Visualizations: DFG Graph, Petri Net, BPMN, SVG exports              │
│   Analytics: Variants, Bottlenecks, Rework, Cycle Time, Throughput      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## DOCUMENT REFERENCE

| Document | Purpose |
|----------|---------|
| **This file** | Master guide - start here |
| `PM4PY_IMPLEMENTATION.md` | Exact PM4Py code for all algorithms |
| `FULLSTACK_MVP_FIX.md` | Full stack details |
| `FE_BE_CONNECTION.md` | CORS, API config, auth |
| `UI_VISUALIZATION.md` | Cytoscape, SVG rendering |

---

## PHASE 1: START SERVERS (5 min)

### Terminal 1: Backend
```bash
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
```

### Terminal 2: Frontend
```bash
cd /Users/namanagarwal/system/frontend-new
npm install  # if needed
npm run start
```

### Terminal 3: Verify
```bash
# Backend health
curl -s http://localhost:8001/health/live | jq .

# Frontend
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4200

# Auth
export TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')
echo "TOKEN=$TOKEN"
```

---

## PHASE 2: FIX BACKEND PIPELINE (30 min)

### 2.1 Test Complete Pipeline

```bash
# Full pipeline test script
BASE="http://localhost:8001/api/v1"
PROJECT="mvp-proj-001"

echo "=== 1. UPLOAD ==="
UPLOAD=$(curl -s -X POST "$BASE/datasets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
  -F "name=Test $(date +%s)" \
  -F "project_id=$PROJECT")
echo "$UPLOAD" | jq '{id, status}'
DATASET_ID=$(echo "$UPLOAD" | jq -r '.id')

echo "=== 2. COLUMNS ==="
curl -s "$BASE/datasets/$DATASET_ID/columns" -H "Authorization: Bearer $TOKEN" | jq '.columns[:5]'

echo "=== 3. MAPPING ==="
curl -s -X POST "$BASE/datasets/$DATASET_ID/mapping" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}'

echo "=== 4. INGEST ==="
curl -s -X POST "$BASE/datasets/$DATASET_ID/ingest" -H "Authorization: Bearer $TOKEN"

echo "=== 5. WAIT FOR READY ==="
for i in {1..30}; do
  STATUS=$(curl -s "$BASE/datasets/$DATASET_ID" -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  echo "[$i] $STATUS"
  [ "$STATUS" = "ready" ] && break
  [ "$STATUS" = "failed" ] && echo "FAILED!" && break
  sleep 2
done

echo "=== 6. DFG DISCOVERY ==="
curl -s "$BASE/visualization/$DATASET_ID/dfg" -H "Authorization: Bearer $TOKEN" | \
  jq '{nodes: (.nodes | length), edges: (.edges | length)}'

echo "=== 7. INDUCTIVE MINER ==="
DISCOVERY=$(curl -s -X POST "$BASE/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"inductive\",\"parameters\":{\"noise_threshold\":0.2}}")
echo "$DISCOVERY" | jq '{model_id, algorithm}'
MODEL_ID=$(echo "$DISCOVERY" | jq -r '.model_id // .id')

echo "=== 8. PETRI NET VIZ ==="
curl -s "$BASE/visualization/models/$MODEL_ID/petri" -H "Authorization: Bearer $TOKEN" | \
  jq '{places: (.places | length), transitions: (.transitions | length)}'

echo "=== 9. ANALYTICS ==="
curl -s "$BASE/analytics/datasets/$DATASET_ID/variants" -H "Authorization: Bearer $TOKEN" | \
  jq '{total_variants, variants: (.variants[:2])}'

curl -s "$BASE/analytics/datasets/$DATASET_ID/bottlenecks" -H "Authorization: Bearer $TOKEN" | \
  jq '{bottlenecks: (.bottlenecks[:2])}'

echo ""
echo "=== RESULTS ==="
echo "Dataset: $DATASET_ID"
echo "Model: $MODEL_ID"
```

### 2.2 Key Backend Files to Fix

```
src/api/routes/
├── datasets.py          # Upload, columns, mapping, ingest
├── discovery.py         # Algorithm execution
├── visualization.py     # DFG, Petri net, SVG generation
├── analytics.py         # Variants, bottlenecks, rework
└── conformance.py       # Fitness, precision

src/services/
├── ingestion/           # CSV/XES parsing, PM4Py log creation
├── discovery/           # Algorithm wrappers
├── visualization/       # Graph/SVG generation
└── analytics/           # Metrics calculation

src/domain/process_mining/
├── discovery/           # PM4Py algorithm calls
├── conformance/         # Conformance checking
├── visualization/       # SVG generators
└── log_utils.py         # Event log handling
```

### 2.3 Critical PM4Py Patterns

**Loading Event Log from DataFrame:**
```python
import pm4py
import pandas as pd
from pm4py.objects.conversion.log import converter

def create_event_log(df, case_col, activity_col, timestamp_col):
    # Rename to PM4Py standard names
    df = df.rename(columns={
        case_col: "case:concept:name",
        activity_col: "concept:name",
        timestamp_col: "time:timestamp"
    })
    
    # Ensure timestamp is datetime
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    
    # Sort by case and time
    df = df.sort_values(["case:concept:name", "time:timestamp"])
    
    # Convert to EventLog
    log = converter.apply(df, variant=converter.Variants.TO_EVENT_LOG)
    return log
```

**Discovery Algorithms:**
```python
import pm4py

# DFG (fastest)
dfg, start_activities, end_activities = pm4py.discover_dfg(log)

# Inductive Miner (recommended - sound)
net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2)

# Heuristics Miner (for noisy logs)
net, im, fm = pm4py.discover_petri_net_heuristics(log, dependency_threshold=0.5)

# Alpha Miner (simple/clean logs)
net, im, fm = pm4py.discover_petri_net_alpha(log)

# BPMN
bpmn = pm4py.discover_bpmn_inductive(log, noise_threshold=0.2)
```

**SVG Generation:**
```python
from pm4py.visualization.petri_net import visualizer as pn_viz
from pm4py.visualization.dfg import visualizer as dfg_viz

# Petri Net SVG
gviz = pn_viz.apply(net, im, fm)
svg_bytes = pn_viz.serialize(gviz)
svg_string = svg_bytes.decode('utf-8')

# DFG SVG
gviz = dfg_viz.apply(dfg, variant=dfg_viz.Variants.FREQUENCY)
svg_bytes = dfg_viz.serialize(gviz)
svg_string = svg_bytes.decode('utf-8')
```

---

## PHASE 3: FIX FE-BE CONNECTION (15 min)

### 3.1 Backend CORS

**File:** `src/api/main.py`
```python
from fastapi.middleware.cors import CORSMiddleware

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
    expose_headers=["Content-Disposition"],
)
```

### 3.2 Frontend API Config

**File:** `src/services/api.ts`
```typescript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,  // 60s for long operations
});

// Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401
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
```

### 3.3 Test Connection

In browser console (F12):
```javascript
fetch('http://localhost:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'analyst@example.com', password: 'TestPass123' })
}).then(r => r.json()).then(console.log);
```

---

## PHASE 4: FIX FRONTEND VISUALIZATION (20 min)

### 4.1 Install Dependencies

```bash
cd /Users/namanagarwal/system/frontend-new
npm install cytoscape cytoscape-dagre @types/cytoscape react-zoom-pan-pinch
```

### 4.2 Visualization Service

**File:** `src/services/visualizationService.ts`
```typescript
import { api } from './api';

export interface DFGData {
  nodes: Array<{ id: string; label: string; frequency: number; type?: string }>;
  edges: Array<{ source: string; target: string; value: number }>;
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
}

export interface PetriNetData {
  places: Array<{ id: string; tokens: number }>;
  transitions: Array<{ id: string; label: string }>;
  arcs: Array<{ source: string; target: string }>;
}

export const visualizationService = {
  // DFG as JSON (for Cytoscape)
  getDFG: async (datasetId: string): Promise<DFGData> => {
    const response = await api.get(`/visualization/${datasetId}/dfg`);
    return response.data;
  },

  // DFG as SVG
  getDFGSvg: async (datasetId: string): Promise<string> => {
    const response = await api.get(`/visualization/${datasetId}/dfg/svg`);
    return response.data;
  },

  // Petri Net as JSON
  getPetriNet: async (modelId: string): Promise<PetriNetData> => {
    const response = await api.get(`/visualization/models/${modelId}/petri`);
    return response.data;
  },

  // Petri Net as SVG
  getPetriNetSvg: async (modelId: string): Promise<string> => {
    const response = await api.get(`/visualization/models/${modelId}/svg`);
    return response.data;
  },

  // Explorer data (combined view)
  getExplorerData: async (datasetId: string) => {
    const response = await api.get(`/visualization/${datasetId}/explorer-data`);
    return response.data;
  }
};
```

### 4.3 Process Map Component (Cytoscape)

**File:** `src/components/ProcessMap/ProcessMap.tsx`
```typescript
import React, { useEffect, useRef } from 'react';
import cytoscape, { Core } from 'cytoscape';
import dagre from 'cytoscape-dagre';

cytoscape.use(dagre);

interface Props {
  nodes: Array<{ id: string; label: string; frequency?: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
  onNodeClick?: (nodeId: string) => void;
}

export const ProcessMap: React.FC<Props> = ({ nodes, edges, onNodeClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || !nodes.length) return;

    const maxFreq = Math.max(...nodes.map(n => n.frequency || 1));
    const maxEdge = Math.max(...edges.map(e => e.value || 1));

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map(n => ({
          data: { id: n.id, label: `${n.label}\n(${n.frequency || 0})`, frequency: n.frequency || 0 }
        })),
        ...edges.map(e => ({
          data: { id: `${e.source}->${e.target}`, source: e.source, target: e.target, value: e.value }
        }))
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#4A90D9',
            'label': 'data(label)',
            'text-valign': 'center',
            'color': '#fff',
            'text-outline-width': 2,
            'text-outline-color': '#4A90D9',
            'font-size': '11px',
            'text-wrap': 'wrap',
            'width': `mapData(frequency, 0, ${maxFreq}, 40, 80)`,
            'height': `mapData(frequency, 0, ${maxFreq}, 40, 80)`,
          }
        },
        {
          selector: 'edge',
          style: {
            'width': `mapData(value, 0, ${maxEdge}, 1, 6)`,
            'line-color': '#95A5A6',
            'target-arrow-color': '#95A5A6',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(value)',
            'font-size': '9px',
          }
        }
      ],
      layout: { name: 'dagre', rankDir: 'LR', nodeSep: 60, rankSep: 100 }
    });

    if (onNodeClick) {
      cyRef.current.on('tap', 'node', (e) => onNodeClick(e.target.id()));
    }

    return () => { cyRef.current?.destroy(); };
  }, [nodes, edges, onNodeClick]);

  return <div ref={containerRef} style={{ width: '100%', height: '500px', border: '1px solid #ddd' }} />;
};
```

### 4.4 SVG Viewer Component

**File:** `src/components/SVGViewer/SVGViewer.tsx`
```typescript
import React from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';

interface Props {
  svg: string;
}

export const SVGViewer: React.FC<Props> = ({ svg }) => {
  return (
    <div style={{ border: '1px solid #ddd', background: '#fafafa' }}>
      <TransformWrapper>
        <TransformComponent>
          <div dangerouslySetInnerHTML={{ __html: svg }} />
        </TransformComponent>
      </TransformWrapper>
    </div>
  );
};
```

### 4.5 Explorer Page

**File:** `src/pages/Explorer/Explorer.tsx`
```typescript
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ProcessMap } from '../../components/ProcessMap/ProcessMap';
import { SVGViewer } from '../../components/SVGViewer/SVGViewer';
import { visualizationService, DFGData } from '../../services/visualizationService';

export const Explorer: React.FC = () => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [viewMode, setViewMode] = useState<'graph' | 'svg'>('graph');
  const [dfgData, setDfgData] = useState<DFGData | null>(null);
  const [svgData, setSvgData] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) return;
    
    const load = async () => {
      try {
        setLoading(true);
        const [dfg, svg] = await Promise.all([
          visualizationService.getDFG(datasetId),
          visualizationService.getDFGSvg(datasetId)
        ]);
        setDfgData(dfg);
        setSvgData(svg);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [datasetId]);

  if (loading) return <div>Loading process map...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="explorer">
      <header>
        <h1>Process Explorer</h1>
        <div>
          <button onClick={() => setViewMode('graph')} disabled={viewMode === 'graph'}>
            Interactive Graph
          </button>
          <button onClick={() => setViewMode('svg')} disabled={viewMode === 'svg'}>
            SVG View
          </button>
        </div>
        {dfgData && (
          <span>{dfgData.nodes.length} activities, {dfgData.edges.length} transitions</span>
        )}
      </header>
      
      <main>
        {viewMode === 'graph' && dfgData && (
          <ProcessMap nodes={dfgData.nodes} edges={dfgData.edges} />
        )}
        {viewMode === 'svg' && svgData && (
          <SVGViewer svg={svgData} />
        )}
      </main>
    </div>
  );
};
```

---

## PHASE 5: FULL UI TEST (10 min)

### Manual Test Checklist

Open http://localhost:4200 and test:

- [ ] **Login:** `analyst@example.com` / `TestPass123` → Redirects to workspace
- [ ] **Workspace:** Shows projects list
- [ ] **Upload:** 
  - [ ] Drag & drop CSV file
  - [ ] Column detection shows columns
  - [ ] Map case_id, activity, timestamp
  - [ ] Click "Start Import"
  - [ ] See progress indicator
  - [ ] Status becomes "Ready"
- [ ] **Explorer:**
  - [ ] Process map renders with nodes
  - [ ] Edges visible between nodes
  - [ ] Can zoom/pan
  - [ ] Node click works
  - [ ] SVG view toggle works
- [ ] **Discovery:**
  - [ ] Algorithm dropdown shows options
  - [ ] Can run Inductive Miner
  - [ ] Can run Heuristics Miner
  - [ ] Results display
- [ ] **Analytics:**
  - [ ] Variants list shows
  - [ ] Bottlenecks display
  - [ ] Charts render
- [ ] **Console:** No red errors (F12)

---

## PHASE 6: VERIFICATION SCRIPT

Save and run this complete verification:

```bash
#!/bin/bash
# save as verify_mvp.sh

set -e
BASE="http://localhost:8001/api/v1"
PASS=0
FAIL=0

check() {
  if [ "$1" = "0" ]; then
    echo "✅ $2"
    PASS=$((PASS+1))
  else
    echo "❌ $2"
    FAIL=$((FAIL+1))
  fi
}

echo "=== MVP VERIFICATION ==="
echo ""

# 1. Auth
TOKEN=$(curl -s -X POST "$BASE/auth/login" -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token // empty')
[ -n "$TOKEN" ]; check $? "Auth login"

# 2. Upload
DATASET_ID=$(curl -s -X POST "$BASE/datasets/" -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
  -F "name=Verify" -F "project_id=mvp-proj-001" | jq -r '.id // empty')
[ -n "$DATASET_ID" ]; check $? "Dataset upload"

# 3. Columns
COLS=$(curl -s "$BASE/datasets/$DATASET_ID/columns" -H "Authorization: Bearer $TOKEN" | jq '.columns | length')
[ "$COLS" -gt 0 ]; check $? "Column detection ($COLS columns)"

# 4. Mapping
curl -s -X POST "$BASE/datasets/$DATASET_ID/mapping" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}' > /dev/null
check $? "Column mapping"

# 5. Ingest
curl -s -X POST "$BASE/datasets/$DATASET_ID/ingest" -H "Authorization: Bearer $TOKEN" > /dev/null
for i in {1..30}; do
  STATUS=$(curl -s "$BASE/datasets/$DATASET_ID" -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  [ "$STATUS" = "ready" ] && break
  sleep 1
done
[ "$STATUS" = "ready" ]; check $? "Ingestion (status: $STATUS)"

# 6. DFG
NODES=$(curl -s "$BASE/visualization/$DATASET_ID/dfg" -H "Authorization: Bearer $TOKEN" | jq '.nodes | length')
[ "$NODES" -gt 0 ]; check $? "DFG visualization ($NODES nodes)"

# 7. DFG SVG
SVG=$(curl -s "$BASE/visualization/$DATASET_ID/dfg/svg" -H "Authorization: Bearer $TOKEN" | head -c 50)
[[ "$SVG" == *"<"* ]]; check $? "DFG SVG generation"

# 8. Inductive Miner
MODEL_ID=$(curl -s -X POST "$BASE/discovery/discover" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"inductive\"}" | jq -r '.model_id // .id // empty')
[ -n "$MODEL_ID" ]; check $? "Inductive Miner"

# 9. Heuristics Miner
HEUR=$(curl -s -X POST "$BASE/discovery/discover" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"heuristic\"}" | jq -r '.model_id // .id // empty')
[ -n "$HEUR" ]; check $? "Heuristics Miner"

# 10. Variants
VARIANTS=$(curl -s "$BASE/analytics/datasets/$DATASET_ID/variants" -H "Authorization: Bearer $TOKEN" | jq '.variants | length')
[ "$VARIANTS" -gt 0 ]; check $? "Variants analysis ($VARIANTS variants)"

# 11. Bottlenecks
BOTTLENECKS=$(curl -s "$BASE/analytics/datasets/$DATASET_ID/bottlenecks" -H "Authorization: Bearer $TOKEN" | jq '.bottlenecks | length')
[ "$BOTTLENECKS" -gt 0 ]; check $? "Bottleneck detection ($BOTTLENECKS found)"

# 12. Petri Net
PLACES=$(curl -s "$BASE/visualization/models/$MODEL_ID/petri" -H "Authorization: Bearer $TOKEN" | jq '.places | length // 0')
[ "$PLACES" -gt 0 ]; check $? "Petri Net visualization ($PLACES places)"

echo ""
echo "=== RESULTS ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "🎉 MVP COMPLETE! All checks passed."
  exit 0
else
  echo "⚠️  Some checks failed. Fix issues and re-run."
  exit 1
fi
```

---

## DONE CHECKLIST

### Backend ✅
- [ ] Health endpoints work
- [ ] Auth login returns token
- [ ] Dataset upload creates record
- [ ] Column detection returns columns
- [ ] Column mapping saves
- [ ] Ingestion completes to "ready"
- [ ] DFG discovery works
- [ ] Inductive Miner works
- [ ] Heuristics Miner works
- [ ] Petri Net serialization works
- [ ] SVG generation works
- [ ] Variants analysis works
- [ ] Bottleneck detection works

### Frontend ✅
- [ ] Login page works
- [ ] Token stored in localStorage
- [ ] Upload wizard complete
- [ ] Process map renders (Cytoscape)
- [ ] SVG view works
- [ ] Analytics page displays
- [ ] No console errors

### Integration ✅
- [ ] No CORS errors
- [ ] All API calls succeed
- [ ] Full user journey works in browser

---

## SUCCESS 🎉

When you can:
1. Open http://localhost:4200
2. Login with test credentials
3. Upload CSV → Map columns → See process map
4. Switch between graph and SVG view
5. Run different discovery algorithms
6. View variants and bottlenecks
7. All without errors

**The MVP is COMPLETE!**

```bash
git add .
git commit -m "feat: MVP complete - full process mining pipeline working

- Data ingestion (CSV upload, column mapping, PM4Py log creation)
- Process discovery (DFG, Alpha, Heuristic, Inductive miners)
- Visualization (Cytoscape graphs, PM4Py SVG generation)
- Analytics (variants, bottlenecks, rework, cycle time)
- Frontend UI (upload wizard, process explorer, analytics dashboard)
- Full FE-BE integration with CORS and auth"
```
