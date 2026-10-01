import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.full_scope import FullFormulationInput, HumanReviewCaseCreate
from app.services.manifest_ingestion_service import ManifestIngestionService
from app.services.database_retriever import DatabaseRetrievalProvider
from app.services.mock_providers import MockEmbeddingProvider
from app.services.full_scope_engine import (
    FormulationClassificationEngine,
    FullIPRoutingEngine,
    FullRegulatoryRoutingEngine,
    ABSTKRoutingEngine,
    KnowledgeGraphService
)
from app.services.human_review_service import HumanReviewService
from app.services.paid_connector_service import PaidConnectorService
from app.services.evaluation_runner_service import EvaluationRunnerService

@pytest.mark.asyncio
async def test_full_scope_classification_engine(db_session: AsyncSession):
    # Test classification categories
    input_aahara = FullFormulationInput(
        product_name="Ayurveda Aahara Herbal Tea",
        product_type="Ayurveda Aahara / Nutraceutical",
        ingredients=["Ashwagandha", "Tulsi"],
        purpose="Dietary wellness food supplement"
    )
    res_aahara = FormulationClassificationEngine.classify(input_aahara, [])
    assert res_aahara.classification == "AYURVEDA_AAHARA"

    input_cosmetic = FullFormulationInput(
        product_name="Kumkumadi Face Cream",
        product_type="Cosmetic",
        ingredients=["Saffron", "Sandalwood"],
        purpose="Skin beautification and cleansing"
    )
    res_cosmetic = FormulationClassificationEngine.classify(input_cosmetic, [])
    assert res_cosmetic.classification == "COSMETIC"

    input_classical = FullFormulationInput(
        product_name="Chyawanprash Awaleha",
        product_type="Classical Churna / Kwath",
        ingredients=["Amla", "Guduchi"],
        purpose="Rejuvenative tonic",
        is_classical=True
    )
    res_classical = FormulationClassificationEngine.classify(input_classical, [])
    assert res_classical.classification == "CLASSICAL_GENERIC"


@pytest.mark.asyncio
async def test_full_scope_ip_routing(db_session: AsyncSession):
    input_data = FullFormulationInput(
        product_name="Ashwagandha Synergistic Extract",
        ingredients=["Ashwagandha", "Brahmi"],
        purpose="Cognitive enhancement and regional geographical botanical good"
    )
    routes = FullIPRoutingEngine.route_ip(input_data, [])
    categories = [r.category for r in routes]

    assert "Patent" in categories
    assert "Geographical Indications" in categories
    assert "Trade Marks" in categories
    assert "Designs" in categories
    assert "Copyright" in categories
    assert "Trade Secret" in categories
    assert "Plant Variety" in categories


@pytest.mark.asyncio
async def test_full_scope_regulatory_routing(db_session: AsyncSession):
    input_data = FullFormulationInput(
        product_name="ASU Proprietary Syrup",
        product_type="Proprietary ASU Medicine",
        ingredients=["Vasaka", "Tulsi"],
        purpose="Cough relief"
    )
    routes = FullRegulatoryRoutingEngine.route_regulatory(input_data, [])
    categories = [r.category for r in routes]

    assert "ASU&H Medicine" in categories
    assert "Advertising & Labeling" in categories


@pytest.mark.asyncio
async def test_full_scope_abs_tk_engine(db_session: AsyncSession):
    input_foreign = FullFormulationInput(
        product_name="Herbal Extract",
        ingredients=["Curcumin"],
        purpose="Commercial use",
        applicant_type="Foreign entity",
        foreign_participation=True
    )
    res_abs = ABSTKRoutingEngine.route_abs_tk(input_foreign, [])
    assert "Mandatory NBA Approval" in res_abs.abs_relevance
    assert "Form I" in res_abs.authority_and_forms


@pytest.mark.asyncio
async def test_full_scope_knowledge_graph_and_human_review(db_session: AsyncSession):
    # Test Knowledge Graph Generation
    input_data = FullFormulationInput(
        product_name="NeuroBoost Extract",
        ingredients=["Brahmi", "Shankhpushpi"],
        purpose="Memory retention"
    )
    graph = KnowledgeGraphService.generate_graph(input_data)
    assert len(graph.nodes) >= 6
    assert len(graph.edges) >= 5

    # Test Human Review Case Creation
    service = HumanReviewService(db_session)
    payload = HumanReviewCaseCreate(
        user_question="Complex novelty query on novel extraction method",
        reason_for_escalation="Novelty evaluation requires specialized patent attorney opinion"
    )
    case_res = await service.create_case(payload)
    assert case_res.case_id.startswith("CASE-")
    assert case_res.status == "Pending Review"


@pytest.mark.asyncio
async def test_50_benchmark_evaluation_suite(db_session: AsyncSession):
    ingestor = ManifestIngestionService(db_session, MockEmbeddingProvider())
    await ingestor.load_and_sync_manifest("research/source_manifest.json")
    await ingestor.ingest_p0_source_documents("knowledge_base")

    service = EvaluationRunnerService(db_session)
    report = await service.run_50_benchmark_evaluation()

    assert report.total_benchmark_queries == 50
    assert report.precision_rate >= 90.0
    assert report.safe_abstention_rate == 100.0
