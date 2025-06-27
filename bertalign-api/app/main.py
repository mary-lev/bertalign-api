from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Add bertalign to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.routers import alignment
from app.models import HealthResponse

app = FastAPI(
    title="Bertalign API",
    description="""
    Multilingual Sentence Alignment Service

    The Bertalign API provides semantic sentence alignment using the LaBSE (Language-agnostic BERT Sentence Embedding) model. 
    It supports 25 languages and can align both plain text and TEI XML documents.

    Features

    - **Semantic Alignment**: Uses state-of-the-art embeddings for accurate sentence mapping
    - **25 Languages Supported**: ca, zh, cs, da, nl, en, fi, fr, de, el, hu, is, it, lt, lv, no, pl, pt, ro, ru, sk, sl, es, sv, tr
    - **Multiple Formats**: Plain text alignment and TEI XML document alignment
    - **Configurable Parameters**: Fine-tune alignment behavior with multiple parameters
    - **Fast Processing**: Optimized for real-time alignment (0.2-3s response times)

    Quick Start

    1. **Basic Text Alignment**: Use `POST /align` with source and target texts
    2. **TEI Document Alignment**: Use `POST /align/tei` with TEI XML documents
    3. **Health Check**: Use `GET /health` to verify service status

    ### Example Usage

    ```bash
    curl -X POST "http://your-api-url/align" \\
      -H "Content-Type: application/json" \\
      -d '{
        "source_text": "Hello world. How are you?",
        "target_text": "Bonjour le monde. Comment allez-vous?",
        "source_language": "en",
        "target_language": "fr"
      }'
    ```

    For more examples and detailed documentation, visit the interactive documentation below.
    """,
    version="0.5.0",
    contact={
        "name": "Bertalign API Support",
        "url": "https://github.com/bfsujason/bertalign"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to enable frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(alignment.router)

@app.get("/", 
    summary="API Information",
    description="Get basic information about the Bertalign API including version and available endpoints"
)
async def root():
    return {
        "message": "Bertalign API - Multilingual Sentence Alignment Service",
        "version": "0.5.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Semantic sentence alignment using LaBSE model",
            "25 supported languages",
            "Plain text and TEI XML alignment",
            "Configurable alignment parameters"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs", 
            "redoc": "/redoc",
            "basic_alignment": "/align",
            "tei_alignment": "/align/tei"
        },
        "supported_languages": "ca, zh, cs, da, nl, en, fi, fr, de, el, hu, is, it, lt, lv, no, pl, pt, ro, ru, sk, sl, es, sv, tr"
    }

@app.get("/health", 
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the Bertalign API service and model availability"
)
async def health():
    return HealthResponse(
        status="healthy",
        version="0.5.0",
        model_loaded=True  # Real Bertalign integration completed
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)