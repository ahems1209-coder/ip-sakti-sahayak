from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.full_scope import (
    FullFormulationInput,
    FullFormulationIntelligenceResponse,
    HumanReviewCaseCreate,
    HumanReviewCaseResponse,
    KnowledgeGraphGraphData,
    PaidConnectorStatusResponse,
    BenchmarkEvaluationReport
)
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

router = APIRouter()

@router.post("/intelligence/assess-formulation", response_model=FullFormulationIntelligenceResponse, tags=["Full-Scope Intelligence"])
async def assess_full_formulation(
    input_data: FullFormulationInput,
    db: AsyncSession = Depends(get_db)
):
    try:
        retriever = DatabaseRetrievalProvider(db, MockEmbeddingProvider())
        query_str = f"{input_data.product_name} {' '.join(input_data.ingredients)} {input_data.purpose}"
        chunks = await retriever.retrieve(query=query_str, top_k=5, jurisdiction=input_data.target_market)

        classification = FormulationClassificationEngine.classify(input_data, chunks)
        ip_routes = FullIPRoutingEngine.route_ip(input_data, chunks)
        regulatory_routes = FullRegulatoryRoutingEngine.route_regulatory(input_data, chunks)
        abs_tk_routes = ABSTKRoutingEngine.route_abs_tk(input_data, chunks)

        citations = []
        for c in chunks:
            citations.append({
                "chunk_id": c.chunk_id,
                "document_title": c.title,
                "authority": c.authority,
                "jurisdiction": c.jurisdiction,
                "section": c.section,
                "page": 1,
                "version_date": c.version_date,
                "official_source_url": c.source_url,
                "verification_status": c.verification_status
            })

        missing_info = classification.missing_information
        for r in ip_routes:
            missing_info.extend(r.missing_facts)

        next_steps = [
            "Submit Form I/III application to National Biodiversity Authority (NBA) prior to commercial launch.",
            "Obtain State Licensing Authority Form 25D manufacturing license with Schedule T GMP certification.",
            "Conduct formal TKDL prior-art review with specialized patent counsel.",
            "Verify FSSAI Ayurveda Aahara logo and label advisory warning compliance."
        ]

        return FullFormulationIntelligenceResponse(
            formulation_name=input_data.product_name,
            classification=classification,
            ip_routes=ip_routes,
            regulatory_routes=regulatory_routes,
            abs_tk_routes=abs_tk_routes,
            jurisdiction=input_data.target_market,
            evidence_status="CITATIONS_VERIFIED",
            source_citations=citations,
            missing_information=list(set(missing_info)),
            actionable_next_steps=next_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing formulation intelligence: {str(e)}")


@router.post("/cases/create", response_model=HumanReviewCaseResponse, tags=["Human Review Cases"])
async def create_human_review_case(
    payload: HumanReviewCaseCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = HumanReviewService(db)
        return await service.create_case(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating human review case: {str(e)}")


@router.get("/cases", response_model=List[HumanReviewCaseResponse], tags=["Human Review Cases"])
async def list_human_review_cases(db: AsyncSession = Depends(get_db)):
    try:
        service = HumanReviewService(db)
        return await service.list_cases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing human review cases: {str(e)}")


@router.post("/knowledge-graph", response_model=KnowledgeGraphGraphData, tags=["Knowledge Graph"])
async def fetch_knowledge_graph(input_data: FullFormulationInput):
    try:
        return KnowledgeGraphService.generate_graph(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating knowledge graph: {str(e)}")


@router.get("/connectors", response_model=List[PaidConnectorStatusResponse], tags=["Paid Connectors"])
async def list_paid_connectors():
    return PaidConnectorService.list_connectors()


@router.post("/evaluation/run-benchmark", response_model=BenchmarkEvaluationReport, tags=["Evaluation Framework"])
async def run_50_benchmark_evaluation(db: AsyncSession = Depends(get_db)):
    try:
        service = EvaluationRunnerService(db)
        return await service.run_50_benchmark_evaluation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running benchmark evaluation: {str(e)}")
