"""
Processing router - Handles process mining job execution.

For MVP, processing is synchronous. This router:
1. Takes a mapping ID
2. Loads the file and applies the mapping
3. Runs PM4Py analysis (DFG, variants, statistics)
4. Stores results and returns a dataset ID

In Phase 3, this would be async with Redis job queue.
"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, HTTPException

from ..models.schemas import JobResponse, ProcessingRequest
from ..services import parse_file, pm4py_service
from .uploads import get_upload_info
from .mappings import get_mapping_info

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/processing", tags=["processing"])

# In-memory storage for MVP
jobs_store: dict[str, dict] = {}
datasets_store: dict[str, dict] = {}


@router.post("/mappings/{mapping_id}/process", response_model=JobResponse)
async def start_processing(mapping_id: str, request: ProcessingRequest | None = None):
    """
    Start processing a mapped file.
    
    For MVP, this runs synchronously and returns immediately with results.
    In production, would queue a background job.
    """
    # Get mapping
    mapping_data = get_mapping_info(mapping_id)
    if not mapping_data:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    # Get upload
    upload_info = get_upload_info(mapping_data["upload_id"])
    if not upload_info:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Create job record
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "mapping_id": mapping_id,
        "status": "processing",
        "progress": 0,
        "progress_message": "Starting...",
        "dataset_id": None,
        "error": None,
        "created_at": datetime.now(timezone.utc),
        "completed_at": None,
    }
    jobs_store[job_id] = job
    
    try:
        # Load full file
        file_path = Path(upload_info["file_path"])
        logger.info(f"Loading file: {file_path}")
        
        job["progress"] = 10
        job["progress_message"] = "Loading file..."
        
        df = parse_file(file_path)
        
        # Create event log
        job["progress"] = 30
        job["progress_message"] = "Creating event log..."
        
        log = pm4py_service.create_event_log(
            df=df,
            case_id_col=mapping_data["case_id_column"],
            activity_col=mapping_data["activity_column"],
            timestamp_col=mapping_data["timestamp_column"],
            resource_col=mapping_data.get("resource_column"),
            timestamp_format=mapping_data.get("timestamp_format"),
        )
        
        # Discover DFG
        job["progress"] = 50
        job["progress_message"] = "Discovering process graph..."
        
        dfg_data = pm4py_service.discover_dfg(log)
        
        # Get statistics
        job["progress"] = 60
        job["progress_message"] = "Calculating statistics..."
        
        stats = pm4py_service.get_statistics(log)
        
        # Get variants
        job["progress"] = 70
        job["progress_message"] = "Extracting variants..."
        
        variants = pm4py_service.get_variants(log)
        
        # Get activity stats
        job["progress"] = 80
        job["progress_message"] = "Analyzing activities..."
        
        activity_stats = pm4py_service.get_activity_stats(log)
        
        # Detect deviations
        job["progress"] = 90
        job["progress_message"] = "Detecting deviations..."
        
        deviations = pm4py_service.detect_deviations(log, variants)
        
        # Transform to React Flow format
        dfg_response = pm4py_service.transform_dfg_for_react_flow(dfg_data, stats)
        variants_response = pm4py_service.transform_variants(variants)
        
        # Store dataset
        dataset_id = str(uuid.uuid4())
        datasets_store[dataset_id] = {
            "dataset_id": dataset_id,
            "mapping_id": mapping_id,
            "upload_id": mapping_data["upload_id"],
            "dfg": dfg_response.model_dump(),
            "variants": variants_response.model_dump(),
            "stats": stats,
            "activity_stats": activity_stats,
            "deviations": [d.model_dump() for d in deviations],
            "created_at": datetime.now(timezone.utc),
        }
        
        # Complete job
        job["progress"] = 100
        job["progress_message"] = "Complete"
        job["status"] = "completed"
        job["dataset_id"] = dataset_id
        job["completed_at"] = datetime.now(timezone.utc)
        
        logger.info(f"Processing complete: job={job_id}, dataset={dataset_id}")
        
        return JobResponse(
            job_id=job_id,
            status="completed",
            progress=100,
            progress_message="Complete",
            dataset_id=dataset_id,
            error=None,
            created_at=job["created_at"],
            completed_at=job["completed_at"],
        )
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        job["status"] = "failed"
        job["error"] = str(e)
        job["completed_at"] = datetime.now(timezone.utc)
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Get job status by ID."""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    return JobResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        progress_message=job.get("progress_message"),
        dataset_id=job.get("dataset_id"),
        error=job.get("error"),
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
    )


# Export for use by other routers
def get_dataset_info(dataset_id: str) -> dict | None:
    """Get dataset info for internal use."""
    return datasets_store.get(dataset_id)
