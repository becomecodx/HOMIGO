"""
Standard API response schemas.
Defines common response formats for success and error cases.
"""

from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Standard success response schema."""
    
    success: bool = Field(default=True, description="Indicates request was successful")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(default=None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class ErrorDetail(BaseModel):
    """Error detail for validation errors."""
    
    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Error message for this field")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    success: bool = Field(default=False, description="Indicates request failed")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code for client handling")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    errors: Optional[List[ErrorDetail]] = Field(default=None, description="Validation errors (for 422 responses)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Invalid CAPTCHA",
                "error_code": "INVALID_CAPTCHA",
                "details": {}
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    active_captchas: int = Field(..., description="Number of active CAPTCHAs in memory")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "HOMIGO Authentication API",
                "active_captchas": 3
            }
        }

