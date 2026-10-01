from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.source import Document, DocumentSection
from app.schemas.source import DocumentResponse, DocumentSectionResponse

router = APIRouter()

@router.get("", response_model=List[DocumentResponse], tags=["Source Explorer"])
async def list_sources(db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Document)
        result = await db.execute(stmt)
        docs = result.scalars().all()
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.get("/{document_id}/sections", response_model=List[DocumentSectionResponse], tags=["Source Explorer"])
async def list_document_sections(document_id: str, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(DocumentSection).where(DocumentSection.document_id == document_id)
        result = await db.execute(stmt)
        sections = result.scalars().all()
        return sections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sections for document {document_id}: {str(e)}")
