"""
Pydantic models for the Bertalign API.

This module defines the request and response schemas for all alignment endpoints,
including validation rules, examples, and comprehensive documentation for the
automatically generated OpenAPI/Swagger documentation.

Supported Endpoints:
- POST /align: Basic text alignment
- POST /align/tei: TEI XML document alignment
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class AlignmentRequest(BaseModel):
    """
    Request model for basic text alignment using Bertalign's semantic similarity.
    
    This endpoint aligns sentences between source and target texts using the LaBSE
    (Language-agnostic BERT Sentence Embedding) model. The service automatically
    detects sentence boundaries and creates alignments based on semantic similarity.
    """
    
    source_text: str = Field(
        ..., 
        description="Source text to align. Can be raw text (sentences will be automatically detected) or pre-split sentences (one per line with is_split=True)",
        min_length=1,
        max_length=50000,
        example="Hello world. This is a test sentence. How are you today?"
    )
    
    target_text: str = Field(
        ..., 
        description="Target text to align against the source text. Should be the translation or parallel version of the source text", 
        min_length=1,
        max_length=50000,
        example="Bonjour le monde. Ceci est une phrase de test. Comment allez-vous aujourd'hui?"
    )
    
    source_language: str = Field(
        ...,
        description="ISO 639-1 language code for source text. Must be one of the 25 supported languages: ca, zh, cs, da, nl, en, fi, fr, de, el, hu, is, it, lt, lv, no, pl, pt, ro, ru, sk, sl, es, sv, tr",
        pattern="^[a-z]{2}$",
        example="en"
    )
    
    target_language: str = Field(
        ...,
        description="ISO 639-1 language code for target text. Must be one of the 25 supported languages", 
        pattern="^[a-z]{2}$",
        example="fr"
    )
    
    max_align: int = Field(
        default=5,
        description="Maximum number of sentences that can be aligned together (e.g., 1-to-many or many-to-many alignments). Higher values allow more complex alignments but increase processing time",
        ge=1,
        le=10,
        example=5
    )
    
    top_k: int = Field(
        default=3,
        description="Number of top candidate alignments to consider during the search process. Higher values improve alignment quality but increase processing time",
        ge=1,
        le=10,
        example=3
    )
    
    win: int = Field(
        default=5,
        description="Search window size for alignment candidates. Larger windows consider more distant alignments but increase computational cost",
        ge=1,
        le=20,
        example=5
    )
    
    skip: float = Field(
        default=-0.1,
        description="Penalty for skipping sentences during alignment. Negative values (closer to 0) make skipping less likely",
        ge=-1.0,
        le=0.0,
        example=-0.1
    )
    
    margin: bool = Field(
        default=True,
        description="Whether to use margin-based scoring in the alignment algorithm. Generally improves alignment quality",
        example=True
    )
    
    len_penalty: bool = Field(
        default=True,
        description="Whether to apply length-based penalties during alignment. Helps balance alignments for texts of different lengths",
        example=True
    )
    
    is_split: bool = Field(
        default=False,
        description="Set to true if input texts are already split into sentences (one sentence per line). If false, automatic sentence detection will be performed",
        example=False
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
    """
    A single alignment pair between source and target sentences.
    
    Represents one alignment unit, which can be 1-to-1, 1-to-many, many-to-1, 
    or many-to-many sentence alignments based on semantic similarity.
    """
    
    source_sentences: List[str] = Field(
        ...,
        description="List of source language sentences that are aligned together",
        example=["Hello world.", "This is a test."]
    )
    
    target_sentences: List[str] = Field(
        ...,
        description="List of target language sentences that are aligned together",
        example=["Bonjour le monde.", "Ceci est un test."]
    )
    
    alignment_score: float = Field(
        ...,
        description="Confidence score for this alignment (0.0 to 1.0). Higher scores indicate stronger semantic similarity",
        ge=0.0,
        le=1.0,
        example=0.85
    )
    
    source_indices: List[int] = Field(
        ...,
        description="Zero-based indices of the source sentences in the original text",
        example=[0, 1]
    )
    
    target_indices: List[int] = Field(
        ...,
        description="Zero-based indices of the target sentences in the original text",
        example=[0, 1]
    )


class AlignmentResponse(BaseModel):
    """
    Response model for text alignment containing aligned sentence pairs and metadata.
    
    Returns the complete alignment result with confidence scores, processing statistics,
    and the parameters used for the alignment.
    """
    
    alignments: List[AlignmentPair] = Field(
        ...,
        description="List of aligned sentence pairs ordered by their position in the source text",
        example=[
            {
                "source_sentences": ["Hello world."],
                "target_sentences": ["Bonjour le monde."],
                "alignment_score": 0.89,
                "source_indices": [0],
                "target_indices": [0]
            }
        ]
    )
    
    source_language: Optional[str] = Field(
        None,
        description="Confirmed source language (from request parameters)",
        example="en"
    )
    
    target_language: Optional[str] = Field(
        None,
        description="Confirmed target language (from request parameters)",
        example="fr"
    )
    
    processing_time: float = Field(
        ...,
        description="Total processing time in seconds",
        example=0.23
    )
    
    total_source_sentences: int = Field(
        ...,
        description="Total number of sentences detected in the source text",
        example=3
    )
    
    total_target_sentences: int = Field(
        ...,
        description="Total number of sentences detected in the target text",
        example=3
    )
    
    parameters: AlignmentRequest = Field(
        ...,
        description="Complete parameters used for this alignment (includes defaults)"
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


class TEIAlignmentRequest(BaseModel):
    """
    Request model for TEI document alignment.
    
    This endpoint aligns TEI XML documents and generates standOff annotations with
    linkGrp elements that reference aligned paragraphs across documents. Useful for
    creating aligned parallel corpora with TEI-compliant markup.
    """
    
    source_tei: str = Field(
        ...,
        description="Source TEI XML document as string. Must be valid TEI XML with text content in <body> elements. Supports <p> and <head> elements for alignment",
        min_length=1,
        max_length=1000000,  # 1MB limit for XML content
        example='<?xml version="1.0" encoding="UTF-8"?>\n<TEI xmlns="http://www.tei-c.org/ns/1.0">\n  <teiHeader>\n    <fileDesc>\n      <titleStmt><title>Example</title></titleStmt>\n    </fileDesc>\n  </teiHeader>\n  <text><body><p>Hello world.</p></body></text>\n</TEI>'
    )
    
    target_tei: str = Field(
        ...,
        description="Target TEI XML document as string. Should be the parallel/translated version of the source TEI document",
        min_length=1,
        max_length=1000000,  # 1MB limit for XML content
        example='<?xml version="1.0" encoding="UTF-8"?>\n<TEI xmlns="http://www.tei-c.org/ns/1.0">\n  <teiHeader>\n    <fileDesc>\n      <titleStmt><title>Exemple</title></titleStmt>\n    </fileDesc>\n  </teiHeader>\n  <text><body><p>Bonjour le monde.</p></body></text>\n</TEI>'
    )
    
    source_language: str = Field(
        ...,
        description="ISO 639-1 language code for source document. Overrides any language specified in TEI metadata. Must be one of the 25 supported languages",
        pattern="^[a-z]{2}$",
        example="en"
    )
    
    target_language: str = Field(
        ...,
        description="ISO 639-1 language code for target document. Overrides any language specified in TEI metadata", 
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
    
    @validator('source_tei', 'target_tei')
    def validate_tei_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('TEI XML cannot be empty or whitespace only')
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


class TEIAlignmentResponse(BaseModel):
    """
    Response model for TEI document alignment.
    
    Returns a complete TEI document with standOff annotations containing linkGrp
    elements that reference aligned text segments. The aligned XML includes both
    source and target documents with xml:id attributes for referencing.
    """
    
    aligned_xml: str = Field(
        ...,
        description="Complete aligned TEI XML document with standOff structure. Contains both source and target documents with xml:id attributes and linkGrp elements for alignments",
        example='<?xml version="1.0" encoding="UTF-8"?>\n<TEI xmlns="http://www.tei-c.org/ns/1.0">\n  <teiHeader>...</teiHeader>\n  <standOff>\n    <linkGrp type="translation">\n      <link target="#uuid1 #uuid2" type="Linguistic"/>\n    </linkGrp>\n  </standOff>\n  <text><body><p xml:id="uuid1">Hello world.</p></body></text>\n  <text><body><p xml:id="uuid2">Bonjour le monde.</p></body></text>\n</TEI>'
    )
    
    source_language: str = Field(
        ...,
        description="Source document language used for alignment",
        example="en"
    )
    
    target_language: str = Field(
        ...,
        description="Target document language used for alignment",
        example="fr"
    )
    
    alignment_count: int = Field(
        ...,
        description="Number of alignment pairs created between the documents",
        example=5
    )
    
    processing_time: float = Field(
        ...,
        description="Total processing time in seconds",
        example=1.2
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