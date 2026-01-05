# API Issues Checklist

- [x] **Critical: Server Crash on Jobs (500) [ROOT CAUSE FOUND]**
    - `GET /api/v1/jobs` -> 500 Error.
    - `GET /api/v1/jobs/{id}` -> 500 Error.
    - `GET /api/v1/jobs/{id}/stream` -> 500 Error.
    - `GET /api/v1/predictions/jobs/{id}` -> 500 Error.
    - **Verdict**: RESOLVED. Fixed DB schema (`async_jobs` table).

- [x] **Critical: Server Crash on Analyses (500)**
    - `GET /api/v1/analyses` -> 500 Error.
    - **Verdict**: RESOLVED. Fixed DB schema.

- [x] **Critical: Dataset Upload Fails (500)**
    - `POST /api/v1/datasets/upload` -> 500 Error.
    - **Verdict**: RESOLVED. Patched `process_events` table (missing activity_id) and fixed `datasets.py` Attribute Error.
    - **Impact**: Unblocked. Analysis happy path is now testable.
- [x] **Major: Explicit Auth Broken**
    - `POST /register` passed with correct payload (`name` instead of `full_name`).
- [ ] **Minor: 404 Confusion**
    - `GET /api/v1/workspaces/{id}/projects` returns 404, assumed valid path by client but likely not in spec.
