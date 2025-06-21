#!/usr/bin/env python3
"""
Simple test for TEI parsing without bertalign dependencies.
"""
import uuid
from xml.etree import ElementTree as ET

def test_tei_parsing():
    """Test basic TEI XML parsing and structure creation."""
    print("Testing TEI XML parsing...")
    
    # Sample TEI document
    italian_tei = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Contributi alla teoria figurativa della forma</title>
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
                <p>Come introduzione un breve chiarimento concettuale.</p>
                <p>In primo luogo ciò che è contenuto nel concetto di analisi.</p>
            </div>
        </body>
    </text>
</TEI>'''
    
    # Parse XML
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    root = ET.fromstring(italian_tei)
    
    # Extract language
    lang_elem = root.find('.//tei:profileDesc/tei:langUsage/tei:language', ns)
    language = lang_elem.attrib['ident'] if lang_elem is not None else 'unknown'
    print(f"✓ Language: {language}")
    
    # Extract title
    title_elem = root.find('.//tei:titleStmt/tei:title', ns)
    title = title_elem.text.strip() if title_elem is not None and title_elem.text else 'Untitled'
    print(f"✓ Title: {title}")
    
    # Extract paragraphs
    body = root.find('.//tei:body', ns)
    paragraphs = []
    for elem in body.iter():
        if elem.tag.endswith('}p'):
            text_content = elem.text.strip() if elem.text else ''
            if text_content:
                paragraphs.append(text_content)
    
    print(f"✓ Found {len(paragraphs)} paragraphs:")
    for i, p in enumerate(paragraphs):
        print(f"  [{i}] {p[:50]}...")
    
    return paragraphs

def test_alignment_xml_generation():
    """Test creation of aligned TEI XML structure."""
    print("\nTesting aligned XML generation...")
    
    # Mock alignment data
    alignments = [
        {
            'source_text': 'Come introduzione un breve chiarimento concettuale.',
            'target_text': 'By way of introduction, a brief clarification of concepts.'
        },
        {
            'source_text': 'In primo luogo ciò che è contenuto nel concetto di analisi.',
            'target_text': 'First, what the concept of analysis encompasses.'
        }
    ]
    
    # Create root TEI with standOff
    root = ET.Element('TEI', attrib={
        'xmlns': 'http://www.tei-c.org/ns/1.0',
        'version': '3.3.0'
    })
    
    # Add minimal header
    header = ET.SubElement(root, 'teiHeader')
    file_desc = ET.SubElement(header, 'fileDesc')
    title_stmt = ET.SubElement(file_desc, 'titleStmt')
    ET.SubElement(title_stmt, 'title')
    pub_stmt = ET.SubElement(file_desc, 'publicationStmt')
    ET.SubElement(pub_stmt, 'p')
    
    # Create standOff with alignment links
    standoff = ET.SubElement(root, 'standOff')
    link_grp = ET.SubElement(standoff, 'linkGrp', attrib={'type': 'translation'})
    
    # Generate UUIDs and create links
    alignment_map = {}
    for alignment in alignments:
        source_uuid = str(uuid.uuid4())
        target_uuid = str(uuid.uuid4())
        
        alignment_map[alignment['source_text']] = source_uuid
        alignment_map[alignment['target_text']] = target_uuid
        
        # Create link element
        ET.SubElement(link_grp, 'link', attrib={
            'target': f'#{source_uuid} #{target_uuid}',
            'type': 'Linguistic'
        })
    
    print(f"✓ Created {len(alignments)} alignment links")
    print(f"✓ Generated {len(alignment_map)} UUIDs")
    
    # Convert to string to check structure
    xml_string = ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    # Verify structure
    assert '<standOff>' in xml_string
    assert '<linkGrp type="translation">' in xml_string
    assert 'target="#' in xml_string
    print("✓ XML structure validation passed")
    
    print(f"✓ Generated XML preview:\n{xml_string[:500]}...")
    
    return xml_string

if __name__ == "__main__":
    print("=== Simple TEI Test ===\n")
    paragraphs = test_tei_parsing()
    aligned_xml = test_alignment_xml_generation()
    print("\n=== Test completed successfully ===")