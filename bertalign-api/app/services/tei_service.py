"""
TEI XML parsing and alignment service.
Handles extraction, alignment, and output generation for TEI documents.
"""
import uuid
import logging
from typing import List, Dict, Any, Tuple, Optional
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from dataclasses import dataclass

from .bertalign_service import BertalignService
from ..models import AlignmentPair

logger = logging.getLogger(__name__)

@dataclass
class TEIElement:
    """Represents a TEI element with its text content and structure info."""
    tag: str
    text: str
    attrib: Dict[str, str]
    element_id: Optional[str] = None
    parent_path: Optional[str] = None

@dataclass
class TEIDocument:
    """Represents a parsed TEI document."""
    root: Element
    text_elements: List[TEIElement]
    language: str
    title: str
    header: Element

class TEIService:
    """Service for processing TEI documents and generating alignments."""
    
    def __init__(self, bertalign_service: BertalignService):
        self.bertalign_service = bertalign_service
        self.ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    def parse_tei_file(self, xml_content: str) -> TEIDocument:
        """Parse TEI XML content and extract text elements."""
        try:
            root = ET.fromstring(xml_content)
            
            # Extract language from profileDesc or default to 'unknown'
            language = self._extract_language(root)
            
            # Extract title
            title = self._extract_title(root)
            
            # Extract header
            header = root.find('.//tei:teiHeader', self.ns)
            
            # Extract text elements (paragraphs, heads, etc.)
            text_elements = self._extract_text_elements(root)
            
            return TEIDocument(
                root=root,
                text_elements=text_elements,
                language=language,
                title=title,
                header=header
            )
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse TEI XML: {e}")
            raise ValueError(f"Invalid TEI XML: {e}")
    
    def _extract_language(self, root: Element) -> str:
        """Extract language code from TEI header."""
        lang_elem = root.find('.//tei:profileDesc/tei:langUsage/tei:language', self.ns)
        if lang_elem is not None and 'ident' in lang_elem.attrib:
            return lang_elem.attrib['ident']
        return 'unknown'
    
    def _extract_title(self, root: Element) -> str:
        """Extract title from TEI header."""
        title_elem = root.find('.//tei:titleStmt/tei:title', self.ns)
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        return 'Untitled'
    
    def _extract_text_elements(self, root: Element) -> List[TEIElement]:
        """Extract all text-containing elements from TEI body."""
        text_elements = []
        body = root.find('.//tei:body', self.ns)
        
        if body is None:
            return text_elements
        
        # Find all text-containing elements (p, head, etc.)
        for elem in body.iter():
            if elem.tag.endswith('}p') or elem.tag.endswith('}head'):
                # Clean and join all text content
                text_content = self._get_element_text(elem)
                if text_content and text_content.strip():
                    # Get parent path for structure preservation
                    parent_path = self._get_element_path(elem)
                    
                    text_elements.append(TEIElement(
                        tag=elem.tag.split('}')[-1],  # Remove namespace
                        text=text_content.strip(),
                        attrib=dict(elem.attrib),
                        parent_path=parent_path
                    ))
        
        return text_elements
    
    def _get_element_text(self, element: Element) -> str:
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
    
    def _get_element_path(self, element: Element) -> str:
        """Get the structural path to this element."""
        path_parts = []
        current = element
        
        while current is not None:
            tag = current.tag.split('}')[-1]  # Remove namespace
            if 'xml:id' in current.attrib:
                path_parts.append(f"{tag}[@xml:id='{current.attrib['{http://www.w3.org/XML/1998/namespace}id']}']")
            elif 'type' in current.attrib:
                path_parts.append(f"{tag}[@type='{current.attrib['type']}']")
            else:
                path_parts.append(tag)
            
            # Move to parent (this is simplified - in real XML tree traversal you'd need to track parents)
            break  # For now, just get the immediate element info
        
        return '/'.join(reversed(path_parts))
    
    def align_tei_documents(self, source_xml: str, target_xml: str, 
                           source_language: Optional[str] = None, 
                           target_language: Optional[str] = None) -> Dict[str, Any]:
        """Align two TEI documents and return alignment result."""
        try:
            # Parse both documents
            source_doc = self.parse_tei_file(source_xml)
            target_doc = self.parse_tei_file(target_xml)
            
            # Use provided languages or fall back to extracted ones, with defaults
            final_source_lang = source_language or (source_doc.language if source_doc.language != 'unknown' else 'en')
            final_target_lang = target_language or (target_doc.language if target_doc.language != 'unknown' else 'en')
            
            # Extract texts for alignment
            source_texts = [elem.text for elem in source_doc.text_elements]
            target_texts = [elem.text for elem in target_doc.text_elements]
            
            # Create alignment request
            from app.models import AlignmentRequest
            alignment_request = AlignmentRequest(
                source_text='\n'.join(source_texts),
                target_text='\n'.join(target_texts),
                source_language=final_source_lang,
                target_language=final_target_lang,
                is_split=True  # Already split into sentences/paragraphs
            )
            
            # Perform alignment
            alignment_result = self.bertalign_service.align_texts(alignment_request)
            
            # Generate aligned TEI output
            aligned_xml = self._generate_aligned_tei(
                source_doc, target_doc, alignment_result.alignments,
                final_source_lang, final_target_lang
            )
            
            return {
                'aligned_xml': aligned_xml,
                'source_language': final_source_lang,
                'target_language': final_target_lang,
                'alignment_count': len(alignment_result.alignments),
                'processing_time': alignment_result.processing_time
            }
            
        except Exception as e:
            logger.error(f"TEI alignment failed: {e}")
            raise
    
    def _generate_aligned_tei(self, source_doc: TEIDocument, target_doc: TEIDocument, 
                             alignments: List[AlignmentPair], source_language: str, target_language: str) -> str:
        """Generate aligned TEI XML with standOff linkGrp structure."""
        
        # Create root TEI element with proper namespace
        root = ET.Element('TEI')
        root.set('xmlns', 'http://www.tei-c.org/ns/1.0')
        
        # Add comprehensive header
        header = ET.SubElement(root, 'teiHeader')
        file_desc = ET.SubElement(header, 'fileDesc')
        title_stmt = ET.SubElement(file_desc, 'titleStmt')
        title_elem = ET.SubElement(title_stmt, 'title')
        title_elem.text = "Aligned Parallel Texts"
        
        pub_stmt = ET.SubElement(file_desc, 'publicationStmt')
        pub_p = ET.SubElement(pub_stmt, 'p')
        pub_p.text = "Aligned using Bertalign API"
        
        # Add profile description with languages
        profile_desc = ET.SubElement(header, 'profileDesc')
        lang_usage = ET.SubElement(profile_desc, 'langUsage')
        
        # Add both languages to the header
        source_lang_elem = ET.SubElement(lang_usage, 'language', attrib={'ident': source_language})
        source_lang_elem.text = f"Source language: {source_language}"
        target_lang_elem = ET.SubElement(lang_usage, 'language', attrib={'ident': target_language})
        target_lang_elem.text = f"Target language: {target_language}"
        
        # Create standOff with alignment links
        standoff = ET.SubElement(root, 'standOff')
        link_grp = ET.SubElement(standoff, 'linkGrp', attrib={'type': 'translation'})
        
        # Generate UUIDs for aligned elements and create links
        alignment_map = {}
        for alignment in alignments:
            source_uuid = str(uuid.uuid4())
            target_uuid = str(uuid.uuid4())
            
            # Join sentences to create text keys for mapping
            source_text = ' '.join(alignment.source_sentences)
            target_text = ' '.join(alignment.target_sentences)
            
            # Store mapping for later use
            alignment_map[source_text] = source_uuid
            alignment_map[target_text] = target_uuid
            
            # Create link element with correct type
            ET.SubElement(link_grp, 'link', attrib={
                'target': f'#{source_uuid} #{target_uuid}',
                'type': 'Linguistic'
            })
        
        # Create source text group
        source_group = ET.SubElement(root, 'group', attrib={'type': 'source'})
        source_group.set('{http://www.w3.org/XML/1998/namespace}lang', source_language)
        source_text_elem = ET.SubElement(source_group, 'text')
        source_body = ET.SubElement(source_text_elem, 'body')
        self._add_text_elements_with_ids(source_doc, source_body, alignment_map)
        
        # Create target text group  
        target_group = ET.SubElement(root, 'group', attrib={'type': 'target'})
        target_group.set('{http://www.w3.org/XML/1998/namespace}lang', target_language)
        target_text_elem = ET.SubElement(target_group, 'text')
        target_body = ET.SubElement(target_text_elem, 'body')
        self._add_text_elements_with_ids(target_doc, target_body, alignment_map)
        
        # Convert to string with proper formatting
        ET.register_namespace('', 'http://www.tei-c.org/ns/1.0')
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode')
    
    def _add_text_elements_with_ids(self, doc: TEIDocument, body_elem: Element, alignment_map: Dict[str, str]) -> None:
        """Add text elements from TEI document to body with xml:id attributes."""
        for text_elem in doc.text_elements:
            # Create paragraph element
            p_elem = ET.SubElement(body_elem, 'p')
            p_elem.text = text_elem.text
            
            # Add xml:id if this text is in an alignment
            if text_elem.text in alignment_map:
                p_elem.set('{http://www.w3.org/XML/1998/namespace}id', alignment_map[text_elem.text])
    
    def _create_tei_with_ids(self, doc: TEIDocument, alignment_map: Dict[str, str], language: str) -> Element:
        """Create TEI element with xml:id attributes for aligned elements."""
        
        # Create a copy of the original document
        tei_copy = ET.fromstring(ET.tostring(doc.root, encoding='unicode'))
        
        # Add language to profileDesc
        profile_desc = tei_copy.find('.//tei:profileDesc', self.ns)
        if profile_desc is None:
            profile_desc = ET.SubElement(tei_copy.find('.//tei:teiHeader', self.ns), 'profileDesc')
        
        lang_usage = profile_desc.find('.//tei:langUsage', self.ns)
        if lang_usage is None:
            lang_usage = ET.SubElement(profile_desc, 'langUsage')
        
        # Clear existing language elements and add the correct one
        for existing_lang in lang_usage.findall('.//tei:language', self.ns):
            lang_usage.remove(existing_lang)
        
        language_elem = ET.SubElement(lang_usage, 'language', attrib={'ident': language})
        language_elem.text = language
        
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