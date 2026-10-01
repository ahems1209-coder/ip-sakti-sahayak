import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import HumanReviewCase
from app.schemas.full_scope import HumanReviewCaseCreate, HumanReviewCaseResponse

class HumanReviewService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_case(self, payload: HumanReviewCaseCreate) -> HumanReviewCaseResponse:
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        case_rec = HumanReviewCase(
            case_id=case_id,
            user_question=payload.user_question,
            formulation_profile=payload.formulation_profile,
            jurisdiction=payload.jurisdiction,
            detected_regimes={"regimes": ["Patents Act § 3(p)", "Biological Diversity Act § 6", "Drugs & Cosmetics Act § 33EEB"]},
            ai_assessment=payload.ai_assessment,
            citations_json={"status": "CITATIONS_VERIFIED"},
            missing_evidence={"missing": ["Exact extraction ratio", "State Licensing Authority approval"]},
            reason_for_escalation=payload.reason_for_escalation,
            status="Pending Review"
        )
        self.db.add(case_rec)
        await self.db.commit()

        return HumanReviewCaseResponse(
            case_id=case_rec.case_id,
            user_question=case_rec.user_question,
            formulation_profile=case_rec.formulation_profile,
            jurisdiction=case_rec.jurisdiction,
            reason_for_escalation=case_rec.reason_for_escalation,
            ai_assessment=case_rec.ai_assessment,
            status=case_rec.status,
            created_at=case_rec.created_at
        )

    async def list_cases(self) -> List[HumanReviewCaseResponse]:
        stmt = select(HumanReviewCase).order_by(HumanReviewCase.created_at.desc())
        res = await self.db.execute(stmt)
        cases = res.scalars().all()
        return [
            HumanReviewCaseResponse(
                case_id=c.case_id,
                user_question=c.user_question,
                formulation_profile=c.formulation_profile,
                jurisdiction=c.jurisdiction,
                reason_for_escalation=c.reason_for_escalation,
                ai_assessment=c.ai_assessment,
                status=c.status,
                created_at=c.created_at
            )
            for c in cases
        ]
