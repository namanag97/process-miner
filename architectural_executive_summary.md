# ARIA PHASE 2: ARCHITECTURAL REDESIGN

A distilled summary of critical architectural gaps and the implemented solutions.

---

## 🏗️ 1. Core Domain: Outdated Data Model → OCEL 2.0

> **Problem**: We store events as simple "Case → Activity" chains, but real business processes are "Order → Line Items → Shipments" (many-to-many). We're forcing round pegs into square holes.

| Feature        | Before                                           | After                                                         |
| :------------- | :----------------------------------------------- | :------------------------------------------------------------ |
| **Structure**  | Order123 → Activity → Activity (flat chain)      | Order123 → [Item1, Item2] → [Shipment1] → [Invoice] (network) |
| **Problem**    | Can't see when 3 orders converge into 1 shipment | Full visibility into M:N object relationships                 |
| **Capability** | Limited to single-case analysis                  | Object-Centric Process Mining (OCPM)                          |

- **Framework**: [OCEL 2.0 Standard](https://ocel-standard.org)
- **Implemented**: `backend/src/models/ocel2.py`

---

## ⚡ 2. Performance: Object Tax & Bottlenecks → DuckDB/Arrow

> **Problem**: Data is converted 4 times for every operation (SQL → Dict → ORM → PM4Py). Ingestion iterates over millions of rows in slow Python loops.

| Feature        | Before                              | After                                  |
| :------------- | :---------------------------------- | :------------------------------------- |
| **Processing** | Row-by-row Python loops             | Vectorized columnar execution          |
| **Data Flow**  | SQL → Dict → ORM → PM4Py (4 copies) | SQL → Arrow Table → PM4Py (1-2 copies) |
| **Speed**      | 60s for 1M rows                     | ~3-5s for 1M rows                      |

- **Framework**: [DuckDB](https://duckdb.org) + [Apache Arrow](https://arrow.apache.org)
- **Implemented**: `backend/src/services/duckdb_ingestion.py`

---

## 📋 Remaining Strategic Roadmap

### 3. AI: Predictive → Prescriptive

- **Problem**: The AI warns of failure (Predictive) but provides no steering wheel (Prescriptive).
- **Target**: Recommendation engine that suggests reassigning resources or rerouting processes.

### 4. Privacy: The Panopticon Effect → Anonymization

- **Problem**: Employee data is analyzed with real names/timestamps (potential GDPR violation).
- **Target**: Configurable pseudonymization layer for resources and timestamp generalization.

### 5. Semantics: String Labels → Rich Activity Objects

- **Problem**: Activities are simple strings, making the system "domain blind" to SLAs or Cost.
- **Target**: Activity domain model with cost-per-execution and SLA thresholds.

### 6. Simulation: Simple Scaling → Queuing Theory

- **Problem**: Simulation assumes 10 people = 2x output, ignoring burnout and wait times.
- **Target**: M/M/c queuing models for realistic capacity planning.
