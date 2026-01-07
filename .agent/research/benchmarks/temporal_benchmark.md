# Benchmark Report: Temporal Workflows Implementation

**Date**: 2026-01-07
**Component**: Temporal Workflows (`src/platform/temporal`)
**Focus Area**: Scalability, Architecture, and Best Practices

## Executive Summary
The Temporal implementation demonstrates a solid understanding of the basics (activities, retries, heartbeats) but suffers from a **CRITICAL scalability flaw** in data passing. The current implementation passes entire datasets (cases/events) through Activity inputs/outputs, which will cause Temporal history to exceed size limits (typ. 50MB) and fail for even medium-sized datasets. 

Additionally, there is architectural ambiguity between the "Legacy Workflows" (Temporal) and "New DAGs" (Celery-based), which creates confusion about the long-term orchestration strategy.

---

## 1. Architectural Analysis

| Feature | Implementation Status | Rating | Notes |
|---------|----------------------|--------|-------|
| **Activity Separation** | ✅ Well defined | Good | Distinct activities for validation, parsing, mining. |
| **Input/Output Typing** | ✅ Dataclasses used | Good | `types.py` provides clear contracts. |
| **Error Handling** | ✅ Explicit | Good | Try/except blocks with logging and custom error returns. |
| **Orchestration Model** | ⚠️ Ambiguous | Concern | Router says "Migrated to DAGs" (Celery), but Temporal code suggests it's the "Modern" choice. |

### Major Finding: "DAG" vs "Workflow" Confusion
- `api/routers/workflows.py` exposes Temporal status.
- `features/process_mining/workflows/router.py` deprecates Workflows in favor of DAGs.
- `platform/dag/executor.py` runs on **Celery**.
- `platform/temporal/compat.py` allows switching between Celery and Temporal via `USE_TEMPORAL` flag.

**Risk**: The system supports two parallel orchestration engines. The "DAG" system (Celery) appears to be the "new" recommended one according to API routers, while Temporal (usually the superior choice for complex flows) is treated as an alternative or legacy, despite being more robust.

---

## 2. Scalability & Performance Guidelines

### Critical Flaw: Data Bloat in Workflow History
The `parse_to_parquet_activity` returns `ParseToParquetOutput` containing:
```python
cases_data: list[dict[str, Any]]
events_data: list[dict[str, Any]]
```
These lists are then passed to `bulk_copy_to_db_activity`.
- **Impact**: For a 50MB CSV, the JSON representation might be ~200MB.
- **Consequence**: Temporal Workflow History limit (50MB hard limit) will be breached immediately.
- **Verdict**: **FAILED** for production usage.

### Memory Management
- **Good**: `parse_to_parquet_activity` uses batched Arrow processing.
- **Bad**: It then converts everything to Python lists (`batch.to_pylist()`) and stores them in memory to return them! This negates the streaming/batching benefits.
- **Correction**: Data should be streamed to S3/DB directly or written to intermediate files.

---

## 3. Reliability & Best Practices

| Best Practice | Implemented? | Assessment |
|---------------|--------------|------------|
| **Activity Timeouts** | ✅ Yes | Good use of `start_to_close_timeout`. |
| **Heartbeating** | ✅ Yes | Correctly used in long-running `parse_activity`. |
| **Retries** | ✅ Yes | Standard policies applied. |
| **Idempotency** | ⚠️ Partial | Database inserts are generally idempotent if IDs conflict, but bulk copy might duplicate if partially failed and retried without cleanup. |
| **Determinism** | ✅ Yes | Workflow logic seems deterministic (no random/time calls inside workflow logic). |

---

## 4. Benchmark Estimates (Theoretical)

Based on code analysis, here are the expected performance envelopes:

| Dataset Size | Events | Estimated Time | Success Probability | Bottleneck |
|--------------|--------|----------------|---------------------|------------|
| **Small** | < 10k | < 5s | High | None |
| **Medium** | 10k - 100k | 10s - 30s | **Low** | Payload Size Limit (Temporal) |
| **Large** | 100k - 1M | N/A | **0% (Fail)** | OOM / History Limit |
| **Huge** | > 1M | N/A | **0% (Fail)** | OOM / History Limit |

*Note: Without the payload fix, the system is limited to "Toy" datasets only.*

---

## 5. Recommendations

### P0: Critical Fixes (Must Do)
1.  **Implement Reference Passing**:
    -   Modify `parse_to_parquet_activity` to write results to S3 (Parquet/JSON).
    -   Return **ONLY** the S3 keys (`s3://.../cases.parquet`).
    -   Modify `bulk_copy_to_db_activity` to read from S3.
    -   **Result**: Payload size drops to bytes; History limit avoided.

2.  **Clarify Orchestration Strategy**:
    -   Decide between Temporal (robust) and Celery-DAGs (simple).
    -   If migrating to Temporal, update `router.py` to stop deprecating it.

### P1: Performance Improvements
1.  **Direct S3 Loading**: DuckDB can query S3 directly. Use `INSERT INTO postgres_table SELECT * FROM read_parquet('s3://...')` (if using PG extension) or stream directly without converting to Python dicts.

### P2: Quality of Life
1.  **Typed Workflow Results**: Return Pydantic objects or strong types from workflows instead of generic `dict`.

---

## Conclusion
The Temporal implementation logic is sound, but the data passing strategy renders it unusable for real-world process mining datasets. One critical refactor (Reference Passing) will unlock its full potential.
