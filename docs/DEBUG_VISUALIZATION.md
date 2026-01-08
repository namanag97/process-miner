# 🔍 DEBUG: Visualization Not Showing

**Problem:** Data uploads but Explorer page shows nothing.

**This guide will find the ACTUAL issue, not theoretical fixes.**

---

## STEP 1: IDENTIFY WHERE IT BREAKS

### 1.1 Check Backend Returns Data

```bash
# Get auth token
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')

# List datasets - find one with status "ready"
curl -s "http://localhost:8001/api/v1/datasets/" \
  -H "Authorization: Bearer $TOKEN" | jq '.items[] | {id, name, status}'
```

**Copy a dataset ID that has status "ready":**
```bash
DATASET_ID="<paste_ready_dataset_id_here>"
```

### 1.2 Test Visualization Endpoint Directly

```bash
# Test DFG endpoint
echo "=== DFG Endpoint ==="
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq .

# What do you see?
# A) {"nodes": [...], "edges": [...]}  → Backend works, problem is frontend
# B) {"detail": "..."}                 → Backend error, fix backend first
# C) Empty response or error           → Endpoint broken
```

### 1.3 Check Browser Network Tab

1. Open http://localhost:4200
2. Press F12 → Network tab
3. Navigate to Explorer page with your dataset
4. Look for request to `/visualization/{id}/dfg`

**What do you see?**
- ❌ No request made → Frontend not calling API
- ❌ Request returns 401 → Auth token issue
- ❌ Request returns 404 → Wrong endpoint URL
- ❌ Request returns 500 → Backend error
- ❌ Request returns 200 but empty → Backend returns no data
- ✅ Request returns 200 with data → Problem is rendering

### 1.4 Check Browser Console

Press F12 → Console tab. Look for:
- Red errors (JavaScript exceptions)
- Yellow warnings
- Any message when Explorer loads

**Common errors:**
- `Cannot read property 'map' of undefined` → Data not in expected format
- `cytoscape is not defined` → Library not installed
- `Container has no height` → CSS issue

---

## STEP 2: DIAGNOSE THE SPECIFIC ISSUE

### Issue A: Backend Returns No Data

If curl to `/visualization/{id}/dfg` returns empty or error:

```bash
# Check dataset status
curl -s "http://localhost:8001/api/v1/datasets/$DATASET_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '{status, event_count, error_message}'
```

**If status is NOT "ready":**
- `pending/uploaded` → Ingestion never started
- `processing` → Still ingesting, wait
- `failed` → Check error_message

**If status IS "ready" but no visualization:**

Check if the visualization endpoint exists:
```bash
# List all routes
curl -s "http://localhost:8001/openapi.json" | jq '.paths | keys | map(select(contains("visualization")))'
```

**Backend file to check:** `src/api/routes/visualization.py`

---

### Issue B: Frontend Not Calling API

If Network tab shows no request to visualization endpoint:

**Find the Explorer page:**
```bash
cd /Users/namanagarwal/system/frontend-new
find src -name "*[Ee]xplorer*" -o -name "*[Pp]rocess*[Mm]ap*" | head -10
```

**Check what the Explorer component does:**
```bash
# Look at the main explorer file
cat src/pages/Explorer/Explorer.tsx 2>/dev/null || \
cat src/pages/Explorer/index.tsx 2>/dev/null || \
cat src/components/Explorer/Explorer.tsx 2>/dev/null
```

**Look for:**
1. Does it have a `useEffect` that fetches data?
2. Does it use the correct API endpoint?
3. Does it get the dataset ID from URL params?

**Common problems:**
```typescript
// WRONG: Hardcoded or wrong ID
const datasetId = "some-hardcoded-id";

// RIGHT: From URL params
const { datasetId } = useParams();

// WRONG: Wrong endpoint
api.get(`/datasets/${datasetId}/visualization`)

// RIGHT: Correct endpoint
api.get(`/visualization/${datasetId}/dfg`)
```

---

### Issue C: Data Fetched But Not Rendered

If Network shows 200 with data, but nothing displays:

**Check the response format:**
```bash
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq 'keys'
```

**Expected keys:** `["nodes", "edges", "start_activities", "end_activities"]`

**Check frontend expects same format:**
```bash
cd /Users/namanagarwal/system/frontend-new
grep -r "nodes\|edges" src/pages/Explorer/ --include="*.tsx" | head -10
```

