from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy import desc
from ..database import AsyncSessionLocal
from ..models import Competitor, Alert, CompetitorSnapshot
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/{competitor_id}")
async def get_competitor_alerts(competitor_id: int, user_id: str = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        comp = (await session.execute(select(Competitor).where(Competitor.id == competitor_id, Competitor.user_id == user_id))).scalar_one_or_none()
        if not comp:
            raise HTTPException(status_code=404, detail="Competitor not found")
            
        alerts_result = await session.execute(
            select(Alert).where(Alert.competitor_id == competitor_id).order_by(desc(Alert.created_at)).limit(10)
        )
        alerts = alerts_result.scalars().all()
        
        snapshots_result = await session.execute(
            select(CompetitorSnapshot).where(CompetitorSnapshot.competitor_id == competitor_id).order_by(desc(CompetitorSnapshot.snapshot_date)).limit(5)
        )
        snapshots = snapshots_result.scalars().all()
        
        return {
            "alerts": alerts,
            "snapshots": snapshots
        }
