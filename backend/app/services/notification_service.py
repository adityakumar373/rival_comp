# app/services/notification_service.py
"""
Dispatcher service for real-time alert notifications.
Supports Slack, Discord, and generic Webhook endpoints.
"""

import httpx
from app.core.config import settings
from app.core.logger import get_logger
from app.models.alert import Alert
from app.models.ai_insight import AIInsight
from app.models.competitor import Competitor

logger = get_logger(__name__)


def dispatch_alert_notifications(alert: Alert, insight: AIInsight | None = None, competitor: Competitor | None = None) -> bool:
    """
    Sends real-time webhook notifications if configured in settings.
    Dispatches synchronously or via non-blocking HTTP requests.
    """
    comp_name = competitor.name if competitor else "Tracked Competitor"
    category = (insight.category.value if hasattr(insight.category, "value") else str(insight.category)) if insight else "Strategic Change"
    summary = insight.summary if insight else alert.message
    reasoning = insight.reasoning if insight else ""
    impact_score = alert.impact_score

    sent_any = False

    # 1. Slack Webhook
    if settings.SLACK_WEBHOOK_URL:
        slack_payload = {
            "text": f"🚨 *Rival Comp Alert: {comp_name}* (Impact: {impact_score}/100)",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 Competitive Shift Detected: {comp_name}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Category:*\n{category.title()}"},
                        {"type": "mrkdwn", "text": f"*Impact Score:*\n{impact_score}/100"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{summary}\n\n*Why it matters:*\n_{reasoning}_"
                    }
                }
            ]
        }
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(settings.SLACK_WEBHOOK_URL, json=slack_payload)
                if resp.status_code < 400:
                    sent_any = True
                    logger.info("slack_alert_dispatched", extra={"alert_id": str(alert.id)})
        except Exception as exc:
            logger.error("slack_dispatch_failed", extra={"error": str(exc), "alert_id": str(alert.id)})

    # 2. Discord Webhook
    if settings.DISCORD_WEBHOOK_URL:
        color = 15158332 if impact_score >= 70 else 15844367  # Red or Gold
        discord_payload = {
            "content": f"🚨 **Rival Comp Strategic Alert** for **{comp_name}**",
            "embeds": [
                {
                    "title": f"Shift in {category.title()} — Score: {impact_score}/100",
                    "description": f"**Summary:** {summary}\n\n**Reasoning:** {reasoning}",
                    "color": color,
                    "footer": {"text": "Rival Comp AI Market Intelligence"}
                }
            ]
        }
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(settings.DISCORD_WEBHOOK_URL, json=discord_payload)
                if resp.status_code < 400:
                    sent_any = True
                    logger.info("discord_alert_dispatched", extra={"alert_id": str(alert.id)})
        except Exception as exc:
            logger.error("discord_dispatch_failed", extra={"error": str(exc), "alert_id": str(alert.id)})

    # 3. Generic JSON Webhook
    if settings.GENERIC_WEBHOOK_URL:
        generic_payload = {
            "event": "competitor.alert",
            "alert_id": str(alert.id),
            "competitor_id": str(alert.competitor_id),
            "competitor_name": comp_name,
            "category": category,
            "impact_score": impact_score,
            "summary": summary,
            "reasoning": reasoning,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        }
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(settings.GENERIC_WEBHOOK_URL, json=generic_payload)
                if resp.status_code < 400:
                    sent_any = True
                    logger.info("generic_webhook_dispatched", extra={"alert_id": str(alert.id)})
        except Exception as exc:
            logger.error("generic_webhook_failed", extra={"error": str(exc), "alert_id": str(alert.id)})

    return sent_any
