# Enhanced TEI Corpus Usage Examples

This document provides comprehensive examples of the enhanced Bertalign API functionality, demonstrating both paragraph-level and sentence-level alignments with `<seg>` tags. Scenarios: https://docs.google.com/document/d/1hkd8eW4YotfhOG1HANSpu8dv3VRKUhZLCMi0nHvwZNI/edit?tab=t.0

## 🚀 Quick Start

### Basic API Usage

```bash
# Start the API server
uvicorn app.main:app --reload

# Test with basic text alignment first
curl -X POST "http://localhost:8000/align" \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Hello world. How are you?",
    "target_text": "Bonjour le monde. Comment allez-vous?",
    "source_language": "en",
    "target_language": "fr"
  }'
```

### Frontend Integration (JavaScript/TypeScript)

The API includes CORS configuration to support frontend applications:

```javascript
// Basic text alignment from frontend
async function alignTexts(sourceText, targetText, sourceLang, targetLang) {
  const response = await fetch('http://localhost:8000/align', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      source_text: sourceText,
      target_text: targetText,
      source_language: sourceLang,
      target_language: targetLang
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// TEI document alignment from frontend
async function alignTEIDocuments(sourceTEI, targetTEI, sourceLang, targetLang) {
  const response = await fetch('http://localhost:8000/align/tei', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      source_tei: sourceTEI,
      target_tei: targetTEI,
      source_language: sourceLang,
      target_language: targetLang
    })
  });
  
  return await response.json();
}
```

## 📚 TEI Document Alignment Examples

### Example 1: Consistent Seg Tag Usage

The system now consistently creates `<seg>` tags for all alignments, regardless of whether they are paragraph-level or sentence-level alignments.

**Input Italian TEI:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Documento di Test</title></titleStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <p>Questo è un paragrafo completo che verrà allineato come unità singola.</p>
            <p>Un altro paragrafo che non ha corrispondenza diretta.</p>
        </body>
    </text>
</TEI>
```

**Input English TEI:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test Document</title></titleStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <p>This is a complete paragraph that will be aligned as a single unit.</p>
            <p>Another paragraph without direct correspondence.</p>
        </body>
    </text>
</TEI>
```

**API Call:**
```bash
curl -X POST "http://localhost:8000/align/tei" \
  -H "Content-Type: application/json" \
  -d '{
    "source_tei": "<?xml version=\"1.0\"?>...",
    "target_tei": "<?xml version=\"1.0\"?>...",
    "source_language": "it",
    "target_language": "en"
  }'
```

**Output TEI Corpus (Consistent seg tag usage):**
```xml
<teiCorpus version="3.3.0" xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Aligned Parallel Texts</title></titleStmt>
            <publicationStmt><p>Aligned using Bertalign API</p></publicationStmt>
        </fileDesc>
        <profileDesc>
            <langUsage>
                <language ident="it">Source language: it</language>
                <language ident="en">Target language: en</language>
            </langUsage>
        </profileDesc>
    </teiHeader>
    
    <standOff>
        <linkGrp type="translation">
            <link target="#para-uuid-it #para-uuid-en" type="Linguistic"/>
        </linkGrp>
    </standOff>
    
    <!-- Italian document with consistent <seg> tags -->
    <TEI>
        <teiHeader>
            <fileDesc>
                <titleStmt><title>Documento di Test</title></titleStmt>
            </fileDesc>
        </teiHeader>
        <text>
            <body>
                <p><seg xml:id="para-uuid-it">Questo è un paragrafo completo che verrà allineato come unità singola.</seg></p>
                <p>Un altro paragrafo che non ha corrispondenza diretta.</p>
            </body>
        </text>
    </TEI>
    
    <!-- English document with consistent <seg> tags -->
    <TEI>
        <teiHeader>
            <fileDesc>
                <titleStmt><title>Test Document</title></titleStmt>
            </fileDesc>
        </teiHeader>
        <text>
            <body>
                <p><seg xml:id="para-uuid-en">This is a complete paragraph that will be aligned as a single unit.</seg></p>
                <p>Another paragraph without direct correspondence.</p>
            </body>
        </text>
    </TEI>
</teiCorpus>
```

### Example 2: Multiple Sentence Alignments with `<seg>` Tags

When bertalign creates multiple sentence-level alignments within paragraphs and headers, all alignments consistently use `<seg>` tags.

