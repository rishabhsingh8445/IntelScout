import os
import asyncio
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from openai import AsyncOpenAI
from ..config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
INDEX_NAME = "intelscout-index"
DIMENSION = 1024  # NV-Embed-QA-E5-V5 dimension

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=settings.NVIDIA_API_KEY
)

def get_or_create_index():
    if INDEX_NAME not in [index.name for index in pc.list_indexes()]:
        print(f"Creating Pinecone index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    return pc.Index(INDEX_NAME)

index = get_or_create_index()

async def get_embeddings(texts: List[str], input_type: str = "passage") -> List[List[float]]:
    try:
        response = await client.embeddings.create(
            input=texts,
            model="nvidia/nv-embedqa-e5-v5",
            encoding_format="float",
            extra_body={"input_type": input_type, "truncate": "END"},
            timeout=30.0
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []

def chunk_text(text: str, max_chunk_size: int = 1000) -> List[str]:
    # Simple chunking by character length
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

async def upsert_multiple_contexts(competitor_name: str, contexts: List[Dict[str, str]]):
    all_chunks = []
    all_metadata = []
    
    for ctx in contexts:
        chunks = chunk_text(ctx["content"])
        all_chunks.extend(chunks)
        for i, chunk in enumerate(chunks):
            all_metadata.append({
                "id": f"comp_{competitor_name.replace(' ', '_')}_{ctx['source_type']}_{ctx['url']}_{i}",
                "metadata": {
                    "competitor_name": competitor_name,
                    "source_type": ctx["source_type"],
                    "url": ctx["url"],
                    "text": chunk
                }
            })
            
    if not all_chunks:
        return
        
    embeddings = []
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        emb_batch = await get_embeddings(all_chunks[i:i+batch_size], input_type="passage")
        embeddings.extend(emb_batch)
    
    vectors = []
    for meta, emb in zip(all_metadata, embeddings):
        vectors.append({
            "id": meta["id"],
            "values": emb,
            "metadata": meta["metadata"]
        })
        
    for i in range(0, len(vectors), 100):
        batch = vectors[i:i+100]
        await asyncio.to_thread(index.upsert, vectors=batch)
    print(f"Upserted {len(vectors)} vectors to Pinecone for competitor {competitor_name}")

async def query_context(competitor_name: str, query: str, top_k: int = 10) -> str:
    query_embedding = await get_embeddings([query], input_type="query")
    if not query_embedding:
        return ""
        
    def do_query():
        return index.query(
            vector=query_embedding[0],
            top_k=top_k,
            include_metadata=True,
            filter={
                "competitor_name": {"$eq": competitor_name}
            }
        )
        
    results = await asyncio.to_thread(do_query)
    
    contexts = []
    for match in results.matches:
        if match.score > 0.3:  # Threshold lowered to accommodate e5-v5 scores
            text = match.metadata.get("text", "")
            source = match.metadata.get("source_type", "unknown")
            contexts.append(f"[{source.upper()}] {text}")
            
    return "\n\n---\n\n".join(contexts)
