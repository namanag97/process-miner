# Comprehensive Integration Testing Plan for Process Mining SaaS

## Executive Summary

Create a complete integration test suite covering all **237 business activities** across **15 use cases** from the business requirements document. The plan includes tests for 45 currently implemented endpoints plus test stubs for 192 future features.

**Current Status**: ~15% coverage (35 activities tested)
**Target**: 100% coverage (237 activities tested)

---

## 1. Test Organization Strategy

### 1.1 Directory Structure

```
tests/
├── conftest.py                           # [EXISTS] Global fixtures
├── pytest.ini                            # [NEW] Pytest configuration
├── markers.ini                           # [NEW] Custom markers definition
│
├── integration/                          # [NEW] All integration tests
│   ├── __init__.py
│   ├── conftest.py                       # Integration-specific fixtures
│   │
│   ├── test_discovery_flows.py          # DIS-001 to DIS-015 (15 tests)
│   ├── test_variant_analysis.py         # VAR-001 to VAR-015 (15 tests)
│   ├── test_conformance_flows.py        # CON-001 to CON-022 (22 tests)
│   ├── test_performance_analysis.py     # PER-001 to PER-020 (20 tests)
│   ├── test_bottleneck_detection.py     # BOT-001 to BOT-012 (12 tests)
│   ├── test_root_cause_analysis.py      # RCA-001 to RCA-013 (13 tests)
│   ├── test_organizational_mining.py    # ORG-001 to ORG-015 (15 tests)
│   ├── test_predictive_monitoring.py    # PRD-001 to PRD-015 (15 tests)
│   ├── test_drift_detection.py          # DRF-001 to DRF-012 (12 tests)
│   ├── test_ocpm_flows.py                # OCE-001 to OCE-019 (19 tests)
│   ├── test_rpa_discovery.py            # RPA-001 to RPA-014 (14 tests)
│   ├── test_compliance_monitoring.py    # CMP-001 to CMP-017 (17 tests)
│   ├── test_simulation_whatif.py        # SIM-001 to SIM-014 (14 tests)
│   ├── test_dashboard_reporting.py      # DSH-001 to DSH-018 (18 tests)
│   └── test_alerting_monitoring.py      # ALR-001 to ALR-016 (16 tests)
│
├── e2e/                                  # [NEW] End-to-end user journeys
│   ├── __init__.py
│   ├── conftest.py                       # E2E-specific fixtures
│   ├── test_analyst_journey.py          # Process Analyst full workflow
│   ├── test_compliance_officer_journey.py # Compliance Officer workflow
│   ├── test_operations_manager_journey.py # Operations Manager workflow
│   └── test_complete_platform_journey.py # Multi-persona workflows
│
├── fixtures/                             # [NEW] Test data repository
│   ├── __init__.py
│   ├── csv/                              # CSV test files
│   │   ├── basic_2_cases.csv
│   │   ├── multiple_variants_6_cases.csv
│   │   ├── bottleneck_scenario.csv
│   │   ├── performance_analysis_50_cases.csv
│   │   ├── organizational_mining_100_cases.csv
│   │   ├── drift_detection_time_series.csv
│   │   ├── rpa_repetitive_tasks.csv
│   │   └── compliance_violations.csv
│   ├── xes/                              # XES test files
│   │   ├── bpi_challenge_2012_sample.xes
│   │   └── simple_process.xes
│   ├── ocel/                             # OCEL test files
│   │   ├── order_management.jsonocel
│   │   ├── logistics_multi_object.sqlite
│   │   └── procurement_process.xmlocel
│   └── models/                           # Reference process models
│       ├── reference_petri_net.pnml
│       └── reference_bpmn.bpmn
│
├── unit/                                 # [EXISTS] Unit tests (keep as-is)
│   ├── test_domain.py                    # [EXISTS]
│   └── test_services/                    # [NEW] Service unit tests
│       ├── test_ingestion_service.py
│       ├── test_mining_service.py
│       ├── test_conformance_service.py
│       ├── test_ocpm_service.py
│       └── test_workflow_service.py
│
└── legacy/                               # [NEW] Move existing tests here
    ├── test_api.py                       # [MOVE FROM ROOT]
    ├── test_business_flows.py            # [MOVE FROM ROOT]
    └── integration_test.py               # [MOVE FROM ROOT]
```

