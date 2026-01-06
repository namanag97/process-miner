"""Conformance Services.

Conformance checking algorithms and services.
"""

from src.domains.analysis.services.conformance.service import ConformanceService

conformance_service = ConformanceService()

__all__ = [
    "ConformanceService",
    "conformance_service",
]
