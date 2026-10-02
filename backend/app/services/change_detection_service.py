# app/services/change_detection_service.py
"""
Diffs a newly-created ContentVersion against the one before it and
stores a ChangeDetected row. Deliberately does NOT decide "is this
important" — that's the AI classification layer's job later. This
stage only answers "what textually changed", cheaply and
deterministically.

Replaces diff_service.py + change_detection.py + change_service.py,
which did this same job three separate, slightly different ways.
"""

import difflib
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.change_detected import ChangeDetected
from app.models.content_version import ContentVersion

logger = get_logger(__name__)

# Diffs can get long (e.g. a full careers page listing). Cap what we
# store — the full text of both versions already lives in
# ContentVersion, so this is evidence, not an archive.
_MAX_DIFF_CHARS = 8000


def detect_change(db: Session, new_version: ContentVersion) -> ChangeDetected | None:
    """
    Compares `new_version` to the immediately preceding version for the
    same source. Returns None (creates nothing) if this is the source's
    first-ever version — there's nothing to diff against yet.
    """
    previous_version = (
        db.query(ContentVersion)
        .filter(
            ContentVersion.source_id == new_version.source_id,
            ContentVersion.version_number == new_version.version_number - 1,
        )
        .first()
    )

    if previous_version is None:
        logger.info(
            "change_detection_skipped_first_version",
            extra={"source_id": str(new_version.source_id)},
        )
        return None

    old_lines = previous_version.content.splitlines()
    new_lines = new_version.content.splitlines()

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    similarity_ratio = matcher.ratio()

    diff_lines = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"version_{previous_version.version_number}",
            tofile=f"version_{new_version.version_number}",
            lineterm="",
        )
    )
    lines_added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    lines_removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    diff_text = "\n".join(diff_lines)[:_MAX_DIFF_CHARS]

    change = ChangeDetected(
        source_id=new_version.source_id,
        previous_version_id=previous_version.id,
        new_version_id=new_version.id,
        lines_added=lines_added,
        lines_removed=lines_removed,
        similarity_ratio=similarity_ratio,
        diff_text=diff_text,
    )
    db.add(change)
    db.flush()  # assigns change.id; caller (scraper_service) commits

    logger.info(
        "change_detected",
        extra={
            "source_id": str(new_version.source_id),
            "change_id": str(change.id),
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "similarity_ratio": round(similarity_ratio, 4),
        },
    )

    # TODO(next phase): enqueue `change` for Gemini classification —
    # populate change_summary, create an ai_insights row with impact
    # score + reasoning, and raise an alert if score >= threshold.
    return change


def list_changes_for_source(
    db: Session, source_id: UUID, skip: int = 0, limit: int = 50
) -> list[ChangeDetected]:
    return (
        db.query(ChangeDetected)
        .filter(ChangeDetected.source_id == source_id)
        .order_by(ChangeDetected.detected_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_change(db: Session, change_id: UUID) -> ChangeDetected | None:
    return db.query(ChangeDetected).filter(ChangeDetected.id == change_id).first()
