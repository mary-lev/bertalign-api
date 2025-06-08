"""
Pydantic models for the Bertalign API.
Defines request and response schemas for alignment endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class AlignmentRequest(BaseModel):
    """Request model for text alignment."""
    
    source_text: str = Field(
        ..., 
        description="Source text to align",
        min_length=1,
        max_length=50000,
        example="Hello world. This is a test."
    )
    
    target_text: str = Field(
        ..., 
        description="Target text to align", 
        min_length=1,
        max_length=50000,
        example="Bonjour le monde. Ceci est un test."
    )
    
    source_language: str = Field(
        ...,
        description="ISO 639-1 language code for source text",
        pattern="^[a-z]{2}$",
        example="en"
    )
    
    target_language: str = Field(
        ...,
        description="ISO 639-1 language code for target text", 
        pattern="^[a-z]{2}$",
        example="fr"
    )
    
    max_align: int = Field(
        default=5,
        description="Maximum alignment size (1-1, 1-2, etc.)",
        ge=1,
        le=10
    )
    
    top_k: int = Field(
        default=3,
        description="Top K candidates for alignment",
        ge=1,
        le=10
    )
    
    win: int = Field(
        default=5,
        description="Window size for search",
        ge=1,
        le=20
    )
    
    skip: float = Field(
        default=-0.1,
        description="Skip penalty",
        ge=-1.0,
        le=0.0
    )
    
    margin: bool = Field(
        default=True,
        description="Use margin in scoring"
    )
    
    len_penalty: bool = Field(
        default=True,
        description="Apply length penalty"
    )
    
    is_split: bool = Field(
        default=False,
        description="Whether input texts are pre-split into sentences"
    )
    
    @validator('source_text', 'target_text')
    def validate_text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()
    
    @validator('source_language', 'target_language')
    def validate_supported_language(cls, v):
        # Supported languages from bertalign/utils.py LANG.SPLITTER
        supported_langs = {
            'ca', 'zh', 'cs', 'da', 'nl', 'en', 'fi', 'fr', 'de', 'el', 
            'hu', 'is', 'it', 'lt', 'lv', 'no', 'pl', 'pt', 'ro', 'ru', 
            'sk', 'sl', 'es', 'sv', 'tr'
        }
        if v not in supported_langs:
            raise ValueError(f'Language "{v}" is not supported. Supported languages: {sorted(supported_langs)}')
        return v


class AlignmentPair(BaseModel):
    """A single alignment pair between source and target sentences."""
    
    source_sentences: List[str] = Field(
        ...,
        description="Source sentences in this alignment"
    )
    
    target_sentences: List[str] = Field(
        ...,
        description="Target sentences in this alignment"
    )
    
    alignment_score: float = Field(
        ...,
        description="Alignment confidence score"
    )
    
    source_indices: List[int] = Field(
        ...,
        description="Indices of source sentences"
    )
    
    target_indices: List[int] = Field(
        ...,
        description="Indices of target sentences"
    )


class AlignmentResponse(BaseModel):
    """Response model for text alignment."""
    
    alignments: List[AlignmentPair] = Field(
        ...,
        description="List of aligned sentence pairs"
    )
    
    source_language: Optional[str] = Field(
        None,
        description="Detected source language"
    )
    
    target_language: Optional[str] = Field(
        None,
        description="Detected target language"
    )
    
    processing_time: float = Field(
        ...,
        description="Processing time in seconds"
    )
    
    total_source_sentences: int = Field(
        ...,
        description="Total number of source sentences"
    )
    
    total_target_sentences: int = Field(
        ...,
        description="Total number of target sentences"
    )
    
    parameters: AlignmentRequest = Field(
        ...,
        description="Parameters used for alignment"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(
        ...,
        description="Error message"
    )
    
    detail: Optional[str] = Field(
        None,
        description="Detailed error information"
    )
    
    error_code: Optional[str] = Field(
        None,
        description="Error code for programmatic handling"
    )


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(
        default="healthy",
        description="Service health status"
    )
    
    version: str = Field(
        default="v0.2",
        description="API version"
    )
    
    model_loaded: bool = Field(
        default=False,
        description="Whether the Bertalign model is loaded"
    )