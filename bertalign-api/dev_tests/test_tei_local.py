#!/usr/bin/env python3
"""
Test TEI alignment with actual files using mock bertalign service.
"""
import uuid
from xml.etree import ElementTree as ET
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class MockAlignmentPair:
    """Mock alignment pair for testing."""
    source_text: str
    target_text: str
    source_sentences: List[str]
    target_sentences: List[str]
    alignment_score: float
    source_indices: List[int]
    target_indices: List[int]

@dataclass
class MockAlignmentResult:
    """Mock alignment result for testing."""
    alignments: List[MockAlignmentPair]
    source_language: str
    target_language: str
    processing_time: float

class MockTEIService:
    """Simplified TEI service for local testing."""
    
    def __init__(self):
        self.ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    def parse_tei_file(self, xml_content: str) -> Dict[str, Any]:
        """Parse TEI XML content and extract information."""
        root = ET.fromstring(xml_content)
        
        # Extract language
        lang_elem = root.find('.//tei:profileDesc/tei:langUsage/tei:language', self.ns)
        language = lang_elem.attrib.get('ident', 'unknown') if lang_elem is not None else 'unknown'
        
        # Extract title
        title_elem = root.find('.//tei:titleStmt/tei:title', self.ns)
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else 'Untitled'
        
        # Extract text elements
        text_elements = []
        body = root.find('.//tei:body', self.ns)
        
        if body is not None:
            for elem in body.iter():
                if elem.tag.endswith('}p') or elem.tag.endswith('}head'):
                    text_content = self._get_element_text(elem)
                    if text_content and text_content.strip():
                        text_elements.append({
                            'tag': elem.tag.split('}')[-1],
                            'text': text_content.strip(),
                            'attrib': dict(elem.attrib)
                        })
        
        return {
            'root': root,
            'language': language,
            'title': title,
            'text_elements': text_elements
        }
    
    def _get_element_text(self, element: ET.Element) -> str:
        """Extract all text content from element and its children."""
        texts = []
        if element.text:
            texts.append(element.text.strip())
        
        for child in element:
            child_text = self._get_element_text(child)
            if child_text:
                texts.append(child_text)
            if child.tail:
                texts.append(child.tail.strip())
        
        return ' '.join(texts).strip()
    
    def mock_align_texts(self, source_texts: List[str], target_texts: List[str]) -> MockAlignmentResult:
        """Create mock alignment between text lists."""
        alignments = []
        
        # Simple 1:1 alignment for first few pairs
        min_len = min(len(source_texts), len(target_texts))
        for i in range(min_len):
            if source_texts[i] and target_texts[i]:  # Skip empty texts
                alignments.append(MockAlignmentPair(
                    source_text=source_texts[i],
                    target_text=target_texts[i],
                    source_sentences=[source_texts[i]],
                    target_sentences=[target_texts[i]],
                    alignment_score=0.85 + (i * 0.02),  # Mock varying scores
                    source_indices=[i],
                    target_indices=[i]
                ))
        
        return MockAlignmentResult(
            alignments=alignments,
            source_language="it",
            target_language="en",
            processing_time=0.5
        )
    
    def align_tei_documents(self, source_xml: str, target_xml: str) -> Dict[str, Any]:
        """Align two TEI documents and return result."""
        # Parse documents
        source_doc = self.parse_tei_file(source_xml)
        target_doc = self.parse_tei_file(target_xml)
        
        print(f"Source ({source_doc['language']}): {source_doc['title']}")
        print(f"Target ({target_doc['language']}): {target_doc['title']}")
        print(f"Source elements: {len(source_doc['text_elements'])}")
        print(f"Target elements: {len(target_doc['text_elements'])}")
        
        # Extract texts
        source_texts = [elem['text'] for elem in source_doc['text_elements']]
        target_texts = [elem['text'] for elem in target_doc['text_elements']]
        
        # Mock alignment
        alignment_result = self.mock_align_texts(source_texts, target_texts)
        
        # Generate aligned XML
        aligned_xml = self._generate_aligned_tei(source_doc, target_doc, alignment_result.alignments)
        
        return {
            'aligned_xml': aligned_xml,
            'source_language': source_doc['language'],
            'target_language': target_doc['language'],
            'alignment_count': len(alignment_result.alignments),
            'processing_time': alignment_result.processing_time
        }
    
    def _generate_aligned_tei(self, source_doc: Dict, target_doc: Dict, alignments: List[MockAlignmentPair]) -> str:
        """Generate aligned TEI XML with standOff structure."""
        
        # Create root TEI element
        root = ET.Element('TEI', attrib={
            'xmlns': 'http://www.tei-c.org/ns/1.0',
            'version': '3.3.0'
        })
        
        # Add minimal header
        header = ET.SubElement(root, 'teiHeader')
        file_desc = ET.SubElement(header, 'fileDesc')
        title_stmt = ET.SubElement(file_desc, 'titleStmt')
        title_elem = ET.SubElement(title_stmt, 'title')
        title_elem.text = f"Aligned: {source_doc['title']} - {target_doc['title']}"
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
            
            alignment_map[alignment.source_text] = source_uuid
            alignment_map[alignment.target_text] = target_uuid
            
            # Create link element
            ET.SubElement(link_grp, 'link', attrib={
                'target': f'#{source_uuid} #{target_uuid}',
                'type': 'Linguistic'
            })
        
        # Add source document with IDs
        source_tei = self._create_tei_with_ids(source_doc, alignment_map, 'it')
        root.append(source_tei)
        
        # Add target document with IDs
        target_tei = self._create_tei_with_ids(target_doc, alignment_map, 'en')
        root.append(target_tei)
        
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    def _create_tei_with_ids(self, doc: Dict, alignment_map: Dict[str, str], lang: str) -> ET.Element:
        """Create TEI element with xml:id attributes for aligned elements."""
        
        # Create a copy of the original document
        tei_copy = ET.fromstring(ET.tostring(doc['root'], encoding='unicode'))
        
        # Add/update language in profileDesc
        profile_desc = tei_copy.find('.//tei:profileDesc', self.ns)
        if profile_desc is None:
            profile_desc = ET.SubElement(tei_copy.find('.//tei:teiHeader', self.ns), 'profileDesc')
        
        lang_usage = profile_desc.find('.//tei:langUsage', self.ns)
        if lang_usage is None:
            lang_usage = ET.SubElement(profile_desc, 'langUsage')
        
        # Clear existing language elements and add new one
        for lang_elem in lang_usage.findall('.//tei:language', self.ns):
            lang_usage.remove(lang_elem)
        
        language = ET.SubElement(lang_usage, 'language', attrib={'ident': lang})
        language.text = lang
        
        # Add xml:id to aligned elements
        body = tei_copy.find('.//tei:body', self.ns)
        if body is not None:
            for elem in body.iter():
                if elem.tag.endswith('}p') or elem.tag.endswith('}head'):
                    elem_text = self._get_element_text(elem)
                    if elem_text and elem_text.strip() in alignment_map:
                        elem.set('{http://www.w3.org/XML/1998/namespace}id', 
                                alignment_map[elem_text.strip()])
        
        # Add empty facsimile element
        ET.SubElement(tei_copy, 'facsimile')
        
        return tei_copy

