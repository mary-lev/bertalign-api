import pytest
from pydantic import ValidationError
from app.models import AlignmentRequest


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