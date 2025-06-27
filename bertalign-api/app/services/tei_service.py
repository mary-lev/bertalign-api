"""
TEI XML parsing and alignment service.
Handles extraction, alignment, and output generation for TEI documents.
"""
import uuid
import logging
import re
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

        return self._clean_text(' '.join(texts).strip())
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing line breaks and normalizing whitespace."""
        if not text:
            return text
            
        # Remove line breaks and carriage returns
        cleaned = re.sub(r'[\r\n]+', ' ', text)
        
        # Replace multiple spaces/tabs with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Strip leading/trailing whitespace
        return cleaned.strip()
    
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
            
            # Extract texts for alignment (properly handle paragraphs)
            source_texts = [elem.text.strip() for elem in source_doc.text_elements if elem.text and elem.text.strip()]
            target_texts = [elem.text.strip() for elem in target_doc.text_elements if elem.text and elem.text.strip()]
            
            # Create alignment request with proper text handling
            from app.models import AlignmentRequest
            alignment_request = AlignmentRequest(
                source_text='\n\n'.join(source_texts),  # Use double newlines to separate paragraphs
                target_text='\n\n'.join(target_texts),
                source_language=final_source_lang,
                target_language=final_target_lang,
                is_split=False  # Let bertalign handle sentence splitting
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
    
    def _create_enhanced_alignment_map(self, source_doc: TEIDocument, target_doc: TEIDocument, 
                                      alignments: List[AlignmentPair]) -> Dict[str, Any]:
        """Create enhanced alignment mapping that preserves original XML structure."""
        alignment_map = {
            'links': [],
            'source_elements': {},  # element_text -> {'uuid': str, 'element': TEIElement, 'alignment_type': str}
            'target_elements': {}   # element_text -> {'uuid': str, 'element': TEIElement, 'alignment_type': str}
        }
        
        # Create mapping of original text elements
        source_text_to_element = {elem.text.strip(): elem for elem in source_doc.text_elements if elem.text and elem.text.strip()}
        target_text_to_element = {elem.text.strip(): elem for elem in target_doc.text_elements if elem.text and elem.text.strip()}
        
        for alignment in alignments:
            source_uuid = str(uuid.uuid4())
            target_uuid = str(uuid.uuid4())
            
            # Get the aligned text content
            source_text = ' '.join(alignment.source_sentences).strip()
            target_text = ' '.join(alignment.target_sentences).strip()
            
            # Store both individual sentences AND combined forms to handle all cases
            
            # First, try to find elements that match the combined alignment text
            source_element = self._find_best_matching_element(source_text, source_text_to_element)
            target_element = self._find_best_matching_element(target_text, target_text_to_element)
            
            # Store combined alignment text (handles cases like headers spanning multiple sentences)
            if source_element:
                source_alignment_type = self._determine_alignment_type(source_text, source_element)
                alignment_map['source_elements'][source_text] = {
                    'uuid': source_uuid,
                    'element': source_element,
                    'alignment_type': source_alignment_type,
                    'aligned_sentences': alignment.source_sentences
                }
            
            if target_element:
                target_alignment_type = self._determine_alignment_type(target_text, target_element)
                alignment_map['target_elements'][target_text] = {
                    'uuid': target_uuid,
                    'element': target_element,
                    'alignment_type': target_alignment_type,
                    'aligned_sentences': alignment.target_sentences
                }
            
            # Then store individual sentences (for cases where individual sentences match elements)
            for sentence in alignment.source_sentences:
                sentence = sentence.strip()
                if sentence and sentence not in alignment_map['source_elements']:
                    source_element = self._find_best_matching_element(sentence, source_text_to_element)
                    if source_element:
                        source_alignment_type = self._determine_alignment_type(sentence, source_element)
                        alignment_map['source_elements'][sentence] = {
                            'uuid': source_uuid,
                            'element': source_element,
                            'alignment_type': source_alignment_type,
                            'aligned_sentences': alignment.source_sentences
                        }
            
            for sentence in alignment.target_sentences:
                sentence = sentence.strip()
                if sentence and sentence not in alignment_map['target_elements']:
                    target_element = self._find_best_matching_element(sentence, target_text_to_element)
                    if target_element:
                        target_alignment_type = self._determine_alignment_type(sentence, target_element)
                        alignment_map['target_elements'][sentence] = {
                            'uuid': target_uuid,
                            'element': target_element,
                            'alignment_type': target_alignment_type,
                            'aligned_sentences': alignment.target_sentences
                        }
            
            # Store link information
            alignment_map['links'].append({
                'source_uuid': source_uuid,
                'target_uuid': target_uuid,
                'source_text': source_text,
                'target_text': target_text
            })
        
        return alignment_map
    
    def _find_best_matching_element(self, text: str, text_to_element: Dict[str, TEIElement]) -> TEIElement:
        """Find the best matching TEI element for the given text."""
        # First try exact match
        if text in text_to_element:
            return text_to_element[text]
        
        # Then try to find element that contains this text
        best_match = None
        best_coverage = 0
        
        for element_text, element in text_to_element.items():
            if text in element_text:
                coverage = len(text) / len(element_text)
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_match = element
        
        return best_match
    
    def _determine_alignment_type(self, aligned_text: str, element: TEIElement) -> str:
        """Determine if alignment is paragraph-level or sentence-level."""
        if not element or not element.text:
            return 'paragraph'  # Default to paragraph level
        
        element_text = element.text.strip()
        
        # If the aligned text matches the entire element text, it's paragraph-level
        if aligned_text == element_text:
            return 'paragraph'
        
        # If the aligned text is contained within element text, it's sentence-level
        if aligned_text in element_text and len(aligned_text) < len(element_text) * 0.9:
            return 'sentence'
        
        # Default to paragraph level for ambiguous cases
        return 'paragraph'

    def _generate_aligned_tei(self, source_doc: TEIDocument, target_doc: TEIDocument, 
                             alignments: List[AlignmentPair], source_language: str, target_language: str) -> str:
        """Generate aligned TEI XML with teiCorpus structure following TEI P5 guidelines."""
        
        # Register TEI namespace and create root teiCorpus element
        ET.register_namespace('', 'http://www.tei-c.org/ns/1.0')
        root = ET.Element('{http://www.tei-c.org/ns/1.0}teiCorpus')
        root.set('version', '3.3.0')
        
        # Add comprehensive corpus-level header
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
        
        # Add both languages to the corpus header
        source_lang_elem = ET.SubElement(lang_usage, 'language', attrib={'ident': source_language})
        source_lang_elem.text = f"Source language: {source_language}"
        target_lang_elem = ET.SubElement(lang_usage, 'language', attrib={'ident': target_language})
        target_lang_elem.text = f"Target language: {target_language}"
        
        # Generate enhanced alignment mapping that handles both paragraph and sentence-level alignments
        alignment_map = self._create_enhanced_alignment_map(source_doc, target_doc, alignments)
        
        # Create standOff with alignment links
        standoff = ET.SubElement(root, 'standOff')
        link_grp = ET.SubElement(standoff, 'linkGrp', attrib={'type': 'translation'})
        
        # Create link elements with proper target references using enhanced alignment map
        for link_data in alignment_map['links']:
            ET.SubElement(link_grp, 'link', attrib={
                'target': f"#{link_data['source_uuid']} #{link_data['target_uuid']}",
                'type': 'Linguistic'
            })
        
        # Include complete original source TEI document with xml:id attributes for aligned elements
        source_tei_with_ids = self._create_tei_with_ids(source_doc, alignment_map, source_language)
        root.append(source_tei_with_ids)
        
        # Include complete original target TEI document with xml:id attributes for aligned elements
        target_tei_with_ids = self._create_tei_with_ids(target_doc, alignment_map, target_language)
        root.append(target_tei_with_ids)
        
        # Convert to string with proper formatting
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode')
    
    def _create_tei_with_ids(self, doc: TEIDocument, alignment_map: Dict[str, Any], language: str) -> Element:
        """Create TEI element with xml:id attributes for aligned elements and <seg> tags for sentence alignments."""
        
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
        
        # Process alignments with new enhanced format
        elements_map = alignment_map.get('source_elements', {}) if language in ['it', 'de', 'fr'] else alignment_map.get('target_elements', {})
        
        # Always create <seg> tags for all alignments regardless of element type or alignment granularity
        body = tei_copy.find('.//tei:body', self.ns)
        if body is not None:
            for elem in body.iter():
                if elem.tag.endswith('}p') or elem.tag.endswith('}head'):
                    elem_text = self._get_element_text(elem)
                    if elem_text and elem_text.strip():
                        elem_text_clean = elem_text.strip()
                        
                        # Collect all alignments that match this element
                        all_matches = []
                        
                        for aligned_text, alignment_info in elements_map.items():
                            if self._texts_match(elem_text_clean, aligned_text) or aligned_text in elem_text_clean:
                                all_matches.append(alignment_info)
                        
                        # Always create <seg> tags for any matches found
                        if all_matches:
                            self._create_seg_tags_for_sentences(elem, all_matches, elem_text_clean)
        
        # Fallback for old alignment map format (simple text -> uuid mapping)
        if not elements_map and isinstance(alignment_map, dict):
            body = tei_copy.find('.//tei:body', self.ns)
            if body is not None:
                for elem in body.iter():
                    if elem.tag.endswith('}p') or elem.tag.endswith('}head'):
                        elem_text = self._get_element_text(elem)
                        if elem_text and elem_text.strip() in alignment_map:
                            # Always create <seg> tags even for simple mappings
                            uuid_val = alignment_map[elem_text.strip()]
                            fallback_match = [{
                                'uuid': uuid_val,
                                'aligned_sentences': [elem_text.strip()]
                            }]
                            self._create_seg_tags_for_sentences(elem, fallback_match, elem_text.strip())
        
        # Add empty facsimile element
        ET.SubElement(tei_copy, 'facsimile')
        
        return tei_copy
    
    def _texts_match(self, text1: str, text2: str) -> bool:
        """Check if two texts match with some tolerance for whitespace and punctuation."""
        # Normalize whitespace and compare
        norm1 = ' '.join(text1.split())
        norm2 = ' '.join(text2.split())
        
        # Try exact match first
        if norm1 == norm2:
            return True
        
        # Try substring match (for partial alignments)
        if norm1 in norm2 or norm2 in norm1:
            # Only match if the overlap is significant
            overlap = len(min(norm1, norm2, key=len))
            total = len(max(norm1, norm2, key=len))
            return overlap / total > 0.8
        
        return False
    
    def _create_seg_tags_for_sentences(self, elem: Element, sentence_matches: List[Dict[str, Any]], full_text: str) -> None:
        """Create <seg> tags for alignments within any element (paragraph, head, etc.)."""
        # Get the sentences we need to segment
        sentences_to_segment = []
        for match in sentence_matches:
            for sentence in match['aligned_sentences']:
                if sentence.strip() and sentence.strip() in full_text:
                    sentences_to_segment.append({
                        'text': sentence.strip(),
                        'uuid': match['uuid']
                    })
        
        if not sentences_to_segment:
            # Fallback: assign first sentence UUID to element (should not happen with new approach)
            elem.set('{http://www.w3.org/XML/1998/namespace}id', sentence_matches[0]['uuid'])
            return
        
        # Clear the element content
        original_text = elem.text or ""
        original_tail = elem.tail
        elem.clear()
        elem.tail = original_tail
        
        # Process the text and create seg elements
        remaining_text = full_text
        
        for i, sentence_info in enumerate(sentences_to_segment):
            sentence_text = sentence_info['text']
            sentence_uuid = sentence_info['uuid']
            
            if sentence_text in remaining_text:
                # Find the position of this sentence
                sentence_start = remaining_text.find(sentence_text)
                
                # Add any text before this sentence
                if sentence_start > 0:
                    before_text = remaining_text[:sentence_start].strip()
                    if before_text:
                        if i == 0:
                            elem.text = before_text + " "
                        else:
                            # Add to tail of previous element
                            if len(elem) > 0:
                                prev_elem = elem[-1]
                                prev_elem.tail = (prev_elem.tail or "") + before_text + " "
                
                # Create seg element for this sentence
                seg_elem = ET.SubElement(elem, '{http://www.tei-c.org/ns/1.0}seg')
                seg_elem.set('{http://www.w3.org/XML/1998/namespace}id', sentence_uuid)
                seg_elem.text = sentence_text
                
                # Update remaining text
                sentence_end = sentence_start + len(sentence_text)
                remaining_text = remaining_text[sentence_end:]
        
        # Add any remaining text after the last sentence
        if remaining_text.strip():
            if len(elem) > 0:
                last_seg = elem[-1]
                last_seg.tail = " " + remaining_text.strip()
            else:
                elem.text = (elem.text or "") + remaining_text.strip()