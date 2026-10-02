# app/services/dashboard_service.py
"""
Read-only aggregation queries for the dashboard. No writes happen
here — this layer just shapes data that's already been produced by
scraping / change detection / AI classification / alerting.
"""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.competitor import Competitor
from app.models.source import Source
from app.models.ai_insight import AIInsight, InsightCategory
from app.models.alert import Alert
from app.models.change_detected import ChangeDetected


def competitor_overview(db: Session) -> list[dict]:
    """
    One row per active competitor: source count, most recent scrape
    time across all its sources, total insights, average impact
    score, and how many alerts are still unsent.
    """
    competitors = (
        db.query(Competitor).filter(Competitor.is_active.is_(True)).all()
    )

    results = []
    for competitor in competitors:
        source_count = (
            db.query(func.count(Source.id))
            .filter(Source.competitor_id == competitor.id, Source.is_active.is_(True))
            .scalar()
        )
        last_scraped_at = (
            db.query(func.max(Source.last_scraped))
            .filter(Source.competitor_id == competitor.id)
            .scalar()
        )
        insight_count = (
            db.query(func.count(AIInsight.id))
            .filter(AIInsight.competitor_id == competitor.id)
            .scalar()
        )
        avg_impact_score = (
            db.query(func.avg(AIInsight.impact_score))
            .filter(AIInsight.competitor_id == competitor.id)
            .scalar()
        )
        unsent_alert_count = (
            db.query(func.count(Alert.id))
            .filter(Alert.competitor_id == competitor.id, Alert.sent_at.is_(None))
            .scalar()
        )

        results.append({
            "competitor_id": competitor.id,
            "name": competitor.name,
            "industry": competitor.industry,
            "source_count": source_count or 0,
            "last_scraped_at": last_scraped_at,
            "insight_count": insight_count or 0,
            "avg_impact_score": round(float(avg_impact_score), 1) if avg_impact_score else None,
            "unsent_alert_count": unsent_alert_count or 0,
        })

    return results


def competitor_detail(db: Session, competitor_id: UUID) -> dict | None:
    """
    Full detail for one competitor: its sources (with last scrape
    time), its most recent insights, and its most recent alerts.
    """
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        return None

    sources = (
        db.query(Source)
        .filter(Source.competitor_id == competitor_id, Source.is_active.is_(True))
        .order_by(Source.created_at.desc())
        .all()
    )

    recent_insights = (
        db.query(AIInsight)
        .filter(AIInsight.competitor_id == competitor_id)
        .order_by(AIInsight.created_at.desc())
        .limit(20)
        .all()
    )

    recent_alerts = (
        db.query(Alert)
        .filter(Alert.competitor_id == competitor_id)
        .order_by(Alert.created_at.desc())
        .limit(20)
        .all()
    )

    # Enrich insights with source_url for evidence links
    source_map = {s.id: s.url for s in sources}
    # Also include inactive sources referenced by old insights
    all_source_ids = {i.source_id for i in recent_insights} - set(source_map.keys())
    if all_source_ids:
        extra = db.query(Source).filter(Source.id.in_(all_source_ids)).all()
        for s in extra:
            source_map[s.id] = s.url
    for insight in recent_insights:
        insight.source_url = source_map.get(insight.source_id)

    return {
        "competitor": competitor,
        "sources": sources,
        "recent_insights": recent_insights,
        "recent_alerts": recent_alerts,
    }


def get_analytics_summary(db: Session) -> dict:
    """
    Returns aggregated analytics across all competitors:
    - total insights, changes, alerts
    - category breakdown (count per category)
    - top 5 highest-impact insights (with competitor name + source URL)
    - per-competitor activity bar chart data
    """
    from app.models.source import Source

    total_insights = db.query(func.count(AIInsight.id)).scalar() or 0
    total_changes = db.query(func.count(ChangeDetected.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    avg_impact = db.query(func.avg(AIInsight.impact_score)).scalar()

    # Category breakdown
    category_rows = (
        db.query(AIInsight.category, func.count(AIInsight.id).label("cnt"))
        .group_by(AIInsight.category)
        .all()
    )
    category_breakdown = [
        {"category": row.category.value if hasattr(row.category, "value") else str(row.category),
         "count": row.cnt}
        for row in category_rows
    ]

    # Top 5 highest-impact insights with competitor name and source URL
    top_insights_rows = (
        db.query(AIInsight, Competitor.name.label("comp_name"), Source.url.label("source_url"))
        .join(Competitor, AIInsight.competitor_id == Competitor.id)
        .join(Source, AIInsight.source_id == Source.id)
        .order_by(AIInsight.impact_score.desc())
        .limit(5)
        .all()
    )
    top_insights = [
        {
            "id": str(row.AIInsight.id),
            "competitor_name": row.comp_name,
            "source_url": row.source_url,
            "category": row.AIInsight.category.value if hasattr(row.AIInsight.category, "value") else str(row.AIInsight.category),
            "summary": row.AIInsight.summary,
            "reasoning": row.AIInsight.reasoning,
            "impact_score": row.AIInsight.impact_score,
            "confidence_score": row.AIInsight.confidence_score,
            "created_at": row.AIInsight.created_at.isoformat() if row.AIInsight.created_at else None,
        }
        for row in top_insights_rows
    ]

    # Per-competitor activity (insight count + avg impact) for bar chart
    competitors = db.query(Competitor).filter(Competitor.is_active.is_(True)).all()
    competitor_activity = []
    for c in competitors:
        cnt = db.query(func.count(AIInsight.id)).filter(AIInsight.competitor_id == c.id).scalar() or 0
        avg = db.query(func.avg(AIInsight.impact_score)).filter(AIInsight.competitor_id == c.id).scalar()
        competitor_activity.append({
            "competitor_id": str(c.id),
            "name": c.name,
            "insight_count": cnt,
            "avg_impact_score": round(float(avg), 1) if avg else 0,
        })

    return {
        "total_insights": total_insights,
        "total_changes": total_changes,
        "total_alerts": total_alerts,
        "avg_impact_score": round(float(avg_impact), 1) if avg_impact else None,
        "category_breakdown": category_breakdown,
        "top_insights": top_insights,
        "competitor_activity": competitor_activity,
    }
