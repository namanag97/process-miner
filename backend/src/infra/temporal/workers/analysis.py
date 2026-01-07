"""Analysis Worker.

Temporal worker for process mining analysis workflows and activities.
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from src.infra.temporal.activities.analysis import (
    check_conformance_activity,
    compute_metrics_activity,
    load_event_log_activity,
    mine_model_activity,
)
from src.infra.temporal.config import get_temporal_config
from src.infra.temporal.workflows.analysis import (
    ConformanceCheckWorkflow,
    ProcessDiscoveryWorkflow,
)


async def run_analysis_worker() -> None:
    """Run the analysis worker."""
    config = get_temporal_config()

    client = await Client.connect(
        config.host,
        namespace=config.namespace,
    )

    worker = Worker(
        client,
        task_queue=config.QUEUE_ANALYSIS,
        workflows=[
            ProcessDiscoveryWorkflow,
            ConformanceCheckWorkflow,
        ],
        activities=[
            load_event_log_activity,
            mine_model_activity,
            compute_metrics_activity,
            check_conformance_activity,
        ],
        max_concurrent_activities=config.max_concurrent_activities,
        max_cached_workflows=config.max_cached_workflows,
    )

    await worker.run()


def main() -> None:
    """Entry point for analysis worker."""
    asyncio.run(run_analysis_worker())


if __name__ == "__main__":
    main()
