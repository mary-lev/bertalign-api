import time
import logging
from bertalign.aligner import Bertalign
from app.models import AlignmentRequest, AlignmentResponse, AlignmentPair

logger = logging.getLogger(__name__)


class BertalignService:
    @staticmethod
    def align_texts(request: AlignmentRequest) -> AlignmentResponse:
        start_time = time.time()
        
        try:
            logger.info(f"Initializing Bertalign for {request.source_language} -> {request.target_language}")
            # Create Bertalign instance - model already loaded globally
            aligner = Bertalign(
                src=request.source_text,
                tgt=request.target_text,
                src_lang=request.source_language,
                tgt_lang=request.target_language,
                max_align=request.max_align,
                top_k=request.top_k,
                win=request.win,
                skip=request.skip,
                margin=request.margin,
                len_penalty=request.len_penalty,
                is_split=request.is_split
            )
            logger.info(f"Source: {aligner.src_lang_name} ({aligner.src_num} sentences), Target: {aligner.tgt_lang_name} ({aligner.tgt_num} sentences)")
        except KeyError as e:
            raise ValueError(f"Unsupported language: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Bertalign: {e}")
        
        # Perform alignment
        try:
            logger.info("Starting alignment process...")
            aligner.align_sents()
            logger.info(f"Alignment completed: {len(aligner.result)} alignment pairs found")
        except Exception as e:
            raise RuntimeError(f"Alignment failed: {e}")
        
        # Extract alignment results
        alignments = []
        for src_indices, tgt_indices in aligner.result:
            # Get sentence texts using Bertalign's helper method
            src_sentences = []
            if src_indices:
                src_text = aligner._get_line(src_indices, aligner.src_sents)
                src_sentences = [aligner.src_sents[i] for i in src_indices]
            
            tgt_sentences = []
            if tgt_indices:
                tgt_text = aligner._get_line(tgt_indices, aligner.tgt_sents)
                tgt_sentences = [aligner.tgt_sents[i] for i in tgt_indices]
            
            alignments.append(AlignmentPair(
                source_sentences=src_sentences,
                target_sentences=tgt_sentences,
                source_indices=list(src_indices),
                target_indices=list(tgt_indices),
                alignment_score=0.0  # Bertalign doesn't expose individual scores
            ))
        
        processing_time = time.time() - start_time
        
        return AlignmentResponse(
            alignments=alignments,
            source_language=aligner.src_lang_name,
            target_language=aligner.tgt_lang_name,
            processing_time=processing_time,
            total_source_sentences=aligner.src_num,
            total_target_sentences=aligner.tgt_num,
            parameters=request
        )