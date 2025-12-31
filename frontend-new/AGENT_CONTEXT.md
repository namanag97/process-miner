╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
Process Mining SaaS: Architectural Improvement Plan

Vision

Transform the current codebase from a "prototype with bugs" into a production-ready SaaS platform with proper domain modeling, state machines, and data contracts.

---

Domain Model (Target State)

Bounded Contexts

┌─────────────────────────────────────────────────────────────────────────┐
│ PROCESS MINING SAAS │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│ │ Core Domain │ │ Analytics │ │ Predictions │ │
│ │ ───────────── │ │ ────────── │ │ ─────────── │ │
│ │ • EventLog │ │ • Bottlenecks │ │ • MLModel │ │
│ │ • ProcessModel │ │ • Rework │ │ • TrainingJob │ │
│ │ • Conformance │ │ • Performance │ │ • Prediction │ │
│ └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘ │
│ │ │ │ │
│ └─────────────────────┼─────────────────────┘ │
│ │ │
│ ┌────────────┴────────────┐ │
│ │ Shared Kernel │ │
│ │ ───────────── │ │
│ │ • Project │ │
│ │ • AsyncJob │ │
│ │ • DomainEvents │ │
│ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

Core Aggregates & State Machines

EventLog Aggregate

Identity: log_id (UUID)
State Machine:
┌──────────┐ ┌────────────┐ ┌─────────┐ ┌──────────┐
│ UPLOADING│────►│ VALIDATING │────►│ READY │────►│ ARCHIVED │
└──────────┘ └────────────┘ └─────────┘ └──────────┘
│ │
▼ ▼
┌──────────┐ ┌────────────┐
│ FAILED │ │ ERROR │
└──────────┘ └────────────┘

Invariants:

- Cannot run analytics unless state = READY
- Cannot delete if referenced by active predictions
- total_events must match actual event count

Domain Events:

- LogUploadStarted { log_id, filename, size }
- LogValidated { log_id, cases, events, activities }
- LogValidationFailed { log_id, errors[] }
- LogArchived { log_id, archived_by }

AsyncJob Aggregate (CRITICAL FIX)

Identity: job_id (UUID)
External Reference: task_id (Celery task ID)

State Machine:
┌─────────┐ ┌─────────┐ ┌───────────┐
│ PENDING │────►│ RUNNING │────►│ COMPLETED │
└─────────┘ └─────────┘ └───────────┘
│
▼
┌─────────┐
│ FAILED │
└─────────┘

Fields (CURRENT vs TARGET):
Current ORM: Target ORM:
───────────── ──────────────────────────────
id id
job_type job_type
status status (enum, not string)
progress progress
result_json result_json
error error
created_at created_at
updated_at updated_at
(missing) task_id ← CRITICAL: Links to Celery
(missing) parameters_json ← Job input params
(missing) started_at ← When RUNNING began
(missing) completed_at ← When terminal state

Domain Events:

- JobCreated { job_id, job_type, parameters }
- JobStarted { job_id, task_id }
- JobProgress { job_id, progress, message }
- JobCompleted { job_id, result }
- JobFailed { job_id, error }

PredictionModel Aggregate

Identity: model_id (UUID)
Reference: log_id (EventLog FK)

State Machine:
┌─────────┐ ┌──────────┐ ┌────────────┐ ┌────────┐
│ PENDING │────►│ TRAINING │────►│ EVALUATING │────►│ ACTIVE │
└─────────┘ └──────────┘ └────────────┘ └────────┘
│ │
▼ ▼
┌─────────┐ ┌────────────┐
│ FAILED │ │ DEPRECATED │
└─────────┘ └────────────┘

Invariants:

- Only ONE active model per (log_id, target_type)
- Cannot predict unless state = ACTIVE
- Must have metrics before ACTIVE

Fields (add to ORM):
status: ModelStatus enum
trained_at: datetime (null until ACTIVE)
deprecated_at: datetime (null unless DEPRECATED)
job_id: FK to AsyncJob (training job reference)

---

PART 1: Critical Schema Fixes (Backend)

1.1 AsyncJob ORM Enhancement

File: backend/src/models/orm.py (line 455)

class JobStatus(str, Enum):
"""AsyncJob state machine states."""
PENDING = "pending"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
CANCELLED = "cancelled"

class AsyncJob(Base):
"""Async job tracking with proper state machine."""
**tablename** = "async_jobs"

     # Identity
     id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

     # External reference (Celery task ID)
     task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

     # Type & State
     job_type: Mapped[str] = mapped_column(String(50), nullable=False)
     status: Mapped[str] = mapped_column(String(20), default=JobStatus.PENDING.value)
     progress: Mapped[int] = mapped_column(Integer, default=0)

     # Input/Output
     parameters_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
     result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
     error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

     # Timestamps for state transitions
     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
     started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
     completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
     updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

