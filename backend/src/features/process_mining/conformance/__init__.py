"""Conformance Module - Conformance checking services.

Components:
- service.py: ConformanceService for fitness, precision, diagnostics
- router.py: API router (not used in DDD - routers stay in api layer)
"""

from .service import ConformanceService, conformance_service

__all__ = [
    "ConformanceService",
    "conformance_service",
]
