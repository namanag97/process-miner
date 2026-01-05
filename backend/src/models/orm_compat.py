"""LEGACY ORM Models - Backwards compatibility shim.

DEPRECATED: Import from the separated layers instead:
- Platform: from src.platform.models import Organization, User, Workspace, Project, AsyncJob
- Features: from src.features.process_mining.models import Dataset, Analysis, ProcessCase

This file re-exports from src.models.orm for backwards compatibility.
"""

import warnings
warnings.warn(
    "src.models.orm_compat is deprecated. Use src.models.orm or import from "
    "src.platform.models for Platform entities and src.features.process_mining.models "
    "for Feature entities.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the main orm.py shim
from src.models.orm import *  # noqa: F401, F403
from src.models.orm import __all__  # noqa: F401
