"""Operational Mode API endpoints for FastAPI.

Provides GET and PUT endpoints for managing operational mode via REST API.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from loguru import logger

from console.schemas import OperationalModeRequest, OperationalModeResponse, OperationalModeUpdateResponse


# Create router for operational mode endpoints
router = APIRouter(prefix="/api", tags=["operational_mode"])


@router.get("/operational_mode", response_model=OperationalModeResponse)
async def get_operational_mode() -> OperationalModeResponse:
    """Get current operational mode.
    
    Returns:
        Current operational mode with timestamp.
        
    Raises:
        HTTPException: If unable to read operational mode.
    """
    try:
        from config.operational_mode import get_mode
        
        current_mode = get_mode()
        
        logger.debug(f"GET /api/operational_mode: {current_mode}")
        
        return OperationalModeResponse(
            mode=current_mode,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting operational mode: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get operational mode: {str(e)}"
        ) from e


@router.put("/operational_mode", response_model=OperationalModeUpdateResponse)
async def set_operational_mode(request: OperationalModeRequest) -> OperationalModeUpdateResponse:
    """Set operational mode.
    
    Args:
        request: Request containing new operational mode.
        
    Returns:
        Success response with new mode.
        
    Raises:
        HTTPException: If mode is invalid or update fails.
    """
    try:
        from config.operational_mode import get_valid_modes, is_valid_mode, set_mode
        
        new_mode = request.mode  # Already validated by Pydantic enum
        
        # Validate mode
        if not is_valid_mode(new_mode):
            valid_modes = get_valid_modes()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operational mode '{new_mode}'. Valid modes: {', '.join(valid_modes)}"
            )
        
        # Set the new mode
        set_mode(new_mode)  # type: ignore[arg-type]
        
        logger.info(f"PUT /api/operational_mode: {new_mode}")
        
        return OperationalModeUpdateResponse(
            success=True,
            mode=new_mode,
            message=f"Operational mode successfully set to '{new_mode}'",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Invalid mode value
        logger.warning(f"Invalid operational mode in PUT request: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except OSError as e:
        # File operation error
        logger.error(f"Error persisting operational mode: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist operational mode: {str(e)}"
        ) from e
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error setting operational mode: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) from e
