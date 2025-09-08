"""Request and response schemas for WatchLockAI Sentinel API.

Provides strict Pydantic models for API input validation and response serialization.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# Valid operational modes as strict literal type
OperationalModeLiteral = Literal["observe", "alert", "contain", "quarantine", "offline"]


class OperationalModeRequest(BaseModel):
    """Request model for PUT /api/operational_mode with strict validation."""
    
    mode: OperationalModeLiteral = Field(
        ..., 
        description="Operational mode - must be one of: observe, alert, contain, quarantine, offline"
    )
    
    class Config:
        """Pydantic model configuration."""
        extra = "forbid"  # Reject requests with extra fields


class OperationalModeResponse(BaseModel):
    """Response model for GET /api/operational_mode."""
    
    mode: OperationalModeLiteral = Field(..., description="Current operational mode")
    timestamp: str = Field(..., description="Response timestamp in ISO format")
    
    class Config:
        """Pydantic model configuration."""
        extra = "forbid"


class OperationalModeUpdateResponse(BaseModel):
    """Response model for PUT /api/operational_mode."""
    
    success: bool = Field(..., description="Whether the update was successful")
    mode: OperationalModeLiteral = Field(..., description="New operational mode")  
    message: str = Field(..., description="Success message")
    timestamp: str = Field(..., description="Response timestamp in ISO format")
    
    class Config:
        """Pydantic model configuration."""
        extra = "forbid"
