import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Text, Float, Integer, Boolean, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class SourceRegistry(Base):
    __tablename__ = "source_registry"

    id: Mapped[str] = mapped_column(String(64), primary_key=True) # source_id
    source_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False) # title
    authority_type: Mapped[str] = mapped_column(String(255), nullable=False) # authority
    jurisdiction: Mapped[str] = mapped_column(String(50), default="India")
    document_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    official_url: Mapped[str] = mapped_column(Text, nullable=False)
    direct_pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(10), default="P0")
    access_type: Mapped[str] = mapped_column(String(50), default="public")
    access_status: Mapped[str] = mapped_column(String(50), default="ACCESSIBLE") # ACCESSIBLE, NOT_CURRENTLY_ACCESSIBLE, RESTRICTED
    technical_access_status: Mapped[str] = mapped_column(String(50), default="ACCESSIBLE") # ACCESSIBLE, NOT_CURRENTLY_ACCESSIBLE, RESTRICTED
    legal_access_status: Mapped[str] = mapped_column(String(50), default="NOT_VERIFIED") # PUBLIC_DOMAIN, RESTRICTED_TERMS, NOT_VERIFIED
    source_category: Mapped[str] = mapped_column(String(50), default="SUPPORTING_AUTHORITATIVE") # SIH_PORTAL_SPECIFIED, SUPPORTING_AUTHORITATIVE
    source_origin: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # SIH_PORTAL_SPECIFIED vs SUPPORTING_AUTHORITATIVE
    adapter_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Dedicated adapter class name

    # Stage 2.2 Source Access Model Fields
    registered: Mapped[bool] = mapped_column(Boolean, default=True)
    portal_accessible: Mapped[bool] = mapped_column(Boolean, default=False)
    document_available: Mapped[bool] = mapped_column(Boolean, default=False)
    content_ingested: Mapped[bool] = mapped_column(Boolean, default=False)
    searchable: Mapped[bool] = mapped_column(Boolean, default=False)
    automated_integration: Mapped[bool] = mapped_column(Boolean, default=False)
    restricted: Mapped[bool] = mapped_column(Boolean, default=False)
    retrieval_method: Mapped[str] = mapped_column(String(50), default="hybrid_database")
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)

    verification_status: Mapped[str] = mapped_column(String(50), default="verified")
    ingestion_recommendation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ingestion_status: Mapped[str] = mapped_column(String(50), default="awaiting_manual_document")
    trust_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)



    documents: Mapped[List["Document"]] = relationship("Document", back_populates="source_registry")



class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("source_registry.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authority: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(50), default="India")
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    version_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    ingestion_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="verified")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


    source_registry: Mapped[Optional["SourceRegistry"]] = relationship("SourceRegistry", back_populates="documents")
    sections: Mapped[List["DocumentSection"]] = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")


class DocumentSection(Base):
    __tablename__ = "document_sections"

    chunk_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    section_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    section_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="General")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Mapped["Document"] = relationship("Document", back_populates="sections")
    embeddings: Mapped[List["EmbeddingRecord"]] = relationship("EmbeddingRecord", back_populates="section", cascade="all, delete-orphan")


class EmbeddingRecord(Base):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chunk_id: Mapped[str] = mapped_column(String(128), ForeignKey("document_sections.chunk_id", ondelete="CASCADE"), nullable=False)
    # Store embedding array as JSON for universal dialect support (e.g. SQLite tests + pgvector)
    vector_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    section: Mapped["DocumentSection"] = relationship("DocumentSection", back_populates="embeddings")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    detected_language: Mapped[str] = mapped_column(String(10), default="en")
    jurisdiction: Mapped[str] = mapped_column(String(50), default="India")
    confidence_status: Mapped[str] = mapped_column(String(50), nullable=False)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    citations: Mapped[List["AnswerCitation"]] = relationship("AnswerCitation", back_populates="audit_log", cascade="all, delete-orphan")


class AnswerCitation(Base):
    __tablename__ = "answer_citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_log_id: Mapped[str] = mapped_column(String(36), ForeignKey("audit_logs.id", ondelete="CASCADE"), nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_id: Mapped[str] = mapped_column(String(128), ForeignKey("document_sections.chunk_id", ondelete="SET NULL"), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="verified")

    audit_log: Mapped["AuditLog"] = relationship("AuditLog", back_populates="citations")


class HumanReviewCase(Base):
    __tablename__ = "human_review_cases"

    case_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"CASE-{uuid.uuid4().hex[:8].upper()}")
    user_question: Mapped[str] = mapped_column(Text, nullable=False)
    formulation_profile: Mapped[dict] = mapped_column(JSON, default=dict)
    jurisdiction: Mapped[str] = mapped_column(String(50), default="India")
    detected_regimes: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_assessment: Mapped[str] = mapped_column(Text, nullable=False)
    citations_json: Mapped[dict] = mapped_column(JSON, default=dict)
    missing_evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    reason_for_escalation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Pending Review") # Pending Review, Assigned, Resolved
    assigned_facilitator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class KnowledgeGraphNode(Base):
    __tablename__ = "knowledge_graph_nodes"

    node_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False) # Formulation, Ingredient, BiologicalResource, TraditionalKnowledge, Patent, GI, Trademark, Copyright, Design, PlantVariety, Regulation, Authority, Jurisdiction, Country, ProductCategory, Source, Claim, Case
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class KnowledgeGraphEdge(Base):
    __tablename__ = "knowledge_graph_edges"

    edge_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_node_id: Mapped[str] = mapped_column(String(128), ForeignKey("knowledge_graph_nodes.node_id", ondelete="CASCADE"), nullable=False)
    target_node_id: Mapped[str] = mapped_column(String(128), ForeignKey("knowledge_graph_nodes.node_id", ondelete="CASCADE"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False) # contains, derived_from, relates_to, regulated_by, protected_by, subject_to, supported_by, applies_in, issued_by, requires, potentially_triggers
    provenance_chunk_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PaidSourceConnector(Base):
    __tablename__ = "paid_source_connectors"

    connector_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(100), nullable=False) # Licensed Patent DB, Paid Registry, Subscription Journal
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    explicit_consent_granted: Mapped[bool] = mapped_column(Boolean, default=False)
    auth_status: Mapped[str] = mapped_column(String(100), default="Not Configured")
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_id: Mapped[str] = mapped_column(String(64), nullable=False)
    domain_category: Mapped[str] = mapped_column(String(100), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    expected_behavior: Mapped[str] = mapped_column(String(100), nullable=False)
    actual_confidence: Mapped[str] = mapped_column(String(100), nullable=False)
    retrieval_correct: Mapped[bool] = mapped_column(Boolean, default=True)
    citation_correct: Mapped[bool] = mapped_column(Boolean, default=True)
    abstention_correct: Mapped[bool] = mapped_column(Boolean, default=True)
    overall_pass: Mapped[bool] = mapped_column(Boolean, default=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

