"""
Alignment router for the Bertalign API.
Handles text alignment endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import AlignmentRequest, AlignmentResponse, ErrorResponse
from app.services.bertalign_service import BertalignService

router = APIRouter(prefix="/align", tags=["alignment"])


@router.post(
    "",
    response_model=AlignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Align two texts",
    description="Align sentences between source and target texts using semantic similarity",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def align_texts(request: AlignmentRequest) -> AlignmentResponse:
    """Align sentences between source and target texts using Bertalign."""
    try:
        return BertalignService.align_texts(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


