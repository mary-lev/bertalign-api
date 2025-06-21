"""
Test configuration and fixtures for Bertalign API tests.

This module provides shared fixtures and configuration for all test modules.
Organized to support both basic alignment and TEI XML alignment testing.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


# =============================================================================
# Base Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def client():
    """Test client for the FastAPI app (session-scoped for efficiency)."""
    return TestClient(app)


# =============================================================================
# Basic Alignment Test Data
# =============================================================================

@pytest.fixture
def basic_alignment_request():
    """Basic alignment request for standard testing."""
    return {
        "source_text": "Hello world. This is a test.",
        "target_text": "Bonjour le monde. Ceci est un test.",
        "source_language": "en",
        "target_language": "fr"
    }

@pytest.fixture
def medium_alignment_request():
    """Medium-sized text for performance testing."""
    return {
        "source_text": "Hello world. This is a test sentence. We are testing the alignment system. It should work well with multiple sentences. Each sentence should be aligned properly.",
        "target_text": "Bonjour le monde. Ceci est une phrase de test. Nous testons le système d'alignement. Il devrait bien fonctionner avec plusieurs phrases. Chaque phrase devrait être alignée correctement.",
        "source_language": "en",
        "target_language": "fr"
    }

@pytest.fixture
def multilanguage_test_cases():
    """Multiple language pairs for comprehensive testing."""
    return [
        {
            "source_text": "Hello world.",
            "target_text": "Hallo Welt.",
            "source_language": "en",
            "target_language": "de",
            "description": "English-German"
        },
        {
            "source_text": "Hello world.",
            "target_text": "Hola mundo.",
            "source_language": "en", 
            "target_language": "es",
            "description": "English-Spanish"
        },
        {
            "source_text": "Bonjour le monde.",
            "target_text": "Hello world.",
            "source_language": "fr",
            "target_language": "en", 
            "description": "French-English"
        }
    ]

@pytest.fixture
def pre_split_request():
    """Request with pre-split sentences."""
    return {
        "source_text": "Hello world.\nThis is a test.",
        "target_text": "Bonjour le monde.\nCeci est un test.",
        "source_language": "en",
        "target_language": "fr",
        "is_split": True
    }


# =============================================================================
# TEI XML Test Data
# =============================================================================

@pytest.fixture
def simple_italian_tei():
    """Simple Italian TEI document for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test Document</title></titleStmt>
        </fileDesc>
        <profileDesc>
            <langUsage><language ident="it">Italian</language></langUsage>
        </profileDesc>
    </teiHeader>
    <text><body><div><p>Ciao mondo.</p></div></body></text>
</TEI>'''

@pytest.fixture
def simple_english_tei():
    """Simple English TEI document for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test Document</title></titleStmt>
        </fileDesc>
        <profileDesc>
            <langUsage><language ident="en">English</language></langUsage>
        </profileDesc>
    </teiHeader>
    <text><body><div><p>Hello world.</p></div></body></text>
</TEI>'''

@pytest.fixture
def basic_tei_request(simple_italian_tei, simple_english_tei):
    """Basic TEI alignment request."""
    return {
        "source_tei": simple_italian_tei,
        "target_tei": simple_english_tei,
        "source_language": "it",
        "target_language": "en"
    }


# =============================================================================
# Legacy Fixtures (for backward compatibility)
# =============================================================================

@pytest.fixture
def sample_request(basic_alignment_request):
    """Legacy fixture name for backward compatibility."""
    return basic_alignment_request

@pytest.fixture  
def sample_request_large(medium_alignment_request):
    """Legacy fixture name for backward compatibility."""
    return medium_alignment_request