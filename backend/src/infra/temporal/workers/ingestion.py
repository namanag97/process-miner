"""Ingestion Worker.

Temporal worker for dataset ingestion workflows and activities.
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from src.infra.temporal.activities.dataset import (
    compute_statistics_activity,
    detect_columns_activity,
    parse_to_parquet_activity,
    validate_file_activity,
)
from src.infra.temporal.config import get_temporal_config
from src.infra.temporal.workflows.ingestion import (
    DatasetIngestionWorkflow,
    DatasetValidationWorkflow,
)


async def run_ingestion_worker() -> None:
    """Run the ingestion worker."""
    config = get_temporal_config()

    client = await Client.connect(
        config.host,
        namespace=config.namespace,
    )

    worker = Worker(
        client,
        task_queue=config.QUEUE_INGESTION,
        workflows=[
            DatasetIngestionWorkflow,
            DatasetValidationWorkflow,
        ],
        activities=[
            validate_file_activity,
            detect_columns_activity,
            parse_to_parquet_activity,
            compute_statistics_activity,
        ],
        max_concurrent_activities=config.max_concurrent_activities,
        max_cached_workflows=config.max_cached_workflows,
    )

    await worker.run()


def main() -> None:
    """Entry point for ingestion worker."""
    asyncio.run(run_ingestion_worker())


if __name__ == "__main__":
    main()
