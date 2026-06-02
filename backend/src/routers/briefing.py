from fastapi import APIRouter
from sqlalchemy.future import select
from datetime import datetime, timedelta
from ..database import AsyncSessionLocal
from ..models import Insight, Competitor
from ..services.ai import client, MODEL_NAME

router = APIRouter(prefix="/api/briefing", tags=["briefing"])

briefing_cache = {"time": None, "content": None}

@router.get("")
async def get_daily_briefing():
    global briefing_cache
    if briefing_cache["time"] and datetime.utcnow() - briefing_cache["time"] < timedelta(minutes=15):
        return {"briefing": briefing_cache["content"]}

    yesterday = datetime.utcnow() - timedelta(days=1)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Insight, Competitor).join(Competitor, Insight.competitor_id == Competitor.id).where(Insight.created_at >= yesterday)
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
    
    res = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    
    content = res.choices[0].message.content
    briefing_cache["time"] = datetime.utcnow()
    briefing_cache["content"] = content
    
    return {"briefing": content}
