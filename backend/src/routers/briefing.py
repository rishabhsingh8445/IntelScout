from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from ..database import AsyncSessionLocal
from ..models import Insight, Competitor
from ..services.ai import client, MODEL_NAME
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/briefing", tags=["briefing"])

from collections import OrderedDict
import time

_CACHE_TTL_SECONDS = 900
_CACHE_MAX = 64
_briefing_cache: OrderedDict[str, tuple[float, str]] = OrderedDict()


def _briefing_cache_get(key: str) -> str | None:
    entry = _briefing_cache.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > _CACHE_TTL_SECONDS:
        _briefing_cache.pop(key, None)
        return None
    return value


def _briefing_cache_set(key: str, value: str) -> None:
    _briefing_cache[key] = (time.time(), value)
    _briefing_cache.move_to_end(key)
    while len(_briefing_cache) > _CACHE_MAX:
        _briefing_cache.popitem(last=False)


@router.get("")
async def get_daily_briefing(user_id: str = Depends(get_current_user)):
    cached_content = _briefing_cache_get(user_id)
    if cached_content:
        return {"briefing": cached_content}

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Insight, Competitor).join(Competitor, Insight.competitor_id == Competitor.id).where(
                Insight.created_at >= yesterday, 
                Competitor.user_id == user_id
            )
        )
        rows = result.all()
    
    if not rows:
        return {"briefing": "No new significant activities detected in the last 24 hours across your watched competitors."}
        
    insight_texts = "\n".join([f"- {comp.name}: {ins.title} - {ins.summary}" for ins, comp in rows])
    
    prompt = f"""
    You are an elite Chief of Staff. Summarize the following raw market signals from the last 24 hours into a concise, 3-bullet "Daily Executive Briefing" for the CEO.
    
    Raw Signals:
    {insight_texts[:5000]}
    
    Format:
    Focus strictly on business impact (new products, pricing changes, acquisitions, key hires). Ignore noise.
    Keep it strictly to 3 bullet points using Markdown. Be extremely brief and punchy.
    """
    
    try:
        from ..services.ai import llm_semaphore
        async with llm_semaphore:
            res = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
                timeout=30.0
            )
        content = res.choices[0].message.content
        _briefing_cache_set(user_id, content)
        return {"briefing": content}
    except Exception as e:
        return {"briefing": "Failed to generate daily briefing due to temporary AI service disruption."}
