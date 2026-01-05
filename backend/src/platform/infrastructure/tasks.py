"""Celery task configuration and async task definitions.

Provides background task execution for:
- ML model training (predictions)
- Long-running analytics operations
- Batch processing workflows
"""

import asyncio
import time
from datetime import datetime
from typing import Any

import structlog
from celery import Celery, Task
from celery.result import AsyncResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.platform.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Celery app configuration
celery_app = Celery(
    "process_mining",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,
)


# Async database session for tasks
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class AsyncTask(Task):
    """Base task class with async support."""

    def __call__(self, *args, **kwargs):
        """Run async function in event loop."""
        # Celery binds the decorated async function to self.run
        return asyncio.run(self.run(*args, **kwargs))

    async def run(self, *args, **kwargs):
        """Standard Celery method, implementing classes should override."""
        raise NotImplementedError


@celery_app.task(bind=True, base=AsyncTask, name="train_prediction_model")
async def train_prediction_model_task(
    self,
    log_id: str,
    target_type: str,
    algorithm: str = "random_forest",
    **params: Any,
) -> dict[str, Any]:
    """Async task for training ML prediction models.

    Args:
        log_id: Event log ID to train on
        target_type: Type of prediction ('next_activity' or 'remaining_time')
        algorithm: ML algorithm to use
        **params: Additional training parameters

    Returns:
        dict with model_id, metrics, and training info
    """
    logger.info(
        "prediction_training_started",
        log_id=log_id,
        target_type=target_type,
        algorithm=algorithm,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        # Update task state to PROGRESS
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Loading event log",
                "progress": 10,
                "started_at": datetime.utcnow().isoformat(),
            },
        )

        async with AsyncSessionLocal() as db:
            # Import here to avoid circular dependencies
            from src.features.process_mining.models import Dataset, PredictionModel
            from src.features.process_mining.services.loader import event_log_loader
            from src.features.process_mining.services.prediction import prediction_service
            from src.platform.models import AsyncJob

            # Verify dataset exists
            result = await db.execute(select(Dataset).where(Dataset.id == log_id))
            dataset = result.scalar_one_or_none()

            if not dataset:
                raise ValueError(f"Dataset not found: {log_id}")

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Converting to PM4Py format",
                    "progress": 20,
                },
            )

            # Convert to PM4Py log (Synchronous DuckDB load)
            # Note: We call sync function directly since we are in a task runner
            pm4py_log = event_log_loader.load_as_pm4py_log(log_id)

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": f"Training {algorithm} model",
                    "progress": 40,
                },
            )

            # Train model based on target type
            if target_type == "next_activity":
                model_info = prediction_service.train_next_activity_model(
                    pm4py_log=pm4py_log,
                    algorithm=algorithm,
                    **params,
                )
            elif target_type == "remaining_time":
                model_info = prediction_service.train_remaining_time_model(
                    pm4py_log=pm4py_log,
                    algorithm=algorithm,
                    **params,
                )
            else:
                raise ValueError(f"Unknown target type: {target_type}")

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Saving model to database",
                    "progress": 80,
                },
            )

            # Save model to database
            # BUG-047 FIX: Use correct field names (dataset_id, target_type not log_id, model_type)
            db_model = PredictionModel(
                dataset_id=log_id,  # ORM field is dataset_id
                target_type=target_type,  # ORM field is target_type, not model_type
                algorithm=algorithm,
                model_binary=model_info["model_binary"],
                metrics_json=model_info.get("metrics_json"),
                trained_at=datetime.utcnow(),
            )
            db.add(db_model)

            # Update async job status
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "completed"
                job.result_json = str({"model_id": db_model.id})
                job.completed_at = datetime.utcnow()

            await db.commit()
            await db.refresh(db_model)

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "prediction_training_completed",
                model_id=db_model.id,
                target_type=target_type,
                algorithm=algorithm,
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "model_id": db_model.id,
                "log_id": log_id,
                "target_type": target_type,
                "algorithm": algorithm,
                "metrics": model_info.get("metrics", {}),
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error(
            "prediction_training_failed",
            error=str(e),
            log_id=log_id,
            target_type=target_type,
            task_id=self.request.id,
        )

        # Update async job status
        async with AsyncSessionLocal() as db:
            from src.platform.models import AsyncJob

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                await db.commit()

        raise


