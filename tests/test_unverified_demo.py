import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.assistant import QueryRequest
from app.services.rag_pipeline import RAGPipeline
from app.services.mock_providers import MockLLMProvider, MockTranslationProvider, MockEmbeddingProvider
from app.services.database_retriever import DatabaseRetrievalProvider
from app.services.ingestion_service import DocumentIngestionService
from app.main import DEMO_SEED_DATA

@pytest.mark.asyncio
async def test_demo_seed_data_marked_unverified_demo(db_session: AsyncSession):
    # Ingest demo seed data
    ingestor = DocumentIngestionService(db_session, MockEmbeddingProvider())
    doc = await ingestor.ingest_document_structure(DEMO_SEED_DATA)
    assert doc.verification_status == "unverified_demo"

    # Query RAG pipeline against demo seed data
    retriever = DatabaseRetrievalProvider(db_session=db_session)
    pipeline = RAGPipeline(
        retriever=retriever,
        llm=MockLLMProvider(),
        translator=MockTranslationProvider(),
        embedding=MockEmbeddingProvider(),
        db_session=db_session
    )

    req = QueryRequest(query="Is traditional knowledge patentable under Section 3(p)?", jurisdiction="India")
    response = await pipeline.process_query(req)

    # Verify that response highlights unverified_demo status and marks needs_review=True
    assert len(response.citations) > 0
    assert response.citations[0].verification_status == "unverified_demo"
    assert response.needs_review is True
