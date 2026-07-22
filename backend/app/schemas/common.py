"""
schemas/common.py — Shared Pydantic response models used across all routers.
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated response wrapper."""

    results: List[DataT] = Field(description="List of items on the current page")
    count: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")
    next_page: Optional[int] = Field(default=None, description="Next page number, or null")
    previous_page: Optional[int] = Field(default=None, description="Previous page number, or null")


class ErrorResponse(BaseModel):
    """Standard error response shape returned by all endpoints on failure."""

    error: str = Field(description="Short error code or message")
    detail: Optional[str] = Field(default=None, description="Detailed description of the error")
    path: Optional[str] = Field(default=None, description="Request path that caused the error")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="'ok' if the service is healthy")
    version: str = Field(description="Backend version string")
    uptime_seconds: float = Field(description="Seconds since the server started")
    environment: str = Field(description="'development' or 'production'")
    cache_stats: dict = Field(description="Current in-memory cache statistics")
