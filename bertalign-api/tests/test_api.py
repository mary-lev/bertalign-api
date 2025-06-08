import pytest
import time
from fastapi.testclient import TestClient


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_alignment_endpoint_basic(client, sample_request):
    """Test basic alignment functionality."""
    response = client.post("/align", json=sample_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "alignments" in data
    assert "source_language" in data
    assert "target_language" in data
    assert "processing_time" in data
    assert "total_source_sentences" in data
    assert "total_target_sentences" in data
    
    # Check language detection
    assert data["source_language"] == "English"
    assert data["target_language"] == "French"
    
    # Check we got some alignments
    assert len(data["alignments"]) > 0


def test_alignment_endpoint_different_languages(client):
    """Test alignment with different language pairs."""
    test_cases = [
        ("en", "de", "Hello world.", "Hallo Welt."),
        ("en", "es", "Hello world.", "Hola mundo."),
        ("fr", "en", "Bonjour le monde.", "Hello world.")
    ]
    
    for src_lang, tgt_lang, src_text, tgt_text in test_cases:
        request = {
            "source_text": src_text,
            "target_text": tgt_text,
            "source_language": src_lang,
            "target_language": tgt_lang
        }
        response = client.post("/align", json=request)
        assert response.status_code == 200, f"Failed for {src_lang}->{tgt_lang}"


def test_alignment_endpoint_custom_parameters(client, sample_request):
    """Test alignment with custom parameters."""
    custom_request = {
        **sample_request,
        "max_align": 3,
        "top_k": 5,
        "win": 10,
        "skip": -0.2,
        "margin": False,
        "len_penalty": False
    }
    
    response = client.post("/align", json=custom_request)
    assert response.status_code == 200
    
    data = response.json()
    # Check that custom parameters are returned
    params = data["parameters"]
    assert params["max_align"] == 3
    assert params["top_k"] == 5
    assert params["win"] == 10


def test_alignment_endpoint_pre_split(client):
    """Test alignment with pre-split sentences."""
    request = {
        "source_text": "Hello world.\nThis is a test.",
        "target_text": "Bonjour le monde.\nCeci est un test.",
        "source_language": "en",
        "target_language": "fr",
        "is_split": True
    }
    
    response = client.post("/align", json=request)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_source_sentences"] == 2
    assert data["total_target_sentences"] == 2


def test_alignment_endpoint_performance(client, sample_request_large):
    """Test alignment performance with larger text."""
    start_time = time.time()
    response = client.post("/align", json=sample_request_large)
    end_time = time.time()
    
    assert response.status_code == 200
    
    # Should complete within reasonable time
    assert end_time - start_time < 5.0  # 5 seconds max
    
    data = response.json()
    # Processing time should be reported
    assert data["processing_time"] > 0
    assert data["processing_time"] < 5.0


def test_alignment_endpoint_invalid_request(client):
    """Test alignment endpoint with invalid requests."""
    # Missing required fields
    response = client.post("/align", json={})
    assert response.status_code == 422
    
    # Invalid language
    invalid_request = {
        "source_text": "Hello world.",
        "target_text": "Bonjour le monde.",
        "source_language": "invalid",
        "target_language": "fr"
    }
    response = client.post("/align", json=invalid_request)
    assert response.status_code == 422
    
    # Empty text
    empty_request = {
        "source_text": "",
        "target_text": "Bonjour le monde.",
        "source_language": "en",
        "target_language": "fr"
    }
    response = client.post("/align", json=empty_request)
    assert response.status_code == 422


def test_alignment_endpoint_edge_cases(client):
    """Test alignment with edge cases."""
    # Single sentence
    single_request = {
        "source_text": "Hello world.",
        "target_text": "Bonjour le monde.",
        "source_language": "en",
        "target_language": "fr"
    }
    response = client.post("/align", json=single_request)
    assert response.status_code == 200
    
    # Very short text
    short_request = {
        "source_text": "Hi.",
        "target_text": "Bonjour.",
        "source_language": "en",
        "target_language": "fr"
    }
    response = client.post("/align", json=short_request)
    assert response.status_code == 200
    
    # Mismatched sentence counts
    mismatch_request = {
        "source_text": "Hello. World. Test.",
        "target_text": "Bonjour le monde.",
        "source_language": "en",
        "target_language": "fr"
    }
    response = client.post("/align", json=mismatch_request)
    assert response.status_code == 200


def test_openapi_docs(client):
    """Test that OpenAPI documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    assert "/align" in data["paths"]