### 1.2 Naming Conventions

**Test Files**: `test_<use_case_name>.py` (e.g., `test_discovery_flows.py`)

**Test Classes**: `Test<UseCase><Aspect>` (e.g., `TestDiscoveryAlgorithms`, `TestDiscoveryVisualization`)

**Test Functions**: `test_<activity_id>_<description>` (e.g., `test_DIS001_upload_event_log`)

**Fixtures**: `<domain>_<type>` (e.g., `performance_log`, `bottleneck_csv`, `ocel_order_management`)

### 1.3 Organization Principles

1. **One file per use case** - Each of the 15 use cases gets its own test file
2. **Class-based grouping** - Group related activities into classes within each file
3. **Activity ID in test name** - Always include the business activity ID (e.g., DIS-001)
4. **Priority markers** - Use pytest markers: `@pytest.mark.priority_high`, `@pytest.mark.priority_medium`, `@pytest.mark.priority_low`
5. **Implementation status markers** - Use `@pytest.mark.implemented` or `@pytest.mark.stub` (for future features)
6. **E2E separate** - End-to-end flows in dedicated `e2e/` directory

---

## 2. Fixture Strategy

### 2.1 Enhanced Global Fixtures (conftest.py)

**Keep Existing**:

- `event_loop` - Session-scoped async loop
- `test_engine` - In-memory SQLite engine
- `test_session` - Function-scoped DB session
- `client` - HTTP test client

**Add New Global Fixtures**:

```python
# Data generators
@pytest.fixture
def csv_generator():
    """Factory for generating custom CSV test data."""
    def _generate(cases, activities, timestamp_start, with_resource=False):
        # Generate CSV bytes
        pass
    return _generate

# Time utilities
@pytest.fixture
def freeze_time():
    """Freeze time for drift detection tests."""
    import freezegun
    return freezegun.freeze_time

# PM4Py utilities
@pytest.fixture
def pm4py_log_converter():
    """Convert CSV/XES to PM4Py log object for assertions."""
    pass
```

### 2.2 Domain-Specific Fixtures (integration/conftest.py)

**Discovery & Variants**:

```python
@pytest.fixture
async def uploaded_basic_log(client, basic_csv):
    """Pre-uploaded basic event log."""

@pytest.fixture
async def discovered_alpha_model(client, uploaded_basic_log):
    """Pre-discovered model using Alpha miner."""

@pytest.fixture
async def multi_variant_log(client, multi_variant_csv):
    """Log with 3+ distinct variants."""
```

**Performance & Bottlenecks**:

```python
@pytest.fixture
def performance_csv():
    """CSV with 50 cases, clear performance patterns."""

@pytest.fixture
def bottleneck_csv():
    """CSV with identifiable bottleneck activity."""

@pytest.fixture
async def performance_analysis_result(client, performance_csv):
    """Pre-computed performance analysis."""
```

**Organizational Mining**:

```python
@pytest.fixture
def organizational_csv():
    """CSV with 100 cases, 10 resources, clear handover patterns."""

@pytest.fixture
async def handover_network(client, organizational_csv):
    """Pre-computed handover network."""
```

**OCPM**:

```python
@pytest.fixture
def ocel_order_management():
    """OCEL file: orders + items + deliveries."""

@pytest.fixture
def ocel_logistics():
    """OCEL file: logistics scenario with 4 object types."""

@pytest.fixture
async def uploaded_ocel_log(client, ocel_order_management):
    """Pre-uploaded OCEL log."""
```

**Conformance**:

```python
@pytest.fixture
def reference_petri_net():
    """PNML file with reference process model."""

@pytest.fixture
def conformant_log():
    """CSV that perfectly conforms to reference model."""

@pytest.fixture
def non_conformant_log():
    """CSV with deliberate deviations."""
```

**Predictive Monitoring**:

```python
@pytest.fixture
def training_log():
    """Large CSV (200+ cases) for ML training."""

@pytest.fixture
def running_cases_log():
    """CSV with incomplete cases for prediction."""
```

**Drift Detection**:

```python
@pytest.fixture
def drift_log():
    """CSV with clear process change at midpoint."""
```

