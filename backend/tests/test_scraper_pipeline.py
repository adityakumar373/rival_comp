# tests/test_scraper_pipeline.py
import uuid
from unittest.mock import MagicMock, patch
import pytest

from app.models.competitor import Competitor
from app.models.source import Source, SourceType
from app.models.content_version import ContentVersion
from app.models.scraped_content import ScrapedContent
from app.models.change_detected import ChangeDetected
from app.models.ai_insight import AIInsight, InsightCategory
from app.models.alert import Alert
from app.services import scraper_service, alert_service


def test_scraper_pipeline_first_scrape():
    """First scrape creates ScrapedContent and ContentVersion 1, but no ChangeDetected."""
    source_id = uuid.uuid4()
    competitor_id = uuid.uuid4()

    source = Source(
        id=source_id,
        competitor_id=competitor_id,
        source_type=SourceType.PRICING_PAGE,
        url="https://example.com/pricing",
        scrape_frequency=1440,
        is_active=True,
    )

    db = MagicMock()

    def mock_query(model):
        q = MagicMock()
        if model == Source:
            q.filter.return_value.first.return_value = source
        elif model == ContentVersion:
            # Both .order_by().first() and .filter().first() return None for first scrape
            q.filter.return_value.order_by.return_value.first.return_value = None
            q.filter.return_value.first.return_value = None
        return q

    db.query.side_effect = mock_query

    with patch.object(scraper_service, "_fetch", return_value=(200, "<html>Starter $10</html>", "Starter $10")):
        result = scraper_service.scrape_source(db, source_id)

    assert result["status_code"] == 200
    assert result["changed"] is True
    assert result["version_number"] == 1
    assert result["change_id"] is None
    assert result["insight_id"] is None
    assert result["alert_id"] is None
    assert result["error"] is None

    assert db.add.call_count >= 2
    db.commit.assert_called_once()


def test_scraper_pipeline_identical_second_scrape():
    """Second scrape with identical content creates ScrapedContent but no new ContentVersion."""
    source_id = uuid.uuid4()
    competitor_id = uuid.uuid4()

    source = Source(
        id=source_id,
        competitor_id=competitor_id,
        source_type=SourceType.PRICING_PAGE,
        url="https://example.com/pricing",
        scrape_frequency=1440,
        is_active=True,
    )

    text = "Starter $10"
    from app.utils.hash_utils import generate_hash
    content_hash = generate_hash(text)

    existing_v1 = ContentVersion(
        id=uuid.uuid4(),
        source_id=source_id,
        version_number=1,
        content=text,
        hash=content_hash,
    )

    db = MagicMock()

    def mock_query(model):
        q = MagicMock()
        if model == Source:
            q.filter.return_value.first.return_value = source
        elif model == ContentVersion:
            q.filter.return_value.order_by.return_value.first.return_value = existing_v1
            q.filter.return_value.first.return_value = existing_v1
        return q

    db.query.side_effect = mock_query

    with patch.object(scraper_service, "_fetch", return_value=(200, "<html>Starter $10</html>", text)):
        result = scraper_service.scrape_source(db, source_id)

    assert result["status_code"] == 200
    assert result["changed"] is False
    assert result["version_number"] is None
    assert result["change_id"] is None
    assert result["error"] is None
    db.commit.assert_called_once()


