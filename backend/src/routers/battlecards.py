from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
from ..tasks.scraping_tasks import get_search_results
from ..services.ai import generate_research_plan, generate_battlecard

router = APIRouter(prefix="/api/battlecards", tags=["battlecards"])

class BattlecardRequest(BaseModel):
    company_a: str
    company_b: str
    timeframe: str = "Last 1 Year"

from playwright.async_api import async_playwright

async def scrape_company_context(name: str, timeframe: str) -> str:
    queries = await generate_research_plan(name, timeframe)
    all_snippets = []
    urls_to_scrape = []
    
    async def run_worker_agent(query):
        results = await asyncio.to_thread(get_search_results, query, timeframe, 2)
        snippets = []
        urls = []
        if results:
            for r in results:
                link = r.get('url') or r.get('href')
                body = r.get('body') or r.get('title')
                if link and body:
                    snippets.append(f"Source: {link}\nSnippet: {body}")
                    urls.append(link)
        return snippets, urls

    worker_results = await asyncio.gather(*(run_worker_agent(q) for q in queries))
    for snippets, urls in worker_results:
        all_snippets.extend(snippets)
        urls_to_scrape.extend(urls)
        
    # Deduplicate and limit
    urls_to_scrape = list(dict.fromkeys(urls_to_scrape))[:3]
    scraped_texts = []
    
    try:
        from ..services.vector_db import upsert_multiple_contexts, query_context
        import httpx
        from bs4 import BeautifulSoup

        async def fetch_page(url):
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                async with httpx.AsyncClient(timeout=4.0, verify=False, headers=headers) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.extract()
                    text = soup.get_text(separator=' ', strip=True)
                    return {"source_type": "website", "content": text, "url": url}
            except Exception:
                return None

        results = await asyncio.gather(*(fetch_page(url) for url in urls_to_scrape))
        scraped_contexts = [r for r in results if r]
            
        if scraped_contexts:
            await upsert_multiple_contexts(competitor_name=name, contexts=scraped_contexts)


    except Exception as e:
        print(f"Playwright error: {e}")

    # Query the Vector DB for the most relevant context instead of dumping all text
    rag_context = await query_context(competitor_name=name, query="What are the key products, pricing, features, target audience, and recent announcements?")

    return "--- SNIPPETS ---\n" + "\n\n".join(all_snippets) + "\n\n--- RAG RETRIEVED CONTEXT ---\n" + rag_context

battlecard_cache = {}

@router.post("")
async def create_battlecard(req: BattlecardRequest):
    cache_key = f"{req.company_a}_{req.company_b}_{req.timeframe}"
    if cache_key in battlecard_cache:
        return {"report": battlecard_cache[cache_key]}
        
    # Run research for both companies in parallel
    comp_a_task = scrape_company_context(req.company_a, req.timeframe)
    comp_b_task = scrape_company_context(req.company_b, req.timeframe)
    
    comp_a_data, comp_b_data = await asyncio.gather(comp_a_task, comp_b_task)
    
    # Generate battlecard
    report = await generate_battlecard(req.company_a, comp_a_data, req.company_b, comp_b_data)
    
    battlecard_cache[cache_key] = report
    return {"report": report}

from ..services.debate_engine import run_multi_agent_debate

class DebateRequest(BaseModel):
    competitor: str
    our_company: str

@router.post("/debate")
async def trigger_debate(req: DebateRequest):
    comp_data = await scrape_company_context(req.competitor, "Last 1 Year")
    debate_output = await run_multi_agent_debate(req.competitor, req.our_company, comp_data)
    return {"debate": debate_output}