### 2.3 Fixture Chaining for Flows

```python
uploaded_log → discovered_model → conformance_result → diagnostics
uploaded_log → variants → variant_comparison → variant_report
ocel_log → object_types → oc_petri_net → visualization
```

---

## 3. Test Data Requirements

### 3.1 CSV Test Files (tests/fixtures/csv/)

| File                                  | Cases | Variants | Purpose                         |
| ------------------------------------- | ----- | -------- | ------------------------------- |
| `basic_2_cases.csv`                   | 2     | 1        | Basic smoke tests               |
| `multiple_variants_6_cases.csv`       | 6     | 3        | Variant analysis                |
| `bottleneck_scenario.csv`             | 10    | 2        | Bottleneck with clear wait time |
| `performance_analysis_50_cases.csv`   | 50    | 5        | Statistical analysis            |
| `organizational_mining_100_cases.csv` | 100   | 8        | 10 resources, handovers         |
| `drift_detection_time_series.csv`     | 200   | 4        | Process change at case 100      |
| `rpa_repetitive_tasks.csv`            | 100   | 1        | Highly repetitive for RPA       |
| `compliance_violations.csv`           | 30    | 6        | SoD violations, missing steps   |
| `prediction_training.csv`             | 300   | 10       | Training set for ML             |
| `prediction_running_cases.csv`        | 20    | N/A      | Incomplete cases                |

### 3.2 XES Test Files (tests/fixtures/xes/)

- `bpi_challenge_2012_sample.xes` - Real-world sample (100 cases)
- `simple_process.xes` - Basic A→B→C process

### 3.3 OCEL Test Files (tests/fixtures/ocel/)

- `order_management.jsonocel` - Orders + OrderItems + Deliveries
- `logistics_multi_object.sqlite` - Shipments + Packages + Routes + Drivers
- `procurement_process.xmlocel` - POs + PRs + Invoices + Payments

### 3.4 Reference Models (tests/fixtures/models/)

- `reference_petri_net.pnml` - Standard approval process
- `reference_bpmn.bpmn` - BPMN 2.0 model for import tests

---

## 4. Test Stub Strategy

### 4.1 Marking Strategy

**Pytest Markers**:

```python
# In pytest.ini
[tool.pytest.ini_options]
markers =
    implemented: Tests for implemented features
    stub: Tests for planned features (will skip)
    priority_high: High-frequency activities (daily use)
    priority_medium: Medium-frequency activities (weekly)
    priority_low: Low-frequency activities (monthly)
    e2e: End-to-end integration tests
    slow: Tests that take >5 seconds
```

**Test Stub Template**:

```python
@pytest.mark.stub
@pytest.mark.priority_medium
@pytest.mark.asyncio
async def test_VAR005_filter_top_variants(client: AsyncClient, multi_variant_log: str):
    """
    Business Activity: VAR-005 - Filter Top Variants

    Description:
        Focus on most common paths by filtering variants above a frequency threshold.

    Input: Variants + threshold (e.g., top 80%)
    Output: Filtered variant list

    API Endpoint (Planned): GET /api/v1/processes/{log_id}/variants/filter?top_percent=80

    Implementation TODO:
        - Add filter parameter to variants endpoint
        - Calculate cumulative frequency
        - Return variants covering top X%

    PM4Py Mapping: filter_variants()
    """
    pytest.skip("Feature not yet implemented - API endpoint planned")

    # Expected behavior (specification):
    response = await client.get(
        f"/api/v1/processes/{multi_variant_log}/variants/filter",
        params={"top_percent": 80}
    )
    assert response.status_code == 200
    data = response.json()

    # Business logic assertions (when implemented)
    assert "variants" in data
    assert "coverage_percent" in data
    assert data["coverage_percent"] >= 80
    assert len(data["variants"]) < 10  # Should filter out rare variants
```

### 4.2 Implementation Tracking

Create `IMPLEMENTATION_PROGRESS.md` with checklist:

```markdown
# Integration Test Implementation Progress

## Discovery & Variants (30 tests)

- [x] DIS-001: Upload Event Log
- [x] DIS-002: Configure Column Mapping
- [ ] DIS-005: Select Discovery Algorithm (STUB)
- [ ] VAR-005: Filter Top Variants (STUB)
      ...

Progress: 35/237 (14.8%)
```

