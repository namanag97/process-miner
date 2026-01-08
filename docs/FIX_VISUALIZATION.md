# 🔧 FIX VISUALIZATION - Step by Step

**Problem:** Upload works, but Explorer shows nothing.

**Solution:** Trace data flow and fix where it breaks.

---

## RUN DIAGNOSTIC FIRST

```bash
chmod +x /path/to/diagnose.sh
./diagnose.sh
```

This tells you exactly where it breaks.

---

## THE DATA FLOW (Each Step Must Work)

```
1. Dataset status = "ready"         ← Ingestion complete?
         ↓
2. Backend loads event log          ← Can PM4Py read data?
         ↓
3. Backend discovers DFG            ← PM4Py working?
         ↓
4. Backend returns JSON             ← API endpoint exists?
         ↓
5. Frontend fetches JSON            ← API call made?
         ↓
6. Frontend passes to component     ← Data passed correctly?
         ↓
7. Cytoscape renders                ← Library working?
         ↓
8. User sees graph                  ← CSS not hiding it?
```

---

## FIX EACH STEP

### STEP 1: Dataset Must Be "ready"

```bash
# Check status
curl -s "http://localhost:8001/api/v1/datasets/{DATASET_ID}" \
  -H "Authorization: Bearer $TOKEN" | jq '.status'
```

**If not "ready":**
- `pending` → Run ingestion: `POST /datasets/{id}/ingest`
- `failed` → Check error, re-upload
- `processing` → Wait, then check again

---

### STEP 2: Backend Must Load Event Log

**File:** Wherever you load the log (e.g., `src/services/ingestion/log_loader.py` or `src/domain/process_mining/log_utils.py`)

```python
# Add this debug to wherever you load the event log
def load_event_log(dataset):
    print(f"Loading event log for dataset: {dataset.id}")
    print(f"  File path: {dataset.processed_path or dataset.file_path}")
    
    # Your loading code...
    import pandas as pd
    df = pd.read_parquet(dataset.processed_path)  # or CSV
    print(f"  Loaded {len(df)} rows")
    print(f"  Columns: {df.columns.tolist()}")
    
    # Convert to PM4Py
    from pm4py.objects.conversion.log import converter
    df = df.rename(columns={
        dataset.case_column: "case:concept:name",
        dataset.activity_column: "concept:name",
        dataset.timestamp_column: "time:timestamp"
    })
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    
    log = converter.apply(df, variant=converter.Variants.TO_EVENT_LOG)
    print(f"  Event log has {len(log)} traces")
    
    return log
```

---

### STEP 3: Backend Must Discover DFG

**File:** `src/api/routes/visualization.py`

```python
@router.get("/{dataset_id}/dfg")
async def get_dfg(dataset_id: str, ...):
    # Debug: Log the request
    print(f"=== DFG Request for {dataset_id} ===")
    
    # Get dataset
    dataset = await get_dataset(db, dataset_id)
    if not dataset:
        print(f"  ERROR: Dataset not found")
        raise HTTPException(404, "Dataset not found")
    
    print(f"  Dataset status: {dataset.status}")
    
    # Load log
    log = load_event_log(dataset)
    print(f"  Loaded log with {len(log)} traces")
    
    # Discover DFG
    import pm4py
    dfg, start_acts, end_acts = pm4py.discover_dfg(log)
    print(f"  DFG has {len(dfg)} edges")
    
    # Get frequencies
    from pm4py.statistics.attributes.log.get import get_attribute_values
    freq = get_attribute_values(log, "concept:name")
    print(f"  Found {len(freq)} activities")
    
    # Build response
    nodes = [{"id": a, "label": a, "frequency": f} for a, f in freq.items()]
    edges = [{"source": s, "target": t, "value": c} for (s, t), c in dfg.items()]
    
    print(f"  Returning {len(nodes)} nodes, {len(edges)} edges")
    
    return {
        "nodes": nodes,
        "edges": edges,
        "start_activities": dict(start_acts),
        "end_activities": dict(end_acts)
    }
```

**Test:**
```bash
curl -s "http://localhost:8001/api/v1/visualization/{DATASET_ID}/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq '{nodes: (.nodes | length), edges: (.edges | length)}'
```

Expected: `{"nodes": 5, "edges": 8}` (positive numbers)

---

### STEP 4: Frontend Must Fetch Data

**File:** `src/pages/Explorer/Explorer.tsx` (or similar)

