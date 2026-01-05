"""Platform User and Organization models.

For now, these re-export from the unified orm.py.
Full split will be done in a future refactoring phase.
"""

from src.platform.models import Organization, User

__all__ = ["Organization", "User"]
