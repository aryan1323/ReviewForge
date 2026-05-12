import logging
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.rag.embedder import embed_text

logger = logging.getLogger(__name__)
settings = get_settings()


async def get_relevant_context(
    db: AsyncSession,
    repository_id: uuid.UUID,
    query_text: str,
    top_k: int | None = None,
) -> list[str]:
    """
    Embed query_text and retrieve the top-K most similar code chunks
    from pgvector using cosine distance.
    """
    k = top_k or settings.RAG_TOP_K
    query_vec = await embed_text(query_text)
    if query_vec is None:
        logger.info("No embedding client configured — skipping RAG retrieval")
        return []

    # Check if any chunks exist for this repo first
    count_result = await db.execute(
        text("SELECT COUNT(*) FROM code_chunks WHERE repository_id = :repo_id"),
        {"repo_id": str(repository_id)},
    )
    count = count_result.scalar_one()
    if count == 0:
        logger.info("No code chunks indexed for repo %s — skipping RAG", repository_id)
        return []

    rows = await db.execute(
        text("""
            SELECT content, file_path,
                   1 - (embedding <=> :query_vec::vector) AS similarity
            FROM code_chunks
            WHERE repository_id = :repo_id
            ORDER BY embedding <=> :query_vec::vector
            LIMIT :k
        """),
        {
            "repo_id": str(repository_id),
            "query_vec": str(query_vec),
            "k": k,
        },
    )

    results = rows.fetchall()
    return [
        f"// {row.file_path} (similarity: {row.similarity:.3f})\n{row.content}"
        for row in results
    ]
