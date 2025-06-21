"""
Model validation tests for Bertalign API.

This module tests Pydantic model validation for both AlignmentRequest 
and TEIAlignmentRequest models, ensuring proper validation of inputs.
"""

import pytest
from pydantic import ValidationError
from app.models import AlignmentRequest, TEIAlignmentRequest


def test_alignment_request_valid():
    """Test valid alignment request."""
    request = AlignmentRequest(
        source_text="Hello world.",
        target_text="Bonjour le monde.",
        source_language="en",
        target_language="fr"
    )
    assert request.source_language == "en"
    assert request.target_language == "fr"
    assert request.max_align == 5  # default


def test_alignment_request_custom_params():
    """Test alignment request with custom parameters."""
    request = AlignmentRequest(
        source_text="Hello world.",
        target_text="Bonjour le monde.",
        source_language="en",
        target_language="fr",
        max_align=3,
        top_k=5,
        win=10
    )
    assert request.max_align == 3
    assert request.top_k == 5
    assert request.win == 10


def test_empty_text_validation():
    """Test validation for empty texts."""
    with pytest.raises(ValidationError) as exc_info:
        AlignmentRequest(
            source_text="",
            target_text="Bonjour le monde.",
            source_language="en",
            target_language="fr"
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_whitespace_only_text_validation():
    """Test validation for whitespace-only texts."""
    with pytest.raises(ValidationError) as exc_info:
        AlignmentRequest(
            source_text="   \n\t  ",
            target_text="Bonjour le monde.",
            source_language="en",
            target_language="fr"
        )
    assert "Text cannot be empty" in str(exc_info.value)


def test_invalid_language_code():
    """Test validation for invalid language codes."""
    with pytest.raises(ValidationError) as exc_info:
        AlignmentRequest(
            source_text="Hello world.",
            target_text="Bonjour le monde.",
            source_language="eng",  # Invalid - should be 2 chars
            target_language="fr"
        )
    assert "String should match pattern" in str(exc_info.value)


def test_unsupported_language():
    """Test validation for unsupported languages."""
    with pytest.raises(ValidationError) as exc_info:
        AlignmentRequest(
            source_text="Hello world.",
            target_text="Bonjour le monde.",
            source_language="xx",  # Unsupported language
            target_language="fr"
        )
    assert "is not supported" in str(exc_info.value)


def test_parameter_ranges():
    """Test parameter validation ranges."""
    # Test max_align too high
    with pytest.raises(ValidationError):
        AlignmentRequest(
            source_text="Hello world.",
            target_text="Bonjour le monde.",
            source_language="en",
            target_language="fr",
            max_align=15  # Too high, max is 10
        )
    
    # Test skip penalty out of range
    with pytest.raises(ValidationError):
        AlignmentRequest(
            source_text="Hello world.",
            target_text="Bonjour le monde.",
            source_language="en",
            target_language="fr",
            skip=0.5  # Should be negative
        )


class TestTEIAlignmentRequest:
    """Tests for TEI alignment request model validation."""
    
    def test_valid_tei_request(self):
        """Test valid TEI alignment request."""
        simple_tei = '''<?xml version="1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p>Test</p></body></text></TEI>'''
        
        request = TEIAlignmentRequest(
            source_tei=simple_tei,
            target_tei=simple_tei,
            source_language="en",
            target_language="fr"
        )
        assert request.source_language == "en"
        assert request.target_language == "fr"
        assert request.max_align == 5  # default
    
    def test_tei_custom_parameters(self):
        """Test TEI request with custom alignment parameters."""
        simple_tei = '''<?xml version="1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p>Test</p></body></text></TEI>'''
        
        request = TEIAlignmentRequest(
            source_tei=simple_tei,
            target_tei=simple_tei,
            source_language="en",
            target_language="fr",
            max_align=3,
            top_k=2,
            win=4
        )
        assert request.max_align == 3
        assert request.top_k == 2
        assert request.win == 4
    
    def test_missing_language_parameters(self):
        """Test TEI request with missing required language parameters."""
        simple_tei = '''<?xml version="1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p>Test</p></body></text></TEI>'''
        
        with pytest.raises(ValidationError):
            TEIAlignmentRequest(
                source_tei=simple_tei,
                target_tei=simple_tei
                # Missing source_language and target_language
            )
    
    def test_invalid_tei_language_codes(self):
        """Test TEI request with invalid language codes."""
        simple_tei = '''<?xml version="1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p>Test</p></body></text></TEI>'''
        
        with pytest.raises(ValidationError) as exc_info:
            TEIAlignmentRequest(
                source_tei=simple_tei,
                target_tei=simple_tei,
                source_language="invalid",
                target_language="fr"
            )
        assert "String should match pattern" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            TEIAlignmentRequest(
                source_tei=simple_tei,
                target_tei=simple_tei,
                source_language="en",
                target_language="unsupported"
            )
        assert "is not supported" in str(exc_info.value)
    
    def test_empty_tei_xml(self):
        """Test TEI request with empty XML."""
        with pytest.raises(ValidationError):
            TEIAlignmentRequest(
                source_tei="",
                target_tei="<TEI></TEI>",
                source_language="en",
                target_language="fr"
            )
    
    def test_tei_size_limits(self):
        """Test TEI request size limits."""
        # Create a large XML string (over 1MB)
        large_xml = '''<?xml version="1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>''' + \
                   '''<p>''' + "x" * 1000000 + '''</p>''' + \
                   '''</body></text></TEI>'''
        
        with pytest.raises(ValidationError) as exc_info:
            TEIAlignmentRequest(
                source_tei=large_xml,
                target_tei="<TEI></TEI>",
                source_language="en",
                target_language="fr"
            )
        assert "String should have at most" in str(exc_info.value)