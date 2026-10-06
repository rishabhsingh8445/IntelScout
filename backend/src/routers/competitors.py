from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Competitor, Insight
from ..services.ai import answer_rag_question
from ..services.predictive_engine import generate_future_predictions
from ..tasks.scraping_tasks import _async_run_scraping_job

router = APIRouter(prefix="/api", tags=["api"])


def _public_status(comp: Competitor) -> str:
    if comp.scrape_status == "failed":
        return "Failed"
    if comp.scrape_status in ("running", "pending") or not comp.report_markdown:
        return "Researching..."
    return "Active"


@router.post("/competitors")
async def add_competitor(
    background_tasks: BackgroundTasks,
    name: str = Query(..., min_length=1, max_length=200),
    timeframe: str = Query("Since Launch", max_length=64),
    report_type: str = Query("Short", max_length=32),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    comp = Competitor(name=name.strip(), timeframe=timeframe, user_id=user_id, scrape_status="pending")
    db.add(comp)
    await db.commit()
    await db.refresh(comp)

    background_tasks.add_task(_async_run_scraping_job, comp.id, report_type)

    return {"message": "Competitor added and scraping started.", "competitor_id": comp.id}


@router.get("/competitors")
async def list_competitors(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    result = await db.execute(
        select(Competitor)
        .where(Competitor.user_id == user_id)
        .options(selectinload(Competitor.items), selectinload(Competitor.insights))
    )
    competitors = result.scalars().all()

    data = []
    for c in competitors:
        data.append(
            {
                "id": c.id,
                "name": c.name,
                "timeframe": c.timeframe,
                "status": _public_status(c),
                "scrape_status": getattr(c, "scrape_status", "pending"),
                "scrape_error": c.scrape_error,
                "report": c.report_markdown,
                "is_watched": c.is_watched,
                "lastScraped": "Just now" if c.report_markdown else "In progress",
            }
        )
    return data


@router.get("/insights")
async def get_all_insights(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    subquery = select(Competitor.id).where(Competitor.user_id == user_id)
    result = await db.execute(
        select(Insight)
        .where(Insight.competitor_id.in_(subquery))
        .options(selectinload(Insight.competitor))
        .order_by(Insight.created_at.desc())
    )
    insights = result.scalars().all()

    data = []
    for i in insights:
        data.append(
            {
                "id": i.id,
                "competitor_id": i.competitor_id,
                "competitor": i.competitor.name,
                "category": i.category or "Other",
                "title": i.title,
                "summary": i.summary,
                "time": "Just now",
                "score": i.confidence_score or 85,
                "sourceUrl": "",
            }
        )
    return data


@router.post("/competitors/{competitor_id}/rescrape")
async def rescrape_competitor(
    competitor_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    comp = (
        await db.execute(select(Competitor).where(Competitor.id == competitor_id, Competitor.user_id == user_id))
    ).scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    comp.scrape_status = "pending"
    comp.scrape_error = None
    await db.commit()
    background_tasks.add_task(_async_run_scraping_job, comp.id, "Long")
    return {"message": "Rescraping triggered"}


@router.post("/competitors/{competitor_id}/watch")
async def toggle_watch_competitor(
    competitor_id: int, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)
):
    comp = (
        await db.execute(select(Competitor).where(Competitor.id == competitor_id, Competitor.user_id == user_id))
    ).scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    comp.is_watched = not comp.is_watched
    await db.commit()
    return {"message": "Watch status updated", "is_watched": comp.is_watched}


@router.delete("/competitors/{competitor_id}")
async def delete_competitor(
    competitor_id: int, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)
):
    comp = (
        await db.execute(select(Competitor).where(Competitor.id == competitor_id, Competitor.user_id == user_id))
    ).scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    await db.delete(comp)
    await db.commit()
    return {"message": "Competitor deleted successfully"}


@router.post("/trigger-alerts")
async def trigger_alerts(
    background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)
):
    result = await db.execute(select(Competitor).where(Competitor.is_watched == True, Competitor.user_id == user_id))
    watched_comps = result.scalars().all()
    for comp in watched_comps:
        background_tasks.add_task(_async_run_scraping_job, comp.id, "Short")
    return {"message": f"Successfully checked {len(watched_comps)} watched competitors."}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


@router.post("/competitors/{competitor_id}/chat")
async def chat_with_competitor(
    competitor_id: int,
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    comp = (
        await db.execute(select(Competitor).where(Competitor.id == competitor_id, Competitor.user_id == user_id))
    ).scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    if not comp.raw_context:
        return {
            "answer": "This report was generated before the chat feature was added. Please run a new deep research to use chat."
        }

    answer = await answer_rag_question(req.message, comp.raw_context)
    return {"answer": answer}


@router.get("/competitors/{competitor_id}/predictions")
async def get_predictions(
    competitor_id: int, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)
):
    comp = (
        await db.execute(
            select(Competitor)
            .options(selectinload(Competitor.insights))
            .where(Competitor.id == competitor_id, Competitor.user_id == user_id)
        )
    ).scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    insights = [{"title": i.title, "summary": i.summary, "category": i.category} for i in comp.insights]
    predictions_md = await generate_future_predictions(comp.name, insights)
    return {"predictions": predictions_md}
