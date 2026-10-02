from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db, AsyncSessionLocal
from app.api.v1 import health, assistant, formulation, sources, demo, full_scope
from app.services.ingestion_service import DocumentIngestionService
from app.services.mock_providers import MockEmbeddingProvider

# Demo Mode Seed Data — Marked as 'unverified_demo' until official Gazette PDFs are ingested
DEMO_SEED_DATA = {
    "source_registry": {
        "id": "IND-PATENT-OFFICE",
        "name": "Controller General of Patents, Designs & Trade Marks",
        "authority_type": "Statutory Authority",
        "jurisdiction": "India",
        "official_url": "https://ipindia.gov.in"
    },
    "document": {
        "id": "DOC-IND-PAT-1970",
        "title": "The Patents Act, 1970",
        "authority": "Indian Patent Office",
        "jurisdiction": "India",
        "document_type": "Act",
        "version_date": "2005-01-01",
        "source_url": "https://ipindia.gov.in/patents-act-1970.htm",
        "verification_status": "unverified_demo"
    },
    "sections": [
        {
            "chunk_id": "IND-PAT-1970-SEC03P-C01",
            "section_number": "Section 3(p)",
            "section_title": "Inventions Not Patentable - Traditional Knowledge",
            "content": "An invention which in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not patentable under Section 3(p) of the Patents Act, 1970.",
            "page_number": 14,
            "category": "Patents"
        },
        {
            "chunk_id": "IND-BDA-2002-SEC03-C02",
            "section_number": "Section 3",
            "section_title": "Certain Persons Not to Undertake Biodiversity Related Activities Without Approval",
            "content": "No person who is not a citizen of India, or a body corporate having non-Indian participation in share capital or management, shall obtain any biological resource occurring in India or knowledge associated thereto for research or for commercial utilization without prior approval of the National Biodiversity Authority.",
            "page_number": 5,
            "category": "Biodiversity / ABS"
        }
    ]
}


from app.services.manifest_ingestion_service import ManifestIngestionService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup DB initialization
    await init_db()

    # Import AsyncSessionLocal dynamically after init_db has configured SQLite/Postgres engine
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        manifest_ingestor = ManifestIngestionService(session, MockEmbeddingProvider())
        try:
            await manifest_ingestor.load_and_sync_manifest("research/source_manifest.json")
            await manifest_ingestor.ingest_p0_source_documents("knowledge_base")
            print("[Startup]: Source manifest synced and P0 documents ingested successfully.")
        except Exception as e:
            print(f"[Ingestion Warn]: {e}")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
allowed_origins = settings.get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app" if settings.ENVIRONMENT.lower() not in {"production", "prod"} else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint at root level (/api/health)
app.include_router(health.router, prefix="/api")

# API Version 1 Routers (/api/v1/...)
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(assistant.router, prefix=f"{settings.API_V1_STR}/assistant")
app.include_router(formulation.router, prefix=f"{settings.API_V1_STR}/formulation")
app.include_router(sources.router, prefix=f"{settings.API_V1_STR}/sources")
app.include_router(demo.router, prefix=f"{settings.API_V1_STR}/demo")
app.include_router(full_scope.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }
