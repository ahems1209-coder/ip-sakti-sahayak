import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import SourceRegistry, Document, DocumentSection

@pytest.mark.asyncio
async def test_database_models_persistence(db_session: AsyncSession):
    source = SourceRegistry(
        id="TEST-SOURCE-01",
        name="Test Patent Office",
        authority_type="Statutory Authority",
        jurisdiction="India",
        official_url="https://example.gov.in"
    )
    db_session.add(source)
    await db_session.flush()

    document = Document(
        id="DOC-TEST-01",
        source_id="TEST-SOURCE-01",
        title="Test Patent Act",
        authority="Test Patent Office",
        jurisdiction="India",
        document_type="Act",
        version_date=date(2025, 1, 1),
        effective_date=date(2025, 1, 1),
        source_url="https://example.gov.in/act",
        content_hash="abc123hash",
        verification_status="verified"
    )
    db_session.add(document)
    await db_session.flush()

    section = DocumentSection(
        chunk_id="TEST-SEC-01",
        document_id="DOC-TEST-01",
        section_number="Section 1",
        section_title="Short title and extent",
        content="This Act may be called the Test Patent Act.",
        page_number=1,
        category="Patents"
    )
    db_session.add(section)
    await db_session.commit()

    # Query back
    stmt = select(DocumentSection).where(DocumentSection.chunk_id == "TEST-SEC-01")
    result = (await db_session.execute(stmt)).scalar_one_or_none()
    assert result is not None
    assert result.section_number == "Section 1"
    assert result.document.title == "Test Patent Act"
