import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from ..models import Job, Mapping, Upload, Dataset
from ..services import parse_file, pm4py_service
from ..database import engine
from ..core import get_logger

log = get_logger(__name__)

# Create a new session factory for background tasks since they run outside request scope
# Dependencies like 'get_db' are for requests and might close the session too early/late differently.
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def run_mining_job(job_id: str, mapping_id: str):
    """
    Background task to run the process mining job.
    """
    logger.info(f"Starting background job: {job_id}")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Get Job and Mapping
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            
            if not job:
                logger.error(f"Job {job_id} not found!")
                return
            
            result = await db.execute(select(Mapping).where(Mapping.id == mapping_id))
            mapping = result.scalar_one_or_none()
            
            if not mapping:
                raise Exception("Mapping not found")
                
            result = await db.execute(select(Upload).where(Upload.id == mapping.upload_id))
            upload = result.scalar_one_or_none()
            
            if not upload:
                raise Exception("Upload not found")
                
            # 2. Update status to processing
            job.status = "processing"
            job.progress = 5
            job.progress_message = "Initializing..."
            await db.commit()
            
            # 3. Load File
            file_path = Path(upload.file_path)
            logger.info(f"Loading file: {file_path}")
            
            job.progress = 10
            job.progress_message = "Loading file..."
            await db.commit()
            
            # Run blocking file IO in threadpool if needed, but for MVP direct call is okay 
            # as long as we accept one thread per request logic for now. 
            # (In production, we'd use run_in_executor)
            df = parse_file(file_path)
            
            # 4. Create Event Log
            job.progress = 30
            job.progress_message = "Creating event log..."
            await db.commit()
            
            log = pm4py_service.create_event_log(
                df=df,
                case_id_col=mapping.case_id_column,
                activity_col=mapping.activity_column,
                timestamp_col=mapping.timestamp_column,
                resource_col=mapping.resource_column,
                timestamp_format=mapping.timestamp_format,
            )
            
            # 5. Mining Steps
            
            # DFG
            job.progress = 50
            job.progress_message = "Discovering process graph..."
            await db.commit()
            
            # These can be slow, ideally we'd yield control or run in executor
            dfg_data = pm4py_service.discover_dfg(log)
            
            # Stats
            job.progress = 60
            job.progress_message = "Calculating statistics..."
            await db.commit()
            stats = pm4py_service.get_statistics(log)
            
            # Variants
            job.progress = 70
            job.progress_message = "Extracting variants..."
            await db.commit()
            variants = pm4py_service.get_variants(log)
            
            # Activity Stats
            job.progress = 80
            job.progress_message = "Analyzing activities..."
            await db.commit()
            activity_stats = pm4py_service.get_activity_stats(log)
            
            # Deviations
            job.progress = 90
            job.progress_message = "Detecting deviations..."
            await db.commit()
            deviations = pm4py_service.detect_deviations(log, variants)
            
            # Transforms
            dfg_response = pm4py_service.transform_dfg_for_react_flow(dfg_data, stats)
            variants_response = pm4py_service.transform_variants(variants)
            
            # 6. Save Dataset
            job.progress = 95
            job.progress_message = "Saving results..."
            await db.commit()
            
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
            await db.commit()
            await db.refresh(new_dataset)
            
            # 7. Complete Job
            job.status = "completed"
            job.progress = 100
            job.progress_message = "Complete"
            job.dataset_id = new_dataset.id
            job.completed_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            # Re-fetch job in case of transaction rollback issues (safeguard)
            try:
                # We need to ensure we can write the error state
                # In a real async flow with rollback, we might need a fresh transaction
                # Here we just try to update.
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()
                await db.commit()
            except Exception as inner_e:
                logger.error(f"Failed to update job failure status: {inner_e}")
