import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.assistant import QueryRequest
from app.services.rag_pipeline import RAGPipeline
from app.services.mock_providers import (
    MockLLMProvider,
    MockTranslationProvider,
    MockEmbeddingProvider
)
from app.services.database_retriever import DatabaseRetrievalProvider
from app.models.source import AuditLog

@pytest.mark.asyncio
async def test_confidential_mode_bypasses_audit_log_persistence(db_session: AsyncSession):
    retriever = DatabaseRetrievalProvider(db_session=db_session)
    llm = MockLLMProvider()
    translator = MockTranslationProvider()
    embedding = MockEmbeddingProvider()

    pipeline = RAGPipeline(
        retriever=retriever,
        llm=llm,
        translator=translator,
        embedding=embedding,
        db_session=db_session
    )

    req = QueryRequest(
        query="Confidential formulation query containing proprietary herbs",
        jurisdiction="India",
        confidential_mode=True
    )

    response = await pipeline.process_query(req)
    assert response is not None

    # Verify audit logs table is empty because confidential_mode=True
    stmt = select(AuditLog).where(AuditLog.query_text.ilike("%proprietary%"))
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 0
