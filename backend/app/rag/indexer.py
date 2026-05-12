import logging
import os
import tempfile
import uuid
from pathlib import Path

import git
import tiktoken
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.metrics.prometheus import rag_chunks_indexed_total
from app.rag.embedder import embed_batch

logger = logging.getLogger(__name__)
settings = get_settings()

# File extensions to index
_INDEXABLE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".go", ".java", ".rb", ".rs", ".cpp",
    ".c", ".h", ".cs", ".php", ".swift",
    ".kt", ".scala", ".sh", ".yaml", ".yml",
    ".json", ".toml", ".md",
}
_MAX_FILE_SIZE = 100_000  # bytes

_tokenizer = tiktoken.get_encoding("cl100k_base")


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    tokens = _tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(_tokenizer.decode(chunk_tokens))
        start += chunk_size - overlap
    return chunks


async def index_repository(
    db: AsyncSession,
    repository_id: uuid.UUID,
    repo_full_name: str,
    github_token: str,
) -> int:
    """
    Shallow-clone the repo, chunk all source files, embed them,
    and upsert into code_chunks. Returns the number of chunks indexed.
    """
    clone_url = f"https://x-access-token:{github_token}@github.com/{repo_full_name}.git"

    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info("Cloning %s for RAG indexing", repo_full_name)
        git.Repo.clone_from(clone_url, tmpdir, depth=1, single_branch=True)

        all_chunks: list[tuple[str, int, str]] = []  # (file_path, chunk_index, content)

        for root, _, files in os.walk(tmpdir):
            # Skip hidden dirs (.git, .github, node_modules, etc.)
            rel_root = Path(root).relative_to(tmpdir)
            if any(part.startswith(".") or part == "node_modules" for part in rel_root.parts):
                continue

            for fname in files:
                fpath = Path(root) / fname
                if fpath.suffix not in _INDEXABLE_EXTENSIONS:
                    continue
                if fpath.stat().st_size > _MAX_FILE_SIZE:
                    continue

                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                rel_path = str(fpath.relative_to(tmpdir))
                for idx, chunk in enumerate(
                    _chunk_text(content, settings.RAG_CHUNK_SIZE, settings.RAG_CHUNK_OVERLAP)
                ):
                    all_chunks.append((rel_path, idx, chunk))

        if not all_chunks:
            return 0

        # Embed in batches of 500
        batch_size = 500
        total_indexed = 0
        for batch_start in range(0, len(all_chunks), batch_size):
            batch = all_chunks[batch_start : batch_start + batch_size]
            texts = [c[2] for c in batch]
            embeddings = await embed_batch(texts)

            for (file_path, chunk_idx, content), embedding in zip(batch, embeddings):
                await db.execute(
                    text("""
                        INSERT INTO code_chunks
                            (repository_id, file_path, chunk_index, content, embedding)
                        VALUES
                            (:repo_id, :file_path, :chunk_idx, :content, :embedding)
                        ON CONFLICT (repository_id, file_path, chunk_index)
                        DO UPDATE SET content = EXCLUDED.content,
                                      embedding = EXCLUDED.embedding,
                                      indexed_at = NOW()
                    """),
                    {
                        "repo_id": str(repository_id),
                        "file_path": file_path,
                        "chunk_idx": chunk_idx,
                        "content": content,
                        "embedding": str(embedding),
                    },
                )
            await db.commit()
            total_indexed += len(batch)
            rag_chunks_indexed_total.inc(len(batch))
            logger.info("Indexed %d/%d chunks for %s", total_indexed, len(all_chunks), repo_full_name)

    return total_indexed
