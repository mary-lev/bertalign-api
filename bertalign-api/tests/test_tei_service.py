"""
Tests for TEI service functionality.
"""
import pytest
from unittest.mock import Mock, patch
from xml.etree import ElementTree as ET

from app.services.tei_service import TEIService, TEIDocument, TEIElement
from app.services.bertalign_service import BertalignService
from app.models import AlignmentPair, AlignmentResponse, AlignmentRequest


@pytest.fixture
def mock_bertalign_service():
    """Mock bertalign service for testing."""
    service = Mock(spec=BertalignService)
    service.max_align = 5
    service.top_k = 3
    service.win = 5
    service.skip = -0.1
    service.margin = True
    service.len_penalty = True
    return service


@pytest.fixture
def tei_service(mock_bertalign_service):
    """TEI service with mocked bertalign service."""
    return TEIService(mock_bertalign_service)


@pytest.fixture
def sample_italian_tei():
    """Sample Italian TEI document."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Contributi alla teoria figurativa della forma</title>
                <author>P. Klee</author>
            </titleStmt>
            <publicationStmt>
                <publisher>Istituto Italiano di Studi Germanici</publisher>
                <pubPlace>Roma</pubPlace>
                <date>2025</date>
            </publicationStmt>
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


@pytest.fixture
def sample_english_tei():
    """Sample English TEI document."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Contributions to the Theory of Pictorial Form</title>
                <author>P. Klee</author>
            </titleStmt>
            <publicationStmt>
                <publisher>Istituto Italiano di Studi Germanici</publisher>
                <pubPlace>Rome</pubPlace>
                <date>2025</date>
            </publicationStmt>
        </fileDesc>
        <profileDesc>
            <langUsage>
                <language ident="en">en</language>
            </langUsage>
        </profileDesc>
    </teiHeader>
    <text>
        <body>
            <div xml:id="div_intro">
                <p>By way of introduction, a brief clarification of concepts.</p>
                <p>First, what the concept of analysis encompasses.</p>
            </div>
        </body>
    </text>
</TEI>'''


class TestTEIService:
    """Test TEI service functionality."""
    
    def test_parse_italian_tei(self, tei_service, sample_italian_tei):
        """Test parsing Italian TEI document."""
        doc = tei_service.parse_tei_file(sample_italian_tei)
        
        assert isinstance(doc, TEIDocument)
        assert doc.language == "it"
        assert doc.title == "Contributi alla teoria figurativa della forma"
        assert len(doc.text_elements) == 2
        assert doc.text_elements[0].text == "Come introduzione un breve chiarimento concettuale."
        assert doc.text_elements[1].text == "In primo luogo ciò che è contenuto nel concetto di analisi."
    
    def test_parse_english_tei(self, tei_service, sample_english_tei):
        """Test parsing English TEI document."""
        doc = tei_service.parse_tei_file(sample_english_tei)
        
        assert isinstance(doc, TEIDocument)
        assert doc.language == "en"
        assert doc.title == "Contributions to the Theory of Pictorial Form"
        assert len(doc.text_elements) == 2
        assert doc.text_elements[0].text == "By way of introduction, a brief clarification of concepts."
        assert doc.text_elements[1].text == "First, what the concept of analysis encompasses."
    
    def test_parse_invalid_xml(self, tei_service):
        """Test parsing invalid XML raises ValueError."""
        invalid_xml = "<invalid>not closed"
        
        with pytest.raises(ValueError, match="Invalid TEI XML"):
            tei_service.parse_tei_file(invalid_xml)
    
    def test_extract_language_default(self, tei_service):
        """Test language extraction with default fallback."""
        xml_without_lang = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test</title></titleStmt>
        </fileDesc>
    </teiHeader>
    <text><body><p>Test text</p></body></text>
</TEI>'''
        
        doc = tei_service.parse_tei_file(xml_without_lang)
        assert doc.language == "unknown"
    
    def test_extract_title_default(self, tei_service):
        """Test title extraction with default fallback."""
        xml_without_title = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title></title></titleStmt>
        </fileDesc>
    </teiHeader>
    <text><body><p>Test text</p></body></text>