@celery_app.task(bind=True, base=AsyncTask, name="ingest_dataset")
async def ingest_dataset_task(
    self,
    dataset_id: str,
    mapping: dict[str, str],
) -> dict[str, Any]:
    """Async task for background dataset ingestion.

    Phase 2 of deferred ingestion:
    1. Load raw file from storage
    2. Parse with DuckDB (vectorized)
    3. Compute variants and statistics
    4. Bulk insert cases/events to DB
    5. Update dataset status to READY

    Args:
        dataset_id: Dataset ID to ingest
        mapping: Column mapping dict with case_id_column, activity_column, etc.

    Returns:
        dict with dataset_id, stats, and duration info
    """
    logger.info(
        "ingest_dataset_task_started",
        dataset_id=dataset_id,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Loading file", "progress": 5},
        )

        async with AsyncSessionLocal() as db:
            import json

            from src.features.process_mining.models import (
                Dataset,
                DatasetStatus,
                ProcessCase,
                ProcessEvent,
                UploadedFile,
            )
            from src.features.process_mining.services.ingestion.duckdb import (
                duckdb_ingestion_service,
            )
            from src.platform.models import AsyncJob
            from src.platform.storage.storage import storage_service

            # Load dataset and file
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            result = await db.execute(
                select(UploadedFile).where(UploadedFile.dataset_id == dataset_id)
            )
            uploaded_file = result.scalar_one_or_none()
            if not uploaded_file:
                raise ValueError(f"No uploaded file for dataset: {dataset_id}")

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Reading file from storage", "progress": 10},
            )

            # Read file content
            file_content = await storage_service.backend.retrieve(
                f"{dataset_id}/{uploaded_file.filename}"
            )

            # Update progress with stage
            self.update_state(
                state="PROGRESS",
                meta={"status": "Parsing with DuckDB", "progress": 20, "stage": "parsing"},
            )

            # Update job with stage
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "running"
                job.started_at = datetime.utcnow() if not job.started_at else job.started_at
                job.stage = "parsing"
                job.progress = 20
                job.entity_type = "dataset"
                job.entity_id = dataset_id
                await db.flush()

            # Parse with DuckDB
            duck_result = duckdb_ingestion_service.parse_csv_fast(
                file_content=file_content,
                case_id_col=mapping.get("case_id_column", "case_id"),
                activity_col=mapping.get("activity_column", "activity"),
                timestamp_col=mapping.get("timestamp_column", "timestamp"),
                resource_col=mapping.get("resource_column"),
            )

            stats = duck_result["statistics"]
            cases_arrow = duck_result["cases_arrow"]

            # Update progress with stage
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Creating cases and events",
                    "progress": 50,
                    "stage": "creating_entities",
                },
            )
            if job:
                job.stage = "creating_entities"
                job.progress = 50
                await db.flush()

            # BUG-049 FIX: Use Arrow batches instead of to_pandas() to reduce memory 3x
            # Convert Arrow to batches for memory-efficient iteration
            import pyarrow as pa

            cases_arrow = duck_result["cases_arrow"]
            if isinstance(cases_arrow, pa.RecordBatchReader):
                cases_arrow = cases_arrow.read_all()

            events_arrow = duck_result["events_arrow"]
            if isinstance(events_arrow, pa.RecordBatchReader):
                events_arrow = events_arrow.read_all()

            # BUG-061 FIX: Process cases in chunks and flush to avoid memory bloat in ORM session
            case_id_map = {}
            for batch in cases_arrow.to_batches(max_chunksize=5000):
                batch_dict = {col: batch.column(col).to_pylist() for col in batch.schema.names}
                batch_cases = []
                for i in range(batch.num_rows):
                    case = ProcessCase(
                        dataset_id=dataset_id,
                        case_id=str(batch_dict["case_id"][i]),
                        variant_key=batch_dict["variant"][i],
                        start_time=batch_dict["start_time"][i],
                        end_time=batch_dict["end_time"][i],
                    )
                    batch_cases.append(case)

                db.add_all(batch_cases)
                await db.flush()

                # Update map for events reference
                for c in batch_cases:
                    case_id_map[c.case_id] = c.id

                # Clear session to free memory
                db.expunge_all()

            # Update progress with stage
            self.update_state(
                state="PROGRESS",
                meta={"status": "Creating events", "progress": 70, "stage": "creating_events"},
            )
            if job:
                job.stage = "creating_events"
                job.progress = 70
                await db.flush()

            # BUG-061 FIX: Process events in chunks and flush to avoid memory bloat
            for batch in events_arrow.to_batches(max_chunksize=10000):
                batch_dict = {col: batch.column(col).to_pylist() for col in batch.schema.names}
                batch_events = []
                for i in range(batch.num_rows):
                    case_ref_id = case_id_map.get(str(batch_dict["case_id"][i]))
                    if case_ref_id:
                        resource = batch_dict.get("resource", [None] * batch.num_rows)[i]
                        event = ProcessEvent(
                            case_ref_id=case_ref_id,
                            activity=str(batch_dict["activity"][i]),
                            timestamp=batch_dict["timestamp"][i],
                            resource=str(resource) if resource else None,
                        )
                        batch_events.append(event)

                if batch_events:
                    db.add_all(batch_events)
                    await db.flush()
                    db.expunge_all()

            # Update progress with stage
            self.update_state(
                state="PROGRESS",
                meta={"status": "Computing statistics", "progress": 90, "stage": "computing_stats"},
            )
            if job:
                job.stage = "computing_stats"
                job.progress = 90
                await db.flush()

            # Re-fetch dataset after session clear
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()

            # Update dataset with stats
            dataset.total_cases = stats["total_cases"]
            dataset.total_events = stats["total_events"]
            dataset.total_activities = stats["total_activities"]
            dataset.activities_json = json.dumps(stats.get("activities", []))
            dataset.statistics_json = json.dumps(stats)
            dataset.status = DatasetStatus.READY.value
            dataset.error_message = None

            # Update AsyncJob
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "completed"
                job.progress = 100
                job.result_json = json.dumps(
                    {
                        "dataset_id": dataset_id,
                        "total_cases": stats["total_cases"],
                        "total_events": stats["total_events"],
                    }
                )
                job.completed_at = datetime.utcnow()

            await db.commit()

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "ingest_dataset_task_completed",
                dataset_id=dataset_id,
                total_cases=stats["total_cases"],
                total_events=stats["total_events"],
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "dataset_id": dataset_id,
                "total_cases": stats["total_cases"],
                "total_events": stats["total_events"],
                "total_activities": stats["total_activities"],
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error(
            "ingest_dataset_task_failed",
            error=str(e),
            dataset_id=dataset_id,
            task_id=self.request.id,
        )

        # Update dataset and job status
        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.platform.models import AsyncJob

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = str(e)

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()

            await db.commit()

        raise