**Common mismatches:**
```typescript
// Backend returns:
{ "nodes": [...], "edges": [...] }

// But frontend expects:
{ "data": { "nodes": [...] } }  // WRONG - nested differently
{ "activities": [...], "flows": [...] }  // WRONG - different names
```

---

### Issue D: Cytoscape Not Rendering

If data is correct but graph doesn't show:

**Check Cytoscape is installed:**
```bash
cd /Users/namanagarwal/system/frontend-new
grep "cytoscape" package.json
```

If missing:
```bash
npm install cytoscape cytoscape-dagre @types/cytoscape
```

**Check container has dimensions:**
```typescript
// The container MUST have explicit height
<div ref={containerRef} style={{ width: '100%', height: '500px' }} />

// NOT this (zero height):
<div ref={containerRef} style={{ width: '100%' }} />
<div ref={containerRef} className="graph-container" />  // Unless CSS sets height
```

**Check Cytoscape initialization:**
```typescript
// Must check container exists
useEffect(() => {
  if (!containerRef.current) {
    console.log("Container not ready");  // Add this debug
    return;
  }
  if (!nodes || nodes.length === 0) {
    console.log("No nodes to render");  // Add this debug
    return;
  }
  console.log("Initializing cytoscape with", nodes.length, "nodes");  // Debug
  // ... cytoscape code
}, [nodes, edges]);
```

---

## STEP 3: APPLY THE FIX

### Fix A: Backend Visualization Endpoint Missing/Broken

**File:** `src/api/routes/visualization.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import pm4py

router = APIRouter(prefix="/visualization", tags=["visualization"])

@router.get("/{dataset_id}/dfg")
async def get_dfg(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get DFG as JSON for frontend rendering."""
    # 1. Get dataset
    dataset = await dataset_repository.get(db, dataset_id)
    if not dataset:
        raise HTTPException(404, f"Dataset {dataset_id} not found")
    if dataset.status != "ready":
        raise HTTPException(400, f"Dataset not ready: {dataset.status}")
    
    # 2. Load event log
    log = load_event_log(dataset)  # You need this function
    
    # 3. Discover DFG
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    
    # 4. Get activity frequencies
    from pm4py.statistics.attributes.log.get import get_attribute_values
    activity_freq = get_attribute_values(log, "concept:name")
    
    # 5. Build response
    nodes = [
        {"id": act, "label": act, "frequency": freq}
        for act, freq in activity_freq.items()
    ]
    
    edges = [
        {"source": src, "target": tgt, "value": count}
        for (src, tgt), count in dfg.items()
    ]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "start_activities": dict(start_activities),
        "end_activities": dict(end_activities)
    }
```

**Make sure router is registered in `main.py`:**
```python
from api.routes import visualization
app.include_router(visualization.router, prefix="/api/v1")
```

---

### Fix B: Frontend Not Fetching Data

**File:** `src/pages/Explorer/Explorer.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';

interface DFGData {
  nodes: Array<{ id: string; label: string; frequency: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
}

export const Explorer: React.FC = () => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [data, setData] = useState<DFGData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log("Explorer mounted, datasetId:", datasetId);  // DEBUG
    
    if (!datasetId) {
      setError("No dataset ID provided");
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        console.log("Fetching DFG for:", datasetId);  // DEBUG
        const response = await api.get(`/visualization/${datasetId}/dfg`);
        console.log("DFG response:", response.data);  // DEBUG
        setData(response.data);
      } catch (err: any) {
        console.error("DFG fetch error:", err);  // DEBUG
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [datasetId]);

  // Show loading/error states
  if (loading) return <div>Loading visualization...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data available</div>;
  if (data.nodes.length === 0) return <div>No activities found in dataset</div>;

  return (
    <div>
      <h1>Process Explorer</h1>
      <p>{data.nodes.length} activities, {data.edges.length} transitions</p>
      {/* Render graph here */}
      <ProcessMap nodes={data.nodes} edges={data.edges} />
    </div>
  );
};
```

---

### Fix C: Cytoscape Not Rendering

**File:** `src/components/ProcessMap/ProcessMap.tsx`

