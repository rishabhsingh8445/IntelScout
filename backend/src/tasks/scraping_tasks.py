import sys
import asyncio
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import Competitor
from duckduckgo_search import DDGS
from src.services.ai import generate_deep_dive_report, generate_research_plan
from playwright.async_api import async_playwright

fetch_semaphore = asyncio.Semaphore(5)

def get_search_results(query: str, timeframe: str, max_results=3):
    import time
    from duckduckgo_search import DDGS
    import threading

    results = []
    tl = "m" if "1 Month" in timeframe else "y"

    # We use a worker thread to enforce a strict hard timeout for DDGS
    def fetch():
        try:
            res = list(DDGS().text(query, timelimit=tl, max_results=max_results))
            results.extend(res)
        except Exception:
            pass

    thread = threading.Thread(target=fetch)
    thread.start()
    thread.join(timeout=2.0) # STRICT 2 SECOND TIMEOUT
    
    return results

def get_niche_search_results(name: str):
    """
    Hyper-Niche Data Pipeline for Enterprise V2.0
    Targets specific domains where 'secrets' and early signals hide.
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        niche_queries = [
            f"site:reddit.com {name} (complaint OR opinion OR feature)",
            f"site:glassdoor.com {name} (layoffs OR hiring OR culture)",
            f"site:ycombinator.com {name} (launch OR pivot OR bug)"
        ]
        for q in niche_queries:
            try:
                res = list(DDGS().text(q, max_results=2))
                results.extend(res)
            except Exception:
                pass
        return results
    except Exception as e:
        print(f"Niche scraping error: {e}")
        return []

async def _async_run_scraping_job(competitor_id: int, report_type: str = "Short"):
    return await _inner_run_scraping_job(competitor_id, report_type)

async def _inner_run_scraping_job(competitor_id: int, report_type: str = "Short"):
    try:
        async with AsyncSessionLocal() as session:
            comp = (await session.execute(select(Competitor).where(Competitor.id == competitor_id))).scalar_one_or_none()
            if not comp: return
            name = comp.name
            timeframe = comp.timeframe

        # 1. Planner Agent Phase (LLM)
        queries = await generate_research_plan(name, timeframe)

        all_snippets = []
        urls_to_scrape = []

        # 2. Worker Agents Phase (Parallel DDGS)
        async def run_worker_agent(query):
            results = await asyncio.to_thread(get_search_results, query, timeframe, 3)
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
            
        # 2.5 Hyper-Niche Scraping Pipeline (Reddit, Glassdoor, HN)
        # niche_results = await asyncio.to_thread(get_niche_search_results, name)
        # for r in niche_results:
        #     link = r.get('url') or r.get('href')
        #     body = r.get('body') or r.get('title')
        #     if link and body:
        #         all_snippets.append(f"[NICHE SIGNAL] Source: {link}\nSnippet: {body}")
        #         urls_to_scrape.append(link)

        # Remove duplicates while preserving order
        urls_to_scrape = list(dict.fromkeys(urls_to_scrape))[:4] # Up to 4 deep reads

        scraped_texts = []
        
        # 2. Deep Reading Phase (httpx + BeautifulSoup)
        try:
            import httpx
            from bs4 import BeautifulSoup

            async def fetch_page(url):
                try:
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    async with fetch_semaphore:
                        async with httpx.AsyncClient(timeout=4.0, verify=False, headers=headers) as client:
                            resp = await client.get(url)
                            resp.raise_for_status()
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        # Remove script/style elements
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.extract()
                        text = soup.get_text(separator=' ', strip=True)
                        return f"URL: {url}\nContent: {text[:2000]}"
                except Exception:
                    return None

            results = await asyncio.gather(*(fetch_page(url) for url in urls_to_scrape))
            scraped_texts = [r for r in results if r]
            
        except Exception as e:
            print(f"Scraping error: {e}")

        # Combine snippets and texts
        final_research_data = "--- DUCKDUCKGO SNIPPETS ---\n" + "\n\n".join(all_snippets) + "\n\n--- FULL SCRAPED PAGES ---\n" + "\n\n".join(scraped_texts)

        # 3. Synthesis Phase + Insight Extraction (PARALLEL)
        from src.services.ai import extract_key_insights
        report_task = generate_deep_dive_report(name, timeframe, final_research_data, report_type)
        insights_task = extract_key_insights(name, final_research_data)
        report_markdown, raw_insights = await asyncio.gather(report_task, insights_task)

        # 4. Save to DB
        async with AsyncSessionLocal() as session:
            comp = (await session.execute(select(Competitor).where(Competitor.id == competitor_id))).scalar_one_or_none()
            if comp:
                comp.report_markdown = report_markdown
                comp.raw_context = final_research_data
                
                # Update insights
                from src.models import Insight
                from sqlalchemy import delete
                await session.execute(delete(Insight).where(Insight.competitor_id == comp.id))
                
                for ins in raw_insights:
                    new_ins = Insight(
                        competitor_id=comp.id,
                        title=ins.get("title", "Unknown"),
                        summary=ins.get("summary", ""),
                        category=ins.get("category", "Other"),
                        confidence_score=ins.get("confidence_score", 80)
                    )
                    session.add(new_ins)
                    
                await session.commit()

    except Exception as e:
        print(f"Exception in deep research job: {e}")

def run_scraping_job(competitor_id: int, report_type: str = "Short"):
    import sys
    import asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(_async_run_scraping_job(competitor_id, report_type))
