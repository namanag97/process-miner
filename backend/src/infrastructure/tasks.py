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

from src.core.config import get_settings

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
            from src.models.orm import AsyncJob, Dataset, PredictionModel
            from src.services.event_log_loader import event_log_loader
            from src.services.prediction import prediction_service

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
            from src.models.orm import AsyncJob

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
            from src.models.orm import (
                AsyncJob,
                Dataset,
                DatasetStatus,
                ProcessCase,
                ProcessEvent,
                UploadedFile,
            )
            from src.services.storage import storage_service
            from src.services.duckdb_ingestion import duckdb_ingestion_service
            import json

            # Load dataset and file
            result = await db.execute(
                select(Dataset).where(Dataset.id == dataset_id)
            )
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

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Parsing with DuckDB", "progress": 20},
            )

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

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Creating cases and events", "progress": 50},
            )

            # Convert Arrow to pandas for iteration
            # Handle newer DuckDB/PyArrow that may return RecordBatchReader
            import pyarrow as pa
            cases_arrow = duck_result["cases_arrow"]
            if isinstance(cases_arrow, pa.RecordBatchReader):
                cases_arrow = cases_arrow.read_all()
            cases_df = cases_arrow.to_pandas()
            
            events_arrow = duck_result["events_arrow"]
            if isinstance(events_arrow, pa.RecordBatchReader):
                events_arrow = events_arrow.read_all()
            events_df = events_arrow.to_pandas()

            # BUG-048 FIX: Batch create cases first, then flush once
            cases = []
            for _, row in cases_df.iterrows():
                case = ProcessCase(
                    dataset_id=dataset_id,
                    case_id=str(row["case_id"]),
                    variant_key=row["variant"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                )
                cases.append(case)
            
            db.add_all(cases)
            await db.flush()  # Single flush for all cases
            
            # Build case_id map after flush when IDs are assigned
            case_id_map = {case.case_id: case.id for case in cases}

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Creating events", "progress": 70},
            )

            # BUG-048 FIX: Batch create events then add_all (no flush in loop)
            events = []
            for _, row in events_df.iterrows():
                case_ref_id = case_id_map.get(str(row["case_id"]))
                if case_ref_id:
                    event = ProcessEvent(
                        case_ref_id=case_ref_id,
                        activity=str(row["activity"]),
                        timestamp=row["timestamp"],
                        resource=str(row["resource"]) if row["resource"] else None,
                    )
                    events.append(event)
            
            db.add_all(events)  # Single add_all for all events

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"status": "Finalizing dataset", "progress": 90},
            )

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
                job.result_json = json.dumps({
                    "dataset_id": dataset_id,
                    "total_cases": stats["total_cases"],
                    "total_events": stats["total_events"],
                })
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
            from src.models.orm import AsyncJob, Dataset, DatasetStatus

            result = await db.execute(
                select(Dataset).where(Dataset.id == dataset_id)
            )
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


@celery_app.task(bind=True, base=AsyncTask, name="perform_analysis", time_limit=600, soft_time_limit=540)
async def perform_analysis_task(
    self,
    analysis_id: str,
    log_id: str,
    analysis_type: str,
    config: dict[str, Any] = None,
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
            from src.models.orm import Analysis, AnalysisStatus, AnalysisType
            from src.services.mining import mining_service
            import json

            # Load analysis record
            result = await db.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
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

                analysis.result_summary_json = json.dumps({
                    "nodes_count": len(dfg_data.get("nodes", [])),
                    "edges_count": len(dfg_data.get("edges", [])),
                    "start_activities": list(dfg_data.get("start_activities", {}).keys()),
                    "end_activities": list(dfg_data.get("end_activities", {}).keys()),
                })

            elif analysis_type == AnalysisType.VARIANTS.value:
                # Get variants
                self.update_state(
                    state="PROGRESS",
                    meta={"status": "Computing variants", "progress": 50},
                )
                variants_data = mining_service.get_variants_fast(log_id, top_n=50)
                result_data["variants"] = variants_data

                analysis.result_summary_json = json.dumps({
                    "total_variants": variants_data.get("total_variants", 0),
                    "top_variant": variants_data.get("top_variants", [{}])[0] if variants_data.get("top_variants") else None,
                })

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
            from src.models.orm import Analysis, AnalysisStatus

            result = await db.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
            analysis = result.scalar_one_or_none()
            if analysis:
                analysis.status = AnalysisStatus.FAILED.value
                analysis.error_message = str(e)
                analysis.completed_at = datetime.utcnow()
                await db.commit()

        raise


@celery_app.task(bind=True, base=AsyncTask, name="perform_discovery", time_limit=900, soft_time_limit=840)
async def perform_discovery_task(
    self,
    log_id: str,
    miner_type: str,
    model_name: str = None,
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
            meta={"status": "Loading dataset", "progress": 10},
        )

        async with AsyncSessionLocal() as db:
            from src.models.orm import AsyncJob, Dataset, ProcessModel
            from src.services.mining import mining_service
            from src.core.enums import MinerType

            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == log_id))
            dataset = result.scalar_one_or_none()

            if not dataset:
                raise ValueError(f"Dataset not found: {log_id}")

            self.update_state(
                state="PROGRESS",
                meta={"status": f"Running {miner_type} miner", "progress": 30},
            )

            # Run discovery (synchronous PM4Py call)
            try:
                miner_enum = MinerType(miner_type)
            except ValueError:
                raise ValueError(f"Invalid miner type: {miner_type}")

            model_data, model_format = mining_service.discover(dataset, miner_enum)

            self.update_state(
                state="PROGRESS",
                meta={"status": "Serializing model", "progress": 70},
            )

            # Serialize model
            serialized = mining_service.serialize_model(model_data)
            final_name = model_name or f"{dataset.name}_{miner_type}"

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
                fitness=fitness,
                precision=precision,
            )
            db.add(process_model)

            # Update AsyncJob
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                import json
                job.status = "completed"
                job.result_json = json.dumps({"model_id": process_model.id})
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
            from src.models.orm import AsyncJob
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


