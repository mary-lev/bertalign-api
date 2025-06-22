#!/usr/bin/env python3
"""
Manual test for TEI service functionality.
"""
import sys
import os
import pytest
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tei_service import TEIService
from app.services.bertalign_service import BertalignService

def test_basic_tei_parsing():
    """Test basic TEI parsing functionality."""
    # Create services
    bertalign_service = BertalignService()
    tei_service = TEIService(bertalign_service)
    
    # Sample Italian TEI
    italian_tei = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Test Document</title>
                <author>P. Klee</author>
            </titleStmt>
        </fileDesc>
        <profileDesc>
            <langUsage>
                <language ident="it">it</language>
            </langUsage>
        </profileDesc>
    </teiHeader>
    <text>
        <body>
            <div xml:id="div_intro">
                <p>Ciao mondo. Questo è un test.</p>
                <p>Benvenuti nel sistema di allineamento TEI.</p>
            </div>
        </body>
    </text>
</TEI>'''
    
    # Parse document
    doc = tei_service.parse_tei_file(italian_tei)
    
    # Verify parsing results
    assert doc.language == "it", f"Expected language 'it', got '{doc.language}'"
    assert doc.title == "Test Document", f"Expected title 'Test Document', got '{doc.title}'"
    assert len(doc.text_elements) > 0, "No text elements found"
    
    # Verify text elements contain expected content
    text_contents = [elem.text for elem in doc.text_elements]
    assert any("Ciao mondo" in text for text in text_contents), "Expected text content not found"
    assert any("Benvenuti" in text for text in text_contents), "Expected text content not found"

def test_tei_alignment():
    """Test full TEI alignment workflow."""
    # Create services
    bertalign_service = BertalignService()
    tei_service = TEIService(bertalign_service)
    
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
    
    # Load actual test files
    with open(italian_file, 'r', encoding='utf-8') as f:
        italian_tei = f.read()
    
    with open(english_file, 'r', encoding='utf-8') as f:
        english_tei = f.read()
    
    # Verify files were loaded
    assert len(italian_tei) > 100, "Italian TEI file appears to be empty or too small"
    assert len(english_tei) > 100, "English TEI file appears to be empty or too small"
    assert '<TEI' in italian_tei, "Italian file doesn't appear to be valid TEI"
    assert '<TEI' in english_tei, "English file doesn't appear to be valid TEI"
    
    # Perform alignment with explicit language parameters
    result = tei_service.align_tei_documents(italian_tei, english_tei, source_language="it", target_language="en")
    
    # Verify result structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert 'source_language' in result, "Missing source_language in result"
    assert 'target_language' in result, "Missing target_language in result"
    assert 'alignment_count' in result, "Missing alignment_count in result"
    assert 'processing_time' in result, "Missing processing_time in result"
    assert 'aligned_xml' in result, "Missing aligned_xml in result"
    
    # Verify alignment results
    assert result['alignment_count'] > 0, "No alignments were created"
    assert result['processing_time'] > 0, "Processing time should be positive"
    
    # Check aligned XML structure
    aligned_xml = result['aligned_xml']
    assert len(aligned_xml) > 100, "Aligned XML appears to be empty or too small"
    assert '<standOff>' in aligned_xml, "standOff element missing from aligned XML"
    assert '<linkGrp type="translation">' in aligned_xml, "linkGrp element missing from aligned XML"
    assert 'xml:id=' in aligned_xml, "xml:id attributes missing from aligned XML"
    
    # Optionally save result for inspection
    output_file = texts_dir / 'test_output.xml'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(aligned_xml)
    except Exception:
        # Don't fail test if we can't write output file
        pass

if __name__ == "__main__":
    print("=== TEI Service Manual Test ===\n")
    
    print("Running basic TEI parsing test...")
    try:
        test_basic_tei_parsing()
        print("✓ Basic TEI parsing test passed\n")
    except Exception as e:
        print(f"✗ Basic TEI parsing test failed: {e}\n")
        import traceback
        traceback.print_exc()
    
    print("Running TEI alignment test...")
    try:
        test_tei_alignment()
        print("✓ TEI alignment test passed\n")
    except Exception as e:
        print(f"✗ TEI alignment test failed: {e}\n")
        import traceback
        traceback.print_exc()
    
    print("=== Manual tests completed ===")