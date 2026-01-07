# Process Mining MVP - Complete Fix Protocol

**MISSION:** Get the full process mining pipeline working end-to-end.

```
┌────────────────────────────────────────────────────────────────────────────┐
│  THE PIPELINE (All Must Work)                                              │
│                                                                            │
│  INGESTION        DISCOVERY           VISUALIZATION       ANALYTICS       │
│  ─────────        ─────────           ─────────────       ─────────       │
│  Upload CSV  →    Run Algorithm  →    Generate SVG   →    Bottlenecks     │
│  Map Columns →    (DFG/Inductive/     Petri Net View      Variants        │
│  Transform   →     Alpha/Heuristic)   DFG View            Rework          │
│  Status=READY     Store Model         BPMN View           Cycle Time      │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 0: ENVIRONMENT CHECK

```bash
# Terminal 1: Start backend
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Terminal 2: Verify
curl -s http://localhost:8001/health/live | jq .

# Get auth token
export TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')
echo "TOKEN=$TOKEN"

# Check PM4Py
cd /Users/namanagarwal/system/backend
.venv/bin/python -c "
import pm4py
print(f'PM4Py version: {pm4py.__version__}')
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.petri_net import visualizer as pn_viz
from pm4py.visualization.dfg import visualizer as dfg_viz
print('All PM4Py imports OK')
"

# Check GraphViz (needed for visualization)
which dot || echo "MISSING: Install graphviz (brew install graphviz)"
```

---

## PHASE 1: FIX INGESTION

### Test Command
```bash
PROJECT_ID="mvp-proj-001"

# Upload
UPLOAD=$(curl -s -X POST "http://localhost:8001/api/v1/datasets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
  -F "name=Test $(date +%s)" \
  -F "project_id=$PROJECT_ID")
echo "$UPLOAD" | jq .
export DATASET_ID=$(echo "$UPLOAD" | jq -r '.id // empty')
echo "DATASET_ID=$DATASET_ID"

# Column detection
curl -s "http://localhost:8001/api/v1/datasets/$DATASET_ID/columns" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Mapping
curl -s -X POST "http://localhost:8001/api/v1/datasets/$DATASET_ID/mapping" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}' | jq .

