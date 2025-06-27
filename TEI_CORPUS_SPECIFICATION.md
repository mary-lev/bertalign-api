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

The system intelligently handles both paragraph-level and sentence-level alignments:

**Paragraph-level alignment example:**
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

**Sentence-level alignment example (NEW):**
```xml
<TEI>
    <teiHeader>
        <!-- PRESERVE ALL original metadata -->
        <titleStmt>
            <title>Contributi alla teoria figurativa della forma</title>
            <author>P. Klee</author>
        </titleStmt>
    </teiHeader>
    <text>
        <body>
            <div xml:id="div_Klee_introduction">
                <pb/>
                <head type="main">A Lezioni del semestre invernale 1921-1922</head>
                <head type="subtype"><date>14 novembre 1921</date></head>
            
                <!-- Sentence-level alignments use <seg> tags within paragraphs -->
                <p>
                    <seg xml:id="sent-uuid-1">Come introduzione un breve chiarimento concettuale.</seg>
                    <seg xml:id="sent-uuid-2">In primo luogo ciò che è contenuto nel concetto di analisi.</seg>
                    <seg xml:id="sent-uuid-3">Nel linguaggio comune si sente per lo più parlare delle analisi dei chimici.</seg>
                </p>
            
                <!-- Mixed: some sentences aligned, others not -->
                <p>
                    <seg xml:id="sent-uuid-4">Un certo preparato, per esempio, ha grande smercio.</seg>
                    I buoni affari del produttore incuriosiscono gli altri produttori.
                    <seg xml:id="sent-uuid-5">Il chimico deve procedere metodicamente.</seg>
                </p>
            
                <pb/>
            </div>
        </body>
    </text>
    <facsimile/>
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
- **MUST** generate UUID `xml:id` for aligned elements (paragraphs or sentences)
- **MUST** create `<link>` elements with proper target references
- **MUST** use `type="Linguistic"` for alignment links
- **ENHANCED** Support both paragraph-level and sentence-level alignments
- **ENHANCED** Use `<seg>` tags for sentence-level alignments within paragraphs

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

## Enhanced Alignment Behavior (NEW)

### Intelligent Alignment Detection

The Bertalign API now automatically determines the optimal alignment granularity:

1. **Paragraph-level Alignment**: When bertalign aligns entire paragraphs, the `xml:id` is assigned directly to the `<p>` element

2. **Sentence-level Alignment**: When bertalign creates alignments for individual sentences within paragraphs, the system:
   - Preserves the original paragraph structure
   - Wraps aligned sentences in `<seg xml:id="uuid">` elements
   - Leaves unaligned sentences as plain text within the paragraph
   - Maintains text flow and readability

### StandOff Link Examples

**Paragraph-level links:**
```xml
<link target="#para-uuid-it #para-uuid-en" type="Linguistic" />
```

**Sentence-level links:**
```xml
<link target="#sent-uuid-it-1 #sent-uuid-en-1" type="Linguistic" />
<link target="#sent-uuid-it-2 #sent-uuid-en-2" type="Linguistic" />
<link target="#sent-uuid-it-3 #sent-uuid-en-3" type="Linguistic" />
```

### Benefits for Researchers

- **Fine-grained Analysis**: Access sentence-level correspondences for detailed linguistic analysis
- **Preservation of Context**: Original paragraph structure maintains discourse coherence
- **Flexible Granularity**: Automatic selection of appropriate alignment level
- **TEI Compliance**: Full compatibility with existing TEI processing tools
- **Mixed Alignments**: Support for documents with both paragraph and sentence-level alignments

This specification ensures the Bertalign API produces authentic, standards-compliant digital humanities resources with enhanced granular alignment capabilities.

## Known Issues and Future Improvements

### Issue: Many-to-Many Alignment linkGrp Structure

**Problem Description:**
Currently, the system has a limitation with many-to-many alignments where multiple source segments align to multiple target segments. The current implementation assigns the same UUID to all segments that are part of the same alignment pair, but TEI standOff specification requires more sophisticated linkGrp structure.

**Current Behavior:**
```xml
<!-- Italian headers (both get same UUID since they're from same alignment) -->
<head><seg xml:id="6ab1bd5a-973e-4b36-9300-15ab6e578c39">A Lezioni del semestre invernale 1921-1922</seg></head>
<head><seg xml:id="6ab1bd5a-973e-4b36-9300-15ab6e578c39">14 novembre 1921</seg></head>

<!-- English header (gets different UUID for target) -->
<head><seg xml:id="1735b949-c0bf-4998-81fe-2f5db918ca5e">A. Winter semester lectures 1921-1922 Nov. 14, 1921</seg></head>

<!-- StandOff link (simple 1:1 linking) -->
<link target="#6ab1bd5a-973e-4b36-9300-15ab6e578c39 #1735b949-c0bf-4998-81fe-2f5db918ca5e" type="Linguistic"/>
```

**Required Behavior for Proper Many-to-Many Support:**
```xml
<!-- Each segment should have unique UUID -->
<head><seg xml:id="it-header-1">A Lezioni del semestre invernale 1921-1922</seg></head>
<head><seg xml:id="it-header-2">14 novembre 1921</seg></head>
<head><seg xml:id="en-header-1">A. Winter semester lectures 1921-1922 Nov. 14, 1921</seg></head>

<!-- StandOff link should reference all related segments -->
<link target="#it-header-1 #it-header-2 #en-header-1" type="Linguistic"/>
```

**Technical Requirements for Fix:**
1. **Unique IDs per Segment**: Each `<seg>` element must have its own unique `xml:id`
2. **Complex Link Targets**: The `target` attribute in `<link>` elements must list all segment IDs that participate in the many-to-many alignment
3. **Alignment Grouping**: Need to track which segments belong to the same semantic alignment unit
4. **TEI Compliance**: Ensure the multi-target linking follows TEI P5 guidelines for standOff annotation

**Implementation Priority:**
- **Medium Priority**: Current system works for most use cases but could be enhanced for complex alignments
- **Research Impact**: Proper many-to-many linking would enable more sophisticated corpus linguistic analysis
- **TEI Compliance**: Would make output fully compliant with TEI P5 standOff specifications

**Location to Implement:**
- `app/services/tei_service.py` → `_create_enhanced_alignment_map()` method
- `app/services/tei_service.py` → `_generate_aligned_tei()` method for link generation
- Need to modify UUID assignment strategy and link target generation logic

This enhancement would provide complete TEI P5 compliance for complex alignment scenarios while maintaining backward compatibility with simpler alignments.
