from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.assistant import QueryRequest, GroundedResponse
from app.services.database_retriever import DatabaseRetrievalProvider
from app.services.mock_providers import MockLLMProvider, MockTranslationProvider, MockEmbeddingProvider
from app.services.rag_pipeline import RAGPipeline

router = APIRouter()

@router.post("/query", response_model=GroundedResponse, tags=["AI Assistant"])
async def process_assistant_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        retriever = DatabaseRetrievalProvider(db_session=db)
        llm = MockLLMProvider()
        translator = MockTranslationProvider()
        embedding = MockEmbeddingProvider()

        pipeline = RAGPipeline(
            retriever=retriever,
            llm=llm,
            translator=translator,
            embedding=embedding,
            db_session=db
        )

        response = await pipeline.process_query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing assistant query: {str(e)}")
