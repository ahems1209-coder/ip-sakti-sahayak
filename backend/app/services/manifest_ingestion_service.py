import os
import json
import hashlib
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import SourceRegistry, Document, DocumentSection, EmbeddingRecord
from app.services.provider_interface import EmbeddingProvider

class ManifestIngestionService:
    def __init__(self, db_session: AsyncSession, embedding_provider: EmbeddingProvider):
        self.db = db_session
        self.embedding_provider = embedding_provider

    @staticmethod
    def calculate_hash(content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def _resolve_path(path: str) -> str:
        if os.path.isabs(path) and os.path.exists(path):
            return path
        if os.path.exists(path):
            return path
        # Fallback to project root directory (3 levels up from app/services)
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        candidate = os.path.join(root_dir, path)
        if os.path.exists(candidate):
            return candidate
        return path

    async def load_and_sync_manifest(self, manifest_path: str = "research/source_manifest.json") -> Dict[str, Any]:
        """
        Phase 2A: Loads research/source_manifest.json and populates/updates source_registry.
        """
        resolved_manifest_path = self._resolve_path(manifest_path)
        if not os.path.exists(resolved_manifest_path):
            raise FileNotFoundError(f"Source manifest not found at {manifest_path} (resolved: {resolved_manifest_path})")

        with open(resolved_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        sources_data = manifest.get("sources", [])
        total_sources = len(sources_data)
        loaded_sources = 0

        for s_data in sources_data:
            stmt = select(SourceRegistry).where(SourceRegistry.id == s_data["source_id"])
            existing_source = (await self.db.execute(stmt)).scalar_one_or_none()

            if not existing_source:
                source_reg = SourceRegistry(
                    id=s_data["source_id"],
                    source_family=s_data.get("source_family"),
                    name=s_data["title"],
                    authority_type=s_data["authority"],
                    jurisdiction=s_data.get("jurisdiction", "India"),
                    document_type=s_data.get("document_type"),
                    official_url=s_data["official_url"],
                    direct_pdf_url=s_data.get("direct_pdf_url"),
                    priority=s_data.get("priority", "P0"),
                    access_type=s_data.get("access_type", "public"),
                    access_status=s_data.get("access_status", "ACCESSIBLE"),
                    technical_access_status=s_data.get("technical_access_status", "ACCESSIBLE"),
                    legal_access_status=s_data.get("legal_access_status", "NOT_VERIFIED"),
                    source_category=s_data.get("source_category", "SUPPORTING_AUTHORITATIVE"),
                    source_origin=s_data.get("source_origin", "SUPPORTING_AUTHORITATIVE"),
                    adapter_name=s_data.get("adapter_name"),
                    verification_status=s_data.get("verification_status", "verified"),
                    ingestion_recommendation=s_data.get("ingestion_recommendation"),
                    ingestion_status="awaiting_manual_document"
                )
                self.db.add(source_reg)
                loaded_sources += 1
            else:
                existing_source.source_family = s_data.get("source_family")
                existing_source.name = s_data["title"]
                existing_source.authority_type = s_data["authority"]
                existing_source.jurisdiction = s_data.get("jurisdiction", "India")
                existing_source.document_type = s_data.get("document_type")
                existing_source.official_url = s_data["official_url"]
                existing_source.direct_pdf_url = s_data.get("direct_pdf_url")
                existing_source.priority = s_data.get("priority", "P0")
                existing_source.access_type = s_data.get("access_type", "public")
                existing_source.access_status = s_data.get("access_status", "ACCESSIBLE")
                existing_source.technical_access_status = s_data.get("technical_access_status", "ACCESSIBLE")
                existing_source.legal_access_status = s_data.get("legal_access_status", "NOT_VERIFIED")
                existing_source.source_category = s_data.get("source_category", "SUPPORTING_AUTHORITATIVE")
                existing_source.source_origin = s_data.get("source_origin", "SUPPORTING_AUTHORITATIVE")
                existing_source.adapter_name = s_data.get("adapter_name")
                existing_source.verification_status = s_data.get("verification_status", "verified")
                existing_source.ingestion_recommendation = s_data.get("ingestion_recommendation")
                loaded_sources += 1



        await self.db.commit()
        return {"total_sources": total_sources, "loaded_sources": loaded_sources}

    async def ingest_p0_source_documents(self, corpus_directory: str = "knowledge_base") -> Dict[str, Any]:
        """
        Phase 2B & 2C & 2D & 2E: Ingests P0 source documents from corpus directory.
        Preserves structural chunking (Chapter -> Section -> Subsection), access rules, and chunk provenance.
        """
        stmt = select(SourceRegistry).where(SourceRegistry.priority == "P0")
        p0_sources = (await self.db.execute(stmt)).scalars().all()

        p0_ingested_count = 0
        p0_awaiting_count = 0
        total_documents_created = 0
        total_chunks_created = 0

        resolved_corpus_dir = self._resolve_path(corpus_directory)

        for source in p0_sources:
            # Check if a structured file exists in knowledge_base/india or knowledge_base/international
            source_filename = f"{source.id.lower()}.json"
            india_path = os.path.join(resolved_corpus_dir, "india", source_filename)
            intl_path = os.path.join(resolved_corpus_dir, "international", source_filename)
            target_path = india_path if os.path.exists(india_path) else (intl_path if os.path.exists(intl_path) else None)

            if target_path and os.path.exists(target_path):
                with open(target_path, "r", encoding="utf-8") as f:
                    doc_payload = json.load(f)

                # Process Document
                doc_data = doc_payload["document"]
                doc_content_str = json.dumps(doc_payload["sections"])
                content_hash = self.calculate_hash(doc_content_str)
                version_dt = date.fromisoformat(doc_data["version_date"]) if doc_data.get("version_date") else None

                stmt_doc = select(Document).where(Document.id == doc_data["id"])
                document = (await self.db.execute(stmt_doc)).scalar_one_or_none()

                if not document:
                    document = Document(
                        id=doc_data["id"],
                        source_id=source.id,
                        title=doc_data["title"],
                        authority=doc_data["authority"],
                        jurisdiction=doc_data.get("jurisdiction", source.jurisdiction),
                        document_type=doc_data.get("document_type", source.document_type or "Act"),
                        version_date=version_dt,
                        source_url=doc_data.get("source_url", source.official_url),
                        content_hash=content_hash,
                        verification_status=doc_data.get("verification_status", source.verification_status)
                    )
                    self.db.add(document)
                    await self.db.flush()
                    total_documents_created += 1

                # Process Structural Chunks
                for sec_data in doc_payload.get("sections", []):
                    stmt_sec = select(DocumentSection).where(DocumentSection.chunk_id == sec_data["chunk_id"])
                    existing_sec = (await self.db.execute(stmt_sec)).scalar_one_or_none()

                    if not existing_sec:
                        meta = sec_data.get("metadata", {})
                        meta["access_type"] = source.access_type
                        meta["priority"] = source.priority
                        meta["jurisdiction"] = source.jurisdiction
                        if source.access_type == "mixed":
                            meta["access_restriction"] = "Restricted - CSIR Access Agreement Required for Detailed Database Records"


                        section = DocumentSection(
                            chunk_id=sec_data["chunk_id"],
                            document_id=document.id,
                            section_number=sec_data.get("section_number"),
                            section_title=sec_data.get("section_title"),
                            content=sec_data["content"],
                            page_number=sec_data.get("page_number"),
                            category=sec_data.get("category", source.source_family or "General"),
                            metadata_json=meta
                        )
                        self.db.add(section)
                        await self.db.flush()
                        total_chunks_created += 1

                        # Generate Vector Embedding
                        vector = await self.embedding_provider.embed_text(sec_data["content"])
                        emb_rec = EmbeddingRecord(
                            chunk_id=section.chunk_id,
                            vector_data={"vector": vector},
                            model_name="all-MiniLM-L6-v2"
                        )
                        self.db.add(emb_rec)

                source.ingestion_status = "ingested"
                p0_ingested_count += 1
            else:
                # Mark as awaiting manual document without fabricating content
                source.ingestion_status = "awaiting_manual_document"
                p0_awaiting_count += 1

        await self.db.commit()
        return {
            "p0_ingested_count": p0_ingested_count,
            "p0_awaiting_count": p0_awaiting_count,
            "documents_created": total_documents_created,
            "chunks_created": total_chunks_created
        }
