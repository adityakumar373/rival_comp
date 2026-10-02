# tests/test_change_detection.py
import uuid
import datetime
from unittest.mock import MagicMock, patch
import difflib
import pytest

from app.models.content_version import ContentVersion
from app.models.change_detected import ChangeDetected
from app.schemas.change import ChangeDetectedResponse
from app.services import change_detection_service


def test_difflib_unified_diff_pricing_change():
    """Detects price shift from $29 to $49 accurately."""
    old_lines = ["Welcome to Our Platform", "Pricing: $29/mo", "Features: AI Search"]
    new_lines = ["Welcome to Our Platform", "Pricing: $49/mo", "Features: AI Search", "New: Team Collaboration"]

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    similarity = matcher.ratio()

    diff_lines = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    lines_added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    lines_removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    assert lines_added == 2
    assert lines_removed == 1
    assert 0.0 < similarity < 1.0
    assert any("+Pricing: $49/mo" in line for line in diff_lines)
    assert any("-Pricing: $29/mo" in line for line in diff_lines)


def test_difflib_identical_text():
    """Identical text produces similarity 1.0 and zero diff lines."""
    lines = ["Static Header", "Constant Feature 1", "Footer Info"]
    matcher = difflib.SequenceMatcher(None, lines, lines)
    assert matcher.ratio() == 1.0


def test_change_detected_model_instantiation():
    """Verifies that the ChangeDetected model accepts all migration 0005/0009 fields."""
    source_id = uuid.uuid4()
    prev_id = uuid.uuid4()
    new_id = uuid.uuid4()

    change = ChangeDetected(
        source_id=source_id,
        previous_version_id=prev_id,
        new_version_id=new_id,
        lines_added=5,
        lines_removed=2,
        similarity_ratio=0.85,
        diff_text="@@ -1 +1 @@\n-old\n+new",
        change_summary="Price increased from $10 to $20",
    )

    assert change.source_id == source_id
    assert change.previous_version_id == prev_id
    assert change.new_version_id == new_id
    assert change.lines_added == 5
    assert change.lines_removed == 2
    assert change.similarity_ratio == 0.85
    assert change.diff_text == "@@ -1 +1 @@\n-old\n+new"
    assert change.change_summary == "Price increased from $10 to $20"


def test_change_detected_pydantic_v2_serialization():
    """Verifies that ChangeDetectedResponse serializes ORM objects without deprecation errors."""
    source_id = uuid.uuid4()
    prev_id = uuid.uuid4()
    new_id = uuid.uuid4()
    change_id = uuid.uuid4()
    now = datetime.datetime.now(datetime.timezone.utc)

    change = ChangeDetected(
        id=change_id,
        source_id=source_id,
        previous_version_id=prev_id,
        new_version_id=new_id,
        lines_added=3,
        lines_removed=1,
        similarity_ratio=0.92,
        diff_text="+new feature",
        change_summary="Added feature",
        detected_at=now,
    )

    schema = ChangeDetectedResponse.model_validate(change)
    assert schema.id == change_id
    assert schema.source_id == source_id
    assert schema.lines_added == 3
    assert schema.lines_removed == 1
    assert schema.similarity_ratio == 0.92
    assert schema.diff_text == "+new feature"
    assert schema.change_summary == "Added feature"


def test_detect_change_first_version_returns_none():
    """First version of a source has no previous version to diff against and returns None."""
    db = MagicMock()
    # Mock query returning no previous version
    db.query.return_value.filter.return_value.first.return_value = None

    v1 = ContentVersion(
        id=uuid.uuid4(),
        source_id=uuid.uuid4(),
        version_number=1,
        content="Initial content",
        hash="hash1",
    )

    result = change_detection_service.detect_change(db, v1)
    assert result is None
    db.add.assert_not_called()


def test_detect_change_second_version_creates_record():
    """Second version diffs against v1 and generates a ChangeDetected record with metrics."""
    source_id = uuid.uuid4()
    v1_id = uuid.uuid4()
    v2_id = uuid.uuid4()

    v1 = ContentVersion(
        id=v1_id,
        source_id=source_id,
        version_number=1,
        content="Product: AI Assistant\nPrice: $29/mo",
        hash="hash1",
    )

    v2 = ContentVersion(
        id=v2_id,
        source_id=source_id,
        version_number=2,
        content="Product: AI Assistant\nPrice: $49/mo\nSupport: 24/7",
        hash="hash2",
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = v1

    result = change_detection_service.detect_change(db, v2)

    assert result is not None
    assert result.source_id == source_id
    assert result.previous_version_id == v1_id
    assert result.new_version_id == v2_id
    assert result.lines_added == 2
    assert result.lines_removed == 1
    assert 0.0 < result.similarity_ratio < 1.0
    assert "+Price: $49/mo" in result.diff_text
    assert "-Price: $29/mo" in result.diff_text

    db.add.assert_called_once_with(result)
    db.flush.assert_called_once()
