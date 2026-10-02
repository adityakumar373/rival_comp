# Rival Comp — AI Competitor Intelligence & Market Monitoring Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-8E75B2.svg?style=flat-square&logo=google)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

**Rival Comp** is an enterprise-grade AI competitor intelligence platform that continuously tracks competitor websites, pricing pages, career portals, blogs, and public announcements in real time. It uses SHA-256 content versioning to detect structural and textual changes, feeds diffs to **Google Gemini AI** for impact classification, and sends automated real-time alerts to Slack and Discord.

---

## 📸 Key Features

- **🌐 Automated Web Discovery & Multi-Tier Logo Engine**:
  - Automatically identifies official company domains and standard intelligence endpoints (`/pricing`, `/careers`, `/blog`, `/news`, `/features`).
  - Resilient multi-tier brand logo pipeline (Clearbit → Google S2 Favicon → Stylized Gradient Fallback Avatars) ensuring zero broken images.
- **🔍 Content Versioning & SHA-256 Diff Engine**:
  - Scrapes visible text content across monitored sources.
  - Automatically generates cryptographic hashes to detect true changes.
  - Generates line-by-line unified diffs with similarity ratios and additions/deletions tracking.
- **🧠 Gemini AI Impact Scoring & Strategic Categorization**:
  - Classifies market shifts into **Pricing**, **Product / Feature**, **Hiring Surge**, **Partnerships / M&A**, **Marketing**, or **Market Activity**.
  - Assigns an impact score (0–100) and confidence rating with structured strategic reasoning.
- **🚨 Proactive Multi-Channel Notifications**:
  - Configurable threshold-based alerting (`ALERT_IMPACT_THRESHOLD=60`).
  - Native integration with **Slack** and **Discord** webhooks.
- **🏢 Admin Workspace & Niche Competitor Recommendations**:
  - Set up and manage your own company profile.
  - Receive automated competitor recommendations tailored to your exact industry/niche.
- **⚖️ Head-to-Head Benchmark Matrix**:
  - Compare your organization directly against rivals across product velocity, pricing models, target markets, and competitive advantages.
- **📄 Executive Intelligence Briefs**:
  - Clean, exportable executive summary reports synthesizing real-time competitor signals.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────┐
                                  │   Target Public Website   │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
┌──────────────────────────┐       ┌──────────────────────────┐
│ Modern Light-Mode SPA UI │ ◄───► │     FastAPI Backend      │
│ (Vanilla JS, CSS Tokens) │       │     (Async / Python)     │
└──────────────────────────┘       └────────────┬─────────────┘
                                                │
                                ┌───────────────┴───────────────┐
                                │                               │
                                ▼                               ▼
                  ┌───────────────────────────┐   ┌───────────────────────────┐
                  │    PostgreSQL Database    │   │      Google Gemini AI     │
                  │ (Competitors, Diff Vers.) │   │  (Shift Classification)   │
                  └───────────────────────────┘   └─────────────┬─────────────┘
                                                                │
                                                                ▼
                                                  ┌───────────────────────────┐
                                                  │  Slack & Discord Webhooks │
                                                  └───────────────────────────┘
```

---

## 🗄️ Database Schema

The platform relies on a relational PostgreSQL schema:
- **`competitors`**: Core entity tracking name, domain, logo, industry, headquarters, and metadata.
- **`sources`**: Monitored endpoints attached to a competitor (e.g., pricing, careers, changelog).
- **`scraped_contents`**: Raw scrape log with status codes, headers, and execution timestamp.
- **`content_versions`**: Unique content hashes (SHA-256) preventing duplicate processing.
- **`changes_detected`**: Unified diffs, lines added/removed, and content similarity metrics.
- **`ai_insights`**: Gemini AI strategic analysis, impact score (0–100), and category classification.
- **`alerts`**: High-impact alerts dispatched via webhooks.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+**
- **PostgreSQL 15+**
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/))

---

### 2. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file inside `backend/`:
   ```env
   APP_NAME="Rival Comp API"
   ENVIRONMENT="development"
   DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/competitor_db"
   GEMINI_API_KEY="your-gemini-api-key-here"
   GEMINI_MODEL="gemini-2.5-flash"
   SCHEDULER_ENABLED=true
   ALERT_IMPACT_THRESHOLD=60
   
   # Optional Webhook Notifications
   SLACK_WEBHOOK_URL=""
   DISCORD_WEBHOOK_URL=""
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API and interactive documentation will be available at:
   - **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 3. Frontend Setup

The frontend is served directly as static files by the FastAPI backend or can be opened using any HTTP server:

- **Via FastAPI**: Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Or Standalone (Live Server / Python HTTP Server)**:
  ```bash
  cd frontend
  python -m http.server 3000
  ```

---

## 🧪 Running Tests

The test suite validates the entire scraper pipeline, content diffing, Gemini AI mock responses, and API endpoints.

```bash
cd backend
python -m pytest -q
```

---

## 📡 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/discovery/search?q={query}` | Smart web discovery of company and sources |
| `GET` | `/api/v1/discovery/companies` | List directory of popular tracked companies |
| `POST` | `/api/v1/competitors/` | Register a new competitor to track |
| `GET` | `/api/v1/dashboard/overview` | Dashboard overview with KPI metrics & alert count |
| `POST` | `/api/v1/scraper/source/{id}` | Execute on-demand scrape and trigger AI pipeline |
| `POST` | `/api/v1/scraper/competitor/{id}/all` | Scrape all sources for a competitor in batch |
| `GET` | `/api/v1/changes/source/{id}` | Retrieve content version diffs for a source |
| `GET` | `/api/v1/insights/competitor/{id}` | Retrieve Gemini AI classified insights |
| `GET` | `/api/v1/alerts/competitor/{id}` | List triggered alerts for a competitor |

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