@celery_app.task(bind=True, base=AsyncTask, name="validate_dataset")
async def validate_dataset_task(
    self,
    dataset_id: str,
    job_id: str,
) -> dict[str, Any]:
    """Job-Centric Architecture: Async task for CSV validation and column detection.

    Phase 1 of deferred ingestion:
    1. Load raw file from storage
    2. Detect columns using unified ingestion service
    3. Compute AI column suggestions
    4. Update dataset with detected columns and status=AWAITING_MAPPING

    Args:
        dataset_id: Dataset ID to validate
        job_id: Job ID for progress tracking

    Returns:
        dict with detected columns and suggestions
    """
    logger.info(
        "validate_dataset_task_started",
        dataset_id=dataset_id,
        job_id=job_id,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Loading file", "progress": 10, "stage": "loading"},
        )

        async with AsyncSessionLocal() as db:
            import json

            from src.features.process_mining.models import (
                Dataset,
                DatasetStatus,
                UploadedFile,
            )
            from src.features.process_mining.services.ingestion.unified import (
                unified_ingestion_service,
            )
            from src.platform.core.enums import JobStatus
            from src.platform.models import AsyncJob
            from src.platform.storage.storage import storage_service

            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            # Load uploaded file
            result = await db.execute(
                select(UploadedFile).where(UploadedFile.dataset_id == dataset_id)
            )
            uploaded_file = result.scalar_one_or_none()
            if not uploaded_file:
                raise ValueError(f"No uploaded file for dataset: {dataset_id}")

            # Update job progress
            job = await db.get(AsyncJob, job_id)
            if job:
                job.status = JobStatus.RUNNING.value
                job.started_at = datetime.utcnow()
                job.stage = "loading"
                job.progress = 10
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Reading file from storage", "progress": 20, "stage": "reading"},
            )

            # Read file content
            file_content = await storage_service.backend.retrieve(
                f"{dataset_id}/{uploaded_file.filename}"
            )

            # Update job
            if job:
                job.stage = "detecting_columns"
                job.progress = 40
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Detecting columns", "progress": 40, "stage": "detecting_columns"},
            )

            # Detect columns using unified service
            detection_result = unified_ingestion_service.detect_columns(
                file_content, uploaded_file.filename
            )

            columns = detection_result.get("columns", [])
            suggestions = detection_result.get("suggestions", {})
            row_count = detection_result.get("row_count", 0)

            # Update job
            if job:
                job.stage = "computing_suggestions"
                job.progress = 70
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Computing suggestions",
                    "progress": 70,
                    "stage": "computing_suggestions",
                },
            )

            # Update dataset with detection results
            dataset.detected_columns_json = json.dumps(columns)
            dataset.column_suggestions_json = json.dumps(suggestions)
            dataset.file_size_bytes = len(file_content)
            dataset.status = DatasetStatus.AWAITING_MAPPING.value
            dataset.validation_job_id = job_id
            dataset.error_message = None
            dataset.updated_at = datetime.utcnow()

            # Complete job
            if job:
                job.status = JobStatus.COMPLETED.value
                job.progress = 100
                job.stage = "completed"
                job.entity_id = dataset_id
                job.result_json = json.dumps(
                    {
                        "dataset_id": dataset_id,
                        "columns": columns,
                        "suggestions": suggestions,
                        "row_count": row_count,
                    }
                )
                job.completed_at = datetime.utcnow()

            await db.commit()

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "validate_dataset_task_completed",
                dataset_id=dataset_id,
                columns_found=len(columns),
                row_count=row_count,
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "dataset_id": dataset_id,
                "columns": columns,
                "suggestions": suggestions,
                "row_count": row_count,
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error(
            "validate_dataset_task_failed",
            error=str(e),
            dataset_id=dataset_id,
            task_id=self.request.id,
        )

        # Update dataset and job status
        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.platform.core.enums import JobStatus
            from src.platform.models import AsyncJob

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = str(e)

            job = await db.get(AsyncJob, job_id)
            if job:
                job.status = JobStatus.FAILED.value
                job.error = str(e)
                job.completed_at = datetime.utcnow()

            await db.commit()

        raise


