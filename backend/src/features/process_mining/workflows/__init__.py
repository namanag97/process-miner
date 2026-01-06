"""Workflows Package.

Legacy workflow orchestration - superceded by DAGs.
This module provides backward-compatible API endpoints.
"""

from src.features.process_mining.workflows.router import router

__all__ = ["router"]
