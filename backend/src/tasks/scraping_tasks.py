import asyncio
import logging
import sys
import threading
from typing import Set

from sqlalchemy import delete, select

from src.database import AsyncSessionLocal
from src.models import Competitor, Insight
from src.security.url_validation import is_safe_http_url
from src.services.agent_pipeline import run_autonomous_pipeline
from src.services.ai import extract_key_insights, generate_deep_dive_report, generate_research_plan
from src.config import settings

logger = logging.getLogger(__name__)

fetch_semaphore = asyncio.Semaphore(5)
_active_scrapes: Set[int] = set()
_scrape_guard = asyncio.Lock()


def get_search_results(query: str, timeframe: str, max_results=3):
    from duckduckgo_search import DDGS

    results = []
    tl = "m" if "1 Month" in timeframe else "y"

    def fetch():
        try:
            res = list(DDGS().text(query, timelimit=tl, max_results=max_results))
            results.extend(res)
        except Exception:
            logger.debug("DDGS query failed", exc_info=True)

    thread = threading.Thread(target=fetch, daemon=True)
    thread.start()
    thread.join(timeout=2.0)

    return results


async def _set_scrape_status(competitor_id: int, status: str, error: str | None = None) -> None:
    async with AsyncSessionLocal() as session:
        comp = (
            await session.execute(select(Competitor).where(Competitor.id == competitor_id))
        ).scalar_one_or_none()
        if comp:
            comp.scrape_status = status
            comp.scrape_error = error
            await session.commit()


async def _async_run_scraping_job(competitor_id: int, report_type: str = "Short"):
    async with _scrape_guard:
        if competitor_id in _active_scrapes:
            logger.info("Scrape already in progress for competitor_id=%s", competitor_id)
            return
        _active_scrapes.add(competitor_id)
    try:
        await _inner_run_scraping_job(competitor_id, report_type)
    finally:
        async with _scrape_guard:
            _active_scrapes.discard(competitor_id)


async def _inner_run_scraping_job(competitor_id: int, report_type: str = "Short"):
    user_id = ""
    competitor_name = ""
    try:
        await _set_scrape_status(competitor_id, "running", None)

        async with AsyncSessionLocal() as session:
            comp = (
                await session.execute(select(Competitor).where(Competitor.id == competitor_id))
            ).scalar_one_or_none()
            if not comp:
                return
            name = comp.name
            timeframe = comp.timeframe
            user_id = comp.user_id
            competitor_name = comp.name

        queries = await generate_research_plan(name, timeframe)

        all_snippets = []
        urls_to_scrape = []

        async def run_worker_agent(query):
            results = await asyncio.to_thread(get_search_results, query, timeframe, 3)
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

        urls_to_scrape = list(dict.fromkeys(urls_to_scrape))[:4]

        scraped_texts = []
        scraped_contexts: list[dict] = []

        try:
            import httpx
            from bs4 import BeautifulSoup

            async def fetch_page(url):
                if not is_safe_http_url(url):
                    return None
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (compatible; IntelScout/1.0; +https://intel-scout.vercel.app)"
                    }
                    async with fetch_semaphore:
                        async with httpx.AsyncClient(
                            timeout=4.0,
                            verify=settings.HTTP_VERIFY_SSL,
                            headers=headers,
                            follow_redirects=True,
                        ) as client:
                            resp = await client.get(url)
                            resp.raise_for_status()
                            if len(resp.content) > 2_000_000:
                                return None
                        soup = BeautifulSoup(resp.text, "html.parser")
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.extract()
                        text = soup.get_text(separator=" ", strip=True)
                        scraped_contexts.append(
                            {"source_type": "website", "content": text, "url": url}
                        )
                        return f"URL: {url}\nContent: {text[:2000]}"
                except Exception:
                    logger.debug("Failed to fetch url=%s", url, exc_info=True)
                    return None

            results = await asyncio.gather(*(fetch_page(url) for url in urls_to_scrape))
            scraped_texts = [r for r in results if r]

        except Exception as e:
            logger.warning("Scraping error: %s", type(e).__name__)

        final_research_data = (
            "--- DUCKDUCKGO SNIPPETS ---\n"
            + "\n\n".join(all_snippets)
            + "\n\n--- FULL SCRAPED PAGES ---\n"
            + "\n\n".join(scraped_texts)
        )

        report_task = generate_deep_dive_report(name, timeframe, final_research_data, report_type)
        insights_task = extract_key_insights(name, final_research_data)
        report_markdown, raw_insights = await asyncio.gather(report_task, insights_task)

        async with AsyncSessionLocal() as session:
            comp = (
                await session.execute(select(Competitor).where(Competitor.id == competitor_id))
            ).scalar_one_or_none()
            if comp:
                comp.report_markdown = report_markdown
                comp.raw_context = final_research_data
                comp.scrape_status = "completed"
                comp.scrape_error = None

                await session.execute(delete(Insight).where(Insight.competitor_id == comp.id))

                for ins in raw_insights:
                    session.add(
                        Insight(
                            competitor_id=comp.id,
                            title=ins.get("title", "Unknown"),
                            summary=ins.get("summary", ""),
                            category=ins.get("category", "Other"),
                            confidence_score=ins.get("confidence_score", 80),
                        )
                    )

                await session.commit()

        if scraped_contexts and user_id:
            try:
                from src.services.vector_db import upsert_multiple_contexts

                await upsert_multiple_contexts(competitor_name, user_id, scraped_contexts)
            except Exception:
                logger.warning("Vector upsert failed for competitor_id=%s", competitor_id, exc_info=True)

        try:
            await run_autonomous_pipeline(competitor_id)
        except Exception:
            logger.warning("Autonomous pipeline failed for competitor_id=%s", competitor_id, exc_info=True)

    except Exception as e:
        logger.exception("Deep research job failed for competitor_id=%s", competitor_id)
        await _set_scrape_status(competitor_id, "failed", str(e)[:500])


def run_scraping_job(competitor_id: int, report_type: str = "Short"):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(_async_run_scraping_job(competitor_id, report_type))