@celery_app.task(bind=True, base=AsyncTask, name="perform_conformance", time_limit=600, soft_time_limit=540)
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
            from src.models.orm import AsyncJob, Dataset, ProcessModel, ConformanceResult
            from src.services.conformance import conformance_service
            import json

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
                diagnostics_json=json.dumps({
                    "fitting_traces": conf_result["fitting_traces"],
                    "total_traces": conf_result["total_traces"],
                }),
            )
            db.add(conformance_record)

            # Update AsyncJob
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "completed"
                job.result_json = json.dumps({
                    "conformance_id": conformance_record.id,
                    "fitness": conf_result["fitness"],
                })
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
            from src.models.orm import AsyncJob
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
    """Reap zombie jobs that are stuck in RUNNING state.
    
    BUG-057 FIX: Cross-references AsyncJob DB records with Celery's actual task status.
    Should be scheduled via Celery Beat every 5 minutes.
    
    Args:
        timeout_minutes: Consider jobs zombie if RUNNING for longer than this
        
    Returns:
        Summary of reaped jobs
    """
    from datetime import timedelta
    from src.models.orm import AsyncJob, JobStatus
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def _reap():
        async with AsyncSessionLocal() as db:
            try:
                cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
                
                # Find potentially zombie jobs
                result = await db.execute(
                    select(AsyncJob).where(
                        AsyncJob.status == JobStatus.RUNNING.value,
                        AsyncJob.updated_at < cutoff_time
                    )
                )
                stuck_jobs = result.scalars().all()
                
                reaped = []
                for job in stuck_jobs:
                    if not job.task_id:
                        # No task ID, mark as failed
                        job.status = JobStatus.FAILED.value
                        job.error = "No task ID - orphaned job"
                        job.completed_at = datetime.utcnow()
                        reaped.append(job.id)
                        continue
                    
                    # Check actual Celery status
                    celery_result = AsyncResult(job.task_id, app=celery_app)
                    celery_state = celery_result.state
                    
                    if celery_state in ("FAILURE", "REVOKED"):
                        job.status = JobStatus.FAILED.value
                        job.error = f"Celery state: {celery_state}"
                        job.completed_at = datetime.utcnow()
                        reaped.append(job.id)
                    elif celery_state == "SUCCESS":
                        job.status = JobStatus.COMPLETED.value
                        job.completed_at = datetime.utcnow()
                        reaped.append(job.id)
                    elif celery_state == "PENDING" and job.started_at:
                        # Task was never picked up but we thought it started
                        job.status = JobStatus.FAILED.value
                        job.error = "Task lost - worker likely crashed"
                        job.completed_at = datetime.utcnow()
                        reaped.append(job.id)
                
                await db.commit()
                
                logger.info(
                    "zombie_jobs_reaped",
                    total_checked=len(stuck_jobs),
                    total_reaped=len(reaped),
                    job_ids=reaped,
                )
                
                return {
                    "checked": len(stuck_jobs),
                    "reaped": len(reaped),
                    "job_ids": reaped,
                }
                
            except Exception as e:
                logger.error("zombie_reaper_error", error=str(e), exc_info=True)
                raise
    
    return loop.run_until_complete(_reap())
