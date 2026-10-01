import hashlib

from typing import List, Optional
from app.schemas.source import RetrievalResult
from app.schemas.assistant import GroundedResponse, Claim, Citation
from app.services.provider_interface import (
    EmbeddingProvider,
    LLMProvider,
    TranslationProvider
)

class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    async def embed_text(self, text: str) -> List[float]:
        # Generate deterministic float vector from md5 hash
        hasher = hashlib.md5(text.encode('utf-8')).hexdigest()
        vector = []
        for i in range(self.dimension):
            val = int(hasher[i % len(hasher)], 16) / 15.0
            vector.append(round(val, 4))
        return vector

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(t) for t in texts]


class MockTranslationProvider(TranslationProvider):
    async def detect_language(self, text: str) -> str:
        # Basic Devanagari detection for Hindi
        if any('\u0900' <= char <= '\u097F' for char in text):
            return "hi"
        return "en"

    async def translate_to_english(self, text: str, source_language: str) -> str:
        if source_language == "hi":
            # Normalization mock mapping for common Ayurvedic query terms
            return f"[Translated from Hindi]: {text}"
        return text

    async def translate_from_english(self, text: str, target_language: str) -> str:
        if target_language == "hi":
            return f"[Translated to Hindi]: {text}"
        return text


class MockLLMProvider(LLMProvider):
    async def generate_grounded_response(
        self,
        query: str,
        retrieved_chunks: List[RetrievalResult],
        jurisdiction: str = "India"
    ) -> GroundedResponse:
        if not retrieved_chunks:
            return GroundedResponse(
                answer="Insufficient authoritative evidence available in the verified knowledge base to answer this query.",
                claims=[],
                jurisdiction=jurisdiction,
                confidence="insufficient_evidence",
                needs_review=True,
                citations=[]
            )

        chunk_ids = [c.chunk_id for c in retrieved_chunks]
        chunk_map = {c.chunk_id: c for c in retrieved_chunks}

        query_lower = query.lower()
        is_formulation_patent_query = any(k in query_lower for k in ["patent", "patentable"]) and any(k in query_lower for k in ["ayurvedic", "formulation", "ashwagandha", "brahmi"])

        claims = []
        citations = []

        if is_formulation_patent_query:
            sec3p_id = next((cid for cid in chunk_ids if "SEC03P" in cid), chunk_ids[0])
            sec3e_id = next((cid for cid in chunk_ids if "SEC03E" in cid), None)
            sec104_id = next((cid for cid in chunk_ids if "SEC104" in cid), None)
            tkdl_id = next((cid for cid in chunk_ids if "TKDL" in cid), None)
            bda_id = next((cid for cid in chunk_ids if "SEC06" in cid or "BDA" in cid), None)

            # Claim 1: Preliminary & Section 3(p) IP Considerations
            claims.append(Claim(
                text="Patentability cannot be determined from botanical ingredients alone. Under Section 3(p) of the Patents Act, 1970, inventions that are in effect traditional knowledge or an aggregation of known properties of traditionally known components are excluded from patentability. However, Section 3(p) does not automatically disqualify all Ayurvedic formulations—novel, non-obvious synergistic extracts or specialized processing methods may be evaluated subject to prior art scrutiny.",
                source_chunks=[sec3p_id]
            ))

            # Claim 2: Traditional Knowledge & TKDL Scope
            tk_chunks = [tkdl_id] if tkdl_id else [sec3p_id]
            claims.append(Claim(
                text="The Traditional Knowledge Digital Library (TKDL) provides defensive institutional protection against biopiracy. This platform searches public TKDL policy frameworks only and does NOT search detailed, restricted formulation records; therefore, specific presence of formulation recipes in the restricted repository cannot be verified here.",
                source_chunks=tk_chunks
            ))

            # Claim 3: Section 3(e) & Section 10(4)
            add_chunks = [cid for cid in [sec3e_id, sec104_id] if cid]
            if not add_chunks:
                add_chunks = [sec3p_id]
            claims.append(Claim(
                text="Section 3(e) excludes mere admixtures resulting only in the aggregation of component properties, while Section 10(4) mandates explicit disclosure of biological resource geographical origin in patent specifications.",
                source_chunks=add_chunks
            ))

            # Claim 4: NBA ABS Compliance if BDA chunk retrieved
            if bda_id:
                claims.append(Claim(
                    text="Under Section 6 of the Biological Diversity Act, 2002, prior approval from the National Biodiversity Authority (NBA) is mandatory before applying for intellectual property rights based on Indian bio-resources.",
                    source_chunks=[bda_id]
                ))

            # Structured answer output
            synthesis = (
                "1. Preliminary Assessment:\n"
                "Patentability cannot be determined from botanical ingredients alone. The following statutory provisions govern patent eligibility and regulatory compliance.\n\n"
                "2. Relevant IP Considerations:\n"
                "Under Section 3(p) of the Patents Act, 1970, inventions that are in effect traditional knowledge or an aggregation of known properties of traditionally known components are excluded. Section 3(p) does not automatically disqualify all Ayurvedic formulations—novel, non-obvious synergistic extracts or specialized processing methods may be evaluated subject to prior art scrutiny.\n\n"
                "3. Traditional Knowledge & TKDL Scope:\n"
                "The Traditional Knowledge Digital Library (TKDL) provides defensive institutional protection against biopiracy. This platform searches public TKDL policy frameworks only and does NOT search detailed, restricted formulation records.\n\n"
                "4. Statutory Disclosure & ABS Compliance:\n"
                "Section 3(e) excludes mere admixtures, while Section 10(4) requires explicit disclosure of biological resource origin. Additionally, Section 6 of the Biological Diversity Act, 2002 mandates National Biodiversity Authority (NBA) approval prior to IP filing.\n\n"
                "5. Missing Information Needed for Legal Clearance:\n"
                "• Exact quantitative ratio and extraction solvent details\n"
                "• Synergistic efficacy data distinguishing formulation from prior art\n"
                "• Specific claimed scope (process vs. product extract)\n\n"
                "6. Practical Next Steps:\n"
                "• Conduct a formal TKDL prior-art evaluation with patent counsel.\n"
                "• Submit Form I application to National Biodiversity Authority (NBA) prior to commercial release."
            )
        else:
            for chunk in retrieved_chunks:
                claim_text = f"According to {chunk.title} ({chunk.section}), {chunk.content[:150]}..."
                claims.append(Claim(
                    text=claim_text,
                    source_chunks=[chunk.chunk_id]
                ))
            synthesis = f"Based on verified authoritative sources for {jurisdiction}: " + " ".join([c.text for c in claims[:2]])

        used_chunk_ids = set()
        for clm in claims:
            for cid in clm.source_chunks:
                used_chunk_ids.add(cid)

        for cid in used_chunk_ids:
            chunk = chunk_map[cid]
            citations.append(Citation(
                chunk_id=chunk.chunk_id,
                document_title=chunk.title,
                authority=chunk.authority,
                jurisdiction=chunk.jurisdiction,
                version_date=chunk.version_date,
                official_source_url=chunk.source_url,
                verification_status=chunk.verification_status
            ))

        return GroundedResponse(
            answer=synthesis,
            claims=claims,
            jurisdiction=jurisdiction,
            confidence="evidence_supported",
            needs_review=False,
            citations=citations
        )
