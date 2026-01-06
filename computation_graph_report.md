COMPUTATION GRAPH UTILIZATION REPORT
=====================================

Project: Process Mining Application
Date: 2026-01-06

1. OVERVIEW
-----------
This report identifies opportunities for utilizing Computation Graphs (DAGs) within the process-mining application. Computation graphs allow for defining dependencies between tasks, enabling parallel execution, and improving the modularity of complex analytical workflows.

2. TARGET AREAS FOR UTILIZATION
-------------------------------

A. Performance Analytics Dashboard (Analytics Service)
Current State: Sequential execution of multiple independent metrics (bottlenecks, rework, cycle time, throughput).
Opportunity: Use a computation graph to parallelize these calculations. Since they all depend on the same input (PM4PyLog), they can be executed concurrently.
Benefit: Significant reduction in total latency for dashboard generation.

B. Machine Learning Pipelines (Predictions Service)
Current State: Sequential training of next-activity and remaining-time models.
Opportunity:
- Extract features once (Root node).
- Parallelize model training for different targets (Child nodes).
- Build ensemble models where sub-model predictions are aggregated.
Benefit: Faster model training and more robust prediction architecture.

C. Process Discovery Comparison (Discovery Service)
Current State: Single algorithm discovery.
Opportunity: Enable parallel execution of multiple discovery algorithms (e.g., Inductive, Alpha, Heuristics) to compare fitness, precision, and simplicity metrics.
Benefit: Faster benchmarking and automated algorithm selection.

D. Unified Ingestion Pipeline (Ingestion Service)
Current State: Linear processing from file parsing to database persistence.
Opportunity: Use a graph for complex ETL flows:
- Node 1: Raw file parsing.
- Node 2: Data validation & cleaning.
- Node 3: Case grouping (parallelizable).
- Node 4: Stat computation.
- Node 5: Final persistence.
Benefit: Improved error isolation and potential for distributed processing on large datasets.

E. Workflow Orchestration (Workflow Service)
Current State: Linear list-based step execution.
Opportunity: Transform `WorkflowService` into a true DAG-based executor. Users can define non-linear pipelines where steps depend on the output of multiple previous steps.
Benefit: Enhanced flexibility for power users and complex analysis scenarios.

3. RECOMMENDED TOOLS & LIBRARIES
--------------------------------
- NetworkX: For graph construction and analysis if building a custom executor.
- Dask / Ray: For distributed graph execution (overkill for simple parallelism but good for scale).
- Dagster / Prefect: For high-level workflow orchestration.
- Joblib (Existing): Can be combined with custom graph logic for simple in-memory parallelism.

4. CONCLUSION
-------------
Implementing Computation Graphs in the Analytics and Predictions services will yield the most immediate performance benefits. Long-term, evolving the Workflow Service into a DAG-based orchestration engine will significantly enhance the platform's capabilities.
