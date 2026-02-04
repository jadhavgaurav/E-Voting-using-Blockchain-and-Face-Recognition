"""Error response schema for consistent API errors."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Standard error response body."""

    detail: str = Field(..., description="Human-readable error message")
    request_id: str | None = Field(None, description="Request ID for correlation")
    code: str = Field(..., description="Machine-readable error code")
