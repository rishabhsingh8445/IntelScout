from fastapi import APIRouter, Query
import asyncio
from ..services.vector_db import get_embeddings, index

from typing import Optional

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("")
async def search_all(
    q: str = Query(..., description="The search query string"),
    competitor: Optional[str] = Query(None, description="Optional competitor to filter by")
):
    query_embedding = await get_embeddings([q], input_type="query")
    if not query_embedding:
        return {"answer": "No relevant data found.", "results": []}
        
    def do_query():
        filter_dict = {}
        if competitor:
            filter_dict["competitor_name"] = {"$eq": competitor}
            
        return index.query(
            vector=query_embedding[0],
            top_k=6,
            filter=filter_dict if filter_dict else None,
            include_metadata=True
        )
        
    results = await asyncio.to_thread(do_query)
    
    formatted_results = []
    
    for match in results.matches:
        if match.score > 0.3:
            content = match.metadata.get("text", "")
            source = match.metadata.get("url", "unknown")
            competitor_name = match.metadata.get("competitor_name", "unknown")
            formatted_results.append({
                "score": match.score,
                "content": content,
                "source": source,
                "competitor": competitor_name
            })
            
    # Sort by score descending
    formatted_results = sorted(formatted_results, key=lambda x: x["score"], reverse=True)
    
    context_text = ""
    for r in formatted_results:
        context_text += f"\nSource [{r['source']}]:\n{r['content']}\n"
        
    from ..services.ai import client, MODEL_NAME, llm_semaphore
    
    competitor_context = f"The user is asking a question specifically about the competitor: '{competitor}'." if competitor else "The user is asking a general question across all indexed documents."
    
    prompt = f"""
    You are an elite Competitive Intelligence AI assistant.
    {competitor_context}
    The user has searched for: "{q}"
    (Note: The user's query may contain typos or spelling mistakes. Please implicitly correct them and understand their true intent.)
    
    Below is the raw context retrieved from the vector database (Pinecone) across various competitor documents.
    
    Context:
    {context_text[:6000]}
    
    Task:
    1. Synthesize a clear, direct answer to the user's query using the provided context.
    2. If the context contains irrelevant garbage (like cookie banners), ignore it.
    3. If the context does not contain the answer to the user's query, use your general world knowledge to answer the question, but clearly append a note saying: "*Note: This answer is based on general knowledge, as the specific details were not found in the scraped competitor documents.*"
    """
    
    try:
        async with llm_semaphore:
            res = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.3,
                timeout=30.0
            )
        answer = res.choices[0].message.content.strip()
    except Exception as e:
        print(f"RAG Error: {e}")
        answer = "Failed to synthesize AI answer. The AI service is currently unavailable."
            
    return {"answer": answer, "results": formatted_results}
