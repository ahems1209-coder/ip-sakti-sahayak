import pytest
from app.schemas.assistant import GroundedResponse, Claim
from app.schemas.source import RetrievalResult
from app.services.citation_validator import CitationValidator

def test_valid_citation_grounding():
    retrieved_chunk = RetrievalResult(
        chunk_id="CHUNK-01",
        document_id="DOC-01",
        title="Patents Act 1970",
        authority="Patent Office",
        jurisdiction="India",
        section="Section 3(p)",
        content="Traditional knowledge is not patentable.",
        source_url="https://example.gov.in",
        version_information="2005",
        relevance_score=0.90
    )

    candidate = GroundedResponse(
        answer="Traditional knowledge cannot be patented.",
        claims=[
            Claim(text="Traditional knowledge is excluded under Section 3(p).", source_chunks=["CHUNK-01"])
        ],
        jurisdiction="India",
        confidence="evidence_supported",
        needs_review=False
    )

    validated = CitationValidator.validate_response(
        candidate_response=candidate,
        retrieved_chunks=[retrieved_chunk]
    )

    assert validated.confidence == "evidence_supported"
    assert len(validated.claims) == 1
    assert len(validated.citations) == 1
    assert validated.citations[0].chunk_id == "CHUNK-01"

def test_invalid_chunk_citation_triggers_abstention():
    # Candidate refers to CHUNK-UNKNOWN which was never retrieved
    candidate = GroundedResponse(
        answer="Fabricated statement.",
        claims=[
            Claim(text="Fake legal claim", source_chunks=["CHUNK-FAKE-999"])
        ],
        jurisdiction="India",
        confidence="evidence_supported",
        needs_review=False
    )

    validated = CitationValidator.validate_response(
        candidate_response=candidate,
        retrieved_chunks=[]
    )

    assert validated.confidence == "insufficient_evidence"
    assert len(validated.claims) == 0
    assert len(validated.citations) == 0
