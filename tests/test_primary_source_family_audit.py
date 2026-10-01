import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import SourceRegistry
from app.services.manifest_ingestion_service import ManifestIngestionService
from app.services.mock_providers import MockEmbeddingProvider
from app.services.adapters.tkdl_adapter import TKDLAdapter
from app.services.adapters.india_code_adapter import IndiaCodeAdapter
from app.services.adapters.ip_india_adapter import IPIndiaPublicDatabaseAdapter
from app.services.adapters.nba_abs_adapter import NBAABSAdapter

@pytest.mark.asyncio
async def test_sih_primary_source_family_adapters(db_session: AsyncSession):
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")

    # 1. TKDL
    tkdl_info = TKDLAdapter.get_adapter_info()
    assert tkdl_info["source_id"] == "IND-TKDL-GUIDELINES"
    assert tkdl_info["access_status"] == "RESTRICTED_MIXED"
    assert tkdl_info["source_category"] == "SIH_PORTAL_SPECIFIED"

    # 2. India Code
    india_code_info = IndiaCodeAdapter.get_adapter_info()
    assert india_code_info["source_id"] == "IND-INDIA-CODE-PORTAL"
    assert india_code_info["access_status"] == "NOT_CURRENTLY_ACCESSIBLE"
    assert india_code_info["source_category"] == "SIH_PORTAL_SPECIFIED"

    # 3. IP India Public Databases
    ip_india_info = IPIndiaPublicDatabaseAdapter.get_adapter_info()
    assert ip_india_info["source_id"] == "IND-IP-INDIA-PUBLIC-DATABASES"
    assert ip_india_info["access_status"] == "NOT_CURRENTLY_ACCESSIBLE"
    assert len(ip_india_info["sub_databases"]) == 4

    # 4. NBA / ABS
    nba_info = NBAABSAdapter.get_adapter_info()
    assert nba_info["source_id"] == "IND-NBA-ABS-PORTAL"
    assert nba_info["access_status"] == "ACCESSIBLE_STATUTORY_ONLY"

    # Verify Database Persistence of Source Origin and Categorization
    stmt = select(SourceRegistry).where(SourceRegistry.source_category == "SIH_PORTAL_SPECIFIED")
    sih_sources = (await db_session.execute(stmt)).scalars().all()
    assert len(sih_sources) >= 4

