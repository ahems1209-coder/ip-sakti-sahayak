from typing import List, Optional, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

class RetrievalResult(BaseModel):
    chunk_id: str
    source_id: Optional[str] = None
    document_id: str
    title: str
    authority: str
    jurisdiction: str = "India"
    section: Optional[str] = None
    content: str
    source_url: str
    version_date: Optional[str] = None
    score: float = 0.0
    verification_status: str = "verified"



class SourceRegistryCreate(BaseModel):
    id: str
    name: str
    authority_type: str
    jurisdiction: str = "India"
    official_url: str
    trust_score: float = 1.0

class SourceRegistryResponse(SourceRegistryCreate):
    created_at: datetime

class DocumentCreate(BaseModel):
    id: str
    source_id: Optional[str] = None
    title: str
    authority: str
    jurisdiction: str = "India"
    document_type: str
    version_date: Optional[date] = None
    effective_date: Optional[date] = None
    source_url: str
    content_hash: str
    verification_status: str = "verified"

class DocumentResponse(DocumentCreate):
    created_at: datetime

class DocumentSectionCreate(BaseModel):
    chunk_id: str
    document_id: str
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    content: str
    page_number: Optional[int] = None
    category: str = "General"
    metadata_json: Optional[dict] = None

class DocumentSectionResponse(DocumentSectionCreate):
    created_at: datetime
