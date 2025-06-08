import pytest
from unittest.mock import Mock, patch
from app.services.bertalign_service import BertalignService
from app.models import AlignmentRequest


def test_bertalign_service_basic():
    """Test basic service functionality."""
    request = AlignmentRequest(
        source_text="Hello world.",
        target_text="Bonjour le monde.",
        source_language="en",
        target_language="fr"
    )
    
    response = BertalignService.align_texts(request)
    
    assert response.source_language == "English"
    assert response.target_language == "French"
    assert response.processing_time > 0
    assert len(response.alignments) > 0


def test_bertalign_service_alignment_structure():
    """Test alignment response structure."""
    request = AlignmentRequest(
        source_text="Hello world. This is a test.",
        target_text="Bonjour le monde. Ceci est un test.",
        source_language="en",
        target_language="fr"
    )
    
    response = BertalignService.align_texts(request)
    
    # Check alignment structure
    for alignment in response.alignments:
        assert hasattr(alignment, 'source_sentences')
        assert hasattr(alignment, 'target_sentences')
        assert hasattr(alignment, 'source_indices')
        assert hasattr(alignment, 'target_indices')
        assert hasattr(alignment, 'alignment_score')
        
        # Indices should be lists of integers
        assert isinstance(alignment.source_indices, list)
        assert isinstance(alignment.target_indices, list)
        
        # Sentences should be lists of strings
        assert isinstance(alignment.source_sentences, list)
        assert isinstance(alignment.target_sentences, list)


def test_bertalign_service_parameters():
    """Test that service respects custom parameters."""
    request = AlignmentRequest(
        source_text="Hello world. This is a test.",
        target_text="Bonjour le monde. Ceci est un test.",
        source_language="en",
        target_language="fr",
        max_align=3,
        top_k=5
    )
    
    response = BertalignService.align_texts(request)
    
    # Parameters should be preserved in response
    assert response.parameters.max_align == 3
    assert response.parameters.top_k == 5


def test_bertalign_service_error_handling():
    """Test service error handling."""
    # This will likely raise an error due to invalid language in actual Bertalign
    # but should be caught by our service
    with pytest.raises((ValueError, RuntimeError)):
        request = AlignmentRequest(
            source_text="Hello world.",
            target_text="Bonjour le monde.",
            source_language="xx",  # This should be caught by validation first
            target_language="fr"
        )


def test_bertalign_service_different_text_sizes():
    """Test service with different text sizes."""
    # Small text
    small_request = AlignmentRequest(
        source_text="Hi.",
        target_text="Salut.",
        source_language="en",
        target_language="fr"
    )
    response = BertalignService.align_texts(small_request)
    assert response.total_source_sentences >= 1
    assert response.total_target_sentences >= 1
    
    # Medium text
    medium_request = AlignmentRequest(
        source_text="Hello world. This is a test. How are you today?",
        target_text="Bonjour le monde. Ceci est un test. Comment allez-vous aujourd'hui?",
        source_language="en",
        target_language="fr"
    )
    response = BertalignService.align_texts(medium_request)
    assert response.total_source_sentences >= 3
    assert response.total_target_sentences >= 3


def test_bertalign_service_pre_split():
    """Test service with pre-split text."""
    request = AlignmentRequest(
        source_text="Hello world.\nThis is a test.",
        target_text="Bonjour le monde.\nCeci est un test.",
        source_language="en",
        target_language="fr",
        is_split=True
    )
    
    response = BertalignService.align_texts(request)
    assert response.total_source_sentences == 2
    assert response.total_target_sentences == 2


@patch('app.services.bertalign_service.Bertalign')
def test_bertalign_service_initialization_error(mock_bertalign):
    """Test service behavior when Bertalign initialization fails."""
    mock_bertalign.side_effect = Exception("Model loading failed")
    
    request = AlignmentRequest(
        source_text="Hello world.",
        target_text="Bonjour le monde.",
        source_language="en",
        target_language="fr"
    )
    
    with pytest.raises(RuntimeError) as exc_info:
        BertalignService.align_texts(request)
    
    assert "Failed to initialize Bertalign" in str(exc_info.value)


@patch('app.services.bertalign_service.Bertalign')
def test_bertalign_service_alignment_error(mock_bertalign):
    """Test service behavior when alignment fails."""
    mock_instance = Mock()
    mock_instance.align_sents.side_effect = Exception("Alignment computation failed")
    mock_bertalign.return_value = mock_instance
    
    request = AlignmentRequest(
        source_text="Hello world.",
        target_text="Bonjour le monde.",
        source_language="en",
        target_language="fr"
    )
    
    with pytest.raises(RuntimeError) as exc_info:
        BertalignService.align_texts(request)
    
    assert "Alignment failed" in str(exc_info.value)