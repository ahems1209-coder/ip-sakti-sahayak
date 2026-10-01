import pytest
from app.schemas.source import RetrievalResult

def test_retrieval_result_schema():
    result = RetrievalResult(
        chunk_id="IND-PAT-1970-SEC03P-C01",
        source_id="IND-PATENTS-ACT-1970",
        document_id="DOC-IND-PAT-1970",
        title="The Patents Act, 1970",
        authority="Indian Patent Office",
        jurisdiction="India",
        section="Section 3(p)",
        content="Traditional knowledge is non-patentable.",
        source_url="https://ipindia.gov.in/patents-act-1970.htm",
        version_date="2005-01-01",
        score=0.92,
        verification_status="verified"
    )
    assert result.chunk_id == "IND-PAT-1970-SEC03P-C01"
    assert result.score == 0.92
    assert result.authority == "Indian Patent Office"