---

## 5. End-to-End Test Scenarios

### 5.1 Process Analyst Journey (e2e/test_analyst_journey.py)

**Test**: `test_complete_process_discovery_workflow`

```python
"""
Complete workflow: Upload → Validate → Discover → Annotate → Export → Share
Activities covered: DIS-001, DIS-003, DIS-004, DIS-007, DIS-010, DIS-011, DIS-013
"""
```

**Steps**:

1. Upload CSV log (DIS-001)
2. Validate data quality (DIS-003)
3. Preview event data (DIS-004)
4. Execute discovery with Inductive Miner (DIS-007)
5. Annotate model with frequency (DIS-010)
6. Annotate model with performance (DIS-011)
7. Export to PNML (DIS-013)

**Assertions**:

- Each step succeeds
- Data flows correctly between steps
- Final export contains all annotations
- Total duration < 30 seconds

### 5.2 Compliance Officer Journey (e2e/test_compliance_officer_journey.py)

**Test**: `test_complete_conformance_checking_workflow`

```python
"""
Complete workflow: Define Rules → Import Model → Check → Review → Remediate → Report
Activities covered: CMP-001, CON-002, CON-006, CON-011, CON-018
"""
```

**Steps**:

1. Define compliance rules (CMP-001)
2. Import reference BPMN model (CON-002)
3. Execute conformance check (CON-006)
4. Review violations (CON-011)
5. Generate compliance report (CON-018)

### 5.3 Operations Manager Journey (e2e/test_operations_manager_journey.py)

**Test**: `test_performance_optimization_workflow`

```python
"""
Complete workflow: Monitor → Identify → Analyze → Simulate → Track
Activities covered: PER-001, BOT-002, RCA-001, SIM-008, PER-017
"""
```

**Steps**:

1. Calculate case durations (PER-001)
2. Identify bottlenecks (BOT-002)
3. Root cause analysis (RCA-001)
4. Simulate bottleneck removal (SIM-008)
5. Generate performance report (PER-017)

### 5.4 Multi-Persona Platform Journey (e2e/test_complete_platform_journey.py)

**Test**: `test_full_platform_capabilities`

```python
"""
Test all major platform features in realistic sequence.
Activities covered: 20+ across all use cases
"""
```

**Steps**:

1. Upload multiple logs (CSV, XES, OCEL)
2. Discover models with different algorithms
3. Run conformance checks
4. Analyze performance and variants
5. Detect organizational patterns
6. Create dashboards
7. Set up alerts
8. Generate reports

---

## 6. Pytest Configuration

### 6.1 pytest.ini Configuration

```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]

# Markers
markers =
    implemented: Tests for implemented features
    stub: Tests for planned features (will skip)
    priority_high: High-frequency activities (daily use)
    priority_medium: Medium-frequency activities (weekly)
    priority_low: Low-frequency activities (monthly)
    e2e: End-to-end integration tests
    slow: Tests that take >5 seconds
    discovery: Process discovery tests
    variants: Variant analysis tests
    conformance: Conformance checking tests
    performance: Performance analysis tests
    ocpm: Object-centric process mining tests
    organizational: Organizational mining tests
    prediction: Predictive monitoring tests

# Coverage
addopts =
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    -v

# Test discovery
norecursedirs = .git .tox dist build *.egg

# Timeout for slow tests
timeout = 300
```

### 6.2 Required Pytest Plugins

