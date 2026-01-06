"""Analysis Domain Tasks.

Background tasks for analysis operations:
- Process discovery tasks
- Analysis computation tasks
"""

from src.platform.infrastructure.tasks import (
    run_analysis_task,
    run_discovery_task,
)

__all__ = [
    "run_discovery_task",
    "run_analysis_task",
]
