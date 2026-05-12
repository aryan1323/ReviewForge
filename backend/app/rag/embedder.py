import logging
import os

from openai import AsyncAzureOpenAI, AsyncOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _make_client():
    """Use Azure embedding deployment if configured, else fall back to standard OpenAI."""
    if settings.AZURE_EMBEDDING_DEPLOYMENT:
        return AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        return AsyncOpenAI(api_key=openai_key)
    return None


_client = _make_client()


async def embed_text(text: str) -> list[float] | None:
    """Returns None if no embedding client is configured (RAG will be skipped)."""
    if _client is None:
        return None
    model = settings.AZURE_EMBEDDING_DEPLOYMENT or settings.EMBEDDING_MODEL
    response = await _client.embeddings.create(model=model, input=text)
    return response.data[0].embedding


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Returns empty list if no embedding client is configured."""
    if not texts or _client is None:
        return []
    model = settings.AZURE_EMBEDDING_DEPLOYMENT or settings.EMBEDDING_MODEL
    response = await _client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
