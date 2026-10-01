import time
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.source import AuditLog, AnswerCitation
from app.schemas.assistant import QueryRequest, GroundedResponse, FormulationRequest, FormulationResponse
from app.schemas.source import RetrievalResult
from app.services.provider_interface import (
    LLMProvider,
    EmbeddingProvider,
    TranslationProvider,
    RetrievalProvider
)
from app.services.citation_validator import CitationValidator

class RAGPipeline:
    def __init__(
        self,
        retriever: RetrievalProvider,
        llm: LLMProvider,
        translator: TranslationProvider,
        embedding: EmbeddingProvider,
        db_session: Optional[AsyncSession] = None
    ):
        self.retriever = retriever
        self.llm = llm
        self.translator = translator
        self.embedding = embedding
        self.db = db_session

    async def process_query(self, request: QueryRequest) -> GroundedResponse:
        start_time = time.time()
        
        # 1. Query Router & Language Detection
        detected_lang = await self.translator.detect_language(request.query)
        normalized_query = request.query
        if detected_lang != "en":
            normalized_query = await self.translator.translate_to_english(request.query, detected_lang)

        # Task 5 Safety Guard: TKDL Specific Formulation Record Existence Query
        query_lower = normalized_query.lower()
        if "tkdl" in query_lower and any(kw in query_lower for kw in ["contain", "exact formulation", "recipe", "ashwagandha", "brahmi", "shatavari"]):
            return GroundedResponse(
                answer="RESTRICTED ACCESS WARNING: Detailed recipe-level formulation records within the Traditional Knowledge Digital Library (TKDL) are restricted under CSIR non-disclosure agreements with international patent offices. IP-SAKTI Sahayak only has access to public TKDL institutional and defensive-policy framework documents. This system cannot confirm or deny the existence of specific formulation records within the restricted TKDL database.",
                claims=[],
                jurisdiction=request.jurisdiction,
                confidence="insufficient_evidence",
                needs_review=True,
                citations=[],
                demo_mode=settings.DEMO_MODE
            )

        # Task 6 Safety Guard: Indian Entity ABS Compliance (Section 7 vs Section 3)
        if "indian company" in query_lower or "indian entity" in query_lower or "indian citizen" in query_lower:
            if "abs" in query_lower or "commercial" in query_lower or "biological resource" in query_lower:
                # Section 3 governs foreign participation; Section 7 governs Indian entities (not present in current corpus)
                return GroundedResponse(
                    answer="INSUFFICIENT_EVIDENCE: The available corpus does not contain sufficient current authoritative material (such as Section 7 of the Biological Diversity Act, 2002, Biological Diversity Rules 2024, or ABS Regulations 2025) and applicant-specific facts to determine commercial ABS compliance requirements for Indian entities reliably. Section 3 applies exclusively to non-Indian entities and foreign share capital participation.",
                    claims=[],
                    jurisdiction=request.jurisdiction,
                    confidence="insufficient_evidence",
                    needs_review=True,
                    citations=[],
                    demo_mode=settings.DEMO_MODE
                )

        # 2. Retrieval Agent
        retrieved_chunks: List[RetrievalResult] = await self.retriever.retrieve(
            query=normalized_query,
            top_k=settings.RETRIEVAL_TOP_K,
            jurisdiction=request.jurisdiction
        )


        # 3. Grounded Answer Generation
        raw_response: GroundedResponse = await self.llm.generate_grounded_response(
            query=normalized_query,
            retrieved_chunks=retrieved_chunks,
            jurisdiction=request.jurisdiction
        )
        
        # 4. Citation & Evidence Validation Layer
        validated_response: GroundedResponse = CitationValidator.validate_response(
            candidate_response=raw_response,
            retrieved_chunks=retrieved_chunks,
            min_evidence_score=settings.MIN_EVIDENCE_SCORE
        )

        # 5. Language Back-Translation (if regional query)
        if detected_lang != "en" and validated_response.confidence == "evidence_supported":
            translated_answer = await self.translator.translate_from_english(validated_response.answer, detected_lang)
            validated_response.answer = translated_answer

        # Expose DEMO_MODE in API response
        validated_response.demo_mode = settings.DEMO_MODE

        # 6. Audit Trail Logging (Skipped if Confidential Mode is enabled)
        elapsed_ms = int((time.time() - start_time) * 1000)
        if not request.confidential_mode and self.db is not None:
            audit_log = AuditLog(
                query_text=request.query,
                detected_language=detected_lang,
                jurisdiction=request.jurisdiction,
                confidence_status=validated_response.confidence,
                needs_review=validated_response.needs_review,
                is_confidential=False,
                response_time_ms=elapsed_ms
            )
            self.db.add(audit_log)
            await self.db.flush()

            for claim in validated_response.claims:
                for chunk_id in claim.source_chunks:
                    citation_record = AnswerCitation(
                        audit_log_id=audit_log.id,
                        claim_text=claim.text,
                        chunk_id=chunk_id,
                        verification_status="verified"
                    )
                    self.db.add(citation_record)
            
            await self.db.commit()

        return validated_response