1.2 EventLog State Field

File: backend/src/models/orm.py (EventLog class)

Add state field for lifecycle tracking:

class LogStatus(str, Enum):
"""EventLog state machine states."""
UPLOADING = "uploading"
VALIDATING = "validating"
READY = "ready"
ERROR = "error"
ARCHIVED = "archived"

class EventLog(Base): # ... existing fields ...

     # ADD: State machine field
     status: Mapped[str] = mapped_column(String(20), default=LogStatus.READY.value)

     # ADD: Error details for failed uploads
     error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

1.3 Alembic Migration

New File: backend/alembic/versions/006_add_state_machine_fields.py

"""Add state machine fields to AsyncJob and EventLog.

Revision ID: 006
"""
from alembic import op
import sqlalchemy as sa

def upgrade(): # AsyncJob enhancements
op.add_column('async_jobs', sa.Column('task_id', sa.String(255), unique=True, nullable=True))
op.add_column('async_jobs', sa.Column('parameters_json', sa.Text(), nullable=True))
op.add_column('async_jobs', sa.Column('started_at', sa.DateTime(), nullable=True))
op.add_column('async_jobs', sa.Column('completed_at', sa.DateTime(), nullable=True))
op.create_index('ix_async_jobs_task_id', 'async_jobs', ['task_id'])

     # EventLog state field
     op.add_column('event_logs', sa.Column('status', sa.String(20), server_default='ready'))
     op.add_column('event_logs', sa.Column('error_message', sa.Text(), nullable=True))

def downgrade():
op.drop_column('async_jobs', 'task_id')
op.drop_column('async_jobs', 'parameters_json')
op.drop_column('async_jobs', 'started_at')
op.drop_column('async_jobs', 'completed_at')
op.drop_column('event_logs', 'status')
op.drop_column('event_logs', 'error_message')

1.4 Fix Predictions Router Query

File: backend/src/api/routers/predictions.py (line 169)

# BEFORE (bug):

query = select(AsyncJob).where(AsyncJob.id == job_id)

# AFTER (fix):

query = select(AsyncJob).where(AsyncJob.task_id == job_id)

---

PART 2: API Contract Standardization

2.1 Response Envelope Pattern

New File: backend/src/models/response.py

from typing import TypeVar, Generic, Optional
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')

class ResponseMeta(BaseModel):
"""Metadata for all API responses."""
request_id: str
timestamp: datetime
version: str = "1.0"

class APIResponse(BaseModel, Generic[T]):
"""Standard response envelope for all endpoints."""
success: bool
data: Optional[T] = None
error: Optional[dict] = None
meta: ResponseMeta

2.2 Variant Response Enhancement

File: backend/src/models/schemas.py (VariantResponse)

class VariantResponse(BaseModel):
"""Variant with both string trace and parsed activities array."""
variant_key: str
activity_trace: str # "A → B → C" (for display)
activities: list[str] # ["A", "B", "C"] (for FE consumption)
case_count: int
frequency_percent: float
avg_duration_seconds: Optional[float] = None
complexity_score: Optional[float] = None
rework_count: Optional[int] = None

2.3 Backend Service Update

File: backend/src/api/routers/processes.py (get_variants function)

Add activities array parsing in backend instead of relying on fragile FE parsing:

def build_variant_response(variant_key: str, trace: str, ...) -> VariantResponse:
"""Build variant response with parsed activities.""" # Parse activities from trace using standard separator
activities = trace.split(" → ") if " → " in trace else [trace]

     return VariantResponse(
         variant_key=variant_key,
         activity_trace=trace,
         activities=activities,  # Pre-parsed for FE
         case_count=case_count,
         frequency_percent=frequency_percent,
         # ...
     )

---

PART 3: Frontend Architecture Fixes

3.1 Create AI Feature Hooks (Proper Pattern)

New File: frontend-new/src/features/ai/hooks/index.ts

import { createQueryHook, createMutationHook } from '@/core';

// Process list for AI features
export const useAIProcesses = createQueryHook<ProcessListResponse, void>({
queryKey: () => ['ai', 'processes'],
queryFn: async (sdk) => sdk.processes.list({ pageSize: 100 }),
staleTime: 5 _ 60 _ 1000,
});

// Process summary for selected process
export const useAIProcessSummary = createQueryHook<ProcessSummary, string>({
queryKey: (logId) => ['ai', 'summary', logId],
queryFn: async (sdk, logId) => sdk.analytics.getProcessSummary(logId),
enabled: (logId) => !!logId && logId.length > 0,
staleTime: 5 _ 60 _ 1000,
});

