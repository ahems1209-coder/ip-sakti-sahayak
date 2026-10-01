from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.assistant import Citation

class FullFormulationInput(BaseModel):
    product_name: str = Field(..., min_length=2)
    product_type: str = Field(default="Polyherbal Extract") # Classical, Proprietary, Phytopharmaceutical, Ayurveda Aahara, Cosmetic, Plant Variety
    ingredients: List[str] = Field(..., min_length=1)
    proportions: Optional[str] = None
    preparation_method: Optional[str] = None
    purpose: str = Field(...)
    is_classical: bool = Field(default=False)
    classical_reference: Optional[str] = None
    applicant_type: str = Field(default="Indian entity") # Indian entity, Foreign entity, Joint venture
    foreign_participation: bool = Field(default=False)
    commercial_or_research: str = Field(default="Commercial")
    biological_resource_involved: bool = Field(default=True)
    traditional_knowledge_involved: bool = Field(default=True)
    target_market: str = Field(default="India")
    jurisdiction: str = Field(default="India")

class ClassificationResult(BaseModel):
    classification: str # CLASSICAL_GENERIC, PATENT_OR_PROPRIETARY, NEW_NON_CLASSICAL, PHYTOPHARMACEUTICAL, AYURVEDA_AAHARA, COSMETIC, PLANT_VARIETY, OTHER, UNDETERMINED
    classification_reason: str
    supporting_sources: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    review_required: bool = False

class IPRoutingResult(BaseModel):
    category: str # Patent, GI, Trademark, Designs, Copyright, Trade Secret, Plant Variety
    relevance: str # potentially_relevant, not_relevant_based_on_current_facts, insufficient_evidence
    applicable_framework: str
    evidence_summary: str
    missing_facts: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)

class RegulatoryRoutingResult(BaseModel):
    category: str # ASU&H Medicine, Classical/Generic, Proprietary Medicine, Phytopharmaceutical, Ayurveda Aahara, Cosmetic, Advertising
    applicable_framework: str
    authority: str
    required_licensing_or_form: str
    evidence_summary: str
    missing_information: List[str] = Field(default_factory=list)

class ABSTKRoutingResult(BaseModel):
    abs_relevance: str # Mandatory NBA Approval, SBB Intimation Only, Exempted, Insufficient Evidence
    applicable_provisions: str
    authority_and_forms: str # NBA Form I-IV, BD Rules 2024
    tkdl_status_notice: str
    evidence_summary: str
    missing_information: List[str] = Field(default_factory=list)

class FullFormulationIntelligenceResponse(BaseModel):
    formulation_name: str
    classification: ClassificationResult
    ip_routes: List[IPRoutingResult]
    regulatory_routes: List[RegulatoryRoutingResult]
    abs_tk_routes: ABSTKRoutingResult
    jurisdiction: str
    evidence_status: str = "CITATIONS_VERIFIED"
    source_citations: List[Citation] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    actionable_next_steps: List[str] = Field(default_factory=list)

class HumanReviewCaseCreate(BaseModel):
    user_question: str
    formulation_profile: Dict[str, Any] = Field(default_factory=dict)
    jurisdiction: str = "India"
    reason_for_escalation: str
    ai_assessment: str = ""

class HumanReviewCaseResponse(BaseModel):
    case_id: str
    user_question: str
    formulation_profile: Dict[str, Any]
    jurisdiction: str
    reason_for_escalation: str
    ai_assessment: str
    status: str
    created_at: datetime

class KnowledgeGraphGraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class PaidConnectorStatusResponse(BaseModel):
    connector_id: str
    name: str
    provider_type: str
    is_connected: bool
    explicit_consent_granted: bool
    auth_status: str
    disclaimer: str = "Privacy and security controls are implemented; formal legal compliance depends on deployment and organizational assessment."

class BenchmarkEvaluationReport(BaseModel):
    total_benchmark_queries: int
    passed_queries: int
    precision_rate: float
    citation_correctness_rate: float
    safe_abstention_rate: float
    evaluated_at: datetime
    domain_breakdown: Dict[str, int]
