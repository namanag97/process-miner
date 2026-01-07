"""Ingestion Worker v2.

Temporal worker for dataset ingestion using v2 workflows and activities.
Uses chunk-based processing for better failure recovery.
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from src.infra.temporal.activities_v2.ingestion import (
    detect_columns,
    finalize_ingestion,
    get_chunk_list,
    process_chunk,
    update_dataset_status,
    validate_file,
)
from src.infra.temporal.config import get_temporal_config
from src.infra.temporal.workflows_v2.ingestion import (
    DatasetIngestionWorkflowV2,
    DatasetValidationWorkflowV2,
)


async def run_ingestion_worker_v2() -> None:
    """Run the v2 ingestion worker."""
    config = get_temporal_config()

    client = await Client.connect(
        config.host,
        namespace=config.namespace,
    )

    worker = Worker(
        client,
        task_queue=config.QUEUE_INGESTION,
        workflows=[
            DatasetIngestionWorkflowV2,
            DatasetValidationWorkflowV2,
        ],
        activities=[
            validate_file,
            detect_columns,
            get_chunk_list,
            process_chunk,
            finalize_ingestion,
            update_dataset_status,
        ],
        max_concurrent_activities=config.max_concurrent_activities,
        max_cached_workflows=config.max_cached_workflows,
    )

    await worker.run()


def main() -> None:
    """Entry point for ingestion worker v2."""
    asyncio.run(run_ingestion_worker_v2())


if __name__ == "__main__":
    main()
