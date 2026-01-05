# System Architecture: Independent User JTBDs

This document structures the platform into independent "Jobs-To-Be-Done" (JTBDs). Each job represents a distinct user goal and is backed by specific frontend features and backend services.

---

## 🏗️ 1. Data Ingestion & Preparation
**"Get my data into the system and ready for analysis."**

-   **User Experience**: Guided wizard for uploading CSV/XES, mapping columns (Case ID, Activity, Timestamp), and evaluating data quality.
-   **Frontend Feature**: [upload-wizard](file:///Users/namanagarwal/system/frontend-new/src/features/upload-wizard)
-   **Backend Services**: 
    -   `UnifiedIngestionService`: Orchestrates the upload flow.
    -   `DuckDBIngestionService`: Converts raw files into high-performance Parquet/DuckDB tables.
-   **Independent Tech**: Operates largely on raw file storage and DuckDB.

## 🔍 2. Process Discovery
**"Show me how my process actually works, visually."**

-   **User Experience**: Interactive DFG (Directly-Followed Graph) and Petri Net visualizations with various mining algorithms (Alpha, Inductive, Heuristic).
-   **Frontend Feature**: [discovery](file:///Users/namanagarwal/system/frontend-new/src/features/discovery)
-   **Backend Services**: 
    -   `MiningService`: Wraps PM4Py algorithms.
    -   `HierarchicalMiningService`: Handles complex, nested process models.
-   **Independent Tech**: Stateless algorithmic layer.

## 📊 3. Performance & KPI Analysis
**"Find where time and money are lost in the process."**

-   **User Experience**: Dashboard with lead times, bottleneck detection, and frequency analysis.
-   **Frontend Feature**: [analytics](file:///Users/namanagarwal/system/frontend-new/src/features/analytics), [kpi](file:///Users/namanagarwal/system/frontend-new/src/features/kpi)
-   **Backend Services**: 
    -   `AnalyticsService`: Calculates aggregations and lead times.
    -   `BottleneckAnalyzer`: Identifies congestion points in the process.
-   **Independent Tech**: High-intensity analytical queries powered by DuckDB.

## 🤖 4. AI-Powered Insights
**"Query my process data using natural language."**

-   **User Experience**: Chat interface to ask questions like "Why is the 'Invoice Approval' step taking so long?"
-   **Frontend Feature**: [ai](file:///Users/namanagarwal/system/frontend-new/src/features/ai)
-   **Backend Services**: 
    -   `LLMService`: Integrates with LLMs to translate natural language into queries or insights.
-   **Independent Tech**: RAG (Retrieval-Augmented Generation) patterns and external LLM API calls.

## 📂 5. Workspace & Project Management
**"Organize my work into separate environments."**

-   **User Experience**: Dashboard for managing multiple projects, user access control, and workspace settings.
-   **Frontend Feature**: [projects](file:///Users/namanagarwal/system/frontend-new/src/features/projects), [platform](file:///Users/namanagarwal/system/frontend-new/src/features/platform)
-   **Backend Services**: 
    -   `AuthorizationService`: Manages permissions and RBAC.
    -   `StorageService`: Handles metadata persistence for projects.
-   **Independent Tech**: Traditional relational data management (SQLite).

---

## 🛠️ Developer Mental Model

To work on a part of the app, follow the JTBD:

1.  **Identify the Job**: What is the user trying to do?
2.  **Locate the Feature**: Go to `frontend-new/src/features/[job]`.
3.  **Locate the Service**: Go to `backend/src/services/[job_related_service].py`.
4.  **Test in Isolation**: Each job should be testable via E2E tests that mirror the JTBD flow.
