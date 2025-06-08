# Bertalign API

A FastAPI-based web service for multilingual sentence alignment using sentence-transformers (LaBSE model). Deployed on Google Cloud Run with Docker containerization.

## Features

- **Multilingual Support**: Align sentences across 25 languages
- **Semantic Alignment**: Uses LaBSE embeddings for high-quality alignments
- **Flexible Alignment**: Support for 1-1, 1-many, many-1, and many-many alignments
- **FastAPI Backend**: Auto-generated OpenAPI docs and validation
- **Cloud Ready**: Dockerized for Google Cloud Run deployment

## Quick Start

### Local Development

```bash
cd bertalign-api
pip install -r requirements-api.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### API Usage

```bash
curl -X POST "http://localhost:8000/align" \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Hello world. How are you?",
    "target_text": "Bonjour le monde. Comment allez-vous?",
    "source_language": "English",
    "target_language": "French"
  }'
```

## Docker Deployment

```bash
# Build container
docker build -t bertalign-api .

# Run locally
docker run -p 8080:8080 bertalign-api
```

## Google Cloud Run Deployment

```bash
# Deploy to Cloud Run
./deploy.sh v1.0
```

The deployment script handles:
- Building with Cloud Build
- Pushing to Container Registry
- Deploying to Cloud Run with optimal configuration (8GB memory, 4 CPU)

## API Endpoints

- `POST /align` - Align sentence pairs
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Project Status

✅ **Week 1 Completed** (v0.4)
- Real Bertalign integration with LaBSE model
- Comprehensive test suite (24/24 tests passing)
- Cloud Run deployment working
- Performance optimized (<1s response times)

## Architecture

```
bertalign-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── routers/alignment.py # API endpoints
│   └── services/            # Business logic
├── bertalign/               # Core alignment library
├── Dockerfile               # Container configuration
└── deploy.sh               # Cloud Run deployment
```

## Performance

- Small texts: ~0.23s
- Medium texts: ~0.75s
- Memory usage: 8GB (with LaBSE model)
- Concurrent requests: Up to 5 per instance