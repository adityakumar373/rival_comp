# Rival Comp — AI Competitor Intelligence Platform Backend

Full pipeline: monitor competitor sources → scrape → detect changes →
classify with AI → alert → dashboard.

## Setup

```bash
cp .env.example .env          # fill in DATABASE_URL, GEMINI_API_KEY
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
playwright install chromium   # only needed if you add JS-render fallback later
```

Docker: `docker compose up --build`. Swagger: `http://127.0.0.1:8000/docs`.

**If your database already has tables from before this Alembic chain existed**
(e.g. `competitor` created manually), stamp the matching revision instead of
running the create migration for it — `alembic stamp <rev>` then
`alembic upgrade head` for the rest.

---

## Pipeline, end to end

1. **Add a competitor** — `POST /competitor/`
2. **Attach sources to monitor** — `POST /sources/` (pricing page, careers
   page, blog, G2, etc. — see `SourceType` enum)
3. **Scrape a source** — `POST /scraper/source/{id}`. This one call:
   - fetches the URL (`httpx` + `BeautifulSoup`), extracts visible text
   - always logs a `ScrapedContent` row (the raw attempt, even on failure)
   - if the text's hash differs from the last known version, creates a new
     `ContentVersion`
   - diffs the new version against the previous one → `ChangeDetected`
     (unified diff, lines added/removed, similarity ratio)
   - sends that diff to **Gemini** for classification → `AIInsight`
     (category, summary, reasoning, impact_score 0-100, confidence_score)
   - if `impact_score >= ALERT_IMPACT_THRESHOLD` (config, default 60),
     creates an `Alert`
4. **Read results:**
   - `GET /changes/source/{id}` — raw diffs for a source
   - `GET /insights/competitor/{id}` — classified insights for a competitor
   - `GET /alerts/competitor/{id}` (`?unsent_only=true`) — alerts n8n should
     deliver; `POST /alerts/{id}/mark-sent` once delivered
   - `GET /dashboard/competitors` — overview: source count, last scraped,
     insight count, avg impact score, unsent alerts, per competitor
   - `GET /dashboard/competitor/{id}` — drill-down: sources, recent
     insights, recent alerts

Every step is **decoupled and best-effort where it should be**: a failed
scrape still logs a row instead of crashing; if `GEMINI_API_KEY` isn't set
or the Gemini call fails, classification is skipped (logged) but scraping
and change detection still succeed. Nothing downstream ever silently
blocks something upstream.

`n8n`'s job in this architecture is orchestration and delivery — polling
`GET /alerts/.../?unsent_only=true` and fanning out to Slack/email, and/or
calling `POST /scraper/source/{id}` on a schedule per source's
`scrape_frequency`. The FastAPI app's job is to produce correct, evidenced
data; it doesn't send anything anywhere itself.

---

## Researched choices, and why

### Data sources per signal type

| Signal | Source(s) chosen | Why |
|---|---|---|
| **Pricing** | Direct scrape of the competitor's own pricing page | No reliable third-party API for a specific company's live pricing; the primary source is the only ground truth, and it's the evidence link. |
| **Product/marketing/news** | Company blog scrape/RSS. Supplement with a news API (GNews/NewsAPI.org/NewsData.io) filtered by company name for third-party coverage the company won't self-publish. | RSS is cheap and stable; news APIs catch what a company won't self-report (layoffs, lawsuits, acquisitions). |
| **Hiring** | Careers page scrape, filtered by role keywords ("ML", "AI", "LLM"). | LinkedIn/Indeed official job-count APIs require partner approval unlikely for a small project — careers pages are public and sufficient to detect a hiring surge in a category. |
| **Partnerships** | Same blog/news pipeline as marketing. | Partnership announcements are almost always a press release/blog post — classification (not a separate pipeline) is what distinguishes it. |
| **Reviews/sentiment** | G2/Trustpilot rating + review-count trend, not review text (ToS-safer, and rating drift is itself a meaningful signal, e.g. quality regression after a release). | Smaller legal/robots.txt exposure than scraping full review text. |
| **LinkedIn company page** | Deferred — no viable public API, aggressive anti-scraping. | Not worth the ban risk for v1. |

### AI model: Gemini

Structured JSON output (category/summary/reasoning/score) is what this
task needs, not prose — Gemini's JSON mode handles that reliably, and the
flash tier is cheap enough to run on every detected change across every
competitor. The call is isolated in `ai_service.py` behind one function,
so swapping providers later is a contained change.

### Why impact score (0-100), not a fixed severity enum

A numeric score is tunable per-team without a schema change (the alert
threshold is just a config value) and sorts naturally on a dashboard.
`reasoning` is stored next to every score — a score is never shown without
the model's own justification for it.

### Why n8n owns delivery, not the API

Alert *delivery* (Slack, email, webhook fan-out) is glue logic that
changes independently of the data model. The API's responsibility ends at
producing a correct `Alert` row; n8n polls and routes it.

---

## Project structure

```
app/
  models/       competitor, source, scraped_content, content_version,
                change_detected, ai_insight, alert
  services/     one file per pipeline stage — competitor_service,
                source_service, scraper_service (orchestrates the whole
                scrape→version→diff→classify→alert chain),
                change_detection_service, ai_service, alert_service,
                dashboard_service
  api/          competitor, source, scraper, changes, insights, alerts,
                dashboard
  core/         config (pydantic-settings), logger (structured JSON),
                exceptions (domain errors, no FastAPI coupling)
alembic/versions/  0001 competitor -> 0007 alerts, one migration per
                   feature slice, in build order
```

---

## Progress

```
Research Phase:       100%
Architecture:         100%
Database Design:      100%
Backend Foundation:   100%
Competitor Module:    100%
Source Module:        100%
Scraper Module:       100%
Change Detection:     100%
AI Classification:    100%  (Gemini — category, summary, reasoning, impact score)
Alerts:               100%  (threshold-based, delivery left to n8n)
Dashboard:            100%  (overview + per-competitor drill-down)
Deployment:            30%  (Dockerfile + compose done; Oracle Cloud deploy pending)
```

## Still open

- **Deployment** — Oracle Cloud Free Tier VM + `docker compose up -d`,
  GitHub Actions for CI/CD
- **pgvector / RAG search** — flagged as future work in the original spec,
  not built
- **Scheduling** — nothing in this repo calls `POST /scraper/source/{id}`
  on a timer; that's the n8n workflow using each source's
  `scrape_frequency`, still to be built in n8n itself
- **JS-rendered pages** — current scraper is `httpx` + `BeautifulSoup`
  only (static HTML). A Playwright fallback for JS-heavy pricing pages
  (`playwright` is already in requirements.txt) is a reasonable next add
  if a source turns out to need it
