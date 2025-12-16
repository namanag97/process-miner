"""
Mining Tasks - Celery tasks for process mining operations.

These tasks run in a separate worker process, providing:
- Reliable execution (tasks survive API restarts)
- Progress tracking via database updates
- Automatic retry on failure
- Horizontal scaling (multiple workers)
"""

import json
from datetime import datetime
from pathlib import Path

from celery import shared_task
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Job, Mapping, Upload, Dataset
from ..services import parse_file, pm4py_service
from ..core import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Create synchronous engine for Celery (Celery tasks are synchronous)
# We use a separate sync engine because Celery workers don't use asyncio
sync_database_url = settings.database_url.replace("+aiosqlite", "")
sync_engine = create_engine(sync_database_url, echo=False)


def update_job_progress(db: Session, job: Job, progress: int, message: str):
    """Helper to update job progress and commit."""
    job.progress = progress
    job.progress_message = message
    db.commit()
    logger.info(f"Job {job.id}: {progress}% - {message}")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_mining_task(self, job_id: str, mapping_id: str):
    """
    Celery task to run process mining on an uploaded file.
    
    This task:
    1. Loads the uploaded file
    2. Creates a PM4Py event log
    3. Discovers the process graph (DFG)
    4. Calculates statistics and variants
    5. Stores results in a Dataset
    
    Args:
        job_id: The Job record ID for status tracking
        mapping_id: The Mapping record ID with column configuration
    """
    logger.info(f"Starting mining task: job={job_id}, mapping={mapping_id}")
    
    with Session(sync_engine) as db:
        try:
            # 1. Get Job, Mapping, and Upload
            job = db.execute(select(Job).where(Job.id == job_id)).scalar_one_or_none()
            if not job:
                logger.error(f"Job {job_id} not found!")
                return {"error": "Job not found"}
            
            mapping = db.execute(select(Mapping).where(Mapping.id == mapping_id)).scalar_one_or_none()
            if not mapping:
                raise Exception("Mapping not found")
            
            upload = db.execute(select(Upload).where(Upload.id == mapping.upload_id)).scalar_one_or_none()
            if not upload:
                raise Exception("Upload not found")
            
            # 2. Update status to processing
            job.status = "processing"
            update_job_progress(db, job, 5, "Initializing...")
            
            # 3. Load file
            file_path = Path(upload.file_path)
            logger.info(f"Loading file: {file_path}")
            update_job_progress(db, job, 10, "Loading file...")
            
            df = parse_file(file_path)
            
            # 4. Create event log
            update_job_progress(db, job, 30, "Creating event log...")
            
            event_log = pm4py_service.create_event_log(
                df=df,
                case_id_col=mapping.case_id_column,
                activity_col=mapping.activity_column,
                timestamp_col=mapping.timestamp_column,
                resource_col=mapping.resource_column,
                timestamp_format=mapping.timestamp_format,
            )
            
            # 5. Discover DFG
            update_job_progress(db, job, 50, "Discovering process graph...")
            dfg_data = pm4py_service.discover_dfg(event_log)
            
            # 6. Calculate statistics
            update_job_progress(db, job, 60, "Calculating statistics...")
            stats = pm4py_service.get_statistics(event_log)
            
            # 7. Extract variants
            update_job_progress(db, job, 70, "Extracting variants...")
            variants = pm4py_service.get_variants(event_log)
            
            # 8. Activity stats
            update_job_progress(db, job, 80, "Analyzing activities...")
            activity_stats = pm4py_service.get_activity_stats(event_log)
            
            # 9. Detect deviations
            update_job_progress(db, job, 90, "Detecting deviations...")
            deviations = pm4py_service.detect_deviations(event_log, variants)
            
            # 10. Transform for frontend
            dfg_response = pm4py_service.transform_dfg_for_react_flow(dfg_data, stats)
            variants_response = pm4py_service.transform_variants(variants)
            
            # 11. Save Dataset
            update_job_progress(db, job, 95, "Saving results...")
            
            new_dataset = Dataset(
                mapping_id=mapping_id,
                dfg_json=json.dumps(dfg_response.model_dump()),
                variants_json=json.dumps(variants_response.model_dump()),
                stats_json=json.dumps(stats.model_dump()),
                activity_stats_json=json.dumps([a.model_dump() for a in activity_stats]),
                deviations_json=json.dumps([d.model_dump() for d in deviations]),
                created_at=datetime.utcnow()
            )
            db.add(new_dataset)
            db.commit()
            db.refresh(new_dataset)
            
            # 12. Complete job
            job.status = "completed"
            job.progress = 100
            job.progress_message = "Complete"
            job.dataset_id = new_dataset.id
            job.completed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Job {job_id} completed successfully, dataset={new_dataset.id}")
            
            return {
                "status": "completed",
                "dataset_id": new_dataset.id,
                "stats": {
                    "cases": stats.total_cases,
                    "events": stats.total_events,
                    "variants": stats.total_variants,
                }
            }
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            
            # Update job status to failed
            try:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
            except Exception as inner_e:
                logger.error(f"Failed to update job failure status: {inner_e}")
            
            # Retry the task if retries available
            raise self.retry(exc=e)
