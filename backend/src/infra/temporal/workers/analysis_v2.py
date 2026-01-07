"""Analysis Worker v2.

Temporal worker for process discovery and conformance using v2 workflows.
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from src.infra.temporal.activities_v2.analysis import (
    check_conformance,
    compute_model_metrics,
    discover_process_model,
    load_event_log,
    load_process_model,
    save_conformance_result,
    save_process_model,
)
from src.infra.temporal.config import get_temporal_config
from src.infra.temporal.workflows_v2.analysis import (
    ConformanceCheckWorkflowV2,
    ProcessDiscoveryWorkflowV2,
)


async def run_analysis_worker_v2() -> None:
    """Run the v2 analysis worker."""
    config = get_temporal_config()

    client = await Client.connect(
        config.host,
        namespace=config.namespace,
    )

    worker = Worker(
        client,
        task_queue=config.QUEUE_ANALYSIS,
        workflows=[
            ProcessDiscoveryWorkflowV2,
            ConformanceCheckWorkflowV2,
        ],
        activities=[
            load_event_log,
            discover_process_model,
            compute_model_metrics,
            save_process_model,
            load_process_model,
            check_conformance,
            save_conformance_result,
        ],
        max_concurrent_activities=config.max_concurrent_activities,
        max_cached_workflows=config.max_cached_workflows,
    )

    await worker.run()


def main() -> None:
    """Entry point for analysis worker v2."""
    asyncio.run(run_analysis_worker_v2())


if __name__ == "__main__":
    main()
