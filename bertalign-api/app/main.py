from fastapi import FastAPI
from datetime import datetime
import sys
import os

# Add bertalign to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.routers import alignment
from app.models import HealthResponse

app = FastAPI(
    title="Bertalign API",
    description="Multilingual sentence alignment service using LaBSE embeddings",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(alignment.router)

@app.get("/")
async def root():
    return {
        "message": "Bertalign API - Ready to align sentences!",
        "version": "0.2.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "align": "/align"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        version="0.2.0",
        model_loaded=False  # Will be True in v0.3 when we integrate real Bertalign
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)