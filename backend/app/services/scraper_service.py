# app/services/scraper_service.py
"""
Fetches a Source's URL, extracts visible text, and:
  - always writes a ScrapedContent row (the raw attempt log)
  - writes a new ContentVersion only if the content hash changed
  - if a new version was created, calls change_detection_service to
    diff it against the previous version
  - includes dynamic Playwright JS rendering fallback for React/Vue SPA pages.
"""

from datetime import datetime, timezone, timedelta
from uuid import UUID

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.logger import get_logger
from app.models.scraped_content import ScrapedContent
from app.models.content_version import ContentVersion
from app.models.source import Source
from app.utils.hash_utils import generate_hash
from app.services import change_detection_service
from app.services import ai_service
from app.services import alert_service

logger = get_logger(__name__)


def _clean_html_text(html: str) -> str:
    """Extracts clean human-readable text from raw HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _fetch_playwright(url: str) -> tuple[int, str, str]:
    """
    Headless Chromium fallback for JavaScript-rendered SPA pages (React, Next.js, Vue).
    Executes client-side JS before extracting DOM text.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=settings.SCRAPE_USER_AGENT)
        page = context.new_page()
        response = page.goto(url, timeout=settings.SCRAPE_TIMEOUT_SECONDS * 1000, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)  # short wait for dynamic content hydration
        
        status = response.status if response else 200
        html = page.content()
        extracted_text = _clean_html_text(html)
        browser.close()
        return status, html, extracted_text


def _fetch(url: str) -> tuple[int, str, str]:
    """
    Fetches web content:
    1. Tries lightning-fast HTTP request (httpx + BeautifulSoup)
    2. Falls back to headless Chromium (Playwright) if JS-hydration is needed
    """
    headers = {"User-Agent": settings.SCRAPE_USER_AGENT}
    try:
        with httpx.Client(
            follow_redirects=True, timeout=settings.SCRAPE_TIMEOUT_SECONDS
        ) as client:
            response = client.get(url, headers=headers)
        
        raw_html = response.text
        extracted_text = _clean_html_text(raw_html)
        
        # If static HTML returned minimal content (<150 chars) and Playwright is enabled,
        # try dynamic rendering fallback for modern SPA sites
        if len(extracted_text) < 150 and settings.PLAYWRIGHT_ENABLED:
            try:
                logger.info("triggering_playwright_fallback", extra={"url": url, "initial_length": len(extracted_text)})
                return _fetch_playwright(url)
            except Exception as pw_err:
                logger.warning("playwright_fallback_failed_using_static", extra={"error": str(pw_err), "url": url})
        
        return response.status_code, raw_html, extracted_text

    except Exception as http_err:
        if settings.PLAYWRIGHT_ENABLED:
            try:
                logger.info("http_failed_trying_playwright", extra={"url": url, "error": str(http_err)})
                return _fetch_playwright(url)
            except Exception as pw_err:
                raise http_err
        raise http_err


def scrape_source(db: Session, source_id: UUID) -> dict:
    """
    Scrapes a single source. Always logs a ScrapedContent row.
    Creates a new ContentVersion (and runs change detection) only if
    the extracted text changed since the last known version.
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise NotFoundError(f"Source {source_id} not found")

    status_code = None
    raw_html = None
    text = ""
    error = None

    try:
        status_code, raw_html, text = _fetch(source.url)
    except Exception as exc:  # noqa: BLE001 - log and record, don't crash the caller
        error = str(exc)
        logger.error(
            "scrape_failed",
            extra={"source_id": str(source_id), "url": source.url, "error": error},
        )

    content_hash = generate_hash(text) if text else None

    scraped = ScrapedContent(
        source_id=source_id,
        status_code=status_code,
        raw_html=raw_html,
        content=text or None,
        hash=content_hash,
        error=error,
    )
    db.add(scraped)

    source.last_scraped = datetime.now(timezone.utc)

    changed = False
    version_number = None
    change = None
    insight = None
    alert = None

    if content_hash:
        latest_version = (
            db.query(ContentVersion)
            .filter(ContentVersion.source_id == source_id)
            .order_by(ContentVersion.version_number.desc())
            .first()
        )

        if latest_version is None or latest_version.hash != content_hash:
            changed = True
            version_number = (latest_version.version_number + 1) if latest_version else 1

            new_version = ContentVersion(
                source_id=source_id,
                version_number=version_number,
                content=text,
                hash=content_hash,
            )
            db.add(new_version)
            db.flush()  # assigns new_version.id before we diff/commit

            logger.info(
                "content_version_created",
                extra={"source_id": str(source_id), "version_number": version_number},
            )

            change = change_detection_service.detect_change(db, new_version)

            if change is not None:
                insight = ai_service.classify_change(db, change)
                if insight is not None:
                    alert = alert_service.maybe_create_alert(db, insight)
    db.commit()
    db.refresh(scraped)

    return {
        "scraped_content_id": scraped.id,
        "status_code": status_code,
        "changed": changed,
        "version_number": version_number,
        "change_id": change.id if change else None,
        "insight_id": insight.id if insight else None,
        "alert_id": alert.id if alert else None,
        "error": error,
    }


def get_due_sources(db: Session) -> list[Source]:
    """
    Returns active sources that are overdue for scraping.
    A source is due when: last_scraped IS NULL (never scraped)
    OR last_scraped + scrape_frequency minutes < NOW().
    """
    now = datetime.now(timezone.utc)

    sources = (
        db.query(Source)
        .filter(Source.is_active.is_(True))
        .all()
    )

    due = []
    for source in sources:
        if source.last_scraped is None:
            due.append(source)
        else:
            # Normalize to UTC-aware for comparison
            last = source.last_scraped
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            next_due = last + timedelta(minutes=int(source.scrape_frequency))
            if now >= next_due:
                due.append(source)

    return due
