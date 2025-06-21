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
        aligned_xml = tei_service._generate_aligned_tei(source_doc, target_doc, alignments)
        
        # Parse result to verify structure
        root = ET.fromstring(aligned_xml)
        
        # Check root element
        assert root.tag.endswith('TEI')
        assert root.get('xmlns') == 'http://www.tei-c.org/ns/1.0'
        
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
        """Test TEI document creation with XML IDs."""
        doc = tei_service.parse_tei_file(sample_italian_tei)
        
        # Create alignment mapping
        alignment_map = {
            "Come introduzione un breve chiarimento concettuale.": "test-uuid-1",
            "In primo luogo ciò che è contenuto nel concetto di analisi.": "test-uuid-2"
        }
        
        # Generate TEI with IDs
        tei_with_ids = tei_service._create_tei_with_ids(doc, alignment_map)
        
        # Verify IDs were added
        paragraphs = tei_with_ids.findall('.//{http://www.tei-c.org/ns/1.0}p')
        assert len(paragraphs) == 2
        
        # Check that at least one paragraph has an xml:id
        has_id = any(p.get('{http://www.w3.org/XML/1998/namespace}id') for p in paragraphs)
        assert has_id
        
        # Check language was added
        lang_elem = tei_with_ids.find('.//{http://www.tei-c.org/ns/1.0}language')
        assert lang_elem is not None
        assert lang_elem.get('ident') == 'it'
        
        # Check facsimile was added
        facsimile = tei_with_ids.find('.//{http://www.tei-c.org/ns/1.0}facsimile')
        assert facsimile is not None
    
    @patch('app.services.tei_service.uuid.uuid4')
    def test_align_tei_documents_with_explicit_languages(self, mock_uuid, tei_service, sample_italian_tei, sample_english_tei):
        """Test TEI document alignment with explicit language parameters."""
        # Mock UUID generation
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
            parameters=None
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
            parameters=None
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