@celery_app.task(
    bind=True, base=AsyncTask, name="perform_analysis", time_limit=600, soft_time_limit=540
)
async def perform_analysis_task(
    self,
    analysis_id: str,
    log_id: str,
    analysis_type: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Async task for performing process analysis.

    Executes CPU-intensive process mining algorithms in background to prevent
    blocking the API server. Updates the Analysis record with results when complete.

    Args:
        analysis_id: Analysis record ID
        log_id: Dataset ID to analyze
        analysis_type: Type of analysis (discovery, variants, statistics)
        config: Optional configuration dict

    Returns:
        dict with analysis results and duration info
    """
    logger.info(
        "perform_analysis_task_started",
        analysis_id=analysis_id,
        log_id=log_id,
        analysis_type=analysis_type,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    if config is None:
        config = {}

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Starting analysis", "progress": 5},
        )

        async with AsyncSessionLocal() as db:
            import json

            from src.features.process_mining.models import Analysis, AnalysisStatus, AnalysisType
            from src.features.process_mining.services.mining import mining_service

            # Load analysis record
            result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
            analysis = result.scalar_one_or_none()
            if not analysis:
                raise ValueError(f"Analysis not found: {analysis_id}")

            # Update status to RUNNING
            analysis.status = AnalysisStatus.RUNNING.value
            await db.flush()

            # Progress updates
            self.update_state(
                state="PROGRESS",
                meta={"status": f"Running {analysis_type} analysis", "progress": 20},
            )

            # Perform the analysis based on type
            result_data = {}

            if analysis_type == AnalysisType.DISCOVERY.value:
                # Get DFG for discovery
                dfg_data = mining_service.get_dfg_fast(log_id)
                result_data["dfg"] = dfg_data

                analysis.result_summary_json = json.dumps(
                    {
                        "nodes_count": len(dfg_data.get("nodes", [])),
                        "edges_count": len(dfg_data.get("edges", [])),
                        "start_activities": list(dfg_data.get("start_activities", {}).keys()),
                        "end_activities": list(dfg_data.get("end_activities", {}).keys()),
                    }
                )

            elif analysis_type == AnalysisType.VARIANTS.value:
                # Get variants
                self.update_state(
                    state="PROGRESS",
                    meta={"status": "Computing variants", "progress": 50},
                )
                variants_data = mining_service.get_variants_fast(log_id, top_n=50)
                result_data["variants"] = variants_data

                analysis.result_summary_json = json.dumps(
                    {
                        "total_variants": variants_data.get("total_variants", 0),
                        "top_variant": variants_data.get("top_variants", [{}])[0]
                        if variants_data.get("top_variants")
                        else None,
                    }
                )

            else:
                # Generic: get statistics
                self.update_state(
                    state="PROGRESS",
                    meta={"status": "Computing statistics", "progress": 50},
                )
                stats = mining_service.get_statistics_fast(log_id)
                result_data["statistics"] = stats
                analysis.result_summary_json = json.dumps(stats)

            # Store full results in result_json for future retrieval
            analysis.result_json = json.dumps(result_data)
            analysis.status = AnalysisStatus.COMPLETED.value
            analysis.completed_at = datetime.utcnow()

            await db.commit()

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "perform_analysis_task_completed",
                analysis_id=analysis_id,
                analysis_type=analysis_type,
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "analysis_id": analysis_id,
                "log_id": log_id,
                "analysis_type": analysis_type,
                "status": "completed",
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error(
            "perform_analysis_task_failed",
            error=str(e),
            analysis_id=analysis_id,
            task_id=self.request.id,
        )

        # Update analysis status to FAILED
        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Analysis, AnalysisStatus

            result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
            analysis = result.scalar_one_or_none()
            if analysis:
                analysis.status = AnalysisStatus.FAILED.value
                analysis.error_message = str(e)
                analysis.completed_at = datetime.utcnow()
                await db.commit()

        raise


@celery_app.task(
    bind=True, base=AsyncTask, name="perform_discovery", time_limit=900, soft_time_limit=840
)
async def perform_discovery_task(
    self,
    log_id: str,
    miner_type: str,
    model_name: str | None = None,
) -> dict[str, Any]:
    """BUG-054 FIX: Async task for process discovery to prevent API thread blocking.

    Runs heavy PM4Py miners (Alpha, Inductive, ILP) in background.

    Args:
        log_id: Dataset ID to mine
        miner_type: Mining algorithm type (alpha, inductive, heuristic, ilp)
        model_name: Optional name for the discovered model

    Returns:
        dict with model_id and quality metrics
    """
    logger.info(
        "discovery_task_started",
        log_id=log_id,
        miner_type=miner_type,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Loading dataset", "progress": 10, "stage": "loading"},
        )

        async with AsyncSessionLocal() as db:
            from src.features.process_mining.enums import MinerType
            from src.features.process_mining.models import Dataset, ProcessModel
            from src.features.process_mining.services.mining import mining_service
            from src.platform.models import AsyncJob

            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == log_id))
            dataset = result.scalar_one_or_none()

            if not dataset:
                raise ValueError(f"Dataset not found: {log_id}")

            # Update job with stage
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                from src.platform.core.enums import JobStatus

                job.status = JobStatus.RUNNING.value
                job.started_at = datetime.utcnow() if not job.started_at else job.started_at
                job.stage = "mining"
                job.progress = 30
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": f"Running {miner_type} miner", "progress": 30, "stage": "mining"},
            )

            # Run discovery (synchronous PM4Py call)
            try:
                miner_enum = MinerType(miner_type)
            except ValueError:
                raise ValueError(f"Invalid miner type: {miner_type}")

            model_data, model_format = mining_service.discover(dataset, miner_enum)

            if job:
                job.stage = "serializing"
                job.progress = 70
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Serializing model", "progress": 70, "stage": "serializing"},
            )

            # Serialize model (legacy pickle for backward compatibility)
            serialized = mining_service.serialize_model(model_data)
            final_name = model_name or f"{dataset.name}_{miner_type}"

            # Generate graph JSON for frontend visualization (new architecture)
            graph_json = mining_service.serialize_to_graph_json(model_data, model_format)
            graph_structure_json = None
            if graph_json:
                import json

                graph_structure_json = json.dumps(graph_json)

            # Calculate quality metrics if possible
            fitness = None
            precision = None
            if model_format.value in ["petri_net", "process_tree"]:
                try:
                    if model_format.value == "petri_net":
                        net, im, fm = model_data
                    else:
                        net, im, fm = mining_service.tree_to_petri_net(model_data)
                    fitness_result = mining_service.evaluate_fitness(dataset, net, im, fm)
                    fitness = fitness_result.get("fitness")
                    precision = mining_service.evaluate_precision(dataset, net, im, fm)
                except Exception as e:
                    logger.warning("quality_metrics_failed", error=str(e))

            self.update_state(
                state="PROGRESS",
                meta={"status": "Saving model", "progress": 90},
            )

            # Save model
            process_model = ProcessModel(
                name=final_name,
                dataset_id=log_id,
                miner_type=miner_type,
                model_format=model_format.value,
                serialized_model=serialized,
                graph_structure_json=graph_structure_json,  # NEW: Store graph JSON
                fitness=fitness,
                precision=precision,
            )
            db.add(process_model)

            # Update AsyncJob with completed status and entity_id
            if job:
                import json

                job.status = "completed"
                job.progress = 100
                job.stage = "completed"
                job.entity_id = process_model.id  # Link to created model
                job.result_json = json.dumps(
                    {
                        "model_id": process_model.id,
                        "fitness": fitness,
                        "precision": precision,
                    }
                )
                job.completed_at = datetime.utcnow()

            await db.commit()
            await db.refresh(process_model)

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "discovery_task_completed",
                model_id=process_model.id,
                miner_type=miner_type,
                fitness=fitness,
                precision=precision,
                duration_ms=round(duration, 2),
            )

            return {
                "model_id": process_model.id,
                "log_id": log_id,
                "miner_type": miner_type,
                "fitness": fitness,
                "precision": precision,
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error("discovery_task_failed", error=str(e), log_id=log_id, exc_info=True)

        async with AsyncSessionLocal() as db:
            from src.platform.models import AsyncJob

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()
                await db.commit()

        raise


@celery_app.task(
    bind=True, base=AsyncTask, name="perform_conformance", time_limit=600, soft_time_limit=540
)
async def perform_conformance_task(
    self,
    log_id: str,
    model_id: str,
    method: str = "token_replay",
) -> dict[str, Any]:
    """BUG-039 FIX: Async task for conformance checking to prevent API freeze.

    Args:
        log_id: Dataset ID
        model_id: ProcessModel ID
        method: Conformance method (token_replay or alignment)

    Returns:
        dict with conformance results
    """
    logger.info(
        "conformance_task_started",
        log_id=log_id,
        model_id=model_id,
        method=method,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Loading data", "progress": 10},
        )

        async with AsyncSessionLocal() as db:
            import json

            from src.features.process_mining.models import ConformanceResult, Dataset, ProcessModel
            from src.features.process_mining.services.conformance import conformance_service
            from src.platform.models import AsyncJob

            # Load dataset and model
            result = await db.execute(select(Dataset).where(Dataset.id == log_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {log_id}")

            result = await db.execute(select(ProcessModel).where(ProcessModel.id == model_id))
            model = result.scalar_one_or_none()
            if not model:
                raise ValueError(f"Model not found: {model_id}")

            self.update_state(
                state="PROGRESS",
                meta={"status": f"Running {method} conformance", "progress": 40},
            )

            # Run conformance check (synchronous PM4Py call)
            conf_result = conformance_service.check_conformance(
                event_log=dataset,
                model=model,
                method=method,
            )

            self.update_state(
                state="PROGRESS",
                meta={"status": "Saving results", "progress": 80},
            )

            # Save result
            conformance_record = ConformanceResult(
                dataset_id=log_id,
                model_id=model_id,
                fitness=conf_result["fitness"],
                precision=conf_result.get("precision"),
                method=conf_result["method"],
                diagnostics_json=json.dumps(
                    {
                        "fitting_traces": conf_result["fitting_traces"],
                        "total_traces": conf_result["total_traces"],
                    }
                ),
            )
            db.add(conformance_record)

            # Update AsyncJob
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "completed"
                job.result_json = json.dumps(
                    {
                        "conformance_id": conformance_record.id,
                        "fitness": conf_result["fitness"],
                    }
                )
                job.completed_at = datetime.utcnow()

            await db.commit()
            await db.refresh(conformance_record)

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "conformance_task_completed",
                conformance_id=conformance_record.id,
                fitness=conf_result["fitness"],
                duration_ms=round(duration, 2),
            )

            return {
                "conformance_id": conformance_record.id,
                "log_id": log_id,
                "model_id": model_id,
                "fitness": conf_result["fitness"],
                "precision": conf_result.get("precision"),
                "is_conformant": conf_result["is_conformant"],
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error("conformance_task_failed", error=str(e), exc_info=True)

        async with AsyncSessionLocal() as db:
            from src.platform.models import AsyncJob

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()
                await db.commit()

        raise


@celery_app.task(bind=True, base=AsyncTask, name="validate_uploaded_file", max_retries=3)
async def validate_uploaded_file_task(
    self,
    dataset_id: str,
    storage_key: str,
) -> dict[str, Any]:
    """Phase 4: Stream-based file validation for presigned uploads.

    Steps:
    1. Download file from S3 (streamed, memory-efficient)
    2. Magic byte verification (detect real file type)
    3. Schema sniffing (parse first 10MB for columns)
    4. Update dataset status (PENDING → VALIDATING → AWAITING_MAPPING)

    Args:
        dataset_id: Dataset ID to validate
        storage_key: S3 object key

    Returns:
        dict with validation results and detected columns

    Raises:
        Exception: If validation fails (retries up to 3 times)
    """
    logger.info(
        "validate_uploaded_file_started",
        dataset_id=dataset_id,
        storage_key=storage_key,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Downloading file from storage", "progress": 10},
        )

        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.features.process_mining.services.ingestion.unified import (
                unified_ingestion_service,
            )
            from src.platform.infrastructure.object_storage import get_storage_client

            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            # Update status to VALIDATING
            dataset.status = DatasetStatus.VALIDATING.value
            await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Downloading file", "progress": 20},
            )

            # Download file from S3 (streaming to avoid memory exhaustion)
            storage_client = get_storage_client()

            # Stream first 10MB for validation (don't load entire file)
            validation_chunk_size = 10 * 1024 * 1024  # 10 MB
            file_chunks = []
            total_bytes = 0

            try:
                for chunk in storage_client.stream_file("raw", storage_key, chunk_size=64 * 1024):
                    file_chunks.append(chunk)
                    total_bytes += len(chunk)
                    if total_bytes >= validation_chunk_size:
                        break  # Stop after 10MB for validation
            except Exception as e:
                logger.error(
                    "file_download_failed",
                    error=str(e),
                    dataset_id=dataset_id,
                    storage_key=storage_key,
                )
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = f"Failed to download file: {e}"
                await db.commit()
                raise

            file_content = b"".join(file_chunks)

            self.update_state(
                state="PROGRESS",
                meta={"status": "Verifying file signature", "progress": 40},
            )

            # Step 1: Magic byte verification
            # Detect actual file type from content (prevent spoofing)
            file_extension = dataset.source_format.lower()

            if file_extension == "xes":
                # XES files should start with XML declaration
                if not file_content.startswith((b"<?xml", b"<log")):
                    logger.warning(
                        "file_signature_mismatch",
                        dataset_id=dataset_id,
                        expected="XES/XML",
                        actual="binary",
                    )
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = "File appears to be invalid XES format (not valid XML)"
                    await db.commit()
                    raise ValueError("Invalid XES file signature")
            elif file_extension == "csv":
                # CSV should be readable text
                try:
                    file_content[:1024].decode("utf-8")
                except UnicodeDecodeError:
                    logger.warning(
                        "file_signature_mismatch",
                        dataset_id=dataset_id,
                        expected="CSV/text",
                        actual="binary",
                    )
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = (
                        "File appears to be invalid CSV format (contains binary data)"
                    )
                    await db.commit()
                    raise ValueError("Invalid CSV file signature")

            self.update_state(
                state="PROGRESS",
                meta={"status": "Detecting columns", "progress": 60},
            )

            # Step 2: Schema sniffing (detect columns from first chunk)
            # Use unified_ingestion_service to detect columns
            try:
                detection_result = unified_ingestion_service.detect_columns(
                    file_content,
                    dataset.source_file or f"upload.{file_extension}",
                )

                columns = detection_result.get("columns", [])
                suggestions = detection_result.get("suggestions", {})
                row_count_sample = detection_result.get("row_count", 0)

                logger.info(
                    "columns_detected",
                    dataset_id=dataset_id,
                    columns_count=len(columns),
                    sample_rows=row_count_sample,
                )

            except Exception as e:
                logger.error(
                    "column_detection_failed",
                    error=str(e),
                    dataset_id=dataset_id,
                )
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = f"Failed to detect columns: {e}"
                await db.commit()
                raise

            self.update_state(
                state="PROGRESS",
                meta={"status": "Updating dataset metadata", "progress": 90},
            )

            # Step 3: Update dataset with detection results
            import json

            dataset.detected_columns_json = json.dumps(columns)
            dataset.column_suggestions_json = json.dumps(suggestions)
            dataset.status = DatasetStatus.AWAITING_MAPPING.value
            dataset.error_message = None

            # Get actual file size from S3
            try:
                actual_size = storage_client.get_file_size("raw", storage_key)
                dataset.file_size_bytes = actual_size
            except Exception:
                pass  # Not critical if size check fails

            await db.commit()

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "validate_uploaded_file_completed",
                dataset_id=dataset_id,
                columns_detected=len(columns),
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "dataset_id": dataset_id,
                "storage_key": storage_key,
                "columns": columns,
                "suggestions": suggestions,
                "status": "awaiting_mapping",
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error(
            "validate_uploaded_file_failed",
            error=str(e),
            dataset_id=dataset_id,
            storage_key=storage_key,
            task_id=self.request.id,
            exc_info=True,
        )

        # Update dataset status to ERROR
        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = str(e)
                await db.commit()

        # Retry up to 3 times with exponential backoff
        raise self.retry(exc=e, countdown=2**self.request.retries)


def get_task_status(task_id: str) -> dict[str, Any]:
    """Get status of a Celery task.

    Args:
        task_id: Celery task ID

    Returns:
        dict with status, result, and progress info
    """
    task_result = AsyncResult(task_id, app=celery_app)

    result = {
        "task_id": task_id,
        "status": task_result.state,
        "ready": task_result.ready(),
        "successful": task_result.successful() if task_result.ready() else None,
    }

    if task_result.state == "PROGRESS":
        result["progress"] = task_result.info
    elif task_result.ready():
        if task_result.successful():
            result["result"] = task_result.result
        else:
            result["error"] = str(task_result.info)

    return result


# =============================================================================
# BUG-057 FIX: Zombie Job Reaper
# =============================================================================


@celery_app.task(bind=True, name="reap_zombie_jobs")
def reap_zombie_jobs(self, timeout_minutes: int = 10) -> dict[str, Any]:
    """Reap zombie jobs that are stuck in RUNNING/ANALYZING state.

    BUG-057/031/040/022 FIX: Cross-references multiple tables with Celery's actual task status.
    Should be scheduled via Celery Beat every 5 minutes.

    Handles:
    - AsyncJob records stuck in RUNNING
    - Dataset records stuck in ANALYZING (BUG-022)
    - Analysis records stuck in RUNNING (BUG-040)

    Args:
        timeout_minutes: Consider jobs zombie if stuck for longer than this

    Returns:
        Summary of reaped items across all tables
    """
    from datetime import timedelta

    from src.features.process_mining.models import Analysis, AnalysisStatus, Dataset, DatasetStatus
    from src.platform.core.enums import JobStatus
    from src.platform.models import AsyncJob

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _reap():
        async with AsyncSessionLocal() as db:
            try:
                cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
                results = {"async_jobs": [], "datasets": [], "analyses": []}

                # === 1. Reap zombie AsyncJobs ===
                job_result = await db.execute(
                    select(AsyncJob).where(
                        AsyncJob.status == JobStatus.RUNNING.value,
                        AsyncJob.updated_at < cutoff_time,
                    )
                )
                stuck_jobs = job_result.scalars().all()

                for job in stuck_jobs:
                    if not job.task_id:
                        job.status = JobStatus.FAILED.value
                        job.error = "No task ID - orphaned job"
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)
                        continue

                    celery_result = AsyncResult(job.task_id, app=celery_app)
                    celery_state = celery_result.state

                    if celery_state in ("FAILURE", "REVOKED"):
                        job.status = JobStatus.FAILED.value
                        job.error = f"Celery state: {celery_state}"
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)
                    elif celery_state == "SUCCESS":
                        job.status = JobStatus.COMPLETED.value
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)
                    elif celery_state == "PENDING" and job.started_at:
                        job.status = JobStatus.FAILED.value
                        job.error = "Task lost - worker likely crashed"
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)

                # === 2. BUG-022 FIX: Reap zombie Datasets stuck in ANALYZING ===
                dataset_result = await db.execute(
                    select(Dataset).where(
                        Dataset.status == DatasetStatus.ANALYZING.value,
                        Dataset.updated_at < cutoff_time,
                    )
                )
                stuck_datasets = dataset_result.scalars().all()

                for dataset in stuck_datasets:
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = f"Ingestion timed out after {timeout_minutes} minutes"
                    results["datasets"].append(dataset.id)

                # === 2.5. Phase 4 FIX: Reap zombie Datasets stuck in PENDING ===
                # Presigned URLs expire after 1 hour, so datasets older than 2 hours are abandoned
                pending_cutoff = datetime.utcnow() - timedelta(hours=2)
                pending_result = await db.execute(
                    select(Dataset).where(
                        Dataset.status == DatasetStatus.PENDING.value,
                        Dataset.created_at < pending_cutoff,
                    )
                )
                pending_datasets = pending_result.scalars().all()

                for dataset in pending_datasets:
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = "Upload timed out (presigned URL expired)"
                    results["datasets"].append(dataset.id)

                # === 3. BUG-040 FIX: Reap zombie Analyses stuck in RUNNING ===
                analysis_result = await db.execute(
                    select(Analysis).where(
                        Analysis.status == AnalysisStatus.RUNNING.value,
                        Analysis.completed_at.is_(None),
                    )
                )
                # Filter by created_at for analyses (they may not have updated_at)
                stuck_analyses = [
                    a
                    for a in analysis_result.scalars().all()
                    if a.created_at and a.created_at < cutoff_time
                ]

                for analysis in stuck_analyses:
                    analysis.status = AnalysisStatus.FAILED.value
                    analysis.error_message = f"Analysis timed out after {timeout_minutes} minutes"
                    analysis.completed_at = datetime.utcnow()
                    results["analyses"].append(analysis.id)

                await db.commit()

                total_reaped = sum(len(v) for v in results.values())
                logger.info(
                    "zombie_jobs_reaped",
                    async_jobs_reaped=len(results["async_jobs"]),
                    datasets_reaped=len(results["datasets"]),
                    analyses_reaped=len(results["analyses"]),
                    total_reaped=total_reaped,
                )

                return {
                    "async_jobs": results["async_jobs"],
                    "datasets": results["datasets"],
                    "analyses": results["analyses"],
                    "total_reaped": total_reaped,
                }

            except Exception as e:
                logger.error("zombie_reaper_error", error=str(e), exc_info=True)
                raise

    return loop.run_until_complete(_reap())
