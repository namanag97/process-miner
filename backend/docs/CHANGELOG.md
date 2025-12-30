# Changelog

All notable changes to the Process Mining Backend API.

Format: [Semantic Versioning](https://semver.org/)  
Legend: ⚠️ Breaking | ✅ Stable | 🆕 New | 🗑️ Deprecated

---

## [Unreleased]

### 🆕 New Endpoints

- `GET /analytics/logs/{log_id}/rework-chains` — Detect consecutive activity repetitions

### ✅ Enhancements

- `GET /analytics/logs/{log_id}/bottlenecks` — Added `preceding_activities`, `following_activities`, `bottleneck_impact_score`
- `GET /conformance/alignments/{log_id}/{model_id}` — New alignment diagnostics endpoint

### Schema Changes

| Schema                         | Change                                 | Migration              |
| ------------------------------ | -------------------------------------- | ---------------------- |
| `BottleneckResponse`           | Added `preceding_activities: string[]` | None (optional field)  |
| `BottleneckResponse`           | Added `following_activities: string[]` | None (optional field)  |
| `BottleneckResponse`           | Added `bottleneck_impact_score: float` | None (defaults to 0.0) |
| `ReworkChain`                  | 🆕 New schema                          | N/A                    |
| `ReworkChainListResponse`      | 🆕 New schema                          | N/A                    |
| `AlignmentMove`                | 🆕 New schema                          | N/A                    |
| `CaseAlignmentResponse`        | 🆕 New schema                          | N/A                    |
| `AlignmentDiagnosticsResponse` | 🆕 New schema                          | N/A                    |

### Database Migrations

- `001_add_ocel_data_blob.py` — Added `ocel_data` BLOB column to `OCELLog` table

---

## [1.0.0] — 2024-12-30

### ✅ Initial Release

Full Process Mining SaaS API with 11 routers and 60+ endpoints.

### Routers

| Router         | Prefix            | Endpoints |
| -------------- | ----------------- | --------- |
| Processes      | `/processes`      | 8         |
| Discovery      | `/discovery`      | 5         |
| Visualization  | `/visualization`  | 7         |
| Conformance    | `/conformance`    | 8         |
| Analytics      | `/analytics`      | 8         |
| Predictions    | `/predictions`    | 7         |
| Filtering      | `/filtering`      | 6         |
| OCPM           | `/ocpm`           | 12        |
| Organizational | `/organizational` | 6         |
| Simulation     | `/simulation`     | 3         |
| Workflows      | `/workflows`      | 5         |

### Core Features

- **Event Log Management**

  - CSV and XES file upload
  - Auto column detection
  - Variant and activity analysis

- **Process Discovery**

  - Alpha, Alpha+, Inductive, Heuristics miners
  - DFG generation
  - Fitness/precision metrics

- **Conformance Checking**

  - Token replay
  - Alignment-based
  - Deviation detection

- **Performance Analytics**

  - Bottleneck detection
  - Rework analysis
  - Cycle time and throughput

- **ML Predictions**

  - Next activity prediction
  - Remaining time prediction
  - Sync and async training

- **Object-Centric Process Mining**

  - OCEL 2.0 support (JSON, SQLite, XML)
  - OC-DFG discovery
  - Object-Centric Petri Net discovery

- **Organizational Mining**

  - Handover of work networks
  - Working together networks
  - Resource profiling and role discovery

- **Simulation**
  - Model play-out
  - What-if scenarios
  - Capacity planning

---

## Version History

| Version | Date       | Notes           |
| ------- | ---------- | --------------- |
| 1.0.0   | 2024-12-30 | Initial release |

---

## Migration Guides

### From 0.x to 1.0.0

No prior public version. This is the initial release.

### Future Breaking Changes (Planned)

> [!WARNING]
> The following changes are planned for v2.0:

1. **Pagination cursor-based** — Currently offset-based, will move to cursor for large datasets
2. **Unified error codes** — Standardize error `type` URIs
3. **Async-only training** — Remove sync mode from `/predictions/train`

---

## API Deprecation Policy

1. **Announce:** Deprecated endpoints marked with `🗑️` in changelog
2. **Warning period:** 3 months with `Deprecation` header in responses
3. **Removal:** Documented in next major version
4. **SDK:** Types marked `@deprecated` in TypeScript

---

## SDK Compatibility

| Backend Version | SDK Version | Notes              |
| --------------- | ----------- | ------------------ |
| 1.0.0           | 1.0.0+      | Full compatibility |

---

## Upgrade Checklist

### Pre-upgrade

- [ ] Review breaking changes section
- [ ] Update SDK to compatible version
- [ ] Test against staging environment

### Post-upgrade

- [ ] Verify health checks pass
- [ ] Run integration tests
- [ ] Monitor error rates for 24h

---

## Reporting Issues

API issues: [GitHub Issues](https://github.com/your-org/process-mining/issues)

Include:

- Endpoint called
- Request body (sanitized)
- Response received
- Expected behavior
