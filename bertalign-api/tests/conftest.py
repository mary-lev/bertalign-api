import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_request():
    """Sample alignment request for testing."""
    return {
        "source_text": "Hello world. This is a test.",
        "target_text": "Bonjour le monde. Ceci est un test.",
        "source_language": "en",
        "target_language": "fr"
    }


@pytest.fixture
def sample_request_large():
    """Larger sample for performance testing."""
    return {
        "source_text": "Hello world. This is a test sentence. We are testing the alignment system. It should work well with multiple sentences. Each sentence should be aligned properly.",
        "target_text": "Bonjour le monde. Ceci est une phrase de test. Nous testons le système d'alignement. Il devrait bien fonctionner avec plusieurs phrases. Chaque phrase devrait être alignée correctement.",
        "source_language": "en",
        "target_language": "fr"
    }