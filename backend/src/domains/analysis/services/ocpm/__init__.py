"""OCPM Services.

Object-Centric Process Mining (OCEL 2.0).
"""

from src.domains.analysis.services.ocpm.service import OCPMService

ocpm_service = OCPMService()

__all__ = [
    "OCPMService",
    "ocpm_service",
]