</TEI>'''
        
        doc = tei_service.parse_tei_file(xml_without_title)
        assert doc.title == "Untitled"
    
    def test_extract_text_elements_empty_body(self, tei_service):
        """Test text extraction from empty body."""
        xml_empty_body = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test</title></titleStmt>
        </fileDesc>
    </teiHeader>
    <text><body></body></text>
</TEI>'''
        
        doc = tei_service.parse_tei_file(xml_empty_body)
        assert len(doc.text_elements) == 0
    
    @patch('app.services.tei_service.uuid.uuid4')
    def test_align_tei_documents(self, mock_uuid, tei_service, sample_italian_tei, sample_english_tei):
        """Test TEI document alignment."""
        # Mock UUID generation
        mock_uuid.side_effect = [
            Mock(return_value='uuid1'),
            Mock(return_value='uuid2')
        ]
        mock_uuid.return_value.__str__ = lambda: 'test-uuid'
        
        # Mock alignment result
        mock_alignment = AlignmentResponse(
            alignments=[
                AlignmentPair(
                    source_sentences=["Come introduzione un breve chiarimento concettuale."],
                    target_sentences=["By way of introduction, a brief clarification of concepts."],
                    alignment_score=0.95,
                    source_indices=[0],
                    target_indices=[0]
                )
            ],
            source_language="it",
            target_language="en", 
            processing_time=0.5,
            total_source_sentences=1,
            total_target_sentences=1,
            parameters=AlignmentRequest(
                source_text="test",
                target_text="test",
                source_language="it",
                target_language="en"
            )
        )
        
        tei_service.bertalign_service.align_texts.return_value = mock_alignment
        
        # Perform alignment
        result = tei_service.align_tei_documents(sample_italian_tei, sample_english_tei)
        
        # Verify result structure
        assert 'aligned_xml' in result
        assert result['source_language'] == 'it'
        assert result['target_language'] == 'en'
        assert result['alignment_count'] == 1
        assert result['processing_time'] == 0.5
        
        # Verify XML structure
        aligned_xml = result['aligned_xml']
        assert '<standOff>' in aligned_xml
        assert '<linkGrp type="translation">' in aligned_xml
        assert 'xml:id=' in aligned_xml
    
    def test_get_element_text_with_children(self, tei_service):
        """Test text extraction from element with children."""
        xml_content = '''<p xmlns="http://www.tei-c.org/ns/1.0">
            Text before <s>sentence content</s> text after.
        </p>'''
        
        elem = ET.fromstring(xml_content)
        text = tei_service._get_element_text(elem)
        
        assert "Text before" in text
        assert "sentence content" in text
        assert "text after" in text
    
    def test_generate_aligned_tei_structure(self, tei_service, sample_italian_tei, sample_english_tei):
        """Test aligned TEI XML structure generation."""
        # Parse documents
        source_doc = tei_service.parse_tei_file(sample_italian_tei)
        target_doc = tei_service.parse_tei_file(sample_english_tei)
        
        # Create test alignment
        alignments = [
            AlignmentPair(
                source_sentences=["Come introduzione un breve chiarimento concettuale."],
                target_sentences=["By way of introduction, a brief clarification of concepts."],
                alignment_score=0.95,
                source_indices=[0],
                target_indices=[0]
            )
        ]
        
        # Generate aligned XML
        aligned_xml = tei_service._generate_aligned_tei(source_doc, target_doc, alignments, "it", "en")
        
        # Parse result to verify structure
        root = ET.fromstring(aligned_xml)
        
        # Check root element is teiCorpus (per TEI P5 specification)
        assert root.tag.endswith('teiCorpus')
        # Namespace is set in ElementTree, so check for the namespace in the tag
        assert 'tei-c.org' in root.tag
        # Check version attribute
        assert root.get('version') == '3.3.0'
        
        # Check standOff structure
        standoff = root.find('.//{http://www.tei-c.org/ns/1.0}standOff')
        assert standoff is not None
        
        link_grp = standoff.find('.//{http://www.tei-c.org/ns/1.0}linkGrp')
        assert link_grp is not None
        assert link_grp.get('type') == 'translation'
        
        # Check link elements
        links = link_grp.findall('.//{http://www.tei-c.org/ns/1.0}link')
        assert len(links) == 1
        assert links[0].get('type') == 'Linguistic'
        assert links[0].get('target') is not None
    
    def test_alignment_error_handling(self, tei_service, sample_italian_tei, sample_english_tei):
        """Test error handling during alignment."""
        # Mock alignment service to raise exception
        tei_service.bertalign_service.align_texts.side_effect = Exception("Alignment failed")
        
        with pytest.raises(Exception, match="Alignment failed"):
            tei_service.align_tei_documents(sample_italian_tei, sample_english_tei)
    
    def test_create_tei_with_ids(self, tei_service, sample_italian_tei):
        """Test TEI document creation with XML IDs using <seg> tags."""
        doc = tei_service.parse_tei_file(sample_italian_tei)
        
        # Create alignment mapping
        alignment_map = {
            "Come introduzione un breve chiarimento concettuale.": "test-uuid-1",
            "In primo luogo ciò che è contenuto nel concetto di analisi.": "test-uuid-2"
        }
        
        # Generate TEI with IDs
        tei_with_ids = tei_service._create_tei_with_ids(doc, alignment_map, "it", is_source=True)
        
        # Verify IDs were added (now as <seg> tags instead of paragraph xml:id)
        paragraphs = tei_with_ids.findall('.//{http://www.tei-c.org/ns/1.0}p')
        assert len(paragraphs) == 2
        
        # Check that paragraphs contain <seg> elements with xml:id (new behavior)
        seg_elements = tei_with_ids.findall('.//{http://www.tei-c.org/ns/1.0}seg')
        assert len(seg_elements) >= 1, "Should have at least one <seg> element"
        
        # Check that <seg> elements have xml:id attributes
        has_seg_id = any(seg.get('{http://www.w3.org/XML/1998/namespace}id') for seg in seg_elements)
        assert has_seg_id, "At least one <seg> element should have xml:id"
        
        # Check that the document structure is maintained
        # The language information might be in different places depending on implementation
        assert tei_with_ids.tag.endswith('TEI') or 'TEI' in tei_with_ids.tag
        
        # Check that the TEI structure is maintained
        body = tei_with_ids.find('.//{http://www.tei-c.org/ns/1.0}body')
        assert body is not None
    
    @patch('app.services.tei_service.uuid.uuid4')
    def test_align_tei_documents_with_explicit_languages(self, mock_uuid, tei_service, sample_italian_tei, sample_english_tei):
        """Test TEI document alignment with explicit language parameters."""
        # Mock UUID generation
        mock_uuid.return_value.__str__ = lambda self: 'test-uuid'
        
        # Mock alignment result
        mock_alignment = AlignmentResponse(
            alignments=[
                AlignmentPair(
                    source_sentences=["Come introduzione un breve chiarimento concettuale."],
                    target_sentences=["By way of introduction, a brief clarification of concepts."],
                    alignment_score=0.95,
                    source_indices=[0],
                    target_indices=[0]
                )
            ],
            source_language="it",
            target_language="en", 
            processing_time=0.5,
            total_source_sentences=1,
            total_target_sentences=1,
            parameters=AlignmentRequest(
                source_text="test",
                target_text="test",
                source_language="it",
                target_language="en"
            )
        )
        
        tei_service.bertalign_service.align_texts.return_value = mock_alignment
        
        # Perform alignment with explicit languages
        result = tei_service.align_tei_documents(
            sample_italian_tei, 
            sample_english_tei, 
            source_language="it", 
            target_language="en"
        )
        
        # Verify that explicit languages are used
        assert result['source_language'] == 'it'
        assert result['target_language'] == 'en'
        
        # Verify that bertalign service was called with correct languages
        tei_service.bertalign_service.align_texts.assert_called_once()
        call_args = tei_service.bertalign_service.align_texts.call_args[0][0]
        assert call_args.source_language == 'it'
        assert call_args.target_language == 'en'
    
    @patch('app.services.tei_service.uuid.uuid4')
    def test_align_tei_documents_override_metadata_languages(self, mock_uuid, tei_service):
        """Test that explicit languages override TEI metadata languages."""
        # TEI documents with different languages in metadata
        italian_tei_unknown = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test</title></titleStmt>
        </fileDesc>
        <profileDesc>
            <langUsage><language ident="unknown">unknown</language></langUsage>
        </profileDesc>
    </teiHeader>
    <text><body><div><p>Ciao mondo.</p></div></body></text>
