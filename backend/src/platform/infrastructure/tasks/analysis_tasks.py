"""Analysis Tasks.

Celery tasks for process mining analysis, discovery, and conformance checking.
"""

import json
import time
from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import select

from .base import AsyncSessionLocal, AsyncTask, celery_app

logger = structlog.get_logger(__name__)


# =============================================================================
# Perform Analysis Task
# =============================================================================


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="perform_analysis",
    time_limit=600,
    soft_time_limit=540,
    autoretry_for=(),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
async def perform_analysis_task(
    self,
    analysis_id: str,
    dataset_id: str,
    analysis_type: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Async task for performing process analysis.

    Executes CPU-intensive process mining algorithms in background to prevent
    blocking the API server. Updates the Analysis record with results when complete.

    Args:
        analysis_id: Analysis record ID
        dataset_id: Dataset ID to analyze
        analysis_type: Type of analysis (discovery, variants, statistics)
        config: Optional configuration dict

    Returns:
        dict with analysis results and duration info
    """
    logger.info(
        "perform_analysis_task_started",
        analysis_id=analysis_id,
        dataset_id=dataset_id,
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

            self.update_state(
                state="PROGRESS",
                meta={"status": f"Running {analysis_type} analysis", "progress": 20},
            )

            # Perform the analysis based on type
            result_data = {}

            if analysis_type == AnalysisType.DISCOVERY.value:
                dfg_data = mining_service.get_dfg_fast(dataset_id)
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
                self.update_state(
                    state="PROGRESS",
                    meta={"status": "Computing variants", "progress": 50},
                )
                variants_data = mining_service.get_variants_fast(dataset_id, top_n=50)
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
                self.update_state(
                    state="PROGRESS",
                    meta={"status": "Computing statistics", "progress": 50},
                )
                stats = mining_service.get_statistics_fast(dataset_id)
                result_data["statistics"] = stats
                analysis.result_summary_json = json.dumps(stats)

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
                "dataset_id": dataset_id,
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


# =============================================================================
# Perform Discovery Task
# =============================================================================


@celery_app.task(
    bind=True, base=AsyncTask, name="perform_discovery", time_limit=900, soft_time_limit=840
)
async def perform_discovery_task(
    self,
    dataset_id: str,
    miner_type: str,
    model_name: str | None = None,
) -> dict[str, Any]:
    """BUG-054 FIX: Async task for process discovery to prevent API thread blocking.

    Runs heavy PM4Py miners (Alpha, Inductive, ILP) in background.

    Args:
        dataset_id: Dataset ID to mine
        miner_type: Mining algorithm type (alpha, inductive, heuristic, ilp)
        model_name: Optional name for the discovered model

    Returns:
        dict with model_id and quality metrics
    """
    logger.info(
        "discovery_task_started",
        dataset_id=dataset_id,
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
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()

            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

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

            # Run discovery
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

            serialized = mining_service.serialize_model(model_data)
            final_name = model_name or f"{dataset.name}_{miner_type}"

            graph_json = mining_service.serialize_to_graph_json(model_data, model_format)
            graph_structure_json = None
            if graph_json:
                graph_structure_json = json.dumps(graph_json)

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

            process_model = ProcessModel(
                name=final_name,
                dataset_id=dataset_id,
                miner_type=miner_type,
                model_format=model_format.value,
                serialized_model=serialized,
                graph_structure_json=graph_structure_json,
                fitness=fitness,
                precision=precision,
            )
            db.add(process_model)

            if job:
                job.status = "completed"
                job.progress = 100
                job.stage = "completed"
                job.entity_id = process_model.id
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
                "dataset_id": dataset_id,
                "miner_type": miner_type,
                "fitness": fitness,
                "precision": precision,
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error("discovery_task_failed", error=str(e), dataset_id=dataset_id, exc_info=True)

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


# =============================================================================
# Perform Conformance Task
# =============================================================================


@celery_app.task(
    bind=True, base=AsyncTask, name="perform_conformance", time_limit=600, soft_time_limit=540
)
async def perform_conformance_task(
    self,
    dataset_id: str,
    model_id: str,
    method: str = "token_replay",
) -> dict[str, Any]:
    """BUG-039 FIX: Async task for conformance checking to prevent API freeze.

    Args:
        dataset_id: Dataset ID
        model_id: ProcessModel ID
        method: Conformance method (token_replay or alignment)

    Returns:
        dict with conformance results
    """
    logger.info(
        "conformance_task_started",
        dataset_id=dataset_id,
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
            from src.features.process_mining.models import ConformanceResult, Dataset, ProcessModel
            from src.features.process_mining.services.conformance import conformance_service
            from src.platform.models import AsyncJob

            # Load dataset and model
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            result = await db.execute(select(ProcessModel).where(ProcessModel.id == model_id))
            model = result.scalar_one_or_none()
            if not model:
                raise ValueError(f"Model not found: {model_id}")

            self.update_state(
                state="PROGRESS",
                meta={"status": f"Running {method} conformance", "progress": 40},
            )

            conf_result = conformance_service.check_conformance(
                event_log=dataset,
                model=model,
                method=method,
            )

            self.update_state(
                state="PROGRESS",
                meta={"status": "Saving results", "progress": 80},
            )

            conformance_record = ConformanceResult(
                dataset_id=dataset_id,
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
                "dataset_id": dataset_id,
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
