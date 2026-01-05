"""Conformance Module - Conformance checking services.

Components:
- service.py: ConformanceService for fitness, precision, diagnostics
- router.py: API router for conformance checking endpoints
"""

from .router import router
from .service import ConformanceService, conformance_service

__all__ = [
    "router",
    "ConformanceService",
    "conformance_service",
]
