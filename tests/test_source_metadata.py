import pytest
from datetime import date
from app.schemas.source import DocumentCreate, DocumentSectionCreate

def test_document_metadata_validation():
    doc = DocumentCreate(
        id="DOC-IND-PAT-1970",
        source_id="IND-PATENT-OFFICE",
        title="The Patents Act, 1970",
        authority="Indian Patent Office",
        jurisdiction="India",
        document_type="Act",
        version_date=date(2005, 1, 1),
        source_url="https://ipindia.gov.in/patents-act-1970.htm",
        content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        verification_status="verified"
    )
    assert doc.id == "DOC-IND-PAT-1970"
    assert doc.jurisdiction == "India"
    assert doc.verification_status == "verified"

def test_section_metadata_validation():
    sec = DocumentSectionCreate(
        chunk_id="IND-PAT-1970-SEC03P-C01",
        document_id="DOC-IND-PAT-1970",
        section_number="Section 3(p)",
        section_title="Inventions Not Patentable - Traditional Knowledge",
        content="Traditional knowledge is not patentable under Section 3(p).",
        page_number=14,
        category="Patents"
    )
    assert sec.chunk_id == "IND-PAT-1970-SEC03P-C01"
    assert sec.section_number == "Section 3(p)"