// Predictions for a process
export const useAIPredictions = createQueryHook<Prediction[], string>({
queryKey: (logId) => ['ai', 'predictions', logId],
queryFn: async (sdk, logId) => sdk.predictions.list(logId),
enabled: (logId) => !!logId,
});

3.2 Refactor AIAssistantPage (Remove Anti-Pattern)

File: frontend-new/src/features/ai/pages/AIAssistantPage.tsx

Replace lines 55-117 (manual useEffect/useState) with hooks:

// BEFORE (anti-pattern):
const [processes, setProcesses] = useState<ProcessOption[]>([]);
const [processesLoading, setProcessesLoading] = useState(true);
useEffect(() => {
async function loadProcesses() { ... }
loadProcesses();
}, [sdk]);

// AFTER (proper pattern):
const {
data: processesData,
isLoading: processesLoading,
error: processesError,
refetch: refetchProcesses
} = useAIProcesses();

const {
data: processSummary,
isLoading: summaryLoading,
error: summaryError
} = useAIProcessSummary(selectedProcessId || '');

const processes = useMemo(() =>
processesData?.items.map(p => ({
id: p.id,
name: p.name,
totalCases: p.totalCases,
totalActivities: p.totalActivities,
sourceFormat: p.sourceFormat,
})) ?? [],
[processesData]
);

3.3 Add Error Handling UI

File: frontend-new/src/features/ai/pages/AIAssistantPage.tsx

Add proper error states:

// After the empty state check, add error handling:
if (processesError) {
return (
<FeaturePage
       title="AI Assistant"
       error={processesError}
       onRetry={refetchProcesses}
     />
);
}

3.4 Navigation Path Updates

| File                                                 | Line           | Change                          |
| ---------------------------------------------------- | -------------- | ------------------------------- |
| src/pages/questions/questionsData.ts                 | 25,32,39,46,53 | /projects/ → /workspace/        |
| src/pages/questions/ProcessQuestionsPage.tsx         | 76,87,88       | /projects/, /home → /workspace/ |
| src/features/projects/components/DataSourcesList.tsx | 29             | /projects/ → /workspace/        |
| src/features/projects/components/ProjectCard.tsx     | 26             | /projects/ → /workspace/        |

3.5 Fix Upload Navigation (Replace with /workspace)

| File                                              | Line | Change                 |
| ------------------------------------------------- | ---- | ---------------------- |
| src/features/explorer/pages/ExplorerIndexPage.tsx | 57   | navigate('/workspace') |
| src/features/ai/pages/AIAssistantPage.tsx         | 204  | navigate('/workspace') |
| src/features/ai/pages/AIInsightsPage.tsx          | 189  | navigate('/workspace') |
| src/features/ai/pages/PredictionsPage.tsx         | 253  | navigate('/workspace') |
| src/features/analytics/pages/AnalyticsPage.tsx    | 188  | navigate('/workspace') |

3.6 Fix window.location.href (SPA Anti-Pattern)

