from typing import List, Set, Tuple
from app.schemas.assistant import GroundedResponse, Claim, Citation
from app.schemas.source import RetrievalResult

class CitationValidator:
    @staticmethod
    def validate_response(
        candidate_response: GroundedResponse,
        retrieved_chunks: List[RetrievalResult],
        min_evidence_score: float = 0.50
    ) -> GroundedResponse:
        """
        Validates generated claims against retrieved source chunks.
        
        Rules:
        - Every claim must reference at least one valid retrieved chunk_id.
        - Chunk IDs must exist in retrieved_chunks.
        - If claims lack valid chunk citations or no relevant chunks exist, return explicit insufficient-evidence state.
        """
        retrieved_chunk_ids: Set[str] = {c.chunk_id for c in retrieved_chunks}
        chunk_map = {c.chunk_id: c for c in retrieved_chunks}

        if not retrieved_chunks:
            return GroundedResponse(
                answer="Insufficient authoritative evidence available in the verified knowledge base to answer this query safely.",
                claims=[],
                jurisdiction=candidate_response.jurisdiction,
                confidence="insufficient_evidence",
                needs_review=True,
                citations=[],
                demo_mode=candidate_response.demo_mode
            )

        validated_claims: List[Claim] = []
        valid_citations_map = {}

        for claim in candidate_response.claims:
            # Filter chunk IDs to only those actually retrieved
            valid_chunks_for_claim = [cid for cid in claim.source_chunks if cid in retrieved_chunk_ids]
            
            if valid_chunks_for_claim:
                validated_claims.append(Claim(
                    text=claim.text,
                    source_chunks=valid_chunks_for_claim
                ))
                for cid in valid_chunks_for_claim:
                    chunk = chunk_map[cid]
                    if cid not in valid_citations_map:
                        valid_citations_map[cid] = Citation(
                            chunk_id=chunk.chunk_id,
                            document_title=chunk.title,
                            authority=chunk.authority,
                            jurisdiction=chunk.jurisdiction,
                            section=chunk.section,
                            page=1, # Default page if omitted
                            version_date=chunk.version_date,
                            official_source_url=chunk.source_url,
                            verification_status=chunk.verification_status
                        )


        # Check if any citation relies on unverified demo content
        has_unverified_demo = any(c.verification_status == "unverified_demo" for c in valid_citations_map.values())
        needs_review = candidate_response.needs_review or has_unverified_demo


        # If no valid claims with chunk citations survived validation
        if not validated_claims and candidate_response.confidence != "abstain":
            return GroundedResponse(
                answer="Insufficient authoritative evidence available in the verified knowledge base to support legal conclusions for this query.",
                claims=[],
                jurisdiction=candidate_response.jurisdiction,
                confidence="insufficient_evidence",
                needs_review=True,
                citations=[],
                demo_mode=candidate_response.demo_mode
            )

        return GroundedResponse(
            answer=candidate_response.answer,
            claims=validated_claims,
            jurisdiction=candidate_response.jurisdiction,
            confidence="evidence_supported",
            needs_review=needs_review,
            citations=list(valid_citations_map.values()),
            demo_mode=candidate_response.demo_mode
        )

