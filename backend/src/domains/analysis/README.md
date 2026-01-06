# Analysis Domain

**Owner**: Process Mining & Analytics  
**Bounded Context**: Process Discovery, Conformance, Performance Analysis

## Responsibilities

- Dataset statistics and exploration
- Case and event queries
- Variant analysis
- Activity frequency analysis
- Process discovery (Alpha, Inductive, Heuristics miners)
- Conformance checking (token replay, alignments)
- Performance analytics (bottlenecks, cycle times, throughput)
- Process visualization (DFG, Petri nets, BPMN)
- Predictive analytics (next activity, remaining time)
- Organizational mining (social networks, resource handovers)
- Process simulation (what-if scenarios)
- Object-Centric Process Mining (OCEL 2.0)

## Models

| Model | Table | Description |
|-------|-------|-------------|
| `ProcessCase` | `process_cases` | Individual traces/cases |
| `ProcessEvent` | `process_events` | Events within cases |
| `ProcessModel` | `process_models` | Discovered process models |
| `ProcessModelMetrics` | - | Model quality metrics |
| `GraphCache` | `graph_cache` | Cached graph layouts |
| `Analysis` | `analyses` | Stored analysis results |
| `ConformanceResult` | `conformance_results` | Conformance checking results |
| `AnalyticsCache` | `analytics_cache` | Cached analytics computations |

## Enums

- `AnalysisType`: Types of analyses (DISCOVERY, CONFORMANCE, ENHANCEMENT, VARIANTS, BOTTLENECK)
- `AnalysisStatus`: Analysis job states (PENDING, RUNNING, COMPLETED, FAILED)

## APIs

### Core Analysis
- `GET /datasets/{id}/statistics` - Aggregate statistics
- `GET /datasets/{id}/cases` - List cases
- `GET /datasets/{id}/events` - Query events
- `GET /datasets/{id}/variants` - Process variants
- `GET /datasets/{id}/activities` - Activity statistics

### Process Discovery
- `POST /discovery/discover` - Run discovery (Alpha, Inductive, Heuristics)
- `GET /discovery/models` - List discovered models

### Conformance Checking
- `POST /conformance/check` - Run conformance checking
- `GET /conformance/results` - Get conformance results

### Performance Analytics
- `GET /analytics/bottlenecks` - Bottleneck analysis
- `GET /analytics/cycle-times` - Case duration analysis
- `GET /analytics/throughput` - Throughput metrics

### Visualization
- `GET /visualization/dfg` - Directly-Follows Graph
- `GET /visualization/petri-net` - Petri net layout
- `GET /visualization/bpmn` - BPMN diagram

### Advanced
- `POST /predictions/next-activity` - Predict next activity
- `POST /predictions/remaining-time` - Predict remaining time
- `GET /organizational/social-network` - Social network analysis
- `POST /simulation/run` - Run process simulation
- `POST /ocpm/discover` - OCEL 2.0 discovery

## Services

- **Discovery Service**: Process model discovery algorithms (PM4Py integration)
- **Conformance Service**: Token replay and alignment algorithms
- **Analytics Service**: Performance metrics computation
- **Visualization Service**: Graph layout and rendering
- **Prediction Service**: ML-based predictions
- **Organizational Service**: Resource analysis

## Dependencies

**Outbound**:
- Datasets domain (`Dataset`, `DatasetStatus`)
- Platform infrastructure (`AsyncJob` for background analysis)
- PM4Py for process mining algorithms

**Inbound**: None (top of dependency chain)

## Domain Rules

1. Can only analyze READY datasets
2. Discovery creates persistent process models
3. Conformance requires a reference model
4. Analytics computations are cached
5. Predictions require trained ML models
6. All heavy computations run as background jobs

## Migration Notes

**Migrated from**:
- `src/features/process_mining/discovery/` → `src/domains/analysis/services/discovery/`
- `src/features/process_mining/conformance/` → `src/domains/analysis/services/conformance/`
- `src/features/process_mining/analytics/` → `src/domains/analysis/services/analytics/`
- `src/features/process_mining/models/events.py` → `src/domains/analysis/models/events.py`
- `src/features/process_mining/models/process_model.py` → `src/domains/analysis/models/process_model.py`
- `src/features/process_mining/models/analysis.py` → `src/domains/analysis/models/analysis.py`

**Backward compatibility**: Legacy imports still work via re-exports.

## Future Work

- Predictive process monitoring dashboard
- Real-time conformance checking
- Automated recommendation engine
- Advanced OCEL 2.0 features
