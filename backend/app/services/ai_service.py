# app/services/ai_service.py
"""
Sends a detected change's diff to Gemini and gets back a structured
classification: category, plain-language summary, reasoning (why it
matters), an impact score (0-100), and the model's own confidence.

Design choices (see README for the fuller justification):
- Structured JSON output, not prose — this feeds alerts/dashboard,
  not a chat window.
- Never blocks scraping: if GEMINI_API_KEY isn't set, or the API call
  fails, this logs and returns None rather than raising — a scrape
  should still succeed even if classification is unavailable.
- reasoning is stored verbatim next to impact_score so every score is
  auditable, never a bare number.
"""

import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models.ai_insight import AIInsight, InsightCategory
from app.models.change_detected import ChangeDetected
from app.models.source import Source
from app.models.competitor import Competitor

logger = get_logger(__name__)

_MAX_DIFF_CHARS_IN_PROMPT = 4000

_PROMPT_TEMPLATE = """You are a competitive intelligence analyst. A monitored source changed.

Competitor: {competitor_name} ({industry})
Source type: {source_type}
Source URL: {source_url}
Lines added: {lines_added}, Lines removed: {lines_removed}
Text similarity to previous version: {similarity_ratio:.2%}

Unified diff (+ added, - removed):
---
{diff_text}
---

Classify this change and respond with ONLY a JSON object (no markdown fences, no extra text) with exactly these keys:
{{
  "category": one of "pricing", "hiring", "product", "partnership", "marketing", "news", "market_activity", "other",
  "summary": "1-2 sentence plain-language summary of what changed",
  "reasoning": "1-3 sentences on why this matters and the potential business impact",
  "impact_score": integer 0-100, how significant this is competitively (0=noise, 100=major strategic event),
  "confidence_score": float 0.0-1.0, your confidence in this classification
}}
"""


def _build_prompt(change: ChangeDetected, source: Source, competitor: Competitor) -> str:
    return _PROMPT_TEMPLATE.format(
        competitor_name=competitor.name,
        industry=competitor.industry or "unknown",
        source_type=source.source_type.value if hasattr(source.source_type, "value") else source.source_type,
        source_url=source.url,
        lines_added=change.lines_added,
        lines_removed=change.lines_removed,
        similarity_ratio=change.similarity_ratio,
        diff_text=change.diff_text[:_MAX_DIFF_CHARS_IN_PROMPT],
    )


def _parse_response(raw_text: str) -> dict | None:
    text = raw_text.strip()
    # Gemini sometimes wraps JSON in ```json fences despite instructions.
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.error("ai_response_not_json", extra={"raw": raw_text[:500]})
        return None

    category = data.get("category", "other")
    if category not in InsightCategory._value2member_map_:
        category = "other"

    try:
        impact_score = max(0, min(100, int(data["impact_score"])))
        confidence_score = max(0.0, min(1.0, float(data["confidence_score"])))
        summary = str(data["summary"])
        reasoning = str(data["reasoning"])
    except (KeyError, ValueError, TypeError):
        logger.error("ai_response_missing_fields", extra={"raw": raw_text[:500]})
        return None

    return {
        "category": category,
        "summary": summary,
        "reasoning": reasoning,
        "impact_score": impact_score,
        "confidence_score": confidence_score,
    }


def _call_gemini(prompt: str) -> str | None:
    if not settings.GEMINI_API_KEY:
        logger.warning("gemini_not_configured", extra={"reason": "GEMINI_API_KEY not set"})
        return None

    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        settings.GEMINI_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )
    response = model.generate_content(prompt)
    return response.text


def classify_change(db: Session, change: ChangeDetected) -> AIInsight | None:
    """
    Classifies a ChangeDetected row via Gemini and stores the result
    as an AIInsight. Returns None (logs, doesn't raise) if Gemini isn't
    configured or the call/parse fails — classification is best-effort,
    scraping must not depend on it succeeding.
    """
    source = db.query(Source).filter(Source.id == change.source_id).first()
    competitor = db.query(Competitor).filter(Competitor.id == source.competitor_id).first()

    prompt = _build_prompt(change, source, competitor)

    try:
        raw_text = _call_gemini(prompt)
    except Exception as exc:  # noqa: BLE001 - never let AI failures break scraping
        logger.error(
            "gemini_call_failed",
            extra={"change_id": str(change.id), "error": str(exc)},
        )
        return None

    if raw_text is None:
        return None

    parsed = _parse_response(raw_text)
    if parsed is None:
        return None

    insight = AIInsight(
        change_id=change.id,
        competitor_id=competitor.id,
        source_id=source.id,
        category=parsed["category"],
        summary=parsed["summary"],
        reasoning=parsed["reasoning"],
        impact_score=parsed["impact_score"],
        confidence_score=parsed["confidence_score"],
    )
    db.add(insight)

    # Back-fill the human-readable summary onto the change row too,
    # so a change can be scanned without joining to ai_insights.
    change.change_summary = parsed["summary"]

    db.flush()  # assigns insight.id; caller commits

    logger.info(
        "change_classified",
        extra={
            "change_id": str(change.id),
            "insight_id": str(insight.id),
            "category": parsed["category"],
            "impact_score": parsed["impact_score"],
        },
    )
    return insight


def list_insights_for_competitor(
    db: Session, competitor_id: UUID, skip: int = 0, limit: int = 50
) -> list[AIInsight]:
    return (
        db.query(AIInsight)
        .filter(AIInsight.competitor_id == competitor_id)
        .order_by(AIInsight.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_insight(db: Session, insight_id: UUID) -> AIInsight | None:
    return db.query(AIInsight).filter(AIInsight.id == insight_id).first()


def list_all_insights(
    db: Session,
    category: str | None = None,
    min_impact: int = 0,
    skip: int = 0,
    limit: int = 50,
) -> list[AIInsight]:
    """Cross-competitor insights feed sorted by impact_score desc, enriched with source_url & competitor_name."""
    query = (
        db.query(AIInsight, Source.url.label("source_url"), Competitor.name.label("comp_name"))
        .join(Source, AIInsight.source_id == Source.id)
        .join(Competitor, AIInsight.competitor_id == Competitor.id)
    )
    if category:
        query = query.filter(AIInsight.category == category)
    if min_impact > 0:
        query = query.filter(AIInsight.impact_score >= min_impact)

    rows = (
        query
        .order_by(AIInsight.impact_score.desc(), AIInsight.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Attach enriched fields directly onto the ORM objects
    insights = []
    for row in rows:
        insight = row.AIInsight
        insight.source_url = row.source_url
        insight.competitor_name = row.comp_name
        insights.append(insight)

    return insights
