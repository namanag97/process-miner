"""DEPRECATED: Use src.platform.core instead.

This module exists for backwards compatibility during migration.
All new code should import from src.platform.core.
"""

# Re-export everything from new location
from src.platform.core import *  # noqa: F401, F403

import warnings
warnings.warn(
    "src.core is deprecated, use src.platform.core instead",
    DeprecationWarning,
    stacklevel=2,
)
