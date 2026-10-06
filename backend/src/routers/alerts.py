from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select

from ..database import AsyncSessionLocal
from ..dependencies import get_current_user
from ..models import Alert, Competitor, CompetitorSnapshot

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _serialize_alert(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "competitor_id": alert.competitor_id,
        "detected_changes": alert.detected_changes,
        "possible_goal": alert.possible_goal,
        "threat_level": alert.threat_level,
        "recommended_action": alert.recommended_action,
        "confidence_score": alert.confidence_score,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
    }


def _serialize_snapshot(snapshot: CompetitorSnapshot) -> dict:
    return {
        "id": snapshot.id,
        "competitor_id": snapshot.competitor_id,
        "snapshot_date": snapshot.snapshot_date.isoformat() if snapshot.snapshot_date else None,
        "pricing_data": snapshot.pricing_data,
        "feature_list": snapshot.feature_list,
        "messaging": snapshot.messaging,
        "sentiment": snapshot.sentiment,
        "sentiment_score": snapshot.sentiment_score,
        "sentiment_reason": snapshot.sentiment_reason,
    }


@router.get("/{competitor_id}")
async def get_competitor_alerts(competitor_id: int, user_id: str = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        comp = (
            await session.execute(
                select(Competitor).where(Competitor.id == competitor_id, Competitor.user_id == user_id)
            )
        ).scalar_one_or_none()
        if not comp:
            raise HTTPException(status_code=404, detail="Competitor not found")

        alerts_result = await session.execute(
            select(Alert).where(Alert.competitor_id == competitor_id).order_by(desc(Alert.created_at)).limit(10)
        )
        alerts = alerts_result.scalars().all()

        snapshots_result = await session.execute(
            select(CompetitorSnapshot)
            .where(CompetitorSnapshot.competitor_id == competitor_id)
            .order_by(desc(CompetitorSnapshot.snapshot_date))
            .limit(5)
        )
        snapshots = snapshots_result.scalars().all()

        return {
            "alerts": [_serialize_alert(a) for a in alerts],
            "snapshots": [_serialize_snapshot(s) for s in snapshots],
        }
