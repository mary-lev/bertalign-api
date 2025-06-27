"""
Integration tests for enhanced TEI corpus with sentence-level <seg> tag functionality.

These tests validate the complete workflow using real Italian and English TEI documents
to ensure the enhanced alignment system works correctly in real-world scenarios.
"""

import pytest
import os
from pathlib import Path
from xml.etree import ElementTree as ET
from app.services.tei_service import TEIService
from app.services.bertalign_service import BertalignService


class TestTEICorpusIntegration:
    """Integration tests for enhanced TEI corpus functionality."""

    @pytest.fixture
    def tei_service(self):
        """Create TEI service instance."""
        bertalign_service = BertalignService()
        return TEIService(bertalign_service)

    def test_real_italian_english_alignment(self, tei_service):
        """Test alignment of real Italian and English TEI documents."""
        # Get the path to the texts directory relative to the tests directory
        test_dir = Path(__file__).parent
        texts_dir = test_dir.parent / 'texts'
        
        # Read the actual test files
        with open(texts_dir / 'italian.xml', 'r', encoding='utf-8') as f:
            italian_xml = f.read()
        
        with open(texts_dir / 'english.xml', 'r', encoding='utf-8') as f:
            english_xml = f.read()
        
        # Perform alignment
        result = tei_service.align_tei_documents(italian_xml, english_xml, 'it', 'en')
        
        # Validate basic response structure
        assert 'aligned_xml' in result
        assert result['source_language'] == 'it'
        assert result['target_language'] == 'en'
        assert result['alignment_count'] > 0
        assert result['processing_time'] > 0
        
        # Parse the result XML
        aligned_xml = result['aligned_xml']
        root = ET.fromstring(aligned_xml)
        
        # Validate teiCorpus structure
        assert root.tag.endswith('teiCorpus')
        assert root.get('version') == '3.3.0'
        
        # Validate standOff structure
        standoff = root.find('.//{http://www.tei-c.org/ns/1.0}standOff')
        assert standoff is not None
        
        link_grp = standoff.find('.//{http://www.tei-c.org/ns/1.0}linkGrp')
        assert link_grp is not None
        assert link_grp.get('type') == 'translation'
        
        # Validate links exist
        links = link_grp.findall('.//{http://www.tei-c.org/ns/1.0}link')
        assert len(links) == result['alignment_count']
        
        # Validate each link has proper target format
        for link in links:
            target = link.get('target')
            assert target is not None
            assert target.count('#') == 2  # Should have two UUID references
            assert link.get('type') == 'Linguistic'
        
        # Validate both TEI documents are included
        tei_documents = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
        assert len(tei_documents) == 2
        
        # Validate Italian document structure preservation
        italian_tei = tei_documents[0]
        italian_title = italian_tei.find('.//{http://www.tei-c.org/ns/1.0}title')
        assert italian_title is not None
        assert 'teoria figurativa' in italian_title.text.lower()
        
        # Validate English document structure preservation
        english_tei = tei_documents[1]
        english_title = english_tei.find('.//{http://www.tei-c.org/ns/1.0}title')
        assert english_title is not None
        assert 'pictorial form' in english_title.text.lower()
        
        # Validate alignment marking (either paragraph xml:id or seg elements)
        self._validate_alignment_marking(italian_tei, result['alignment_count'])
        self._validate_alignment_marking(english_tei, result['alignment_count'])
        
        # Save result for manual inspection
        with open(texts_dir / 'integration_test_result.xml', 'w', encoding='utf-8') as f:
            f.write(aligned_xml)

    def _validate_alignment_marking(self, tei_doc, expected_alignment_count):
        """Validate that alignment marking is present in the TEI document."""
        # Find all paragraphs
        paragraphs = tei_doc.findall('.//{http://www.tei-c.org/ns/1.0}p')
        assert len(paragraphs) > 0
        
        # Count alignment markers (either paragraph xml:id or seg elements)
        alignment_markers = 0
        
        for p in paragraphs:
            # Check if paragraph has xml:id (paragraph-level alignment)
            if p.get('{http://www.w3.org/XML/1998/namespace}id'):
                alignment_markers += 1
            else:
                # Check for seg elements (sentence-level alignments)
                seg_elements = p.findall('.//{http://www.tei-c.org/ns/1.0}seg')
                for seg in seg_elements:
                    if seg.get('{http://www.w3.org/XML/1998/namespace}id'):
                        alignment_markers += 1
        
        # Should have some alignment markers (the exact count depends on bertalign's behavior)
        if expected_alignment_count > 0:
            assert alignment_markers > 0

    def test_corpus_header_preservation(self, tei_service):
        """Test that corpus header contains proper metadata."""
        # Get the path to the texts directory relative to the tests directory
        test_dir = Path(__file__).parent
        texts_dir = test_dir.parent / 'texts'
        
        with open(texts_dir / 'italian.xml', 'r', encoding='utf-8') as f:
            italian_xml = f.read()
        
        with open(texts_dir / 'english.xml', 'r', encoding='utf-8') as f:
            english_xml = f.read()
        
        result = tei_service.align_tei_documents(italian_xml, english_xml, 'it', 'en')
        root = ET.fromstring(result['aligned_xml'])
        
        # Check corpus-level header
        corpus_header = root.find('.//{http://www.tei-c.org/ns/1.0}teiHeader')
        assert corpus_header is not None
        
        # Check title
        title = corpus_header.find('.//{http://www.tei-c.org/ns/1.0}title')
        assert title is not None
        assert title.text == "Aligned Parallel Texts"
        
        # Check publication statement
        pub_stmt = corpus_header.find('.//{http://www.tei-c.org/ns/1.0}publicationStmt')
        assert pub_stmt is not None
        pub_p = pub_stmt.find('.//{http://www.tei-c.org/ns/1.0}p')
        assert pub_p is not None
        assert "Bertalign API" in pub_p.text
        
        # Check language usage
        lang_usage = corpus_header.find('.//{http://www.tei-c.org/ns/1.0}langUsage')
        assert lang_usage is not None
        
        languages = lang_usage.findall('.//{http://www.tei-c.org/ns/1.0}language')
        assert len(languages) == 2
        
        # Check for Italian and English language declarations
        lang_idents = [lang.get('ident') for lang in languages]
        assert 'it' in lang_idents
        assert 'en' in lang_idents

    def test_original_structure_preservation(self, tei_service):
        """Test that original document structure is completely preserved."""
        # Get the path to the texts directory relative to the tests directory
        test_dir = Path(__file__).parent
        texts_dir = test_dir.parent / 'texts'
        
        with open(texts_dir / 'italian.xml', 'r', encoding='utf-8') as f:
            italian_xml = f.read()
        
        with open(texts_dir / 'english.xml', 'r', encoding='utf-8') as f:
            english_xml = f.read()
        
        # Parse original documents
        italian_orig = ET.fromstring(italian_xml)
        english_orig = ET.fromstring(english_xml)
        
        # Perform alignment
        result = tei_service.align_tei_documents(italian_xml, english_xml, 'it', 'en')
        root = ET.fromstring(result['aligned_xml'])
        
        # Get aligned documents
        tei_documents = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
        italian_aligned = tei_documents[0]
        english_aligned = tei_documents[1]
        
        # Check that key structural elements are preserved
        self._check_structure_preservation(italian_orig, italian_aligned)
        self._check_structure_preservation(english_orig, english_aligned)

    def _check_structure_preservation(self, original, aligned):
        """Check that structural elements are preserved between original and aligned versions."""
        # Check that div elements are preserved
        orig_divs = original.findall('.//{http://www.tei-c.org/ns/1.0}div')
        aligned_divs = aligned.findall('.//{http://www.tei-c.org/ns/1.0}div')
        assert len(orig_divs) == len(aligned_divs)
        
        # Check that pb (page break) elements are preserved
        orig_pbs = original.findall('.//{http://www.tei-c.org/ns/1.0}pb')
        aligned_pbs = aligned.findall('.//{http://www.tei-c.org/ns/1.0}pb')
        assert len(orig_pbs) == len(aligned_pbs)
        
        # Check that head elements are preserved
        orig_heads = original.findall('.//{http://www.tei-c.org/ns/1.0}head')
        aligned_heads = aligned.findall('.//{http://www.tei-c.org/ns/1.0}head')
        assert len(orig_heads) == len(aligned_heads)
        
        # Check that paragraph count is preserved (or higher due to seg elements)
        orig_ps = original.findall('.//{http://www.tei-c.org/ns/1.0}p')
        aligned_ps = aligned.findall('.//{http://www.tei-c.org/ns/1.0}p')
        assert len(aligned_ps) >= len(orig_ps)  # Could be equal or more due to text restructuring

    def test_performance_with_real_documents(self, tei_service):
        """Test performance with real-world document sizes."""
        # Get the path to the texts directory relative to the tests directory
        test_dir = Path(__file__).parent
        texts_dir = test_dir.parent / 'texts'
        
        with open(texts_dir / 'italian.xml', 'r', encoding='utf-8') as f:
            italian_xml = f.read()
        
        with open(texts_dir / 'english.xml', 'r', encoding='utf-8') as f:
            english_xml = f.read()
        
        import time
        start_time = time.time()
        
        result = tei_service.align_tei_documents(italian_xml, english_xml, 'it', 'en')
        
        end_time = time.time()
        actual_time = end_time - start_time
        reported_time = result['processing_time']
        
        # Performance should be reasonable for real documents
        assert actual_time < 30.0  # Should complete within 30 seconds
        assert reported_time > 0
        assert abs(actual_time - reported_time) < 5.0  # Times should be roughly consistent
        
        # Should produce meaningful alignments
        assert result['alignment_count'] > 0
        assert result['alignment_count'] < 1000  # Reasonable upper bound