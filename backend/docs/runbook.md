# Temporal Operational Runbook

Operational procedures for managing Temporal workflows in the Process Mining platform.

## Quick Reference

| Command | Description |
|---------|-------------|
| `make temporal-up` | Start Temporal server (Docker) |
| `make temporal-workers` | Start all workers |
| `make temporal-ingestion-worker` | Start ingestion worker only |
| `make temporal-analysis-worker` | Start analysis worker only |
| `make temporal-stop` | Stop Temporal server |

---

## 1. Local Development Setup

### Start Temporal Server

```bash
cd backend
make temporal-up
```

The Temporal Web UI is available at: **http://localhost:8088**

### Start Workers

```bash
# All workers
make temporal-workers

# Individual workers
make temporal-ingestion-worker   # For dataset processing
make temporal-analysis-worker    # For process mining
```

### Verify Setup

```bash
# Check Temporal server status
temporal server status

# List running workflows
temporal workflow list --namespace default
```

---

## 2. Workflow Management

### View Running Workflows

1. Open Temporal UI: http://localhost:8088
2. Select namespace "default"
3. Browse active workflows

Or via CLI:
```bash
temporal workflow list --namespace default
```

### Get Workflow Details

```bash
temporal workflow describe --workflow-id <workflow-id>
```

### Cancel a Workflow

```bash
temporal workflow cancel --workflow-id <workflow-id>
```

### Terminate a Workflow (Force)

```bash
temporal workflow terminate --workflow-id <workflow-id> --reason "Manual termination"
```

---

## 3. Worker Management

### Worker Queues

| Queue | Worker | Purpose |
|-------|--------|---------|
| `ingestion-queue` | ingestion_worker.py | Dataset validation, parsing, ingestion |
| `analysis-queue` | analysis_worker.py | Process discovery, conformance |

### Check Worker Health

```bash
# View worker activity in Temporal UI
# Workers → Task Queues → Select queue
```

### Restart Workers

```bash
# Stop workers
Ctrl+C

# Restart
make temporal-workers
```

---

## 4. Troubleshooting

### Workflow Stuck - Not Progressing

**Symptoms**: Workflow status shows "Running" but no progress

**Checks**:
1. Is worker running? Check `make temporal-workers` output
2. Correct task queue? Verify workflow task queue matches worker
3. Activity timeout? Check Temporal UI for activity details

**Resolution**:
```bash
# Restart workers
make temporal-workers
```

### Activity Failing Repeatedly

**Symptoms**: Activity retrying multiple times

**Checks**:
1. View activity error in Temporal UI → Workflow → History
2. Check worker logs for exception details

**Resolution**:
- Fix underlying issue (DB connection, service error)
- For permanent failures, cancel workflow

### Worker Crash Recovery

**Temporal automatically handles this**:
1. Workflow state is persisted in Temporal server
2. When new worker starts, it picks up from last heartbeat
3. Long-running activities resume from checkpoint

**If workflow doesn't resume**:
```bash
# Check workflow status
temporal workflow describe --workflow-id <id>

# View history for failures
temporal workflow show --workflow-id <id>
```

---

## 5. Configuration

### Environment Variables

```bash
# Toggle Temporal vs Celery
USE_TEMPORAL=true           # Enable Temporal
USE_TEMPORAL=false          # Use Celery (default)

# Temporal connection
TEMPORAL_HOST=localhost
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=default
```

### Worker Concurrency

Edit `src/platform/temporal/config.py`:
```python
max_concurrent_activities: int = 3
max_cached_workflows: int = 100
```

---

## 6. Monitoring

### Temporal Web UI

- **Workflows**: Active/completed workflow list
- **Task Queues**: Worker activity per queue
- **Schedules**: Scheduled workflow runs

### Key Metrics to Watch

| Metric | Healthy | Action if Unhealthy |
|--------|---------|---------------------|
| Workflow completion rate | >99% | Investigate failures |
| Activity failure rate | <5% | Check worker logs |
| Task queue backlog | <10 | Scale workers |
| Workflow latency | <target SLA | Optimize activities |

---

## 7. Common Scenarios

### Reprocess Failed Dataset

```python
from src.platform.temporal import dispatch_workflow

await dispatch_workflow(
    workflow_type="dataset_ingestion",
    args={
        "dataset_id": "...",
        "storage_key": "...",
        ...
    }
)
```

### Check Workflow Result

```python
from src.platform.temporal.compat import get_workflow_status

status = await get_workflow_status("workflow-id")
print(status)
```

---

## 8. Production Considerations

> [!IMPORTANT]
> For production, consider using Temporal Cloud or self-hosted cluster instead of `temporal server start-dev`.

### Production Checklist

- [ ] Use Temporal Cloud or production cluster
- [ ] Configure PostgreSQL/MySQL for Temporal persistence (not SQLite)
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure alerting for workflow failures
- [ ] Set appropriate retention policies
- [ ] Enable mTLS for security
