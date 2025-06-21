#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/maria/projects/bertalign/bertalign-api')

from bertalign.aligner import Bertalign

# Test the alignment format with simple texts
source_text = "Hello world. This is a test. How are you?"
target_text = "Hola mundo. Esta es una prueba. ¿Cómo estás?"

print("Creating Bertalign instance...")
aligner = Bertalign(
    src=source_text,
    tgt=target_text,
    src_lang='en',
    tgt_lang='es',
    max_align=5,
    top_k=3,
    win=5,
    skip=-0.1,
    margin=True,
    len_penalty=True,
    is_split=False
)

print("\nPerforming alignment...")
aligner.align_sents()

print("\n=== ALIGNMENT RESULTS ===")
print("Result type:", type(aligner.result))
print("Result length:", len(aligner.result) if hasattr(aligner, 'result') else 'No result')

if hasattr(aligner, 'result'):
    print("\nAlignment format:")
    for i, bead in enumerate(aligner.result):
        print(f"Bead {i}: {bead}")
        print(f"  Type: {type(bead)}")
        if len(bead) >= 2:
            print(f"  Source indices: {bead[0]} (type: {type(bead[0])})")
            print(f"  Target indices: {bead[1]} (type: {type(bead[1])})")

print("\n=== SOURCE SENTENCES ===")
for i, sent in enumerate(aligner.src_sents):
    print(f"{i}: {sent}")

print("\n=== TARGET SENTENCES ===")
for i, sent in enumerate(aligner.tgt_sents):
    print(f"{i}: {sent}")

print("\n=== PRINT_SENTS OUTPUT ===")
aligner.print_sents()

print("\n=== MANUAL EXTRACTION ===")
if hasattr(aligner, 'result'):
    for i, bead in enumerate(aligner.result):
        src_indices = bead[0]
        tgt_indices = bead[1]
        
        # Get source text
        if len(src_indices) > 0:
            src_text = ' '.join(aligner.src_sents[src_indices[0]:src_indices[-1]+1])
        else:
            src_text = ""
            
        # Get target text
        if len(tgt_indices) > 0:
            tgt_text = ' '.join(aligner.tgt_sents[tgt_indices[0]:tgt_indices[-1]+1])
        else:
            tgt_text = ""
            
        print(f"Alignment {i}:")
        print(f"  Source: {src_text}")
        print(f"  Target: {tgt_text}")
        print()