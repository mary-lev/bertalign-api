#!/usr/bin/env python3
"""
Test TEI alignment with actual files using real TEI and Bertalign services.
"""
import sys
import os
import pytest
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tei_service import TEIService
from app.services.bertalign_service import BertalignService

def test_with_actual_files():
    """Test with actual Italian and English TEI files using real services."""
    # Find the texts directory relative to this test file
    current_dir = Path(__file__).parent
    texts_dir = current_dir / 'texts'
    if not texts_dir.exists():
        # Try parent directory
        texts_dir = current_dir.parent / 'texts'
    
    italian_file = texts_dir / 'italian.xml'
    english_file = texts_dir / 'english.xml'
    
    # Skip test if files don't exist
    if not italian_file.exists() or not english_file.exists():
        pytest.skip(f"Test files not found: {italian_file} or {english_file}")
    
    # Load files
    with open(italian_file, 'r', encoding='utf-8') as f:
        italian_xml = f.read()
    
    with open(english_file, 'r', encoding='utf-8') as f:
        english_xml = f.read()
    
    # Verify files were loaded
    assert len(italian_xml) > 100, "Italian XML file appears to be empty or too small"
    assert len(english_xml) > 100, "English XML file appears to be empty or too small"
    assert '<TEI' in italian_xml, "Italian file doesn't appear to be valid TEI"
    assert '<TEI' in english_xml, "English file doesn't appear to be valid TEI"
    
    # Create real services
    bertalign_service = BertalignService()
    tei_service = TEIService(bertalign_service)
    
    # Test alignment using real TEI service
    result = tei_service.align_tei_documents(
        italian_xml, 
        english_xml, 
        source_language="it", 
        target_language="en"
    )
    
    # Verify result structure (should match real TEI service output)
    assert isinstance(result, dict), "Result should be a dictionary"
    required_keys = ['aligned_xml', 'source_language', 'target_language', 'alignment_count', 'processing_time']
    for key in required_keys:
        assert key in result, f"Missing key '{key}' in result"
    
    # Verify result values
    assert result['source_language'] == 'it', f"Expected source language 'it', got '{result['source_language']}'"
    assert result['target_language'] == 'en', f"Expected target language 'en', got '{result['target_language']}'"
    assert result['alignment_count'] > 0, "No alignments were created"
    assert result['processing_time'] > 0, "Processing time should be positive"
    assert len(result['aligned_xml']) > 100, "Aligned XML appears to be empty or too small"
    
    # Verify aligned XML structure (real TEI service output)
    aligned_xml = result['aligned_xml']
    assert '<TEI' in aligned_xml, "TEI root element missing"
    assert '<standOff>' in aligned_xml, "standOff element missing"
    assert '<linkGrp' in aligned_xml, "linkGrp element missing"
    assert 'xml:id=' in aligned_xml, "xml:id attributes missing"
    
    # Test individual parsing as well
    source_doc = tei_service.parse_tei_file(italian_xml)
    target_doc = tei_service.parse_tei_file(english_xml)
    
    # Verify parsing results
    assert source_doc.language in ['it', 'unknown'], f"Unexpected source language: {source_doc.language}"
    assert target_doc.language in ['en', 'unknown'], f"Unexpected target language: {target_doc.language}"
    assert len(source_doc.text_elements) > 0, "No source text elements found"
    assert len(target_doc.text_elements) > 0, "No target text elements found"
    
    # Verify text elements have content
    source_texts = [elem.text for elem in source_doc.text_elements if elem.text.strip()]
    target_texts = [elem.text for elem in target_doc.text_elements if elem.text.strip()]
    assert len(source_texts) > 0, "No source text content found"
    assert len(target_texts) > 0, "No target text content found"
    
    # Optionally save result for inspection
    output_file = texts_dir / 'test_aligned_output.xml'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['aligned_xml'])
    except Exception:
        # Don't fail test if we can't write output file
        pass

if __name__ == "__main__":
    print("=== Testing with actual TEI files (using real services) ===\n")
    try:
        test_with_actual_files()
        print("✓ Test completed successfully")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()