**Input Italian TEI:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Testo Complesso</title></titleStmt>
            <author>Paolo Rossi</author>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <div xml:id="intro">
                <head type="main">Introduzione</head>
                <p>Prima frase italiana molto specifica. La seconda frase parla di argomenti diversi. Terza frase con contenuto unico.</p>
                <p>Un paragrafo semplice e diretto.</p>
            </div>
        </body>
    </text>
</TEI>
```

**Input English TEI:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Complex Text</title></titleStmt>
            <author>Paolo Rossi</author>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <div xml:id="intro">
                <head type="main">Introduction</head>
                <p>First very specific Italian sentence. The second sentence discusses different topics. Third sentence with unique content.</p>
                <p>A simple and direct paragraph.</p>
            </div>
        </body>
    </text>
</TEI>
```

**Output TEI Corpus (Automatic sentence-level `<seg>` creation):**
```xml
<teiCorpus version="3.3.0" xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Aligned Parallel Texts</title></titleStmt>
            <publicationStmt><p>Aligned using Bertalign API</p></publicationStmt>
        </fileDesc>
        <profileDesc>
            <langUsage>
                <language ident="it">Source language: it</language>
                <language ident="en">Target language: en</language>
            </langUsage>
        </profileDesc>
    </teiHeader>
    
    <standOff>
        <linkGrp type="translation">
            <!-- Automatic sentence-level alignments -->
            <link target="#sent-uuid-it-1 #sent-uuid-en-1" type="Linguistic"/>
            <link target="#sent-uuid-it-2 #sent-uuid-en-2" type="Linguistic"/>
            <link target="#sent-uuid-it-3 #sent-uuid-en-3" type="Linguistic"/>
            <!-- All alignments consistently use <seg> tags -->
            <link target="#para-uuid-it-2 #para-uuid-en-2" type="Linguistic"/>
        </linkGrp>
    </standOff>
    
    <!-- Italian document with automatic <seg> tag insertion -->
    <TEI>
        <teiHeader>
            <fileDesc>
                <titleStmt><title>Testo Complesso</title></titleStmt>
                <author>Paolo Rossi</author>
            </fileDesc>
        </teiHeader>
        <text>
            <body>
                <div xml:id="intro">
                    <head type="main">Introduzione</head>
                    
                    <!-- Bertalign detected sentence-level alignments - <seg> tags created automatically -->
                    <p>
                        <seg xml:id="sent-uuid-it-1">Prima frase italiana molto specifica.</seg>
                        <seg xml:id="sent-uuid-it-2">La seconda frase parla di argomenti diversi.</seg>
                        <seg xml:id="sent-uuid-it-3">Terza frase con contenuto unico.</seg>
                    </p>
                    
                    <!-- Consistent <seg> tag usage for all alignments -->
                    <p><seg xml:id="para-uuid-it-2">Un paragrafo semplice e diretto.</seg></p>
                </div>
            </body>
        </text>
    </TEI>
    
    <!-- English document with corresponding automatic <seg> tags -->
    <TEI>
        <teiHeader>
            <fileDesc>
                <titleStmt><title>Complex Text</title></titleStmt>
                <author>Paolo Rossi</author>
            </fileDesc>
        </teiHeader>
        <text>
            <body>
                <div xml:id="intro">
                    <head type="main">Introduction</head>
                    
                    <!-- Corresponding automatic <seg> tags -->
                    <p>
                        <seg xml:id="sent-uuid-en-1">First very specific Italian sentence.</seg>
                        <seg xml:id="sent-uuid-en-2">The second sentence discusses different topics.</seg>
                        <seg xml:id="sent-uuid-en-3">Third sentence with unique content.</seg>
                    </p>
                    
                    <!-- Consistent <seg> tag usage for all alignments -->
                    <p><seg xml:id="para-uuid-en-2">A simple and direct paragraph.</seg></p>
                </div>
            </body>
        </text>
    </TEI>
</teiCorpus>
```

## 🔬 Real-World Usage with Python

### Processing the Enhanced Output

