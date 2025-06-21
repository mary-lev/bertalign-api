# Bertalign API

> **Multilingual Sentence Alignment Service using LaBSE Embeddings**

A FastAPI-based web service for multilingual sentence alignment using sentence-transformers (LaBSE model). Supports both plain text and TEI XML document alignment, deployed on Google Cloud Run with Docker containerization.

[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](https://github.com/bfsujason/bertalign)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-yellow.svg)](https://python.org)

## 🚀 Features

- **Multilingual Support**: Align sentences across 25 languages
- **Semantic Alignment**: Uses LaBSE embeddings for high-quality alignments
- **Flexible Alignment**: Support for 1-1, 1-many, many-1, and many-many alignments
- **TEI XML Support**: Align TEI documents with standOff annotations
- **FastAPI Backend**: Auto-generated OpenAPI docs and validation
- **Cloud Ready**: Dockerized for Google Cloud Run deployment
- **Fast Processing**: Optimized response times (0.2-3 seconds)

## 🌍 Supported Languages

`ca` (Catalan), `zh` (Chinese), `cs` (Czech), `da` (Danish), `nl` (Dutch), `en` (English), `fi` (Finnish), `fr` (French), `de` (German), `el` (Greek), `hu` (Hungarian), `is` (Icelandic), `it` (Italian), `lt` (Lithuanian), `lv` (Latvian), `no` (Norwegian), `pl` (Polish), `pt` (Portuguese), `ro` (Romanian), `ru` (Russian), `sk` (Slovak), `sl` (Slovenian), `es` (Spanish), `sv` (Swedish), `tr` (Turkish)

## 📚 Quick Start

### Local Development

```bash
cd bertalign-api
pip install -r requirements-api.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### 1. Basic Text Alignment

```bash
curl -X POST "http://localhost:8000/align" \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Hello world. How are you today?",
    "target_text": "Bonjour le monde. Comment allez-vous aujourd'\''hui?",
    "source_language": "en",
    "target_language": "fr"
  }'
```

**Response:**
```json
{
  "alignments": [
    {
      "source_sentences": ["Hello world."],
      "target_sentences": ["Bonjour le monde."],
      "alignment_score": 0.89,
      "source_indices": [0],
      "target_indices": [0]
    }
  ],
  "processing_time": 0.23,
  "total_source_sentences": 2,
  "total_target_sentences": 2
}
```

### 2. TEI XML Document Alignment

```bash
curl -X POST "http://localhost:8000/align/tei" \
  -H "Content-Type: application/json" \
  -d '{
    "source_tei": "<?xml version=\"1.0\"?><TEI xmlns=\"http://www.tei-c.org/ns/1.0\">...</TEI>",
    "target_tei": "<?xml version=\"1.0\"?><TEI xmlns=\"http://www.tei-c.org/ns/1.0\">...</TEI>",
    "source_language": "en",
    "target_language": "fr"
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

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and status |
| `/health` | GET | Health check and model status |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |
| `/align` | POST | Basic text alignment |
| `/align/tei` | POST | TEI XML document alignment with standOff annotations |

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `source_language` / `target_language` | string | ISO 639-1 language codes (e.g., "en", "fr") |
| `max_align` | integer | Maximum sentences in one alignment (1-10, default: 5) |
| `top_k` | integer | Number of alignment candidates (1-10, default: 3) |
| `win` | integer | Search window size (1-20, default: 5) |
| `is_split` | boolean | Whether text is pre-split into sentences |

## 📊 Project Status

✅ **Week 1 Completed** (v0.5) - **AHEAD OF SCHEDULE!**
- ✅ Real Bertalign integration with LaBSE model
- ✅ Comprehensive test suite (24/24 tests passing) 
- ✅ Cloud Run deployment working
- ✅ Performance optimized (<1s response times)
- ✅ **TEI XML alignment with standOff annotations** (bonus feature)
- ✅ **Language parameter validation** (25 supported languages)
- ✅ **Enhanced API documentation** with examples

### Performance Metrics

| Text Size | Endpoint | Response Time |
|-----------|----------|---------------|
| Small (1-5 sentences) | `/align` | 0.2-0.5 seconds |
| Medium (10-20 sentences) | `/align` | 0.5-1.0 seconds |
| TEI Documents | `/align/tei` | 1.0-3.0 seconds |

### Features Completed Beyond Original Plan

- **TEI XML Support**: Complete TEI document alignment with standOff markup
- **Enhanced Documentation**: Comprehensive API docs with examples
- **Language Validation**: Robust validation for 25 supported languages
- **Extended Test Coverage**: Tests for both basic and TEI alignment

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

## 🔬 TEI XML Features

### Supported TEI Elements
- `<p>` (paragraphs) - Primary alignment units
- `<head>` (headings) - Secondary alignment units  
- Full TEI header preservation
- Automatic `xml:id` generation for aligned elements

### StandOff Annotation Output
```xml
<standOff>
  <linkGrp type="translation">
    <link target="#source-uuid #target-uuid" type="Linguistic"/>
  </linkGrp>
</standOff>
```

### Use Cases
- **Digital Humanities**: Parallel corpus creation
- **Scholarly Editions**: Multilingual text alignment
- **Translation Studies**: Alignment analysis  
- **Text Research**: Cross-lingual text comparison

## 📈 Performance

- **Small texts**: ~0.23s
- **Medium texts**: ~0.75s
- **TEI documents**: ~1.2s 
- **Memory usage**: 8GB (with LaBSE model)
- **Concurrent requests**: Up to 5 per instance