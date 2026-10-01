import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import SourceRegistry, Document, DocumentSection, EmbeddingRecord
from app.services.manifest_ingestion_service import ManifestIngestionService
from app.services.mock_providers import MockEmbeddingProvider, MockLLMProvider, MockTranslationProvider
from app.services.database_retriever import DatabaseRetrievalProvider
from app.services.rag_pipeline import RAGPipeline
from app.schemas.assistant import QueryRequest

@pytest.mark.asyncio
async def test_source_manifest_loading(db_session: AsyncSession):
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    res = await ingestor.load_and_sync_manifest("research/source_manifest.json")
    assert res["total_sources"] >= 12
    assert res["loaded_sources"] >= 12

    # Verify source metadata persistence
    stmt = select(SourceRegistry).where(SourceRegistry.id == "IND-PATENTS-ACT-1970")
    source = (await db_session.execute(stmt)).scalar_one_or_none()
    assert source is not None
    assert source.priority == "P0"
    assert source.jurisdiction == "India"
    assert source.official_url == "https://ipindia.gov.in/patents-act-1970.htm"

from sqlalchemy.orm import selectinload

@pytest.mark.asyncio
async def test_p0_document_ingestion_and_structural_sections(db_session: AsyncSession):
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    ingest_res = await ingestor.ingest_p0_source_documents("knowledge_base")

    assert ingest_res["p0_ingested_count"] >= 8
    assert ingest_res["documents_created"] >= 8

    assert ingest_res["chunks_created"] >= 12

    # Verify chunk provenance & structural section extraction
    stmt = select(DocumentSection).options(selectinload(DocumentSection.document)).where(DocumentSection.chunk_id == "IND-PAT-1970-SEC03P-C01")
    sec = (await db_session.execute(stmt)).scalar_one_or_none()
    assert sec is not None
    assert sec.section_number == "Section 3(p)"
    assert sec.document.title == "The Patents Act, 1970"
    assert sec.document.source_url == "https://ipindia.gov.in/patents-act-1970.htm"


@pytest.mark.asyncio
async def test_tkdl_access_restriction_handling(db_session: AsyncSession):
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    stmt = select(DocumentSection).where(DocumentSection.chunk_id == "IND-TKDL-FRAMEWORK-C01")
    sec = (await db_session.execute(stmt)).scalar_one_or_none()
    assert sec is not None
    assert sec.metadata_json.get("access_type") == "mixed"
    assert "CSIR Access Agreement Required" in sec.metadata_json.get("access_restriction")

@pytest.mark.asyncio
async def test_vector_and_keyword_and_combined_retrieval(db_session: AsyncSession):
    embedding_prov = MockEmbeddingProvider()
    ingestor = ManifestIngestionService(db_session, embedding_prov)
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    retriever = DatabaseRetrievalProvider(db_session, embedding_prov)

    # 1. Keyword Retrieval
    kw_results = await retriever.retrieve_keyword("traditional knowledge patentable", top_k=5, jurisdiction="India")
    assert len(kw_results) > 0
    assert any("SEC03P" in r.chunk_id for r in kw_results)

    # 2. Vector Retrieval
    vec_results = await retriever.retrieve_vector("traditional knowledge patentable", top_k=5, jurisdiction="India")
    assert len(vec_results) > 0

    # 3. Combined Hybrid Retrieval
    combined_results = await retriever.retrieve("traditional knowledge patentable", top_k=5, jurisdiction="India")
    assert len(combined_results) > 0
    assert combined_results[0].score > 0.0
    assert combined_results[0].source_url.startswith("http")

@pytest.mark.asyncio
async def test_jurisdiction_filtering(db_session: AsyncSession):
    embedding_prov = MockEmbeddingProvider()
    ingestor = ManifestIngestionService(db_session, embedding_prov)
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    retriever = DatabaseRetrievalProvider(db_session, embedding_prov)

    # Query Indian jurisdiction specifically
    india_results = await retriever.retrieve("biological resources approval", top_k=5, jurisdiction="India")
    assert all(r.jurisdiction == "India" for r in india_results)

    # Query International jurisdiction specifically
    intl_results = await retriever.retrieve("genetic resources Nagoya protocol", top_k=5, jurisdiction="International")
    assert all(r.jurisdiction == "International" for r in intl_results)

@pytest.mark.asyncio
async def test_citation_grounding_and_unsupported_claim_rejection(db_session: AsyncSession):
    embedding_prov = MockEmbeddingProvider()
    ingestor = ManifestIngestionService(db_session, embedding_prov)
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    retriever = DatabaseRetrievalProvider(db_session, embedding_prov)
    pipeline = RAGPipeline(
        retriever=retriever,
        llm=MockLLMProvider(),
        translator=MockTranslationProvider(),
        embedding=embedding_prov,
        db_session=db_session
    )

    # Supported Query
    req_valid = QueryRequest(query="Is traditional knowledge patentable under Section 3(p)?", jurisdiction="India")
    resp_valid = await pipeline.process_query(req_valid)
    assert resp_valid.confidence == "evidence_supported"
    assert len(resp_valid.claims) > 0
    assert len(resp_valid.citations) > 0
    assert resp_valid.citations[0].official_source_url != ""

    # Query with no matching evidence
    req_unsupported = QueryRequest(query="Quantum propulsion warp core stellar navigation protocol 2099", jurisdiction="India")
    resp_unsupported = await pipeline.process_query(req_unsupported)
    assert resp_unsupported.confidence == "insufficient_evidence"
    assert len(resp_unsupported.claims) == 0