```typescript
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register layout extension ONCE at module level
cytoscape.use(dagre);

interface ProcessMapProps {
  nodes: Array<{ id: string; label: string; frequency?: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
}

export const ProcessMap: React.FC<ProcessMapProps> = ({ nodes, edges }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log("ProcessMap useEffect, container:", containerRef.current);  // DEBUG
    console.log("Nodes:", nodes.length, "Edges:", edges.length);  // DEBUG

    // Guard: need container
    if (!containerRef.current) {
      console.error("Container ref not available");
      return;
    }

    // Guard: need data
    if (!nodes || nodes.length === 0) {
      console.warn("No nodes to render");
      return;
    }

    // Build elements
    const elements = [
      ...nodes.map(n => ({
        data: { 
          id: n.id, 
          label: n.label || n.id,
          frequency: n.frequency || 1 
        }
      })),
      ...edges.map(e => ({
        data: {
          id: `${e.source}->${e.target}`,
          source: e.source,
          target: e.target,
          value: e.value
        }
      }))
    ];

    console.log("Creating cytoscape with elements:", elements.length);  // DEBUG

    // Create cytoscape instance
    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
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
            'width': 60,
            'height': 60,
            'font-size': '10px'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#999',
            'target-arrow-color': '#999',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(value)',
            'font-size': '8px'
          }
        }
      ],
      layout: {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 50,
        rankSep: 100
      }
    });

    console.log("Cytoscape created, nodes:", cy.nodes().length);  // DEBUG

    // Cleanup on unmount
    return () => {
      cy.destroy();
    };
  }, [nodes, edges]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        height: '500px',  // MUST have explicit height
        border: '1px solid #ccc',
        background: '#fafafa'
      }} 
    />
  );
};

export default ProcessMap;
```

---

### Fix D: Route Not Configured

Check frontend routes include Explorer:

**File:** `src/App.tsx` or `src/routes/index.tsx`

```typescript
import { Explorer } from './pages/Explorer/Explorer';

// In your routes:
<Route path="/workspace/:workspaceId/data/:datasetId/explorer" element={<Explorer />} />
// OR
<Route path="/explorer/:datasetId" element={<Explorer />} />
```

**Check the URL matches:**
- If route is `/explorer/:datasetId`, URL should be `/explorer/abc123`
- If route is `/workspace/:wid/data/:did/explorer`, URL should be `/workspace/x/data/abc123/explorer`

---

## STEP 4: VERIFY THE FIX

### 4.1 Test Backend

```bash
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq '{node_count: (.nodes | length), edge_count: (.edges | length)}'
```

**Expected:** `{"node_count": 5, "edge_count": 8}` (some positive numbers)

### 4.2 Test Frontend

1. Open http://localhost:4200
2. Navigate to Explorer page
3. Open browser console (F12)
4. Look for debug messages:
   - "Explorer mounted, datasetId: xxx"
   - "Fetching DFG for: xxx"
   - "DFG response: {...}"
   - "ProcessMap useEffect, container: <div>"
   - "Creating cytoscape with elements: 13"
   - "Cytoscape created, nodes: 5"

### 4.3 Visual Confirmation

You should see:
- Nodes (circles/rectangles) representing activities
- Edges (arrows) connecting them
- Labels on nodes and edges

---

## QUICK DIAGNOSTIC CHECKLIST

Run through this to find the issue:

| Check | Command/Action | Expected |
|-------|----------------|----------|
| Backend running? | `curl localhost:8001/health/live` | `{"status": "healthy"}` |
| Dataset ready? | `curl .../datasets/{id}` | `status: "ready"` |
| DFG endpoint works? | `curl .../visualization/{id}/dfg` | `{nodes: [...]}` |
| Frontend running? | Open localhost:4200 | Page loads |
| Network request made? | F12 → Network | Request to `/visualization` |
| Request succeeds? | Check status code | 200 |
| Data in response? | Check response body | Has nodes/edges |
| Console errors? | F12 → Console | No red errors |
| Container has height? | Inspect element | height > 0 |
| Cytoscape initialized? | Console logs | "Cytoscape created" |

---

## STILL NOT WORKING?

If you've gone through everything and it still doesn't work:

1. **Share the exact error message** from console
2. **Share the Network tab response** for the visualization request
3. **Share the relevant component code** (Explorer.tsx, ProcessMap.tsx)

The issue is in one of these places:
- Backend not returning data
- Frontend not fetching data
- Frontend not rendering data
- CSS hiding the visualization

**Don't guess - trace the data flow from backend → frontend → screen.**
