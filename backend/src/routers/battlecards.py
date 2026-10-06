import asyncio
import logging
import time
from collections import OrderedDict

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select

from ..config import settings
from ..database import AsyncSessionLocal
from ..dependencies import get_current_user
from ..models import Competitor
from ..security.url_validation import is_safe_http_url
from ..services.ai import generate_battlecard, generate_research_plan
from ..services.debate_engine import run_multi_agent_debate
from ..tasks.scraping_tasks import get_search_results

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/battlecards", tags=["battlecards"])

_CACHE_TTL_SECONDS = 900
_CACHE_MAX = 64
_battlecard_cache: OrderedDict[str, tuple[float, str]] = OrderedDict()


class BattlecardRequest(BaseModel):
    company_a: str = Field(..., min_length=1, max_length=200)
    company_b: str = Field(..., min_length=1, max_length=200)
    timeframe: str = Field("Last 1 Year", max_length=64)


class DebateRequest(BaseModel):
    competitor: str = Field(..., min_length=1, max_length=200)
    our_company: str = Field(..., min_length=1, max_length=200)


def _cache_get(key: str) -> str | None:
    entry = _battlecard_cache.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > _CACHE_TTL_SECONDS:
        _battlecard_cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: str) -> None:
    _battlecard_cache[key] = (time.time(), value)
    _battlecard_cache.move_to_end(key)
    while len(_battlecard_cache) > _CACHE_MAX:
        _battlecard_cache.popitem(last=False)


async def scrape_company_context(name: str, timeframe: str, user_id: str) -> str:
    async with AsyncSessionLocal() as session:
        comp = (
            await session.execute(
                select(Competitor).where(Competitor.name.ilike(name), Competitor.user_id == user_id)
            )
        ).scalar_one_or_none()

        if comp and comp.raw_context:
            logger.debug("Using cached raw_context for %s", name)
            return comp.raw_context

    queries = await generate_research_plan(name, timeframe)
    all_snippets = []
    urls_to_scrape = []

    async def run_worker_agent(query):
        results = await asyncio.to_thread(get_search_results, query, timeframe, 2)
        snippets = []
        urls = []
        if results:
            for r in results:
                link = r.get("url") or r.get("href")
                body = r.get("body") or r.get("title")
                if link and body and is_safe_http_url(str(link)):
                    snippets.append(f"Source: {link}\nSnippet: {body}")
                    urls.append(link)
        return snippets, urls

    worker_results = await asyncio.gather(*(run_worker_agent(q) for q in queries))
    for snippets, urls in worker_results:
        all_snippets.extend(snippets)
        urls_to_scrape.extend(urls)

    urls_to_scrape = list(dict.fromkeys(urls_to_scrape))[:3]
    scraped_contexts: list[dict] = []

    async def fetch_page(url):
        if not is_safe_http_url(url):
            return None
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; IntelScout/1.0)"}
            async with httpx.AsyncClient(
                timeout=4.0, verify=settings.HTTP_VERIFY_SSL, headers=headers, follow_redirects=True
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                if len(resp.content) > 2_000_000:
                    return None
                soup = BeautifulSoup(resp.text, "html.parser")
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.extract()
                text = soup.get_text(separator=" ", strip=True)
                return {"source_type": "website", "content": text, "url": url}
        except Exception:
            return None

    results = await asyncio.gather(*(fetch_page(url) for url in urls_to_scrape))
    scraped_contexts = [r for r in results if r]

    full_scraped_text = ""
    for ctx in scraped_contexts:
        full_scraped_text += ctx["content"][:2000] + "\n\n"

    return "--- SNIPPETS ---\n" + "\n\n".join(all_snippets) + "\n\n--- SCRAPED CONTEXT ---\n" + full_scraped_text


@router.post("")
async def create_battlecard(req: BattlecardRequest, user_id: str = Depends(get_current_user)):
    cache_key = f"{user_id}_{req.company_a}_{req.company_b}_{req.timeframe}"
    cached = _cache_get(cache_key)
    if cached:
        return {"report": cached}

    comp_a_data, comp_b_data = await asyncio.gather(
        scrape_company_context(req.company_a, req.timeframe, user_id),
        scrape_company_context(req.company_b, req.timeframe, user_id),
    )

    report = await generate_battlecard(req.company_a, comp_a_data, req.company_b, comp_b_data)
    _cache_set(cache_key, report)
    return {"report": report}


@router.post("/debate")
async def trigger_debate(req: DebateRequest, user_id: str = Depends(get_current_user)):
    comp_data = await scrape_company_context(req.competitor, "Last 1 Year", user_id)
    debate_output = await run_multi_agent_debate(req.competitor, req.our_company, comp_data)
    return {"debate": debate_output}