| File                | Line | Current                      | Fix                            |
| ------------------- | ---- | ---------------------------- | ------------------------------ |
| AIAssistantPage.tsx | 204  | window.location.href = '...' | navigate('/workspace')         |
| ConformanceTab.tsx  | 216  | window.location.href = '...' | navigate(\/explorer/${logId})` |

---

PART 4: Cleanup Legacy Code

4.1 Remove Legacy Exports

File: frontend-new/src/pages/index.ts

Delete these exports (features migrated to /features/):
// DELETE:
export { HomePage } from './home';
export { ProcessExplorerIndexPage, ProcessExplorerPage } from './explorer';
export { AnalyticsPage } from './analytics';
export { AIIndexPage, AIInsightsPage, AIAssistantPage, PredictionsPage, PredictorDetailPage } from './ai';
export { ProjectDetailPage } from './projects';
export { KPIPage } from './kpi';

4.2 Delete Legacy Directories

rm -rf frontend-new/src/pages/home/ # 4 files
rm -rf frontend-new/src/pages/projects/ # 3 files
rm -rf frontend-new/src/pages/explorer/ # 20 files
rm -rf frontend-new/src/pages/kpi/ # 7 files
rm -rf frontend-new/src/pages/analytics/ # 9 files
rm -rf frontend-new/src/pages/ai/ # 11 files

---

Implementation Order

Sprint 1: Critical Fixes (Days 1-2)

1.  Add AsyncJob fields to ORM (task_id, parameters_json, started_at, completed_at)
2.  Add EventLog status field to ORM
3.  Create alembic migration
4.  Run migration
5.  Fix predictions.py query bug (AsyncJob.task_id)
6.  Add activities array to VariantResponse
7.  Verify backend starts without errors

Sprint 2: Frontend Fixes (Days 3-4)

8.  Create AI feature hooks (src/features/ai/hooks/index.ts)
9.  Refactor AIAssistantPage to use hooks
10. Add error handling UI to AIAssistantPage
11. Update 10 path references (/projects/ → /workspace/)
12. Fix 5 upload navigation paths
13. Fix 2 window.location.href usages
14. Verify FE builds: npx nx build frontend-new

Sprint 3: Cleanup (Day 5)

15. Remove legacy exports from pages/index.ts
16. Delete 6 legacy directories (~54 files)
17. Final verification
18. Integration test: FE + BE together

---

Files Modified

Backend (5 files)

| File                           | Type   | Changes                                     |
| ------------------------------ | ------ | ------------------------------------------- |
| src/models/orm.py              | MODIFY | Add AsyncJob fields, EventLog status, enums |
| src/api/routers/predictions.py | MODIFY | Fix task_id query (line 169)                |
| src/api/routers/processes.py   | MODIFY | Add activities array to variants            |
| src/models/schemas.py          | MODIFY | Add activities field to VariantResponse     |
| alembic/versions/006\_\*.py    | CREATE | Migration for new fields                    |

Frontend (14 files)

| File                                                 | Type   | Changes                    |
| ---------------------------------------------------- | ------ | -------------------------- |
| src/features/ai/hooks/index.ts                       | CREATE | AI feature hooks           |
| src/features/ai/pages/AIAssistantPage.tsx            | MODIFY | Refactor to hooks, fix nav |
| src/features/ai/pages/AIInsightsPage.tsx             | MODIFY | Fix upload nav             |
| src/features/ai/pages/PredictionsPage.tsx            | MODIFY | Fix upload nav             |
| src/features/analytics/pages/AnalyticsPage.tsx       | MODIFY | Fix upload nav             |
| src/features/analytics/components/ConformanceTab.tsx | MODIFY | Fix window.location        |
| src/features/explorer/pages/ExplorerIndexPage.tsx    | MODIFY | Fix upload nav             |
| src/features/projects/components/DataSourcesList.tsx | MODIFY | Path update                |
| src/features/projects/components/ProjectCard.tsx     | MODIFY | Path update                |
| src/pages/questions/questionsData.ts                 | MODIFY | 5 path updates             |
| src/pages/questions/ProcessQuestionsPage.tsx         | MODIFY | 3 path updates             |
| src/pages/index.ts                                   | MODIFY | Remove legacy exports      |
| libs/shared/design-system/src/api/transformers.ts    | MODIFY | Handle activities array    |

Files Deleted (~54 files)

- src/pages/home/ (4 files)
- src/pages/projects/ (3 files)
- src/pages/explorer/ (20 files)
- src/pages/kpi/ (7 files)
- src/pages/analytics/ (9 files)
- src/pages/ai/ (11 files)

---

Verification

# Backend

cd backend
alembic upgrade head
python -m pytest tests/ -v
uvicorn src.api.main:app --port 8001

# Frontend

cd frontend-new
npx nx build frontend-new

# Check for legacy paths

grep -r "'/projects/" src/
grep -r "'/home" src/
grep -r "'/processes/upload" src/
grep -r "window.location.href" src/features/

# Integration

# Start BE on 8001, FE on 4200

# Navigate through: /workspace → project → data → explorer

---

Success Criteria

| #   | Criterion                      | Verification                                         |
| --- | ------------------------------ | ---------------------------------------------------- |
| 1   | AsyncJob has task_id field     | alembic current shows migration applied              |
| 2   | Job status query works         | GET /predictions/jobs/{id} returns data              |
| 3   | Variants have activities array | GET /processes/{id}/variants includes activities: [] |
| 4   | FE builds without errors       | npx nx build frontend-new exits 0                    |
| 5   | No legacy paths in code        | grep commands return empty                           |
| 6   | AIAssistantPage shows errors   | Trigger network error, see error UI                  |
| 7   | Navigation works end-to-end    | Manual test through app                              |

---

User Decisions

| Decision                   | Choice              | Rationale                                                           |
| -------------------------- | ------------------- | ------------------------------------------------------------------- |
| Variant activities parsing | Backend fix         | Add activities: list[str] to VariantResponse - cleaner API contract |
| EventLog state machine     | Full implementation | Add status enum with enforcement in services                        |

---

Future Architecture (Not This Sprint)

For next phase, consider:

- Multi-tenancy: Add tenant_id to all tables
- Domain Events: Implement event bus for LogUploaded, ModelTrained, etc.
- Usage Metering: Track events_processed, predictions_made for billing
- Rate Limiting: Protect expensive endpoints (/upload, /train)
- Audit Logging: Track all write operations
- Soft Deletes: Replace hard deletes with deleted_at timestamps