```python
import xml.etree.ElementTree as ET
import requests

# Align TEI documents
response = requests.post('http://localhost:8000/align/tei', json={
    'source_tei': italian_tei_content,
    'target_tei': english_tei_content,
    'source_language': 'it',
    'target_language': 'en'
})

result = response.json()
aligned_xml = result['aligned_xml']

# Parse the enhanced TEI corpus
root = ET.fromstring(aligned_xml)

# Extract alignment information
standoff = root.find('.//{http://www.tei-c.org/ns/1.0}standOff')
links = standoff.findall('.//{http://www.tei-c.org/ns/1.0}link')

print(f"Found {len(links)} alignments")

# Analyze alignment types
paragraph_alignments = 0
sentence_alignments = 0

tei_documents = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
italian_doc = tei_documents[0]

for p in italian_doc.findall('.//{http://www.tei-c.org/ns/1.0}p'):
    # All alignments now use <seg> elements consistently
    seg_elements = p.findall('.//{http://www.tei-c.org/ns/1.0}seg')
    for seg in seg_elements:
        if seg.get('{http://www.w3.org/XML/1998/namespace}id'):
            sentence_alignments += 1
            print(f"Alignment: {seg.text[:50]}...")

print(f"Total alignments: {sentence_alignments}")
```

## 📊 Research Applications

### Digital Humanities Research

```python
# Extract aligned sentence pairs for corpus linguistics analysis
def extract_aligned_pairs(tei_corpus_xml):
    root = ET.fromstring(tei_corpus_xml)
    
    # Get standOff links
    links = root.findall('.//{http://www.tei-c.org/ns/1.0}link')
    
    # Get both TEI documents
    tei_docs = root.findall('.//{http://www.tei-c.org/ns/1.0}TEI')
    italian_doc = tei_docs[0]
    english_doc = tei_docs[1]
    
    aligned_pairs = []
    
    for link in links:
        target = link.get('target')
        source_id, target_id = target.split()[0][1:], target.split()[1][1:]
        
        # Find source text
        source_elem = italian_doc.find(f".//*[@xml:id='{source_id}']")
        target_elem = english_doc.find(f".//*[@xml:id='{target_id}']")
        
        if source_elem is not None and target_elem is not None:
            aligned_pairs.append({
                'italian': source_elem.text,
                'english': target_elem.text,
                'type': 'seg',  # All alignments now use <seg> tags consistently
                'source_id': source_id,
                'target_id': target_id
            })
    
    return aligned_pairs

# Usage
pairs = extract_aligned_pairs(aligned_xml)
for pair in pairs:
    print(f"ALIGNED: {pair['italian']} → {pair['english']}")
```

## 🛠️ Advanced Configuration

### Custom Alignment Parameters

```bash
curl -X POST "http://localhost:8000/align/tei" \
  -H "Content-Type: application/json" \
  -d '{
    "source_tei": "...",
    "target_tei": "...",
    "source_language": "it",
    "target_language": "en",
    "max_align": 3,
    "top_k": 5,
    "win": 10,
    "skip": -0.2,
    "margin": true,
    "len_penalty": true
  }'
```

### Performance Optimization

```python
# For large documents, consider chunking
def process_large_tei_document(large_tei_path, chunk_size=1000):
    # Implementation for processing large TEI documents in chunks
    # while maintaining alignment quality
    pass
```

## 🎯 Key Benefits

1. **Consistent Structure**: All alignments use `<seg>` tags for uniform processing regardless of granularity
2. **Complete Preservation**: All original TEI structure and metadata maintained
3. **Research-Ready**: Output suitable for computational linguistics and digital humanities
4. **TEI P5 Compliant**: Compatible with existing TEI processing tools
5. **Universal Coverage**: Headers and paragraphs processed identically for alignments

## 📝 Tips for Best Results

1. **Document Quality**: Ensure input TEI documents are well-formed and follow TEI guidelines
2. **Language Specification**: Always provide explicit source and target language codes
3. **Text Preprocessing**: The API automatically cleans extracted text by:
   - Removing line breaks and carriage returns
   - Normalizing multiple spaces and tabs to single spaces
   - Stripping leading/trailing whitespace
4. **Parameter Tuning**: Experiment with alignment parameters for domain-specific content
5. **Validation**: Always validate output XML structure before downstream processing

### Automatic Text Cleaning

The API automatically cleans text extracted from TEI documents to improve alignment quality:

```xml
<!-- Input TEI with formatting issues -->
<p>This paragraph
has line breaks    and     multiple spaces.</p>

<!-- Extracted and cleaned text sent to bertalign -->
"This paragraph has line breaks and multiple spaces."
```

**What gets cleaned:**
- `\n` and `\r\n` → single space
- Multiple spaces/tabs → single space  
- Leading/trailing whitespace → removed
- Original XML structure → preserved

For more examples and advanced usage patterns, see the `/tests/test_integration_seg.py` file in the repository.