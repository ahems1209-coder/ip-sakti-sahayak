from typing import List, Optional
from pydantic import BaseModel, Field

class Claim(BaseModel):
    text: str = Field(..., description="Verifiable legal or regulatory claim statement")
    source_chunks: List[str] = Field(default_factory=list, description="List of chunk_ids supporting this claim")

class Citation(BaseModel):
    chunk_id: str
    document_title: str
    authority: str
    jurisdiction: str = "India"
    section: Optional[str] = None
    page: Optional[int] = None
    version_date: Optional[str] = None
    official_source_url: str
    verification_status: str = "verified"


class GroundedResponse(BaseModel):
    answer: str
    claims: List[Claim] = Field(default_factory=list)
    jurisdiction: str = "India"
    confidence: str = Field(..., description="'evidence_supported', 'insufficient_evidence', or 'abstain'")
    needs_review: bool = False
    citations: List[Citation] = Field(default_factory=list)
    demo_mode: bool = False

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="User question or legal query")
    jurisdiction: str = Field(default="India", description="Target jurisdiction (e.g., India)")
    language: str = Field(default="en", description="Query language code (e.g., en, hi)")
    confidential_mode: bool = Field(default=False, description="Ephemeral processing mode without persistent storage")

class FormulationRequest(BaseModel):
    product_name: str = Field(..., min_length=2)
    ingredients: List[str] = Field(..., min_length=1)

    purpose: str = Field(...)
    is_classical_formulation: bool = Field(default=False)
    classical_reference: Optional[str] = None
    target_jurisdiction: str = Field(default="India")
    confidential_mode: bool = Field(default=False)

class FormulationResponse(BaseModel):
    formulation_name: str
    risk_matrix: dict
    missing_information: List[str] = Field(default_factory=list)
    evidence_backed_next_steps: List[str] = Field(default_factory=list)
    source_citations: List[Citation] = Field(default_factory=list)
    confidence: str = "evidence_supported"
    demo_mode: bool = False
