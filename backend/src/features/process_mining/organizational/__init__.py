"""Organizational Module - Organizational mining and social networks.

Components:
- router.py: API router for organizational mining endpoints
- service.py: OrganizationalService for social network analysis
"""

from .router import router
from .service import OrganizationalService, organizational_service

__all__ = [
    "router",
    "OrganizationalService",
    "organizational_service",
]
