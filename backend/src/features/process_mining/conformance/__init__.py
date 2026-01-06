"""Conformance Module - Conformance checking services.

Components:
- service.py: ConformanceService for fitness, precision, diagnostics
- router.py: API router for conformance checking endpoints
"""

from .service import ConformanceService, conformance_service
from .router import router

__all__ = [
    "router",
    "ConformanceService",
    "conformance_service",
]