```typescript
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';

export const Explorer = () => {
  const { datasetId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // DEBUG: Log what we're doing
    console.log('Explorer: datasetId =', datasetId);
    
    if (!datasetId) {
      console.error('Explorer: No datasetId!');
      setError('No dataset ID');
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        console.log('Explorer: Fetching DFG...');
        const response = await api.get(`/visualization/${datasetId}/dfg`);
        console.log('Explorer: Got response:', response.data);
        console.log('Explorer: Nodes:', response.data.nodes?.length);
        console.log('Explorer: Edges:', response.data.edges?.length);
        setData(response.data);
      } catch (err) {
        console.error('Explorer: Fetch failed:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [datasetId]);

  // Render states
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data</div>;
  if (!data.nodes?.length) return <div>No activities in dataset</div>;

  return (
    <div>
      <h1>Process Map</h1>
      <p>{data.nodes.length} activities, {data.edges.length} transitions</p>
      <ProcessMap nodes={data.nodes} edges={data.edges} />
    </div>
  );
};
```

**Check browser console (F12):**
- See "Explorer: datasetId = xxx"
- See "Explorer: Fetching DFG..."
- See "Explorer: Got response: {...}"
- See "Explorer: Nodes: 5"

---

### STEP 5: ProcessMap Must Render

**File:** `src/components/ProcessMap/ProcessMap.tsx`

```typescript
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

cytoscape.use(dagre);

export const ProcessMap = ({ nodes, edges }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    // DEBUG
    console.log('ProcessMap: Rendering');
    console.log('ProcessMap: Container =', containerRef.current);
    console.log('ProcessMap: Nodes =', nodes?.length);
    console.log('ProcessMap: Edges =', edges?.length);

    if (!containerRef.current) {
      console.error('ProcessMap: No container!');
      return;
    }

    if (!nodes || nodes.length === 0) {
      console.warn('ProcessMap: No nodes to render');
      return;
    }

    // Build elements
    const elements = [
      ...nodes.map(n => ({ 
        data: { id: n.id, label: n.label || n.id } 
      })),
      ...edges.map(e => ({ 
        data: { 
          id: `${e.source}->${e.target}`, 
          source: e.source, 
          target: e.target,
          label: String(e.value)
        } 
      }))
    ];

    console.log('ProcessMap: Creating cytoscape with', elements.length, 'elements');

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
            'color': '#fff',
            'width': 50,
            'height': 50
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
            'label': 'data(label)'
          }
        }
      ],
      layout: { name: 'dagre', rankDir: 'LR' }
    });

    console.log('ProcessMap: Cytoscape created, nodes:', cy.nodes().length);

    return () => cy.destroy();
  }, [nodes, edges]);

  // CRITICAL: Container must have explicit height
  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        height: '500px',  // ← MUST have height
        border: '2px solid red'  // ← Debug: see if container exists
      }} 
    />
  );
};
```

**Check browser console:**
- See "ProcessMap: Rendering"
- See "ProcessMap: Container = <div>"
- See "ProcessMap: Nodes = 5"
- See "ProcessMap: Creating cytoscape with 13 elements"
- See "ProcessMap: Cytoscape created, nodes: 5"

**Check the page:**
- Red border visible? Container exists
- No red border? Container not rendering / CSS issue

---

## COMMON FIXES

### Fix: "cytoscape is not defined"
```bash
cd frontend-new
npm install cytoscape cytoscape-dagre
```

### Fix: Container has zero height
```typescript
// Add explicit height
style={{ width: '100%', height: '500px' }}
```

### Fix: No datasetId in URL
Check route definition:
```typescript
// Route must capture :datasetId
<Route path="/explorer/:datasetId" element={<Explorer />} />
```

### Fix: API returns 404
Check endpoint URL matches:
```typescript
// Frontend must match backend route
api.get(`/visualization/${datasetId}/dfg`)  // Not /datasets/{id}/visualization
```

### Fix: API returns 401
Token not being sent. Check axios interceptor:
```typescript
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## VERIFY IT WORKS

1. Open browser to http://localhost:4200
2. Login
3. Navigate to Explorer page for a "ready" dataset
4. Open console (F12)
5. Should see:
   - "Explorer: Fetching DFG..."
   - "Explorer: Got response: {...}"
   - "ProcessMap: Creating cytoscape..."
   - "ProcessMap: Cytoscape created, nodes: X"
6. Should see graph with nodes and edges on screen

**Still not working?** The console logs tell you exactly where it breaks.
