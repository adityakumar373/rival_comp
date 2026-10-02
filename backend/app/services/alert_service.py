# app/services/alert_service.py
"""
Turns a high-impact AIInsight into an Alert row and optionally
dispatches instant webhook notifications (Slack/Discord/Custom).
"""

from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models.ai_insight import AIInsight
from app.models.alert import Alert
from app.models.competitor import Competitor

logger = get_logger(__name__)


def maybe_create_alert(db: Session, insight: AIInsight) -> Alert | None:
    """
    Creates an Alert if insight.impact_score >= settings.ALERT_IMPACT_THRESHOLD.
    Also dispatches to Slack/Discord/Webhooks if configured.
    """
    if insight.impact_score < settings.ALERT_IMPACT_THRESHOLD:
        return None

    message = f"[{insight.category.value if hasattr(insight.category, 'value') else insight.category}] {insight.summary}"

    alert = Alert(
        insight_id=insight.id,
        competitor_id=insight.competitor_id,
        message=message,
        impact_score=insight.impact_score,
    )
    db.add(alert)
    db.flush()  # assigns alert.id; caller commits

    # Dispatch webhooks if configured
    try:
        from app.services.notification_service import dispatch_alert_notifications
        competitor = db.query(Competitor).filter(Competitor.id == insight.competitor_id).first()
        dispatched = dispatch_alert_notifications(alert, insight=insight, competitor=competitor)
        if dispatched:
            alert.sent_at = datetime.now(timezone.utc)
    except Exception as exc:
        logger.error("alert_webhook_dispatch_error", extra={"error": str(exc), "alert_id": str(alert.id)})

    logger.info(
        "alert_created",
        extra={
            "alert_id": str(alert.id),
            "insight_id": str(insight.id),
            "impact_score": insight.impact_score,
            "dispatched": alert.sent_at is not None,
        },
    )
    return alert


def list_alerts_for_competitor(
    db: Session, competitor_id: UUID, unsent_only: bool = False, skip: int = 0, limit: int = 50
) -> list[Alert]:
    query = db.query(Alert).filter(Alert.competitor_id == competitor_id)
    if unsent_only:
        query = query.filter(Alert.sent_at.is_(None))
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def mark_alert_sent(db: Session, alert_id: UUID) -> Alert | None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    alert.sent_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


def list_all_alerts(
    db: Session,
    unsent_only: bool = False,
    min_impact: int = 0,
    skip: int = 0,
    limit: int = 50,
) -> list[Alert]:
    """Cross-competitor alert feed sorted by impact_score desc, then created_at desc."""
    query = db.query(Alert)
    if unsent_only:
        query = query.filter(Alert.sent_at.is_(None))
    if min_impact > 0:
        query = query.filter(Alert.impact_score >= min_impact)
    return (
        query
        .order_by(Alert.impact_score.desc(), Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
