from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/cached-queries", tags=["Demo Mode"])
async def get_cached_demo_queries():
    return {
        "demo_mode": settings.DEMO_MODE,
        "queries": [
            {
                "id": "DEMO-01",
                "title": "Patentability of Ayurvedic Formulation",
                "query": "Is a classical Ayurvedic polyherbal formulation patentable under Section 3(p) or 3(e) of the Indian Patents Act, 1970?",
                "jurisdiction": "India",
                "category": "Patents / Traditional Knowledge",
                "query_type": "Patentability Assessment"
            },
            {
                "id": "DEMO-02",
                "title": "Traditional Knowledge Defensive Protection (TKDL)",
                "query": "How does the TKDL framework prevent bio-piracy and wrongful patent grants for Indian medicinal knowledge?",
                "jurisdiction": "India",
                "category": "Traditional Knowledge",
                "query_type": "Traditional Knowledge Relevance"
            },
            {
                "id": "DEMO-03",
                "title": "Biological Resource Commercialization & ABS Approval",
                "query": "Are foreign companies required to obtain National Biodiversity Authority (NBA) approval before applying for IP on Indian bio-resources?",
                "jurisdiction": "India",
                "category": "Biodiversity / ABS",
                "query_type": "Biological-resource / ABS Consideration"
            },
            {
                "id": "DEMO-04",
                "title": "Geographical Indications Protection for Regional Herbal Goods",
                "query": "What grounds restrict registration of generic geographical plant names under Section 9 of the GI Act, 1999?",
                "jurisdiction": "India",
                "category": "Geographical Indications",
                "query_type": "GI Consideration"
            },
            {
                "id": "DEMO-05",
                "title": "Trademark Restrictions on Classical Botanical Terms",
                "query": "Can generic Ayurvedic plant names or classical formulation terms be registered as exclusive trademarks under Section 9 and 13?",
                "jurisdiction": "India",
                "category": "Trademarks",
                "query_type": "Trademark Consideration"
            },
            {
                "id": "DEMO-06",
                "title": "International Patent Filing & Prior Art Search (PCT & WIPO)",
                "query": "How do PCT Article 15 and WIPO IGC frameworks incorporate traditional knowledge into international patent prior art searches?",
                "jurisdiction": "International",
                "category": "Patents / International Treaties",
                "query_type": "International Patent Filing"
            }
        ]
    }
