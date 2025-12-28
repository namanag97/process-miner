"""RFC 7807 Problem Detail Error Handling.

This module provides standardized error responses following the RFC 7807 specification
for HTTP API problem details.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uuid


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Detail response model."""
    
    type: str = Field(
        default="about:blank",
        description="A URI reference that identifies the problem type"
    )
    title: str = Field(
        description="A short, human-readable summary of the problem type"
    )
    status: int = Field(
        description="The HTTP status code"
    )
    detail: Optional[str] = Field(
        default=None,
        description="A human-readable explanation specific to this occurrence"
    )
    instance: Optional[str] = Field(
        default=None,
        description="A URI reference that identifies the specific occurrence"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When the error occurred"
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        alias="traceId",
        description="Unique identifier for tracing this error"
    )
    errors: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Additional error details for validation errors"
    )

    class Config:
        populate_by_name = True


# Error type URIs
ERROR_TYPES = {
    400: "/errors/bad-request",
    401: "/errors/unauthorized",
    403: "/errors/forbidden",
    404: "/errors/not-found",
    409: "/errors/conflict",
    422: "/errors/validation-failed",
    500: "/errors/internal-error",
    503: "/errors/service-unavailable",
}

ERROR_TITLES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Resource Not Found",
    409: "Conflict",
    422: "Validation Failed",
    500: "Internal Server Error",
    503: "Service Unavailable",
}


def create_problem_response(
    status_code: int,
    detail: str,
    request: Request,
    errors: Optional[List[Dict[str, Any]]] = None,
    error_type: Optional[str] = None,
    title: Optional[str] = None,
) -> JSONResponse:
    """Create a RFC 7807 compliant error response."""
    
    problem = ProblemDetail(
        type=error_type or ERROR_TYPES.get(status_code, "/errors/unknown"),
        title=title or ERROR_TITLES.get(status_code, "Error"),
        status=status_code,
        detail=detail,
        instance=str(request.url.path),
        errors=errors,
    )
    
    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump(by_alias=True, exclude_none=True),
        media_type="application/problem+json",
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with RFC 7807 format."""
    return create_problem_response(
        status_code=exc.status_code,
        detail=str(exc.detail),
        request=request,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with RFC 7807 format."""
    errors = []
    for error in exc.errors():
        loc = ".".join(str(l) for l in error["loc"])
        errors.append({
            "field": loc,
            "message": error["msg"],
            "type": error["type"],
        })
    
    return create_problem_response(
        status_code=422,
        detail="Request validation failed",
        request=request,
        errors=errors,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with RFC 7807 format."""
    return create_problem_response(
        status_code=500,
        detail="An unexpected error occurred",
        request=request,
    )


# Custom domain exceptions
class DomainError(Exception):
    """Base class for domain errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_type: str = "/errors/domain-error",
        title: str = "Domain Error",
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.title = title
        super().__init__(message)


class ResourceNotFoundError(DomainError):
    """Resource not found error."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            status_code=404,
            error_type="/errors/not-found",
            title=f"{resource_type} Not Found",
        )


class ConflictError(DomainError):
    """Resource conflict error."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=409,
            error_type="/errors/conflict",
            title="Resource Conflict",
        )


class ProcessingError(DomainError):
    """Processing failed error."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_type="/errors/processing-failed",
            title="Processing Failed",
        )


async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Handle domain exceptions with RFC 7807 format."""
    return create_problem_response(
        status_code=exc.status_code,
        detail=exc.message,
        request=request,
        error_type=exc.error_type,
        title=exc.title,
    )
