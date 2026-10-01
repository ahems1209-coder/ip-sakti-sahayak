import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import SourceRegistry, Document, DocumentSection
from app.services.manifest_ingestion_service import ManifestIngestionService
from app.services.mock_providers import MockEmbeddingProvider, MockLLMProvider, MockTranslationProvider
from app.services.database_retriever import DatabaseRetrievalProvider
from app.services.rag_pipeline import RAGPipeline
from app.schemas.assistant import QueryRequest

@pytest.mark.asyncio
async def test_data_integrity_and_manifest_db_agreement(db_session: AsyncSession):
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    # Test I: Manifest and DB agreement
    stmt = select(SourceRegistry)
    sources = (await db_session.execute(stmt)).scalars().all()
    assert len(sources) >= 12
    for s in sources:
        assert s.source_origin in ["SIH_PORTAL_SPECIFIED", "SUPPORTING_AUTHORITATIVE"]
        assert s.technical_access_status in ["ACCESSIBLE", "NOT_CURRENTLY_ACCESSIBLE", "RESTRICTED"]

@pytest.mark.asyncio
async def test_non_accessible_sources_have_zero_live_chunks(db_session: AsyncSession):
    # Test A: NOT_CURRENTLY_ACCESSIBLE sources have zero live searchable chunks unless explicitly ingested
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")

    stmt = select(SourceRegistry).where(SourceRegistry.id == "IND-IP-INDIA-INPASS-SEARCH")
    inpass_source = (await db_session.execute(stmt)).scalar_one_or_none()
    assert inpass_source is not None
    assert inpass_source.technical_access_status == "NOT_CURRENTLY_ACCESSIBLE"
    assert inpass_source.automated_integration is False

    # Check zero documents created for non-accessible source
    stmt_docs = select(Document).where(Document.source_id == "IND-IP-INDIA-INPASS-SEARCH")
    docs = (await db_session.execute(stmt_docs)).scalars().all()
    assert len(docs) == 0


@pytest.mark.asyncio
async def test_searchable_chunk_and_provenance_mapping(db_session: AsyncSession):
    # Test B & C & D: Every searchable chunk maps to real document with valid provenance
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    stmt = select(DocumentSection)
    sections = (await db_session.execute(stmt)).scalars().all()
    assert len(sections) >= 12

    for sec in sections:
        assert sec.document_id is not None
        stmt_doc = select(Document).where(Document.id == sec.document_id)
        doc = (await db_session.execute(stmt_doc)).scalar_one_or_none()
        assert doc is not None
        assert doc.source_url.startswith("http")
        assert doc.content_hash != ""

@pytest.mark.asyncio
async def test_tkdl_specific_record_query_safety(db_session: AsyncSession):
    # Test F: TKDL specific-record query never returns yes/no formulation existence claims
    embedding_prov = MockEmbeddingProvider()
    retriever = DatabaseRetrievalProvider(db_session, embedding_prov)
    pipeline = RAGPipeline(
        retriever=retriever,
        llm=MockLLMProvider(),
        translator=MockTranslationProvider(),
        embedding=embedding_prov,
        db_session=db_session
    )

    req = QueryRequest(query="Does TKDL contain the exact formulation Ashwagandha + Brahmi + Shatavari?", jurisdiction="India")
    resp = await pipeline.process_query(req)

    assert resp.confidence == "insufficient_evidence"
    assert "RESTRICTED ACCESS WARNING" in resp.answer
    assert "cannot confirm or deny" in resp.answer
    assert len(resp.claims) == 0

@pytest.mark.asyncio
async def test_indian_entity_section7_abs_adversarial_abstention(db_session: AsyncSession):
    # Test G: Indian company ABS question does not fall back to Section 3-only reasoning
    embedding_prov = MockEmbeddingProvider()
    retriever = DatabaseRetrievalProvider(db_session, embedding_prov)
    pipeline = RAGPipeline(
        retriever=retriever,
        llm=MockLLMProvider(),
        translator=MockTranslationProvider(),
        embedding=embedding_prov,
        db_session=db_session
    )

    req = QueryRequest(query="I am an Indian company using a biological resource for commercial purposes. Do I need ABS compliance?", jurisdiction="India")
    resp = await pipeline.process_query(req)

    assert resp.confidence == "insufficient_evidence"
    assert "INSUFFICIENT_EVIDENCE" in resp.answer
    assert "Section 3 applies exclusively to non-Indian entities" in resp.answer
    assert len(resp.claims) == 0

@pytest.mark.asyncio
async def test_rules_and_forms_abstention_when_uningested(db_session: AsyncSession):
    # Test H: Rules/forms questions abstain when required rules/forms are not ingested
    embedding_prov = MockEmbeddingProvider()
    retriever = DatabaseRetrievalProvider(db_session, embedding_prov)
    pipeline = RAGPipeline(
        retriever=retriever,
        llm=MockLLMProvider(),
        translator=MockTranslationProvider(),
        embedding=embedding_prov,
        db_session=db_session
    )

    req = QueryRequest(query="Form IV fee breakdown under Biological Diversity Amendment Rules 2025", jurisdiction="India")
    resp = await pipeline.process_query(req)

    assert resp.confidence == "insufficient_evidence"
    assert len(resp.claims) == 0


@pytest.mark.asyncio
async def test_hero_demo_ayurvedic_formulation_patentability_query(db_session: AsyncSession):
    # Regression test for SIH Primary Hero Demo query:
    # "I developed an Ayurvedic formulation containing Ashwagandha and Brahmi. Can I patent it?"
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    embedding_prov = MockEmbeddingProvider()
    retriever = DatabaseRetrievalProvider(db_session, embedding_prov)
    pipeline = RAGPipeline(
        retriever=retriever,
        llm=MockLLMProvider(),
        translator=MockTranslationProvider(),
        embedding=embedding_prov,
        db_session=db_session
    )

    query_str = "I developed an Ayurvedic formulation containing Ashwagandha and Brahmi. Can I patent it?"
    req = QueryRequest(query=query_str, jurisdiction="India")
    resp = await pipeline.process_query(req)

    # 1. Must NOT trigger insufficient_evidence when P0 source chunks are present
    assert resp.confidence == "evidence_supported"
    assert len(resp.claims) > 0
    assert len(resp.citations) > 0

    # 2. Must retrieve Section 3(p) patent chunk
    retrieved_chunk_ids = [c.chunk_id for c in resp.citations]
    assert "IND-PAT-1970-SEC03P-C01" in retrieved_chunk_ids

    # 3. Citation validation preserved
    for claim in resp.claims:
        assert len(claim.source_chunks) > 0
        for cid in claim.source_chunks:
            assert cid in retrieved_chunk_ids

    # 4. Does not make a simplistic categorical conclusion unsupported by evidence
    assert "Section 3(p)" in resp.answer
    assert "Preliminary Assessment" in resp.answer
    assert "Relevant IP Considerations" in resp.answer
    assert not resp.answer.startswith("According to")