def test_scraper_pipeline_changed_scrape_with_ai_and_alert():
    """Changed scrape generates ContentVersion v2, ChangeDetected, AI Insight, and Alert."""
    source_id = uuid.uuid4()
    competitor_id = uuid.uuid4()

    competitor = Competitor(
        id=competitor_id,
        name="TestCorp",
        website="https://example.com",
        industry="SaaS",
    )

    source = Source(
        id=source_id,
        competitor_id=competitor_id,
        source_type=SourceType.PRICING_PAGE,
        url="https://example.com/pricing",
        scrape_frequency=1440,
        is_active=True,
    )

    old_text = "Starter $10"
    new_text = "Starter $25 (Enterprise Edition)"

    from app.utils.hash_utils import generate_hash
    old_hash = generate_hash(old_text)

    existing_v1 = ContentVersion(
        id=uuid.uuid4(),
        source_id=source_id,
        version_number=1,
        content=old_text,
        hash=old_hash,
    )

    change_obj = ChangeDetected(
        id=uuid.uuid4(),
        source_id=source_id,
        previous_version_id=existing_v1.id,
        new_version_id=uuid.uuid4(),
        lines_added=1,
        lines_removed=1,
        similarity_ratio=0.5,
        diff_text="-Starter $10\n+Starter $25",
    )

    insight_obj = AIInsight(
        id=uuid.uuid4(),
        change_id=change_obj.id,
        competitor_id=competitor_id,
        source_id=source_id,
        category=InsightCategory.PRICING,
        summary="Raised starter price to $25",
        reasoning="Aggressive expansion into higher ARPU segments",
        impact_score=85,
        confidence_score=0.95,
    )

    alert_obj = Alert(
        id=uuid.uuid4(),
        insight_id=insight_obj.id,
        competitor_id=competitor_id,
        message="[pricing] Raised starter price to $25",
        impact_score=85,
    )

    db = MagicMock()

    def mock_query(model):
        q = MagicMock()
        if model == Source:
            q.filter.return_value.first.return_value = source
        elif model == ContentVersion:
            q.filter.return_value.order_by.return_value.first.return_value = existing_v1
            q.filter.return_value.first.return_value = existing_v1
        elif model == Competitor:
            q.filter.return_value.first.return_value = competitor
        return q

    db.query.side_effect = mock_query

    with patch.object(scraper_service, "_fetch", return_value=(200, "<html>Starter $25</html>", new_text)), \
         patch("app.services.change_detection_service.detect_change", return_value=change_obj), \
         patch("app.services.ai_service.classify_change", return_value=insight_obj), \
         patch("app.services.alert_service.maybe_create_alert", return_value=alert_obj):

        result = scraper_service.scrape_source(db, source_id)

    assert result["status_code"] == 200
    assert result["changed"] is True
    assert result["version_number"] == 2
    assert result["change_id"] == change_obj.id
    assert result["insight_id"] == insight_obj.id
    assert result["alert_id"] == alert_obj.id
    assert result["error"] is None
    db.commit.assert_called_once()


def test_scraper_pipeline_ai_failure_graceful_degradation():
    """If AI classification fails, scraping and change detection still succeed."""
    source_id = uuid.uuid4()
    competitor_id = uuid.uuid4()

    source = Source(
        id=source_id,
        competitor_id=competitor_id,
        source_type=SourceType.PRICING_PAGE,
        url="https://example.com/pricing",
        scrape_frequency=1440,
        is_active=True,
    )

    existing_v1 = ContentVersion(
        id=uuid.uuid4(),
        source_id=source_id,
        version_number=1,
        content="Old",
        hash="oldhash",
    )

    change_obj = ChangeDetected(
        id=uuid.uuid4(),
        source_id=source_id,
        previous_version_id=existing_v1.id,
        new_version_id=uuid.uuid4(),
        lines_added=1,
        lines_removed=0,
        similarity_ratio=0.5,
        diff_text="+New feature",
    )

    db = MagicMock()

    def mock_query(model):
        q = MagicMock()
        if model == Source:
            q.filter.return_value.first.return_value = source
        elif model == ContentVersion:
            q.filter.return_value.order_by.return_value.first.return_value = existing_v1
            q.filter.return_value.first.return_value = existing_v1
        return q

    db.query.side_effect = mock_query

    with patch.object(scraper_service, "_fetch", return_value=(200, "<html>New</html>", "New")), \
         patch("app.services.change_detection_service.detect_change", return_value=change_obj), \
         patch("app.services.ai_service.classify_change", return_value=None):

        result = scraper_service.scrape_source(db, source_id)

    assert result["status_code"] == 200
    assert result["changed"] is True
    assert result["version_number"] == 2
    assert result["change_id"] == change_obj.id
    assert result["insight_id"] is None
    assert result["alert_id"] is None
    assert result["error"] is None
    db.commit.assert_called_once()