# Ingest
curl -s -X POST "http://localhost:8001/api/v1/datasets/$DATASET_ID/ingest" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Wait for ready
for i in {1..20}; do
  STATUS=$(curl -s "http://localhost:8001/api/v1/datasets/$DATASET_ID" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  echo "[$i] Status: $STATUS"
  [ "$STATUS" = "ready" ] && echo "✅ INGESTION OK" && break
  [ "$STATUS" = "failed" ] && echo "❌ INGESTION FAILED" && break
  sleep 2
done
```

### Key Files for Ingestion
```
src/api/routes/datasets.py          # Upload endpoint
src/services/ingestion/              # Ingestion service
src/domain/ingestion/                # Core ingestion logic
src/infrastructure/repositories/     # Database operations
```

### Common Ingestion Fixes
```python
# Fix: PM4Py column names
df = df.rename(columns={
    mapping.case_id_column: "case:concept:name",
    mapping.activity_column: "concept:name",
    mapping.timestamp_column: "time:timestamp"
})

# Fix: Timestamp parsing
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

# Fix: Create event log from DataFrame
from pm4py.objects.conversion.log import converter
log = converter.apply(df, variant=converter.Variants.TO_EVENT_LOG)
```

---

## PHASE 2: FIX DISCOVERY

### Test Command (Requires READY dataset from Phase 1)
```bash
# List available miners
curl -s "http://localhost:8001/api/v1/discovery/miners" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {id, name}'

# Run DFG discovery
echo "=== DFG Discovery ==="
curl -s -X POST "http://localhost:8001/api/v1/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"dfg\"}" | jq .

# Run Inductive Miner
echo "=== Inductive Miner ==="
DISCOVERY=$(curl -s -X POST "http://localhost:8001/api/v1/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"inductive\",\"parameters\":{\"noise_threshold\":0.2}}")
echo "$DISCOVERY" | jq .
export MODEL_ID=$(echo "$DISCOVERY" | jq -r '.model_id // .id // empty')
echo "MODEL_ID=$MODEL_ID"

# Run Alpha Miner
echo "=== Alpha Miner ==="
curl -s -X POST "http://localhost:8001/api/v1/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"alpha\"}" | jq .

# Run Heuristics Miner
echo "=== Heuristics Miner ==="
curl -s -X POST "http://localhost:8001/api/v1/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"heuristic\",\"parameters\":{\"dependency_threshold\":0.5}}" | jq .

# List discovered models
curl -s "http://localhost:8001/api/v1/discovery/models?dataset_id=$DATASET_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {id, algorithm, model_type}'
```

### Key Files for Discovery
```
src/api/routes/discovery.py              # Discovery endpoints
src/services/discovery/                   # Discovery service
src/domain/process_mining/discovery/      # PM4Py algorithm wrappers
src/domain/process_mining/models/         # Model serialization
```

### PM4Py Discovery Code (What Should Run)
```python
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter

# Load log from DataFrame
def load_event_log(df, case_col, activity_col, timestamp_col):
    df = df.rename(columns={
        case_col: "case:concept:name",
        activity_col: "concept:name",
        timestamp_col: "time:timestamp"
    })
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    log = converter.apply(df, variant=converter.Variants.TO_EVENT_LOG)
    return log

# DFG Discovery
def discover_dfg(log):
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    return {"dfg": dfg, "start": start_activities, "end": end_activities}

# Inductive Miner
def discover_inductive(log, noise_threshold=0.2):
    net, im, fm = pm4py.discover_petri_net_inductive(
        log, 
        noise_threshold=noise_threshold
    )
    return net, im, fm

# Alpha Miner
def discover_alpha(log):
    net, im, fm = pm4py.discover_petri_net_alpha(log)
    return net, im, fm

# Heuristics Miner
def discover_heuristics(log, dependency_threshold=0.5, and_threshold=0.65):
    net, im, fm = pm4py.discover_petri_net_heuristics(
        log,
        dependency_threshold=dependency_threshold,
        and_threshold=and_threshold
    )
    return net, im, fm
```

### Common Discovery Fixes
```python
# Fix: Algorithm not found
# Check algorithm ID matches what's registered in discovery service

# Fix: Log format error
# Ensure log is EventLog type, not DataFrame
from pm4py.objects.log.obj import EventLog
if not isinstance(log, EventLog):
    log = converter.apply(df, variant=converter.Variants.TO_EVENT_LOG)

# Fix: Empty log
if len(log) == 0:
    raise ValueError("Event log is empty - check ingestion")

# Fix: Missing case/activity
# Ensure all required columns present before discovery
```

---

## PHASE 3: FIX VISUALIZATION

### Test Command
```bash
# DFG Visualization (JSON for frontend)
echo "=== DFG JSON ==="
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq '{nodes: .nodes[:3], edges: .edges[:3], node_count: (.nodes | length), edge_count: (.edges | length)}'

# DFG as SVG
echo "=== DFG SVG ==="
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg/svg" \
  -H "Authorization: Bearer $TOKEN" | head -c 500
echo "..."

# Petri Net Visualization (requires MODEL_ID from discovery)
echo "=== Petri Net ==="
curl -s "http://localhost:8001/api/v1/visualization/models/$MODEL_ID/petri" \
  -H "Authorization: Bearer $TOKEN" | jq '{places: (.places[:3]), transitions: (.transitions[:3])}'

# Petri Net as SVG
echo "=== Petri Net SVG ==="
curl -s "http://localhost:8001/api/v1/visualization/models/$MODEL_ID/svg" \
  -H "Authorization: Bearer $TOKEN" | head -c 500
echo "..."

# Explorer data (for frontend graph)
echo "=== Explorer Data ==="
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/explorer-data" \
  -H "Authorization: Bearer $TOKEN" | jq '{nodes: (.nodes[:2]), edges: (.edges[:2])}'
```

### Key Files for Visualization
```
src/api/routes/visualization.py           # Visualization endpoints
src/services/visualization/               # Visualization service
src/domain/process_mining/visualization/  # PM4Py visualization wrappers
```

### PM4Py Visualization Code (What Should Run)
```python
import pm4py
from pm4py.visualization.petri_net import visualizer as pn_viz
from pm4py.visualization.dfg import visualizer as dfg_viz

# DFG to SVG
def dfg_to_svg(dfg, start_activities, end_activities):
    gviz = dfg_viz.apply(
        dfg, 
        activities_count=start_activities,  # or separate count dict
        variant=dfg_viz.Variants.FREQUENCY
    )
    svg_string = dfg_viz.serialize(gviz).decode('utf-8')
    return svg_string

# Petri Net to SVG
def petri_net_to_svg(net, im, fm):
    gviz = pn_viz.apply(net, im, fm)
    svg_string = pn_viz.serialize(gviz).decode('utf-8')
    return svg_string

# DFG to JSON (for frontend rendering)
def dfg_to_json(dfg, start_activities, end_activities):
    nodes = set()
    edges = []
    
    for (source, target), count in dfg.items():
        nodes.add(source)
        nodes.add(target)
        edges.append({
            "source": source,
            "target": target,
            "value": count
        })
    
    return {
        "nodes": [{"id": n, "label": n} for n in nodes],
        "edges": edges,
        "start_activities": dict(start_activities),
        "end_activities": dict(end_activities)
    }

# Petri Net to JSON
def petri_net_to_json(net, im, fm):
    places = [{"id": p.name, "tokens": 1 if p in im else 0} for p in net.places]
    transitions = [{"id": t.name, "label": t.label} for t in net.transitions]
    arcs = []
    for arc in net.arcs:
        arcs.append({
            "source": arc.source.name,
            "target": arc.target.name
        })
    return {"places": places, "transitions": transitions, "arcs": arcs}
```

### Common Visualization Fixes
```python
# Fix: GraphViz not installed
# Run: brew install graphviz (macOS) or apt install graphviz (Linux)

# Fix: SVG generation fails
# Check if model was properly discovered first
if net is None:
    raise ValueError("No Petri net model found")

# Fix: Empty visualization
# Ensure DFG/model has data
if len(dfg) == 0:
    raise ValueError("DFG is empty - check discovery")

# Fix: Encoding issues
svg_string = gviz_bytes.decode('utf-8')  # Ensure proper decoding
```

---

## PHASE 4: FIX ANALYTICS

### Test Command
```bash
# Bottlenecks
echo "=== Bottlenecks ==="
curl -s "http://localhost:8001/api/v1/analytics/datasets/$DATASET_ID/bottlenecks" \
  -H "Authorization: Bearer $TOKEN" | jq '.bottlenecks[:3]'

# Variants
echo "=== Variants ==="
curl -s "http://localhost:8001/api/v1/analytics/datasets/$DATASET_ID/variants" \
  -H "Authorization: Bearer $TOKEN" | jq '{total: .total_variants, variants: .variants[:3]}'

# Cycle Time
echo "=== Cycle Time ==="
curl -s "http://localhost:8001/api/v1/analytics/datasets/$DATASET_ID/cycle-time" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Throughput
echo "=== Throughput ==="
curl -s "http://localhost:8001/api/v1/analytics/datasets/$DATASET_ID/throughput" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Rework
echo "=== Rework ==="
curl -s "http://localhost:8001/api/v1/analytics/datasets/$DATASET_ID/rework" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Key Files for Analytics
```
src/api/routes/analytics.py              # Analytics endpoints
src/services/analytics/                   # Analytics service
src/domain/analytics/                     # Analytics calculations
```

### Analytics Calculations (What Should Run)
```python
import pm4py
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.algo.filtering.log.variants import variants_filter

# Get variants
def get_variants(log):
    variants = variants_filter.get_variants(log)
    result = []
    for variant, traces in variants.items():
        result.append({
            "variant": list(variant) if isinstance(variant, tuple) else variant,
            "count": len(traces),
            "percentage": len(traces) / len(log) * 100
        })
    return sorted(result, key=lambda x: x["count"], reverse=True)

# Get case durations (for bottleneck/cycle time)
def get_case_durations(log):
    durations = case_statistics.get_all_case_durations(log)
    return {
        "mean": sum(durations) / len(durations),
        "median": sorted(durations)[len(durations)//2],
        "min": min(durations),
        "max": max(durations)
    }

# Bottleneck detection
def get_bottlenecks(log):
    # Calculate time between activities
    from pm4py.statistics.sojourn_time.log import get as sojourn_get
    sojourn = sojourn_get.apply(log, parameters={"aggregation_measure": "mean"})
    
    bottlenecks = []
    for activity, duration in sojourn.items():
        bottlenecks.append({
            "activity": activity,
            "avg_duration": duration,
            "severity": "high" if duration > 86400 else "medium" if duration > 3600 else "low"
        })
    return sorted(bottlenecks, key=lambda x: x["avg_duration"], reverse=True)

# Rework detection
def get_rework(log):
    rework_cases = []
    for trace in log:
        activities = [event["concept:name"] for event in trace]
        if len(activities) != len(set(activities)):  # Has duplicates
            rework_cases.append({
                "case_id": trace.attributes["concept:name"],
                "repeated_activities": [a for a in set(activities) if activities.count(a) > 1]
            })
    return {
        "rework_rate": len(rework_cases) / len(log) * 100,
        "cases_with_rework": len(rework_cases),
        "examples": rework_cases[:10]
    }
```

---

## PHASE 5: FIX CONFORMANCE (Optional for MVP)

### Test Command
```bash
# Run conformance check
echo "=== Conformance Check ==="
curl -s -X POST "http://localhost:8001/api/v1/conformance/check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"model_id\":\"$MODEL_ID\"}" | jq .

# Get fitness score
echo "=== Fitness ==="
curl -s "http://localhost:8001/api/v1/conformance/quality/$DATASET_ID/$MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '{fitness, precision}'
```

### PM4Py Conformance Code
```python
import pm4py
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay

# Token-based replay
def check_conformance(log, net, im, fm):
    replayed = token_replay.apply(log, net, im, fm)
    
    fitness = sum(r["trace_fitness"] for r in replayed) / len(replayed)
    
    return {
        "fitness": fitness,
        "conforming_cases": sum(1 for r in replayed if r["trace_fitness"] == 1.0),
        "total_cases": len(replayed)
    }
```

---

## COMPLETE VERIFICATION SCRIPT

Run this to verify the full pipeline:

```bash
#!/bin/bash
set -e

BASE="http://localhost:8001/api/v1"
PROJECT="mvp-proj-001"

echo "====== MVP VERIFICATION ======"

# Auth
echo "[1/7] Authenticating..."
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')
[ -z "$TOKEN" ] && echo "❌ Auth failed" && exit 1
echo "✅ Auth OK"

# Upload
echo "[2/7] Uploading dataset..."
UPLOAD=$(curl -s -X POST "$BASE/datasets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
  -F "name=MVP Verify $(date +%s)" \
  -F "project_id=$PROJECT")
DATASET_ID=$(echo "$UPLOAD" | jq -r '.id // empty')
[ -z "$DATASET_ID" ] && echo "❌ Upload failed: $UPLOAD" && exit 1
echo "✅ Upload OK: $DATASET_ID"

# Map columns
echo "[3/7] Mapping columns..."
curl -s -X POST "$BASE/datasets/$DATASET_ID/mapping" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}' > /dev/null
echo "✅ Mapping OK"

# Ingest
echo "[4/7] Ingesting..."
curl -s -X POST "$BASE/datasets/$DATASET_ID/ingest" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

for i in {1..30}; do
  STATUS=$(curl -s "$BASE/datasets/$DATASET_ID" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  [ "$STATUS" = "ready" ] && break
  [ "$STATUS" = "failed" ] && echo "❌ Ingestion failed" && exit 1
  sleep 1
done
[ "$STATUS" != "ready" ] && echo "❌ Ingestion timeout" && exit 1
echo "✅ Ingestion OK (status: ready)"

# Discovery
echo "[5/7] Running discovery..."
DISCOVERY=$(curl -s -X POST "$BASE/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"inductive\"}")
MODEL_ID=$(echo "$DISCOVERY" | jq -r '.model_id // .id // empty')
[ -z "$MODEL_ID" ] && echo "❌ Discovery failed: $DISCOVERY" && exit 1
echo "✅ Discovery OK: $MODEL_ID"

# Visualization
echo "[6/7] Testing visualization..."
DFG=$(curl -s "$BASE/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN")
NODES=$(echo "$DFG" | jq '.nodes | length')
[ "$NODES" -lt 1 ] && echo "❌ Visualization failed: no nodes" && exit 1
echo "✅ Visualization OK ($NODES nodes)"

# Analytics
echo "[7/7] Testing analytics..."
VARIANTS=$(curl -s "$BASE/analytics/datasets/$DATASET_ID/variants" \
  -H "Authorization: Bearer $TOKEN")
VARIANT_COUNT=$(echo "$VARIANTS" | jq '.variants | length')
[ "$VARIANT_COUNT" -lt 1 ] && echo "❌ Analytics failed" && exit 1
echo "✅ Analytics OK ($VARIANT_COUNT variants)"

echo ""
echo "======================================"
echo "  ✅ MVP PIPELINE FULLY WORKING! ✅  "
echo "======================================"
echo "Dataset ID: $DATASET_ID"
echo "Model ID:   $MODEL_ID"
```

---

## KEY FILE REFERENCE

| Component | Primary Files |
|-----------|---------------|
| **Ingestion** | `src/api/routes/datasets.py`, `src/services/ingestion/`, `src/domain/ingestion/` |
| **Discovery** | `src/api/routes/discovery.py`, `src/services/discovery/`, `src/domain/process_mining/discovery/` |
| **Visualization** | `src/api/routes/visualization.py`, `src/domain/process_mining/visualization/` |
| **Analytics** | `src/api/routes/analytics.py`, `src/services/analytics/`, `src/domain/analytics/` |
| **Conformance** | `src/api/routes/conformance.py`, `src/domain/process_mining/conformance/` |
| **Models** | `src/domain/models/`, `src/infrastructure/repositories/` |
| **Config** | `src/core/config.py`, `src/api/main.py` |

---

## COMMON FIX PATTERNS

### Pattern 1: PM4Py Function Changed
```python
# Old PM4Py (< 2.5)
from pm4py.objects.log.util import dataframe_utils
log = dataframe_utils.convert_timestamp_columns_in_df(df)

# New PM4Py (2.5+)
import pm4py
df = pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')
log = pm4py.convert_to_event_log(df)
```

### Pattern 2: Async Database
```python
# Ensure await on all DB operations
async def get_dataset(db: AsyncSession, dataset_id: str):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    return result.scalar_one_or_none()
```

### Pattern 3: Model Serialization
```python
# Petri net to JSON-serializable format
def serialize_petri_net(net, im, fm):
    return {
        "places": [p.name for p in net.places],
        "transitions": [{"name": t.name, "label": t.label} for t in net.transitions],
        "arcs": [{"source": a.source.name, "target": a.target.name} for a in net.arcs],
        "initial_marking": [p.name for p in im],
        "final_marking": [p.name for p in fm]
    }
```

### Pattern 4: Error Handling
```python
from fastapi import HTTPException

async def discover_model(dataset_id: str, algorithm: str):
    dataset = await get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(404, f"Dataset {dataset_id} not found")
    if dataset.status != "ready":
        raise HTTPException(400, f"Dataset not ready: {dataset.status}")
    
    try:
        model = run_discovery(dataset, algorithm)
    except Exception as e:
        raise HTTPException(500, f"Discovery failed: {str(e)}")
    
    return model
```

---

## DONE CHECKLIST

- [ ] Auth: Login returns token
- [ ] Ingestion: Upload → Columns → Mapping → Ingest → READY
- [ ] Discovery: DFG works
- [ ] Discovery: Inductive Miner works
- [ ] Discovery: Alpha Miner works (or graceful error)
- [ ] Discovery: Heuristics Miner works
- [ ] Visualization: DFG JSON returns nodes/edges
- [ ] Visualization: DFG SVG returns valid SVG
- [ ] Visualization: Petri Net JSON works
- [ ] Visualization: Petri Net SVG works
- [ ] Analytics: Variants returns list
- [ ] Analytics: Bottlenecks returns list
- [ ] Analytics: Cycle time returns stats
- [ ] Complete verification script passes

**When all checked: Commit and celebrate! 🎉**
