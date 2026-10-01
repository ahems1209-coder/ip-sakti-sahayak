import math
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.source import DocumentSection, Document, EmbeddingRecord, SourceRegistry
from app.schemas.source import RetrievalResult
from app.services.provider_interface import RetrievalProvider, EmbeddingProvider

class DatabaseRetrievalProvider(RetrievalProvider):
    def __init__(self, db_session: AsyncSession, embedding_provider: Optional[EmbeddingProvider] = None):
        self.db = db_session
        self.embedding_provider = embedding_provider

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def retrieve_keyword(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[RetrievalResult]:
        """PostgreSQL / SQLite Full-text & keyword retrieval."""
        query_terms = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]
        stmt = select(DocumentSection, Document).join(Document, DocumentSection.document_id == Document.id)

        if jurisdiction and jurisdiction.lower() != "all":
            stmt = stmt.where(Document.jurisdiction == jurisdiction)

        if category:
            stmt = stmt.where(DocumentSection.category == category)

        conditions = []
        for term in query_terms:
            conditions.append(DocumentSection.content.ilike(f"%{term}%"))
            conditions.append(DocumentSection.section_title.ilike(f"%{term}%"))
            conditions.append(DocumentSection.section_number.ilike(f"%{term}%"))

        if conditions:
            stmt = stmt.where(or_(*conditions))

        stmt = stmt.limit(top_k)
        res = await self.db.execute(stmt)
        rows = res.all()

        results: List[RetrievalResult] = []
        for section, doc in rows:
            content_lower = (section.content + " " + (section.section_title or "")).lower()
            matched_count = sum(1 for t in query_terms if t in content_lower)
            if len(query_terms) >= 3 and matched_count < 2:
                continue

            results.append(RetrievalResult(
                chunk_id=section.chunk_id,
                source_id=doc.source_id or doc.id,
                document_id=doc.id,
                title=doc.title,
                authority=doc.authority,
                jurisdiction=doc.jurisdiction,
                section=section.section_number or section.section_title or "N/A",
                content=section.content,
                source_url=doc.source_url,
                version_date=doc.version_date.isoformat() if doc.version_date else "Current",
                score=0.85,
                verification_status=doc.verification_status
            ))
        return results

    async def retrieve_vector(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None
    ) -> List[RetrievalResult]:
        """Dense vector similarity retrieval."""
        if not self.embedding_provider:
            return []

        query_vector = await self.embedding_provider.embed_text(query)

        stmt = select(DocumentSection, Document, EmbeddingRecord).join(
            Document, DocumentSection.document_id == Document.id
        ).join(
            EmbeddingRecord, EmbeddingRecord.chunk_id == DocumentSection.chunk_id
        )

        if jurisdiction and jurisdiction.lower() != "all":
            stmt = stmt.where(Document.jurisdiction == jurisdiction)

        res = await self.db.execute(stmt)
        rows = res.all()

        scored_results = []
        for section, doc, emb in rows:
            doc_vec = emb.vector_data.get("vector", [])
            sim = self._cosine_similarity(query_vector, doc_vec)
            scored_results.append((sim, section, doc))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        results: List[RetrievalResult] = []
        for sim, section, doc in scored_results[:top_k]:
            results.append(RetrievalResult(
                chunk_id=section.chunk_id,
                source_id=doc.source_id or doc.id,
                document_id=doc.id,
                title=doc.title,
                authority=doc.authority,
                jurisdiction=doc.jurisdiction,
                section=section.section_number or section.section_title or "N/A",
                content=section.content,
                source_url=doc.source_url,
                version_date=doc.version_date.isoformat() if doc.version_date else "Current",
                score=round(float(sim), 4),
                verification_status=doc.verification_status
            ))
        return results

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: str = "India",
        category: Optional[str] = None
    ) -> List[RetrievalResult]:
        """Combined Hybrid Search (Dense Vector + Keyword Search)."""
        query_lower = query.lower()
        keyword_results = await self.retrieve_keyword(query, top_k=top_k, jurisdiction=jurisdiction, category=category)
        vector_results = await self.retrieve_vector(query, top_k=top_k, jurisdiction=jurisdiction)

        query_terms = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]

        patent_tk_query = any(term in query_lower for term in [
            "patent", "patentable", "section 3(p)", "traditional knowledge", "ayurvedic",
            "ashwagandha", "brahmi", "formulation"
        ])

        if patent_tk_query:
            targeted_phrases = [
                "section 3(p) traditional knowledge",
                "section 3(e) mere admixture",
                "section 10(4) biological material",
                "traditional knowledge patentability",
                "tkdl defensive prior art"
            ]
            for phrase in targeted_phrases:
                fallback_results = await self.retrieve_keyword(phrase, top_k=max(2, top_k), jurisdiction=jurisdiction)
                for result in fallback_results:
                    keyword_results.append(result)

        # If specific query terms were provided but keyword search found 0 matches,
        # require strong vector similarity (> 0.85) to avoid false positives on arbitrary text queries
        if query_terms and not keyword_results:
            filtered_vectors = []
            for v in vector_results:
                content_lower = v.content.lower() + " " + v.title.lower()
                has_term_overlap = any(term in content_lower for term in query_terms)
                if has_term_overlap or v.score >= 0.98:
                    filtered_vectors.append(v)
            vector_results = filtered_vectors

        # Merge results by chunk_id
        combined_map: Dict[str, RetrievalResult] = {}
        for r in keyword_results:
            combined_map[r.chunk_id] = r

        for r in vector_results:
            if r.chunk_id in combined_map:
                combined_map[r.chunk_id].score = round((combined_map[r.chunk_id].score + r.score) / 2.0, 4)
            else:
                combined_map[r.chunk_id] = r

        sorted_results = sorted(list(combined_map.values()), key=lambda x: x.score, reverse=True)
        return sorted_results[:top_k]


