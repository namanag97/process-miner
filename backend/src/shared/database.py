"""Shared database Base class for all ORM models.

Both Platform and Feature layers import this Base.
This is the ONLY shared database dependency.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""