def test_with_actual_files():
    """Test with actual Italian and English TEI files."""
    print("=== Testing with actual TEI files ===\n")
    
    # Load files
    try:
        with open('texts/italian.xml', 'r', encoding='utf-8') as f:
            italian_xml = f.read()
        print("✓ Loaded italian.xml")
        
        with open('texts/english.xml', 'r', encoding='utf-8') as f:
            english_xml = f.read()
        print("✓ Loaded english.xml")
        
    except FileNotFoundError as e:
        print(f"✗ File not found: {e}")
        return
    
    # Test alignment
    tei_service = MockTEIService()
    
    try:
        result = tei_service.align_tei_documents(italian_xml, english_xml)
        
        print(f"\n✓ Alignment completed:")
        print(f"  - Source language: {result['source_language']}")
        print(f"  - Target language: {result['target_language']}")
        print(f"  - Alignments created: {result['alignment_count']}")
        print(f"  - Processing time: {result['processing_time']:.2f}s")
        print(f"  - Output XML length: {len(result['aligned_xml'])} chars")
        
        # Save result
        with open('texts/test_aligned_output.xml', 'w', encoding='utf-8') as f:
            f.write(result['aligned_xml'])
        print("✓ Saved result to texts/test_aligned_output.xml")
        
        # Show preview
        print(f"\nXML Preview:\n{result['aligned_xml'][:800]}...")
        
    except Exception as e:
        print(f"✗ Alignment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_actual_files()