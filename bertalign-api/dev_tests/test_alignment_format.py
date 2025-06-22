#!/usr/bin/env python3
"""
Test alignment format and bertalign integration.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bertalign.aligner import Bertalign
from app.services.bertalign_service import BertalignService
from app.models import AlignmentRequest

def test_bertalign_alignment_format():
    """Test the bertalign alignment format and structure."""
    # Test data
    source_text = "Hello world. This is a test. How are you?"
    target_text = "Hola mundo. Esta es una prueba. ¿Cómo estás?"
    
    # Create Bertalign instance
    aligner = Bertalign(
        src=source_text,
        tgt=target_text,
        src_lang='en',
        tgt_lang='es',
        max_align=5,
        top_k=3,
        win=5,
        skip=-0.1,
        margin=True,
        len_penalty=True,
        is_split=False
    )
    
    # Perform alignment
    aligner.align_sents()
    
    # Verify basic structure
    assert hasattr(aligner, 'result'), "Aligner should have result attribute"
    assert len(aligner.result) > 0, "Should produce at least one alignment"
    assert hasattr(aligner, 'src_sents'), "Aligner should have src_sents"
    assert hasattr(aligner, 'tgt_sents'), "Aligner should have tgt_sents"
    
    # Verify sentence extraction
    assert len(aligner.src_sents) == 3, f"Expected 3 source sentences, got {len(aligner.src_sents)}"
    assert len(aligner.tgt_sents) == 3, f"Expected 3 target sentences, got {len(aligner.tgt_sents)}"
    
    # Verify alignment format
    for i, bead in enumerate(aligner.result):
        assert isinstance(bead, tuple), f"Bead {i} should be a tuple"
        assert len(bead) >= 2, f"Bead {i} should have at least 2 elements"
        
        src_indices, tgt_indices = bead[0], bead[1]
        assert hasattr(src_indices, '__iter__'), f"Source indices should be iterable"
        assert hasattr(tgt_indices, '__iter__'), f"Target indices should be iterable"
        
        # Verify indices are valid
        for idx in src_indices:
            assert 0 <= idx < len(aligner.src_sents), f"Source index {idx} out of range"
        for idx in tgt_indices:
            assert 0 <= idx < len(aligner.tgt_sents), f"Target index {idx} out of range"

def test_bertalign_service_integration():
    """Test that BertalignService correctly processes bertalign results."""
    # Create alignment request
    request = AlignmentRequest(
        source_text="Hello world. This is a test.",
        target_text="Hola mundo. Esta es una prueba.",
        source_language="en",
        target_language="es"
    )
    
    # Use the service
    response = BertalignService.align_texts(request)
    
    # Verify response structure
    assert response.source_language == "en", f"Expected source language 'en', got '{response.source_language}'"
    assert response.target_language == "es", f"Expected target language 'es', got '{response.target_language}'"
    assert len(response.alignments) > 0, "Should produce at least one alignment"
    assert response.processing_time > 0, "Processing time should be positive"
    
    # Verify alignment structure
    for alignment in response.alignments:
        assert len(alignment.source_sentences) > 0 or len(alignment.target_sentences) > 0, "Alignment should have sentences"
        assert len(alignment.source_indices) == len(alignment.source_sentences), "Source indices should match sentences"
        assert len(alignment.target_indices) == len(alignment.target_sentences), "Target indices should match sentences"
        assert 0.0 <= alignment.alignment_score <= 1.0, f"Alignment score should be between 0 and 1, got {alignment.alignment_score}"

def test_manual_alignment_extraction():
    """Test manual extraction of alignment data similar to the original test."""
    # Test data
    source_text = "Hello world. This is a test. How are you?"
    target_text = "Hola mundo. Esta es una prueba. ¿Cómo estás?"
    
    aligner = Bertalign(
        src=source_text,
        tgt=target_text,
        src_lang='en',
        tgt_lang='es'
    )
    
    aligner.align_sents()
    
    # Manual extraction test
    extracted_alignments = []
    for i, bead in enumerate(aligner.result):
        src_indices = bead[0]
        tgt_indices = bead[1]
        
        # Get source sentences
        src_sentences = [aligner.src_sents[idx] for idx in src_indices] if src_indices else []
        
        # Get target sentences
        tgt_sentences = [aligner.tgt_sents[idx] for idx in tgt_indices] if tgt_indices else []
        
        extracted_alignments.append({
            'source_sentences': src_sentences,
            'target_sentences': tgt_sentences,
            'source_indices': list(src_indices),
            'target_indices': list(tgt_indices)
        })
    
    # Verify we extracted some alignments
    assert len(extracted_alignments) > 0, "Should extract at least one alignment"
    
    # Verify structure of extracted alignments
    for alignment in extracted_alignments:
        assert 'source_sentences' in alignment
        assert 'target_sentences' in alignment
        assert 'source_indices' in alignment
        assert 'target_indices' in alignment

if __name__ == "__main__":
    print("=== Testing Bertalign Alignment Format ===\n")
    
    print("Testing basic alignment format...")
    test_bertalign_alignment_format()
    print("✓ Basic alignment format test passed\n")
    
    print("Testing service integration...")
    test_bertalign_service_integration()
    print("✓ Service integration test passed\n")
    
    print("Testing manual extraction...")
    test_manual_alignment_extraction()
    print("✓ Manual extraction test passed\n")
    
    print("=== All alignment format tests completed ===")