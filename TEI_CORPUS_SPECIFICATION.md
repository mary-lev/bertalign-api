# TEI Corpus Output Specification

## Overview

The Bertalign API should produce **TEI-compliant parallel corpora** following TEI P5 guidelines for corpus encoding and standOff annotation.

### Target Implementation Requirements

#### 1. Root Structure: `<teiCorpus>`

```xml
<teiCorpus version="3.3.0" xmlns="http://www.tei-c.org/ns/1.0">
    <!-- Corpus header -->
    <!-- StandOff annotations -->
    <!-- Complete source TEI -->
    <!-- Complete target TEI -->
</teiCorpus>
```

#### 2. Corpus-Level Header

```xml
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
```

#### 3. StandOff Alignment Annotations

```xml
<standOff>
    <linkGrp type="translation">
        <link target="#uuid-source-para #uuid-target-para" type="Linguistic"/>
        <!-- One link per alignment pair -->
    </linkGrp>
</standOff>
```

#### 4. Complete Source Document Preservation

```xml
<TEI>
    <teiHeader>
        <!-- PRESERVE ALL original metadata -->
        <titleStmt>
            <title>Contributi alla teoria figurativa della forma</title>
            <author>P. Klee</author>
        </titleStmt>
        <!-- ALL original publication info, responsibilities, etc. -->
    </teiHeader>
    <text>
        <body>
            <div xml:id="div_Klee_introduction"> <!-- PRESERVE original structure -->
                <pb/> <!-- PRESERVE page breaks -->
                <head type="main">A Lezioni del semestre invernale 1921-1922</head>
                <head type="subtype"><date>14 novembre 1921</date></head>
            
                <!-- Add xml:id ONLY for aligned paragraphs -->
                <p xml:id="72f38fc9-2c66-4e03-ac44-b1fdc25617a2">
                    Come introduzione un breve chiarimento concettuale...
                </p>
            
                <!-- Unaligned paragraphs remain unchanged -->
                <p>
                    In un altro caso un alimento ha conseguenze dannose...
                </p>
            
                <pb/> <!-- PRESERVE all original elements -->
            </div>
        </body>
    </text>
    <facsimile/> <!-- PRESERVE all original elements -->
</TEI>
```

#### 5. Complete Target Document Preservation

- Same principles as source document
- Complete original structure maintained
- Only aligned paragraphs get `xml:id` attributes
- All original metadata and structure preserved

## Implementation Requirements

### 1. Structure Preservation

- **MUST** maintain complete original TEI hierarchy
- **MUST** preserve all `<div>`, `<pb>`, `<head>` elements and their attributes
- **MUST** maintain original `xml:id` attributes from source documents
- **MUST** preserve element ordering and nesting

### 2. Metadata Preservation

- **MUST** preserve complete original `<teiHeader>` for both documents
- **MUST** maintain all author, title, publication information
- **MUST** preserve bibliographic data and source descriptions
- **MUST** maintain all responsibility statements and credits

### 3. Alignment Annotation

- **MUST** use TEI P5 compliant standOff structure
- **MUST** generate UUID `xml:id` only for aligned paragraphs
- **MUST** create `<link>` elements with proper target references
- **MUST** use `type="Linguistic"` for alignment links

### 4. TEI P5 Compliance

- **MUST** use `<teiCorpus>` as root element with proper versioning
- **MUST** handle namespaces correctly for multiple documents
- **MUST** follow TEI guidelines for parallel corpus structure
- **MUST** ensure valid TEI XML output

## Benefits of Correct Implementation

1. **Digital Humanities Standards**: Creates research-grade parallel corpora
2. **Tool Compatibility**: Works with existing TEI processing tools
3. **Scholarly Value**: Preserves complete bibliographic information
4. **Research Applications**: Suitable for corpus linguistics and critical editions
5. **Long-term Preservation**: Follows established digital humanities standards

## Technical Implementation Notes

### Current Service Method to Update

- `app/services/tei_service.py` → `_generate_aligned_tei()`
- Replace current simple structure generation
- Implement proper `<teiCorpus>` creation with preserved documents

### Key Changes Required

1. Create `<teiCorpus>` root with corpus header
2. Add standOff section with alignment links
3. Include complete original source TEI document
4. Include complete original target TEI document
5. Add `xml:id` attributes only to aligned paragraphs
6. Preserve all original structure and metadata

This specification ensures the Bertalign API produces authentic, standards-compliant digital humanities resources.
