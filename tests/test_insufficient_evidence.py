import pytest
from app.schemas.assistant import GroundedResponse, Claim
from app.services.citation_validator import CitationValidator

def test_empty_retrieval_returns_insufficient_evidence_state():
    candidate = GroundedResponse(
        answer="Speculative answer without evidence.",
        claims=[
            Claim(text="Unverified claim", source_chunks=["NON-EXISTENT-CHUNK"])
        ],
        jurisdiction="India",
        confidence="evidence_supported",
        needs_review=False
    )

    result = CitationValidator.validate_response(
        candidate_response=candidate,
        retrieved_chunks=[]
    )

    assert result.confidence == "insufficient_evidence"
    assert result.needs_review is True
    assert "Insufficient authoritative evidence" in result.answer
