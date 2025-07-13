"""
Alignment router for the Bertalign API.

This module handles all text alignment endpoints, including basic text alignment
and TEI XML document alignment. Uses the LaBSE (Language-agnostic BERT Sentence
Embedding) model for semantic similarity-based sentence alignment across 25 languages.

Endpoints:
- POST /align: Basic text-to-text alignment
- POST /align/tei: TEI XML document alignment with standOff annotations
"""

from fastapi import APIRouter, HTTPException, status
from app.models import AlignmentRequest, AlignmentResponse, ErrorResponse, TEIAlignmentRequest, TEIAlignmentResponse
from app.services.bertalign_service import BertalignService
from app.services.tei_service import TEIService

router = APIRouter(prefix="/align", tags=["alignment"])

# Initialize services
bertalign_service = BertalignService()
tei_service = TEIService(bertalign_service)


@router.post(
    "",
    response_model=AlignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Align two texts using semantic similarity",
    description="""
    Align sentences between source and target texts using the LaBSE model for semantic similarity.
    
    This endpoint:
    - Automatically detects sentence boundaries (or uses pre-split text)
    - Generates semantic embeddings for each sentence
    - Creates alignments based on similarity scores
    - Supports 25 languages with configurable alignment parameters
    
    **Typical response time:** 0.2-1.0 seconds depending on text length
    
    **Supported languages:** ca, zh, cs, da, nl, en, fi, fr, de, el, hu, is, it, lt, lv, no, pl, pt, ro, ru, sk, sl, es, sv, tr
    """,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input (malformed request, unsupported language, empty text)"},
        500: {"model": ErrorResponse, "description": "Internal server error (model loading failure, processing error)"},
    }
)
async def align_texts(request: AlignmentRequest) -> AlignmentResponse:
    """Align sentences between source and target texts using Bertalign."""
    try:
        return bertalign_service.align_texts(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tei",
    response_model=TEIAlignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Align TEI XML documents with standOff annotations",
    description="""
    Align TEI XML documents and generate aligned output with standOff linkGrp structure.
    
    This endpoint:
    - Parses TEI XML documents and extracts text from <p> and <head> elements
    - Aligns text segments using semantic similarity
    - Generates standOff annotations with linkGrp elements
    - Creates xml:id attributes for referencing aligned segments
    - Returns complete TEI document with both source and target texts
    
    **Use cases:**
    - Creating parallel corpora with TEI markup
    - Scholarly edition alignment
    - Digital humanities text alignment projects
    
    **Typical response time:** 1-3 seconds depending on document size
    
    **Input format:** Valid TEI XML documents with text content in body elements
    **Output format:** Complete TEI document with standOff linkGrp annotations
    """,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid TEI XML structure, malformed XML, or unsupported language"},
        500: {"model": ErrorResponse, "description": "Internal server error (XML parsing failure, alignment processing error)"},
    }
)
async def align_tei_documents(request: TEIAlignmentRequest) -> TEIAlignmentResponse:
    """Align two TEI documents and return aligned XML with standOff structure."""
    try:
        # Set bertalign parameters from request
        bertalign_service.max_align = request.max_align
        bertalign_service.top_k = request.top_k
        bertalign_service.win = request.win
        bertalign_service.skip = request.skip
        bertalign_service.margin = request.margin
        bertalign_service.len_penalty = request.len_penalty
        
        # Perform TEI alignment
        result = tei_service.align_tei_documents(
            source_xml=request.languageA,
            target_xml=request.languageB,
            source_language=request.languageA_name,
            target_language=request.languageB_name
        )
        print(f"TEI alignment result: {result}")
        return TEIAlignmentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TEI alignment failed: {str(e)}")


