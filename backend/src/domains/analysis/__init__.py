"""Analysis Domain - Process Mining & Analytics.

This domain handles all analytical capabilities:
- Dataset statistics and metadata queries
- Case and event exploration
- Variant analysis
- Activity analysis
- Process discovery (Alpha, Inductive, Heuristics miners)
- Conformance checking (token replay, alignments)
- Performance analytics (bottlenecks, cycle times)
- Visualization (DFG, Petri nets, BPMN)
- Predictive analytics (next activity, remaining time)
- Organizational mining (social networks, handovers)
- Process simulation (what-if analysis)
- Object-centric process mining (OCEL 2.0)

Key Models:
- ProcessCase: Case/trace representation
- ProcessEvent: Individual events in cases
- ProcessModel: Discovered process models
- Analysis: Stored analysis results
- ConformanceResult: Conformance checking results
- PredictionModel: ML prediction models

APIs:
- GET /datasets/{id}/statistics - Aggregate statistics
- GET /datasets/{id}/cases - List cases
- GET /datasets/{id}/events - Query events
- GET /datasets/{id}/variants - Process variants
- GET /datasets/{id}/activities - Activity statistics
- POST /discovery/discover - Run process discovery
- POST /conformance/check - Run conformance checking
- GET /analytics/bottlenecks - Bottleneck analysis
- GET /visualization/dfg - DFG visualization
- POST /predictions/next-activity - Predict next activity
"""
