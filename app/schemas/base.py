"""
Base Pydantic schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class PaginatedResponse(BaseModel):
    """Base paginated response"""
    total: int
    limit: int
    offset: int
    has_more: bool

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    status_code: int