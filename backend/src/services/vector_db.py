import asyncio
import logging
from typing import Any, Dict, List

from openai import AsyncOpenAI
from pinecone import Pinecone, ServerlessSpec

from ..config import settings

logger = logging.getLogger(__name__)

INDEX_NAME = "intelscout-index"
DIMENSION = 1024

_index = None
_pc: Pinecone | None = None

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=settings.NVIDIA_API_KEY,
)


def _pinecone_client() -> Pinecone | None:
    global _pc
    if not settings.PINECONE_API_KEY:
        return None
    if _pc is None:
        _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    return _pc


def get_index():
    global _index
    if _index is not None:
        return _index
    pc = _pinecone_client()
    if pc is None:
        raise RuntimeError("Pinecone is not configured")
    try:
        existing_indexes = [index.name for index in pc.list_indexes()]
        if INDEX_NAME not in existing_indexes:
            logger.info("Creating Pinecone index '%s'...", INDEX_NAME)
            pc.create_index(
                name=INDEX_NAME,
                dimension=DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        _index = pc.Index(INDEX_NAME)
        return _index
    except Exception as e:
        logger.warning("Pinecone index operation failed: %s", e)
        raise


async def get_embeddings(texts: List[str], input_type: str = "passage") -> List[List[float]]:
    if not texts:
        return []
    try:
        response = await client.embeddings.create(
            input=texts,
            model="nvidia/nv-embedqa-e5-v5",
            encoding_format="float",
            extra_body={"input_type": input_type, "truncate": "END"},
            timeout=30.0,
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        logger.warning("Error generating embeddings: %s", type(e).__name__)
        return []


def chunk_text(text: str, max_chunk_size: int = 1000) -> List[str]:
    words = text.split(" ")
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        if current_length + len(word) > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


async def upsert_multiple_contexts(competitor_name: str, user_id: str, contexts: List[Dict[str, str]]):
    if not settings.PINECONE_API_KEY:
        return
    all_chunks: list[str] = []
    all_metadata: list[dict[str, Any]] = []

    for ctx in contexts:
        content = ctx.get("content") or ""
        if not content.strip():
            continue
        chunks = chunk_text(content)
        all_chunks.extend(chunks)
        safe_name = competitor_name.replace(" ", "_")[:80]
        for i, chunk in enumerate(chunks):
            all_metadata.append(
                {
                    "id": f"u_{user_id}_comp_{safe_name}_{ctx.get('source_type', 'web')}_{i}_{hash(ctx.get('url', '')) & 0xFFFF}",
                    "metadata": {
                        "competitor_name": competitor_name,
                        "user_id": user_id,
                        "source_type": ctx.get("source_type", "website"),
                        "url": (ctx.get("url") or "")[:512],
                        "text": chunk[:4000],
                    },
                }
            )

    if not all_chunks:
        return

    embeddings: list[list[float]] = []
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        emb_batch = await get_embeddings(all_chunks[i : i + batch_size], input_type="passage")
        if len(emb_batch) != len(all_chunks[i : i + batch_size]):
            logger.warning("Embedding batch size mismatch; skipping upsert")
            return
        embeddings.extend(emb_batch)

    vectors = []
    for meta, emb in zip(all_metadata, embeddings):
        vectors.append({"id": meta["id"], "values": emb, "metadata": meta["metadata"]})

    index = get_index()
    for i in range(0, len(vectors), 100):
        batch = vectors[i : i + 100]
        await asyncio.to_thread(index.upsert, vectors=batch)
    logger.info("Upserted %s vectors for competitor %s", len(vectors), competitor_name)


async def query_context(competitor_name: str, query: str, user_id: str, top_k: int = 10) -> str:
    query_embedding = await get_embeddings([query], input_type="query")
    if not query_embedding:
        return ""

    def do_query():
        return get_index().query(
            vector=query_embedding[0],
            top_k=top_k,
            include_metadata=True,
            filter={"competitor_name": {"$eq": competitor_name}, "user_id": {"$eq": user_id}},
        )

    results = await asyncio.to_thread(do_query)

    contexts = []
    for match in results.matches:
        if match.score > 0.3:
            text = match.metadata.get("text", "")
            source = match.metadata.get("source_type", "unknown")
            contexts.append(f"[{source.upper()}] {text}")

    return "\n\n---\n\n".join(contexts)
