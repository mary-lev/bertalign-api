#!/usr/bin/env python3
"""
Manual test for TEI service functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.tei_service import TEIService
from app.services.bertalign_service import BertalignService

def test_basic_tei_parsing():
    """Test basic TEI parsing functionality."""
    print("Testing TEI parsing...")
    
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
    
    print(f"✓ Language: {doc.language}")
    print(f"✓ Title: {doc.title}")
    print(f"✓ Text elements found: {len(doc.text_elements)}")
    
    for i, elem in enumerate(doc.text_elements):
        print(f"  [{i}] {elem.tag}: {elem.text[:50]}...")
    
    print("TEI parsing test completed successfully!\n")

def test_tei_alignment():
    """Test full TEI alignment workflow."""
    print("Testing TEI alignment...")
    
    # Create services
    bertalign_service = BertalignService()
    tei_service = TEIService(bertalign_service)
    
    # Load actual test files
    with open('texts/italian.xml', 'r', encoding='utf-8') as f:
        italian_tei = f.read()
    
    with open('texts/english.xml', 'r', encoding='utf-8') as f:
        english_tei = f.read()
    
    print("✓ Loaded test TEI files")
    
    # Perform alignment
    try:
        result = tei_service.align_tei_documents(italian_tei, english_tei)
        
        print(f"✓ Source language: {result['source_language']}")
        print(f"✓ Target language: {result['target_language']}")
        print(f"✓ Alignment count: {result['alignment_count']}")
        print(f"✓ Processing time: {result['processing_time']:.2f}s")
        
        # Check aligned XML structure
        aligned_xml = result['aligned_xml']
        print(f"✓ Generated aligned XML ({len(aligned_xml)} chars)")
        
        # Verify key elements
        assert '<standOff>' in aligned_xml
        assert '<linkGrp type="translation">' in aligned_xml
        assert 'xml:id=' in aligned_xml
        print("✓ XML structure validation passed")
        
        # Save result for inspection
        with open('texts/test_output.xml', 'w', encoding='utf-8') as f:
            f.write(aligned_xml)
        print("✓ Saved aligned XML to texts/test_output.xml")
        
        print("TEI alignment test completed successfully!\n")
        
    except Exception as e:
        print(f"✗ TEI alignment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== TEI Service Manual Test ===\n")
    test_basic_tei_parsing()
    test_tei_alignment()
    print("=== All tests completed ===")