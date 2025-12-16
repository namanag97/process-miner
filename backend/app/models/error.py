from typing import Optional
from sqlmodel import SQLModel

class ErrorResponse(SQLModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
