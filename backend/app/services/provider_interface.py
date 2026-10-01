from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.schemas.source import RetrievalResult
from app.schemas.assistant import GroundedResponse, Claim

class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate vector embedding for input text string."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        pass


class LLMProvider(ABC):
    @abstractmethod
    async def generate_grounded_response(
        self,
        query: str,
        retrieved_chunks: List[RetrievalResult],
        jurisdiction: str = "India"
    ) -> GroundedResponse:
        """Generate structured response strictly grounded in retrieved chunks."""
        pass


class TranslationProvider(ABC):
    @abstractmethod
    async def detect_language(self, text: str) -> str:
        """Detect ISO language code for input text."""
        pass

    @abstractmethod
    async def translate_to_english(self, text: str, source_language: str) -> str:
        """Translate regional query to English for standardized retrieval."""
        pass

    @abstractmethod
    async def translate_from_english(self, text: str, target_language: str) -> str:
        """Translate final response back to user target language."""
        pass


class RetrievalProvider(ABC):
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: str = "India",
        category: Optional[str] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant source chunks using dense + full-text search."""
        pass
