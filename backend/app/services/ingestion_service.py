import os
import json
import hashlib
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import SourceRegistry, Document, DocumentSection, EmbeddingRecord
from app.services.provider_interface import EmbeddingProvider

class DocumentIngestionService:
    def __init__(self, db_session: AsyncSession, embedding_provider: EmbeddingProvider):
        self.db = db_session
        self.embedding_provider = embedding_provider

    @staticmethod
    def calculate_hash(content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def ingest_document_structure(self, doc_payload: Dict[str, Any]) -> Document:
        """
        Ingests a verified structured document payload into database tables.
        Payload format:
        {
          "source_registry": {"id": "...", "name": "...", "authority_type": "...", "official_url": "..."},
          "document": {
            "id": "DOC-IND-PAT-1970",
            "title": "The Patents Act, 1970",
            "authority": "Indian Patent Office",
            "jurisdiction": "India",
            "document_type": "Act",
            "version_date": "2005-01-01",
            "source_url": "https://ipindia.gov.in/patents-act-1970.htm"
          },
          "sections": [
            {
              "chunk_id": "IND-PAT-1970-SEC03P-C01",
              "section_number": "Section 3(p)",
              "section_title": "Inventions Not Patentable - Traditional Knowledge",
              "content": "...",
              "page_number": 14,
              "category": "Patents"
            }
          ]
        }
        """
        # 1. Source Registry
        source_data = doc_payload.get("source_registry")
        if source_data:
            stmt = select(SourceRegistry).where(SourceRegistry.id == source_data["id"])
            existing_source = (await self.db.execute(stmt)).scalar_one_or_none()
            if not existing_source:
                source_reg = SourceRegistry(
                    id=source_data["id"],
                    name=source_data["name"],
                    authority_type=source_data["authority_type"],
                    jurisdiction=source_data.get("jurisdiction", "India"),
                    official_url=source_data["official_url"],
                    source_origin=source_data.get("official_url"),
                    trust_score=source_data.get("trust_score", 1.0)
                )

                self.db.add(source_reg)
                await self.db.flush()

        # 2. Document
        doc_data = doc_payload["document"]
        doc_content_str = json.dumps(doc_payload["sections"])
        content_hash = self.calculate_hash(doc_content_str)

        version_dt = date.fromisoformat(doc_data["version_date"]) if doc_data.get("version_date") else None
        
        stmt = select(Document).where(Document.id == doc_data["id"])
        document = (await self.db.execute(stmt)).scalar_one_or_none()
        
        if not document:
            document = Document(
                id=doc_data["id"],
                source_id=source_data.get("id") if source_data else None,
                title=doc_data["title"],
                authority=doc_data["authority"],
                jurisdiction=doc_data.get("jurisdiction", "India"),
                document_type=doc_data["document_type"],
                version_date=version_dt,
                source_url=doc_data["source_url"],
                content_hash=content_hash,
                verification_status=doc_data.get("verification_status", "unverified_demo")
            )

            self.db.add(document)
            await self.db.flush()

        # 3. Document Sections & Embeddings
        for sec_data in doc_payload.get("sections", []):
            stmt = select(DocumentSection).where(DocumentSection.chunk_id == sec_data["chunk_id"])
            existing_sec = (await self.db.execute(stmt)).scalar_one_or_none()
            
            if not existing_sec:
                section = DocumentSection(
                    chunk_id=sec_data["chunk_id"],
                    document_id=document.id,
                    section_number=sec_data.get("section_number"),
                    section_title=sec_data.get("section_title"),
                    content=sec_data["content"],
                    page_number=sec_data.get("page_number"),
                    category=sec_data.get("category", "General"),
                    metadata_json=sec_data.get("metadata", {})
                )
                self.db.add(section)
                await self.db.flush()

                # Generate vector embedding
                embedding_vector = await self.embedding_provider.embed_text(sec_data["content"])
                embedding_rec = EmbeddingRecord(
                    chunk_id=section.chunk_id,
                    vector_data={"vector": embedding_vector},
                    model_name="all-MiniLM-L6-v2"
                )
                self.db.add(embedding_rec)

        await self.db.commit()
        return document
