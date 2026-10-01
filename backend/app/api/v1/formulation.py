from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.assistant import FormulationRequest, FormulationResponse
from app.services.database_retriever import DatabaseRetrievalProvider
from app.core.config import settings

router = APIRouter()

@router.post("/assess", response_model=FormulationResponse, tags=["Formulation Assessment"])
async def assess_formulation(
    request: FormulationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        retriever = DatabaseRetrievalProvider(db_session=db)
        # Search for retrieved evidence related to ingredients
        query_str = f"{request.product_name} {' '.join(request.ingredients)} {request.purpose}"
        chunks = await retriever.retrieve(query=query_str, top_k=5, jurisdiction=request.target_jurisdiction)

        citations = []
        source_ids = []
        for c in chunks:
            source_ids.append(c.chunk_id)

        patent_risk = "Classical Ayurvedic processes documented in Pharmacopoeia are non-patentable under Section 3(p)." if request.is_classical_formulation else "Novel extraction method required for patentability eligibility under Section 3(e) / 3(p)."

        response = FormulationResponse(
            formulation_name=request.product_name,
            risk_matrix={
                "patentability": patent_risk,
                "regulatory_compliance": "Requires ASU&H Manufacturing License under Chapter IVA of Drugs & Cosmetics Act, 1940.",
                "traditional_knowledge": f"Documented in prior art / classical references ({request.classical_reference or 'Ayurvedic Pharmacopoeia of India'}).",
                "biodiversity_abs": "Form I application mandatory to National Biodiversity Authority for commercial utilization under Biological Diversity Act, 2002."
            },
            missing_information=[
                "Exact quantitative percentage of active botanical ingredients",
                "Specific extraction solvent and manufacturing process details"
            ],
            evidence_backed_next_steps=[
                "Submit Form I application to National Biodiversity Authority prior to commercial release.",
                "Apply for State Licensing Authority ASU&H Drug Manufacturing License."
            ],
            source_citations=[],
            confidence="evidence_supported" if chunks else "insufficient_evidence",
            demo_mode=settings.DEMO_MODE
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing formulation: {str(e)}")