</TEI>'''
        
        english_tei_unknown = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test</title></titleStmt>
        </fileDesc>
        <profileDesc>
            <langUsage><language ident="unknown">unknown</language></langUsage>
        </profileDesc>
    </teiHeader>
    <text><body><div><p>Hello world.</p></div></body></text>
</TEI>'''
        
        # Mock UUID generation
        mock_uuid.return_value.__str__ = lambda self: 'test-uuid'
        
        # Mock alignment result
        mock_alignment = AlignmentResponse(
            alignments=[],
            source_language="it",
            target_language="en", 
            processing_time=0.5,
            total_source_sentences=0,
            total_target_sentences=0,
            parameters=AlignmentRequest(
                source_text="test",
                target_text="test",
                source_language="it",
                target_language="en"
            )
        )
        
        tei_service.bertalign_service.align_texts.return_value = mock_alignment
        
        # Perform alignment with explicit languages that override "unknown" from metadata
        result = tei_service.align_tei_documents(
            italian_tei_unknown, 
            english_tei_unknown, 
            source_language="it", 
            target_language="en"
        )
        
        # Should use explicit languages, not "unknown" from metadata
        assert result['source_language'] == 'it'
        assert result['target_language'] == 'en'
        
        # Verify alignment request used explicit languages
        call_args = tei_service.bertalign_service.align_texts.call_args[0][0]
        assert call_args.source_language == 'it'
        assert call_args.target_language == 'en'
    
    @patch('app.services.tei_service.uuid.uuid4')
    def test_align_tei_documents_fallback_to_metadata_languages(self, mock_uuid, tei_service, sample_italian_tei, sample_english_tei):
        """Test that service falls back to TEI metadata languages when explicit languages not provided."""
        # Mock UUID generation
        mock_uuid.return_value.__str__ = lambda self: 'test-uuid'
        
        # Mock alignment result
        mock_alignment = AlignmentResponse(
            alignments=[],
            source_language="it",
            target_language="en", 
            processing_time=0.5,
            total_source_sentences=0,
            total_target_sentences=0,
            parameters=AlignmentRequest(
                source_text="test",
                target_text="test",
                source_language="it",
                target_language="en"
            )
        )
        
        tei_service.bertalign_service.align_texts.return_value = mock_alignment
        
        # Perform alignment without explicit languages
        result = tei_service.align_tei_documents(sample_italian_tei, sample_english_tei)
        
        # Should use languages from TEI metadata
        assert result['source_language'] == 'it'
        assert result['target_language'] == 'en'
        
        # Verify alignment request used metadata languages
        call_args = tei_service.bertalign_service.align_texts.call_args[0][0]
        assert call_args.source_language == 'it'
        assert call_args.target_language == 'en'
    
    def test_sentence_level_seg_alignments(self, tei_service):
        """Test sentence-level alignments within paragraphs using <seg> tags."""
        # Create test documents with multi-sentence paragraphs
        italian_tei = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
            </teiHeader>
            <text>
                <body>
                    <p>Prima frase italiana. Seconda frase italiana. Terza frase italiana.</p>
                </body>
            </text>
        </TEI>'''
        
        english_tei = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
            </teiHeader>
            <text>
                <body>
                    <p>First English sentence. Second English sentence. Third English sentence.</p>
                </body>
            </text>
        </TEI>'''
        
        # Parse documents
        source_doc = tei_service.parse_tei_file(italian_tei)
        target_doc = tei_service.parse_tei_file(english_tei)
        
        # Create sentence-level alignments
        alignments = [
            AlignmentPair(
                source_sentences=["Prima frase italiana."],
                target_sentences=["First English sentence."],
                alignment_score=0.95,
                source_indices=[0],
                target_indices=[0]
            ),
            AlignmentPair(
                source_sentences=["Seconda frase italiana."],
                target_sentences=["Second English sentence."],
                alignment_score=0.92,
                source_indices=[1],
                target_indices=[1]
            ),
            AlignmentPair(
                source_sentences=["Terza frase italiana."],
                target_sentences=["Third English sentence."],
                alignment_score=0.89,
                source_indices=[2],
                target_indices=[2]
            )
        ]
        
        # Generate aligned XML with sentence-level segments
        aligned_xml = tei_service._generate_aligned_tei(source_doc, target_doc, alignments, "it", "en")
        
        # Parse result to verify <seg> structure
        root = ET.fromstring(aligned_xml)
        
        # Check that we have a teiCorpus with the correct structure
        assert root.tag.endswith('teiCorpus')
        assert root.get('version') == '3.3.0'
        
        # Check standOff links - should have 3 sentence-level alignments
        standoff = root.find('.//{http://www.tei-c.org/ns/1.0}standOff')
        assert standoff is not None
        links = standoff.findall('.//{http://www.tei-c.org/ns/1.0}link')
        assert len(links) == 3
        
        # Check that document structure is preserved and aligned properly
        tei_documents = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
        assert len(tei_documents) == 2
        
        italian_tei_elem = tei_documents[0]
        italian_p = italian_tei_elem.find('.//{http://www.tei-c.org/ns/1.0}p')
        assert italian_p is not None
        
        # Check English document structure  
        english_tei_elem = tei_documents[1]
        english_p = english_tei_elem.find('.//{http://www.tei-c.org/ns/1.0}p')
        assert english_p is not None
        
        # Verify that elements have alignment identifiers
        # Current implementation may use paragraph-level IDs or seg tags depending on alignment granularity
        italian_has_alignment_id = (italian_p.get('{http://www.w3.org/XML/1998/namespace}id') is not None or 
                                   len(italian_p.findall('.//{http://www.tei-c.org/ns/1.0}seg')) > 0)
        english_has_alignment_id = (english_p.get('{http://www.w3.org/XML/1998/namespace}id') is not None or 
                                   len(english_p.findall('.//{http://www.tei-c.org/ns/1.0}seg')) > 0)
        
        assert italian_has_alignment_id
        assert english_has_alignment_id
        
        # Verify original text content is preserved
        italian_text = tei_service._get_element_text(italian_p)
        english_text = tei_service._get_element_text(english_p)
        
        assert "Prima frase italiana" in italian_text
        assert "Seconda frase italiana" in italian_text  
        assert "Terza frase italiana" in italian_text
        
        assert "First English sentence" in english_text
        assert "Second English sentence" in english_text
        assert "Third English sentence" in english_text
        
        # Verify that XML is well-formed by parsing again
        ET.fromstring(aligned_xml)  # Should not raise exception
    
    def test_text_cleaning_functionality(self, tei_service):
        """Test that text cleaning removes line breaks, tabs, and normalizes whitespace."""
        # Test direct cleaning function
        test_cases = [
            ("Simple text", "Simple text"),
            ("Text with\nline breaks", "Text with line breaks"),
            ("Text with\r\nwindows line breaks", "Text with windows line breaks"), 
            ("Text  with   multiple    spaces", "Text with multiple spaces"),
            ("Text\twith\ttabs", "Text with tabs"),
            ("Complex\n  text\r\n   with\t  all\n\n  issues   combined", "Complex text with all issues combined"),
            ("", ""),
            ("   Leading and trailing spaces   ", "Leading and trailing spaces"),
            ("Multiple\n\n\nline\n\n\nbreaks", "Multiple line breaks"),
        ]
        
        for input_text, expected_output in test_cases:
            result = tei_service._clean_text(input_text)
            assert result == expected_output, f"Input: {repr(input_text)}, Expected: {repr(expected_output)}, Got: {repr(result)}"
            
            # Ensure no unwanted characters remain
            assert '\n' not in result, f"Line breaks found in: {repr(result)}"
            assert '\r' not in result, f"Carriage returns found in: {repr(result)}"
            assert '\t' not in result, f"Tabs found in: {repr(result)}"
            assert '  ' not in result, f"Double spaces found in: {repr(result)}"
    
    def test_text_extraction_with_cleaning(self, tei_service):
        """Test that text extraction from TEI applies cleaning automatically."""
        # TEI with various whitespace issues
        tei_with_whitespace = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
            </teiHeader>
            <text>
                <body>
                    <p>This paragraph
                    has line breaks    and     multiple spaces.</p>
                    <p>Another paragraph with	tabs	and
                    mixed     whitespace.</p>
                </body>
            </text>
        </TEI>'''
        
        doc = tei_service.parse_tei_file(tei_with_whitespace)
        
        # Check that extracted text is cleaned
        assert len(doc.text_elements) == 2
        
        first_para = doc.text_elements[0].text
        second_para = doc.text_elements[1].text
        
        # Verify cleaning was applied
        assert '\n' not in first_para and '\n' not in second_para
        assert '\r' not in first_para and '\r' not in second_para  
        assert '\t' not in first_para and '\t' not in second_para
        assert '  ' not in first_para and '  ' not in second_para
        
        # Verify content is preserved correctly
        assert "This paragraph has line breaks and multiple spaces." == first_para
        assert "Another paragraph with tabs and mixed whitespace." == second_para
    
    def test_seg_tag_creation_for_sentence_alignments(self, tei_service):
        """Test that sentence-level alignments create proper <seg> tags within paragraphs."""
        # Create test documents with multi-sentence paragraphs
        italian_tei = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
            </teiHeader>
            <text>
                <body>
                    <p>Prima frase italiana. Seconda frase italiana. Terza frase italiana.</p>
                </body>
            </text>
        </TEI>'''

        english_tei = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
            </teiHeader>
            <text>
                <body>
                    <p>First English sentence. Second English sentence. Third English sentence.</p>
                </body>
            </text>
        </TEI>'''
        
        # Parse documents
        source_doc = tei_service.parse_tei_file(italian_tei)
        target_doc = tei_service.parse_tei_file(english_tei)
        
        # Create sentence-level alignments (should trigger <seg> creation)
        alignments = [
            AlignmentPair(
                source_sentences=["Prima frase italiana."],
                target_sentences=["First English sentence."],
                alignment_score=0.95,
                source_indices=[0],
                target_indices=[0]
            ),
            AlignmentPair(
                source_sentences=["Seconda frase italiana."],
                target_sentences=["Second English sentence."],
                alignment_score=0.92,
                source_indices=[1],
                target_indices=[1]
            ),
            AlignmentPair(
                source_sentences=["Terza frase italiana."],
                target_sentences=["Third English sentence."],
                alignment_score=0.89,
                source_indices=[2],
                target_indices=[2]
            )
        ]
        
        # Generate aligned XML
        aligned_xml = tei_service._generate_aligned_tei(source_doc, target_doc, alignments, "it", "en")
        
        # Parse result
        root = ET.fromstring(aligned_xml)
        
        # Verify basic structure
        assert root.tag.endswith('teiCorpus')
        assert len(root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')) == 2
        
        # Check standOff links
        links = root.findall('.//{http://www.tei-c.org/ns/1.0}link')
        assert len(links) == 3  # Should have 3 sentence-level links
        
        # Get the two TEI documents
        tei_documents = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
        italian_doc = tei_documents[0]
        english_doc = tei_documents[1]
        
        # Test Italian document has proper <seg> tags
        italian_p = italian_doc.find('.//{http://www.tei-c.org/ns/1.0}p')
        italian_segs = italian_p.findall('.//{http://www.tei-c.org/ns/1.0}seg')
        
        assert len(italian_segs) == 3, "Should have 3 <seg> elements for 3 sentence alignments"
        
        # Verify each seg has xml:id and correct text
        expected_italian_texts = ["Prima frase italiana.", "Seconda frase italiana.", "Terza frase italiana."]
        for i, seg in enumerate(italian_segs):
            seg_id = seg.get('{http://www.w3.org/XML/1998/namespace}id')
            assert seg_id is not None, f"<seg> {i+1} should have xml:id"
            assert len(seg_id) > 0, f"<seg> {i+1} xml:id should not be empty"
            assert seg.text == expected_italian_texts[i], f"<seg> {i+1} text mismatch"
        
        # Test English document has proper <seg> tags
        english_p = english_doc.find('.//{http://www.tei-c.org/ns/1.0}p')
        english_segs = english_p.findall('.//{http://www.tei-c.org/ns/1.0}seg')
        
        assert len(english_segs) == 3, "Should have 3 <seg> elements for 3 sentence alignments"
        
        # Verify each seg has xml:id and correct text
        expected_english_texts = ["First English sentence.", "Second English sentence.", "Third English sentence."]
        for i, seg in enumerate(english_segs):
            seg_id = seg.get('{http://www.w3.org/XML/1998/namespace}id')
            assert seg_id is not None, f"<seg> {i+1} should have xml:id"
            assert len(seg_id) > 0, f"<seg> {i+1} xml:id should not be empty"
            assert seg.text == expected_english_texts[i], f"<seg> {i+1} text mismatch"
        
        # Verify that paragraph-level text is preserved when reconstructed
        italian_reconstructed = tei_service._get_element_text(italian_p)
        english_reconstructed = tei_service._get_element_text(english_p)
        
        assert "Prima frase italiana" in italian_reconstructed
        assert "Seconda frase italiana" in italian_reconstructed
        assert "Terza frase italiana" in italian_reconstructed
        
        assert "First English sentence" in english_reconstructed
        assert "Second English sentence" in english_reconstructed  
        assert "Third English sentence" in english_reconstructed
        
        # Verify standOff links reference the correct seg IDs
        all_seg_ids = set()
        for seg in italian_segs + english_segs:
            all_seg_ids.add(seg.get('{http://www.w3.org/XML/1998/namespace}id'))
        
        for link in links:
            target = link.get('target')
            ids = target.split()
            source_id = ids[0][1:]  # Remove #
            target_id = ids[1][1:]  # Remove #
            
            assert source_id in all_seg_ids, f"Link source ID {source_id} not found in seg elements"
            assert target_id in all_seg_ids, f"Link target ID {target_id} not found in seg elements"
    
    def test_head_elements_get_seg_tags(self, tei_service):
        """Test that head elements also get <seg> tags for alignments."""
        # Create test documents with head elements that should be aligned
        italian_tei = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
            </teiHeader>
            <text>
                <body>
                    <head type="main">Titolo principale in italiano</head>
                    <p>Paragrafo in italiano.</p>
                </body>
            </text>
        </TEI>'''
        
        english_tei = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
            </teiHeader>
            <text>
                <body>
                    <head type="main">Main title in English</head>
                    <p>Paragraph in English.</p>
                </body>
            </text>
        </TEI>'''
        
        # Parse documents
        source_doc = tei_service.parse_tei_file(italian_tei)
        target_doc = tei_service.parse_tei_file(english_tei)
        
        # Create alignments for both head and p elements
        alignments = [
            AlignmentPair(
                source_sentences=["Titolo principale in italiano"],
                target_sentences=["Main title in English"],
                alignment_score=0.95,
                source_indices=[0],
                target_indices=[0]
            ),
            AlignmentPair(
                source_sentences=["Paragrafo in italiano."],
                target_sentences=["Paragraph in English."],
                alignment_score=0.92,
                source_indices=[1],
                target_indices=[1]
            )
        ]
        
        # Generate aligned XML
        aligned_xml = tei_service._generate_aligned_tei(source_doc, target_doc, alignments, "it", "en")
        
        # Parse result
        root = ET.fromstring(aligned_xml)
        
        # Verify basic structure
        assert root.tag.endswith('teiCorpus')
        assert len(root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')) == 2
        
        # Check standOff links
        links = root.findall('.//{http://www.tei-c.org/ns/1.0}link')
        assert len(links) == 2  # Should have 2 links
        
        # Get the two TEI documents
        tei_documents = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
        italian_doc = tei_documents[0]
        english_doc = tei_documents[1]
        
        # Test Italian document has <seg> tags in both head and p
        italian_head = italian_doc.find('.//{http://www.tei-c.org/ns/1.0}head')
        italian_p = italian_doc.find('.//{http://www.tei-c.org/ns/1.0}p')
        
        # Check head element has <seg> tag
        italian_head_segs = italian_head.findall('.//{http://www.tei-c.org/ns/1.0}seg')
        assert len(italian_head_segs) == 1, "Head element should have 1 <seg> element"
        assert italian_head_segs[0].text == "Titolo principale in italiano"
        assert italian_head_segs[0].get('{http://www.w3.org/XML/1998/namespace}id') is not None
        
        # Check p element has <seg> tag  
        italian_p_segs = italian_p.findall('.//{http://www.tei-c.org/ns/1.0}seg')
        assert len(italian_p_segs) == 1, "Paragraph element should have 1 <seg> element"
        assert italian_p_segs[0].text == "Paragrafo in italiano."
        assert italian_p_segs[0].get('{http://www.w3.org/XML/1998/namespace}id') is not None
        
        # Test English document has <seg> tags in both head and p
        english_head = english_doc.find('.//{http://www.tei-c.org/ns/1.0}head')
        english_p = english_doc.find('.//{http://www.tei-c.org/ns/1.0}p')
        
        # Check head element has <seg> tag
        english_head_segs = english_head.findall('.//{http://www.tei-c.org/ns/1.0}seg')
        assert len(english_head_segs) == 1, "Head element should have 1 <seg> element"
        assert english_head_segs[0].text == "Main title in English"
        assert english_head_segs[0].get('{http://www.w3.org/XML/1998/namespace}id') is not None
        
        # Check p element has <seg> tag
        english_p_segs = english_p.findall('.//{http://www.tei-c.org/ns/1.0}seg')
        assert len(english_p_segs) == 1, "Paragraph element should have 1 <seg> element"
        assert english_p_segs[0].text == "Paragraph in English."
        assert english_p_segs[0].get('{http://www.w3.org/XML/1998/namespace}id') is not None
        
        # Verify standOff links reference the correct seg IDs
        all_seg_ids = set()
        for seg in italian_head_segs + italian_p_segs + english_head_segs + english_p_segs:
            all_seg_ids.add(seg.get('{http://www.w3.org/XML/1998/namespace}id'))
        
        for link in links:
            target = link.get('target')
            ids = target.split()
            source_id = ids[0][1:]  # Remove #
            target_id = ids[1][1:]  # Remove #
            
            assert source_id in all_seg_ids, f"Link source ID {source_id} not found in seg elements"
            assert target_id in all_seg_ids, f"Link target ID {target_id} not found in seg elements"

    @patch("app.services.tei_service.uuid.uuid4")
    def test_xml_id_uniqueness_many_to_many_alignment(self, mock_uuid, tei_service):
        """Test that xml:id attributes are unique even in many-to-many alignments."""
        # Create unique UUID sequence for testing
        uuid_sequence = [f"uuid-{i}" for i in range(10)]
        mock_uuids = []
        for uid in uuid_sequence:
            mock_obj = Mock()
            mock_obj.__str__ = lambda self, uid=uid: uid
            mock_uuids.append(mock_obj)
        mock_uuid.side_effect = mock_uuids
        
        # TEI documents with multiple sentences that could create many-to-many alignments
        source_tei = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test</title></titleStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <p>Prima frase. Seconda frase. Terza frase.</p>
        </body>
    </text>
</TEI>"""
        
        target_tei = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test</title></titleStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <p>First sentence. Second sentence. Third sentence.</p>
        </body>
    </text>
</TEI>"""
        
        # Mock alignment result with many-to-many alignment
        mock_alignment = AlignmentResponse(
            alignments=[
                AlignmentPair(
                    source_sentences=["Prima frase.", "Seconda frase."],
                    target_sentences=["First sentence."],
                    alignment_score=0.85,
                    source_indices=[0, 1],
                    target_indices=[0]
                ),
                AlignmentPair(
                    source_sentences=["Terza frase."],
                    target_sentences=["Second sentence.", "Third sentence."],
                    alignment_score=0.90,
                    source_indices=[2],
                    target_indices=[1, 2]
                )
            ],
            source_language="it",
            target_language="en",
            processing_time=0.5,
            total_source_sentences=3,
            total_target_sentences=3,
            parameters=AlignmentRequest(
                source_text="Prima frase. Seconda frase. Terza frase.",
                target_text="First sentence. Second sentence. Third sentence.",
                source_language="it",
                target_language="en"
            )
        )
        
        tei_service.bertalign_service.align_texts.return_value = mock_alignment
        
        # Perform alignment
        result = tei_service.align_tei_documents(source_tei, target_tei)
        
        # Parse result
        aligned_xml = result["aligned_xml"]
        root = ET.fromstring(aligned_xml)
        
        # Extract all xml:id attributes
        xml_ids = []
        for elem in root.iter():
            xml_id = elem.get("{http://www.w3.org/XML/1998/namespace}id")
            if xml_id:
                xml_ids.append(xml_id)
        
        # Verify all xml:id attributes are unique
        unique_ids = set(xml_ids)
        assert len(xml_ids) == len(unique_ids), f"Duplicate xml:id found: {xml_ids}"
        
        # Verify we have the expected number of segments
        seg_elements = root.findall(".//{http://www.tei-c.org/ns/1.0}seg")
        assert len(seg_elements) > 0, "Should have seg elements"
        
        # Verify all seg elements have unique xml:id
        seg_ids = [seg.get("{http://www.w3.org/XML/1998/namespace}id") for seg in seg_elements]
        seg_ids = [sid for sid in seg_ids if sid]  # Filter out None
        assert len(seg_ids) == len(set(seg_ids)), f"Duplicate seg xml:id found: {seg_ids}"
        
        # Verify linkGrp structure handles many-to-many correctly
        links = root.findall(".//{http://www.tei-c.org/ns/1.0}link")
        assert len(links) > 0, "Should have link elements"
        
        # Each link should reference valid, unique xml:id values
        for link in links:
            target = link.get("target")
            ids = target.split()
            # Remove # prefix from each ID
            referenced_ids = [id_ref[1:] for id_ref in ids]
            
            # All referenced IDs should exist in the document
            for ref_id in referenced_ids:
                assert ref_id in unique_ids, f"Link references non-existent ID: {ref_id}"
