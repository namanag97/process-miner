"""DEPRECATED: Use src.platform.infrastructure instead.

This module exists for backwards compatibility during migration.
All new code should import from src.platform.infrastructure.
"""

# Re-export everything from new location
from src.platform.infrastructure import *  # noqa: F401, F403

import warnings
warnings.warn(
    "src.infrastructure is deprecated, use src.platform.infrastructure instead",
    DeprecationWarning,
    stacklevel=2,
)
