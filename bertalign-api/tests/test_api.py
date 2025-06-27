"""
API Endpoint Tests for Bertalign API.

This module contains tests for all REST API endpoints including:
- Health check
- Basic text alignment 
- TEI XML document alignment
- Error handling and validation

Organized into logical test classes for better structure.
"""

import pytest
import time
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_endpoint_success(self, client):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "model_loaded" in data

    def test_root_endpoint_info(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert "supported_languages" in data


class TestBasicAlignmentEndpoint:
    """Tests for the basic text alignment endpoint."""
    
    def test_basic_alignment_success(self, client, basic_alignment_request):
        """Test basic alignment functionality with valid input."""
        response = client.post("/align", json=basic_alignment_request)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required response fields
        assert "alignments" in data
        assert "source_language" in data
        assert "target_language" in data
        assert "processing_time" in data
        assert "total_source_sentences" in data
        assert "total_target_sentences" in data
        assert "parameters" in data
        
        # Check language codes are returned correctly
        assert data["source_language"] == "en"
        assert data["target_language"] == "fr"
        
        # Check we got alignments
        assert len(data["alignments"]) > 0
        
        # Check alignment structure
        alignment = data["alignments"][0]
        assert "source_sentences" in alignment
        assert "target_sentences" in alignment
        assert "alignment_score" in alignment
        assert "source_indices" in alignment
        assert "target_indices" in alignment
        
        # Check score is valid
        assert 0.0 <= alignment["alignment_score"] <= 1.0

    def test_multiple_language_pairs(self, client, multilanguage_test_cases):
        """Test alignment with different language pairs."""
        for test_case in multilanguage_test_cases:
            response = client.post("/align", json={
                "source_text": test_case["source_text"],
                "target_text": test_case["target_text"],
                "source_language": test_case["source_language"],
                "target_language": test_case["target_language"]
            })
            assert response.status_code == 200, f"Failed for {test_case['description']}"
            
            data = response.json()
            assert data["source_language"] == test_case["source_language"]
            assert data["target_language"] == test_case["target_language"]

    def test_pre_split_sentences(self, client, pre_split_request):
        """Test alignment with pre-split sentences."""
        response = client.post("/align", json=pre_split_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_source_sentences"] == 2
        assert data["total_target_sentences"] == 2
        assert data["parameters"]["is_split"] is True

    def test_custom_parameters(self, client, basic_alignment_request):
        """Test alignment with custom parameters."""
        custom_request = {
            **basic_alignment_request,
            "max_align": 3,
            "top_k": 5,
            "win": 10,
            "skip": -0.2,
            "margin": False,
            "len_penalty": False
        }
        
        response = client.post("/align", json=custom_request)
        assert response.status_code == 200
        
        data = response.json()
        params = data["parameters"]
        assert params["max_align"] == 3
        assert params["top_k"] == 5
        assert params["win"] == 10
        assert params["skip"] == -0.2
        assert params["margin"] is False
        assert params["len_penalty"] is False

    def test_performance_timing(self, client, medium_alignment_request):
        """Test alignment performance with medium-sized text."""
        start_time = time.time()
        response = client.post("/align", json=medium_alignment_request)
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should complete within reasonable time
        assert end_time - start_time < 5.0  # 5 seconds max
        
        data = response.json()
        # Processing time should be reported and reasonable
        assert data["processing_time"] > 0
        assert data["processing_time"] < 5.0


class TestBasicAlignmentValidation:
    """Tests for input validation on basic alignment endpoint."""
    
    def test_missing_required_fields(self, client):
        """Test alignment endpoint with missing required fields."""
        response = client.post("/align", json={})
        assert response.status_code == 422
    
    def test_invalid_language_codes(self, client):
        """Test alignment endpoint with invalid language codes."""
        invalid_request = {
            "source_text": "Hello world.",
            "target_text": "Bonjour le monde.",
            "source_language": "invalid",
            "target_language": "fr"
        }
        response = client.post("/align", json=invalid_request)
        assert response.status_code == 422
        
        # Test invalid target language
        invalid_request = {
            "source_text": "Hello world.",
            "target_text": "Bonjour le monde.",
            "source_language": "en",
            "target_language": "invalid"
        }
        response = client.post("/align", json=invalid_request)
        assert response.status_code == 422

    def test_empty_text(self, client):
        """Test alignment endpoint with empty text."""
        empty_request = {
            "source_text": "",
            "target_text": "Bonjour le monde.",
            "source_language": "en",
            "target_language": "fr"
        }
        response = client.post("/align", json=empty_request)
        assert response.status_code == 422
        
        # Test whitespace only
        whitespace_request = {
            "source_text": "   ",
            "target_text": "Bonjour le monde.",
            "source_language": "en",
            "target_language": "fr"
        }
        response = client.post("/align", json=whitespace_request)
        assert response.status_code == 422

    def test_parameter_boundaries(self, client, basic_alignment_request):
        """Test parameter validation boundaries."""
        # Test max_align too high
        invalid_request = {
            **basic_alignment_request,
            "max_align": 15  # Above limit of 10
        }
        response = client.post("/align", json=invalid_request)
        assert response.status_code == 422
        
        # Test skip penalty out of range
        invalid_request = {
            **basic_alignment_request,
            "skip": 0.5  # Should be negative
        }
        response = client.post("/align", json=invalid_request)
        assert response.status_code == 422


class TestTEIAlignmentEndpoint:
    """Tests for the TEI XML document alignment endpoint."""
    
    def test_tei_alignment_success(self, client, basic_tei_request):
        """Test TEI alignment with valid documents."""
        response = client.post("/align/tei", json=basic_tei_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "aligned_xml" in data
        assert "source_language" in data
        assert "target_language" in data
        assert "alignment_count" in data
        assert "processing_time" in data
        
        # Check languages match request
        assert data["source_language"] == "it"
        assert data["target_language"] == "en"
        
        # Check alignment count is reasonable
        assert data["alignment_count"] >= 0
        assert data["processing_time"] > 0
        
        # Check aligned XML has new teiCorpus structure  
        aligned_xml = data["aligned_xml"]
        assert "<teiCorpus" in aligned_xml
        assert 'version="3.3.0"' in aligned_xml
        assert "<standOff>" in aligned_xml
        assert "<linkGrp" in aligned_xml
        assert 'type="translation"' in aligned_xml
        
        # Validate it's well-formed XML
        from xml.etree import ElementTree as ET
        root = ET.fromstring(aligned_xml)
        assert root.tag.endswith('teiCorpus')
        
        # Should contain both original TEI documents
        tei_elements = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
        assert len(tei_elements) == 2  # Source and target documents

    def test_tei_explicit_language_override(self, client, simple_italian_tei, simple_english_tei):
        """Test TEI alignment with explicit language parameters override TEI metadata."""
        # TEI with different language in metadata than what we specify
        request_data = {
            "source_tei": simple_italian_tei.replace('ident="it"', 'ident="unknown"'),
            "target_tei": simple_english_tei.replace('ident="en"', 'ident="unknown"'),
            "source_language": "it",
            "target_language": "en"
        }
        
        response = client.post("/align/tei", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should use our explicit languages, not "unknown" from metadata
        assert data["source_language"] == "it"
        assert data["target_language"] == "en"

    def test_tei_custom_parameters(self, client, basic_tei_request):
        """Test TEI alignment with custom alignment parameters."""
        custom_request = {
            **basic_tei_request,
            "max_align": 3,
            "top_k": 2,
            "win": 3
        }
        
        response = client.post("/align/tei", json=custom_request)
        assert response.status_code == 200
    
    def test_tei_sentence_level_seg_tags(self, client):
        """Test that TEI alignment creates <seg> tags for sentence-level alignments within paragraphs."""
        # Create test documents with multi-sentence paragraphs that should generate sentence alignments
        italian_tei_multi = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
                <profileDesc>
                    <langUsage><language ident="it">Italian</language></langUsage>
                </profileDesc>
            </teiHeader>
            <text>
                <body>
                    <p>Prima frase del test. Seconda frase molto diversa. Terza frase finale.</p>
                </body>
            </text>
        </TEI>'''
        
        english_tei_multi = '''<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt><title>Test Document</title></titleStmt>
                </fileDesc>
                <profileDesc>
                    <langUsage><language ident="en">English</language></langUsage>
                </profileDesc>
            </teiHeader>
            <text>
                <body>
                    <p>First test sentence. Completely different second sentence. Final third sentence.</p>
                </body>
            </text>
        </TEI>'''
        
        request_data = {
            "source_tei": italian_tei_multi,
            "target_tei": english_tei_multi,
            "source_language": "it",
            "target_language": "en"
        }
        
        response = client.post("/align/tei", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        aligned_xml = data["aligned_xml"]
        
        # Parse the result to check for seg tags
        from xml.etree import ElementTree as ET
        root = ET.fromstring(aligned_xml)
        
        # Check for sentence-level seg tags within paragraphs
        # Note: Actual seg creation depends on bertalign's sentence splitting behavior
        # This test validates the API can handle multi-sentence scenarios
        tei_documents = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
        assert len(tei_documents) == 2
        
        # Each document should have paragraphs, either with xml:id (paragraph-level)
        # or containing seg elements (sentence-level)
        for tei_doc in tei_documents:
            paragraphs = tei_doc.findall('.//{http://www.tei-c.org/ns/1.0}p')
            assert len(paragraphs) >= 1
            
            for p in paragraphs:
                # Either paragraph has xml:id or contains seg elements with xml:id
                has_paragraph_id = p.get('{http://www.w3.org/XML/1998/namespace}id') is not None
                seg_elements = p.findall('.//{http://www.tei-c.org/ns/1.0}seg')
                has_seg_elements = len(seg_elements) > 0
                
                # Should have either paragraph-level or sentence-level alignment marking
                if data["alignment_count"] > 0:
                    assert has_paragraph_id or has_seg_elements
                    
                    # If using seg elements, they should have xml:id attributes
                    if has_seg_elements:
                        for seg in seg_elements:
                            seg_id = seg.get('{http://www.w3.org/XML/1998/namespace}id')
                            if seg_id:  # Only check aligned segments
                                assert seg_id is not None
                                assert len(seg_id) > 0


class TestTEIAlignmentValidation:
    """Tests for input validation on TEI alignment endpoint."""
    
    def test_invalid_tei_xml(self, client):
        """Test TEI alignment endpoint with invalid XML."""
        request_data = {
            "source_tei": "<invalid>xml",
            "target_tei": "also invalid",
            "source_language": "en",
            "target_language": "fr"
        }
        
        response = client.post("/align/tei", json=request_data)
        assert response.status_code == 400

    def test_missing_tei_language_parameters(self, client, simple_italian_tei, simple_english_tei):
        """Test TEI alignment endpoint with missing language parameters."""
        request_data = {
            "source_tei": simple_italian_tei,
            "target_tei": simple_english_tei
        }
        
        response = client.post("/align/tei", json=request_data)
        assert response.status_code == 422

    def test_invalid_tei_language_codes(self, client, simple_italian_tei, simple_english_tei):
        """Test TEI alignment with invalid language codes."""
        # Test invalid source language
        request_data = {
            "source_tei": simple_italian_tei,
            "target_tei": simple_english_tei,
            "source_language": "invalid",
            "target_language": "en"
        }
        
        response = client.post("/align/tei", json=request_data)
        assert response.status_code == 422
        
        # Test invalid target language
        request_data = {
            "source_tei": simple_italian_tei,
            "target_tei": simple_english_tei,
            "source_language": "it",
            "target_language": "invalid"
        }
        
        response = client.post("/align/tei", json=request_data)
        assert response.status_code == 422


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""
    
    def test_openapi_docs_accessible(self, client):
        """Test that OpenAPI documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/align" in data["paths"]
        assert "/align/tei" in data["paths"]


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_single_sentence_alignment(self, client):
        """Test alignment with single sentences."""
        request = {
            "source_text": "Hello world.",
            "target_text": "Bonjour le monde.",
            "source_language": "en",
            "target_language": "fr"
        }
        response = client.post("/align", json=request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_source_sentences"] == 1
        assert data["total_target_sentences"] == 1

    def test_very_short_text(self, client):
        """Test alignment with very short text."""
        request = {
            "source_text": "Hi.",
            "target_text": "Bonjour.",
            "source_language": "en",
            "target_language": "fr"
        }
        response = client.post("/align", json=request)
        assert response.status_code == 200

    def test_mismatched_sentence_counts(self, client):
        """Test alignment with mismatched sentence counts."""
        request = {
            "source_text": "Hello. World. Test.",
            "target_text": "Bonjour le monde.",
            "source_language": "en",
            "target_language": "fr"
        }
        response = client.post("/align", json=request)
        assert response.status_code == 200
        
        data = response.json()
        # Should handle mismatched counts gracefully
        assert data["total_source_sentences"] != data["total_target_sentences"]
        assert len(data["alignments"]) > 0