Add to `pyproject.toml`:

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^4.1.0"
pytest-timeout = "^2.2.0"
pytest-xdist = "^3.5.0"  # Parallel execution
pytest-html = "^4.1.0"   # HTML reports
pytest-bdd = "^7.0.0"    # BDD-style tests (optional)
freezegun = "^1.4.0"     # Time mocking for drift detection
faker = "^22.0.0"        # Generate test data
```

---

## 7. Execution Strategy

### 7.1 Test Suites

**Smoke Tests** (fast validation):

```bash
pytest tests/integration -m "implemented and priority_high" -v
```

**Regression Tests** (before deployment):

```bash
pytest tests/integration -m "implemented" -v
```

**Full Test Suite** (including stubs):

```bash
pytest tests/ -v
```

**E2E Tests** (complete workflows):

```bash
pytest tests/e2e -m "e2e" -v
```

**By Use Case**:

```bash
pytest tests/integration/test_discovery_flows.py -v
pytest tests/integration -m "discovery" -v
```

**Parallel Execution**:

```bash
pytest tests/integration -m "implemented" -n auto  # Use all CPU cores
```

### 7.2 CI/CD Integration

**GitHub Actions Workflow**:

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run smoke tests
        run: pytest tests/integration -m "implemented and priority_high"
      - name: Run all implemented tests
        run: pytest tests/integration -m "implemented"
      - name: Generate coverage report
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 8. Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal**: Test infrastructure and priority use cases

1. **Setup**:

   - Create directory structure
   - Configure pytest.ini with markers
   - Add new pytest plugins

2. **Fixtures**:

   - Create CSV test data files
   - Add domain-specific fixtures to integration/conftest.py
   - Create fixture factory functions

3. **Priority Tests** (30 tests):
   - `test_discovery_flows.py` - DIS-001 to DIS-015 (6 implemented + 9 stubs)
   - `test_variant_analysis.py` - VAR-001 to VAR-015 (4 implemented + 11 stubs)

**Deliverable**: 30 tests (10 passing, 20 stubs)

---

### Phase 2: Conformance & OCPM (Week 2)

**Goal**: Complete conformance and object-centric PM tests

1. **Conformance**:

   - `test_conformance_flows.py` - CON-001 to CON-022 (8 implemented + 14 stubs)
   - `test_compliance_monitoring.py` - CMP-001 to CMP-017 (0 implemented + 17 stubs)

2. **OCPM**:
   - Create OCEL test files (.jsonocel, .sqlite)
   - `test_ocpm_flows.py` - OCE-001 to OCE-019 (6 implemented + 13 stubs)

**Deliverable**: 58 tests (14 passing, 44 stubs)

---

### Phase 3: Performance & Analytics (Week 3)

**Goal**: Performance, bottleneck, and organizational mining tests

1. **Performance**:

   - `test_performance_analysis.py` - PER-001 to PER-020 (2 implemented + 18 stubs)
   - `test_bottleneck_detection.py` - BOT-001 to BOT-012 (0 implemented + 12 stubs)

2. **Organizational**:
   - Create organizational CSV with handovers
   - `test_organizational_mining.py` - ORG-001 to ORG-015 (0 implemented + 15 stubs)

**Deliverable**: 47 tests (2 passing, 45 stubs)

---

### Phase 4: Advanced Analytics (Week 4)

**Goal**: Prediction, drift, RCA, and RPA tests

1. **Predictive & Drift**:

   - `test_predictive_monitoring.py` - PRD-001 to PRD-015 (0 implemented + 15 stubs)
   - `test_drift_detection.py` - DRF-001 to DRF-012 (0 implemented + 12 stubs)

2. **RCA & RPA**:
   - `test_root_cause_analysis.py` - RCA-001 to RCA-013 (0 implemented + 13 stubs)
   - `test_rpa_discovery.py` - RPA-001 to RPA-014 (0 implemented + 14 stubs)

**Deliverable**: 54 tests (0 passing, 54 stubs)

---

### Phase 5: Platform Features (Week 5)

**Goal**: Dashboards, reporting, alerting, simulation

1. **UI & Monitoring**:

   - `test_dashboard_reporting.py` - DSH-001 to DSH-018 (0 implemented + 18 stubs)
   - `test_alerting_monitoring.py` - ALR-001 to ALR-016 (0 implemented + 16 stubs)

2. **Simulation**:
   - `test_simulation_whatif.py` - SIM-001 to SIM-014 (0 implemented + 14 stubs)

**Deliverable**: 48 tests (0 passing, 48 stubs)

---

### Phase 6: End-to-End & Service Tests (Week 6)

**Goal**: Complete E2E workflows and service layer tests

1. **E2E Tests**:

   - `test_analyst_journey.py` - Process Analyst complete workflow
   - `test_compliance_officer_journey.py` - Compliance Officer workflow
   - `test_operations_manager_journey.py` - Operations Manager workflow
   - `test_complete_platform_journey.py` - Multi-persona workflow

2. **Service Unit Tests**:
   - `test_ingestion_service.py`
   - `test_mining_service.py`
   - `test_conformance_service.py`
   - `test_ocpm_service.py`
   - `test_workflow_service.py`

**Deliverable**: 10+ E2E tests, 25+ service tests

---

### Phase 7: Cleanup & Documentation (Week 7)

**Goal**: Refactor, document, and optimize

1. **Integration**:

   - Move existing tests to legacy/
   - Refactor test_business_flows.py into new structure
   - Deduplicate test coverage

2. **Documentation**:

   - Create TESTING.md guide
   - Update README with test execution instructions
   - Create IMPLEMENTATION_PROGRESS.md tracker

3. **Optimization**:
   - Identify slow tests, add @pytest.mark.slow
   - Optimize fixtures (session scope where appropriate)
   - Add parallel execution support

**Deliverable**: Clean test suite, documentation, CI/CD integration

---

## 9. Integration with Existing Tests

### 9.1 Migration Strategy

**Existing Files**:

- `test_api.py` (15 tests) → Move to `legacy/`
- `test_business_flows.py` (29 tests) → Refactor into new structure
- `test_domain.py` (20 tests) → Keep in `unit/`
- `integration_test.py` → Move to `legacy/` (manual test script)

**Refactoring test_business_flows.py**:

- Extract tests into appropriate integration test files
- Preserve class structure and fixtures
- Update test names to include activity IDs
- Add markers for implemented vs. stub

**Deduplication**:

- Review overlap between legacy and new tests
- Keep most comprehensive version
- Delete redundant tests

### 9.2 Backward Compatibility

- Keep legacy tests runnable during transition
- Use `pytest tests/legacy` to run old tests
- Gradually deprecate as new tests prove stable

---

## 10. Success Metrics

### 10.1 Coverage Metrics

**By End of Implementation**:

- ✅ 237 total integration tests created
- ✅ 35 tests passing (currently implemented features)
- ✅ 202 tests as stubs (future features)
- ✅ 10+ E2E tests for complete workflows
- ✅ 25+ service unit tests
- ✅ 100% of business activities have test specifications

### 10.2 Quality Metrics

- All implemented features have passing tests
- No test should take >10 seconds (except E2E)
- E2E tests complete in <2 minutes
- Test suite runs in <5 minutes with parallel execution
- Code coverage: >80% for implemented features

### 10.3 Maintenance Metrics

- Each new API endpoint must include test before merge
- Test stubs converted to real tests within 1 sprint of implementation
- Documentation updated with each test phase completion

---

## Critical Files to Create/Modify

### New Files (85 files):

```
tests/pytest.ini
tests/markers.ini
tests/fixtures/ (10 CSV + 2 XES + 3 OCEL + 2 model files)
tests/integration/ (15 test files + conftest.py)
tests/e2e/ (4 test files + conftest.py)
tests/unit/test_services/ (5 test files)
tests/legacy/ (move 3 existing files)
TESTING.md
IMPLEMENTATION_PROGRESS.md
```

### Modified Files:

```
tests/conftest.py - Add new global fixtures
pyproject.toml - Add pytest plugins
.github/workflows/test.yml - Add CI configuration
```

---

## Summary

This plan provides:
✅ Complete test coverage for all 237 business activities
✅ Organized structure (15 integration + 4 E2E + 5 service test files)
✅ Test stubs for not-yet-implemented features
✅ Realistic test data (10 CSV + 2 XES + 3 OCEL files)
✅ End-to-end user journey tests
✅ Phased implementation (7 weeks, ~40 hours)
✅ CI/CD integration
✅ Executable specifications for developers

---

## Implementation Steps

### Step 1: Create Documentation

Create `/Users/namanagarwal/system/backend/INTEGRATION_TEST_PLAN.md` with this complete plan for team reference.

### Step 2: Begin Phase 1 (Foundation)

Start implementing the test infrastructure:

1. Create directory structure in `tests/`
2. Configure `pytest.ini` with markers
3. Add new pytest plugins to `pyproject.toml`
4. Create initial CSV test data files
5. Implement priority tests for Discovery & Variants use cases

**Next Steps**: Create the test plan document in the backend folder, then begin Phase 1 implementation.
