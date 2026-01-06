"""Organizational Services.

Organizational mining and social network analysis.
"""

from src.domains.analysis.services.organizational.service import OrganizationalService

organizational_service = OrganizationalService()

__all__ = [
    "OrganizationalService",
    "organizational_service",
]
