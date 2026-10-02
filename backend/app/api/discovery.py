# app/api/discovery.py
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services import discovery_service, competitor_service, source_service, scraper_service
from app.models.competitor import Competitor
from app.models.source import Source, SourceType
from app.schemas.competitor import CompetitorCreate
from app.schemas.source import SourceCreate

router = APIRouter(prefix="/discovery", tags=["Discovery"])


class DiscoverySearchRequest(BaseModel):
    query: str


class SourceItem(BaseModel):
    source_type: SourceType
    url: HttpUrl


class BatchAddCompetitorItem(BaseModel):
    name: str
    website: HttpUrl
    industry: Optional[str] = None
    description: Optional[str] = None
    sources: List[SourceItem] = []


class BatchAddRequest(BaseModel):
    competitors: List[BatchAddCompetitorItem]


@router.get("/autocomplete")
def autocomplete_companies(q: str = Query(..., min_length=1, description="Typeahead query")):
    """
    Instant autocomplete endpoint (<10ms). Returns live company recommendations with logos
    as the user types each character.
    """
    return discovery_service.autocomplete_companies(q)


@router.post("/search")
def search_company(req: DiscoverySearchRequest):
    """
    Given a company query, uses AI to discover website, pricing/blog/careers URLs,
    industry tags, logos, and direct market competitors.
    """
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    return discovery_service.discover_company(req.query.strip())


@router.post("/batch-add")
def batch_add_competitors(req: BatchAddRequest, db: Session = Depends(get_db)):
    """
    Batch creates competitors, attaches their discovered sources,
    and enqueues initial scrapes.
    """
    created_summary = []

    for comp_data in req.competitors:
        competitor = None
        # Check if competitor exists first
        existing_comp = db.query(Competitor).filter(Competitor.name == comp_data.name).first()
        if existing_comp:
            competitor = existing_comp
            if not competitor.is_active:
                competitor.is_active = True
                db.commit()
                db.refresh(competitor)
        else:
            try:
                competitor = competitor_service.create_competitor(
                    db,
                    CompetitorCreate(
                        name=comp_data.name,
                        website=str(comp_data.website),
                        industry=comp_data.industry,
                        description=comp_data.description,
                    )
                )
            except Exception:
                db.rollback()
                competitor = db.query(Competitor).filter(Competitor.name == comp_data.name).first()

        if not competitor:
            continue

        created_sources = []
        for src in comp_data.sources:
            src_url = str(src.url)
            s_id = None

            existing_src = (
                db.query(Source)
                .filter(Source.competitor_id == competitor.id, Source.url == src_url)
                .first()
            )
            if existing_src:
                if not existing_src.is_active:
                    existing_src.is_active = True
                    db.commit()
                    db.refresh(existing_src)
                s_id = existing_src.id
                created_sources.append(s_id)
            else:
                try:
                    s = source_service.create_source(
                        db,
                        SourceCreate(
                            competitor_id=competitor.id,
                            source_type=src.source_type,
                            url=src_url,
                            scrape_frequency=1440,
                        )
                    )
                    s_id = s.id
                    created_sources.append(s_id)
                except Exception:
                    db.rollback()
                    s_id = None

            # Execute initial scrape safely
            if s_id:
                try:
                    scraper_service.scrape_source(db, s_id)
                except Exception:
                    db.rollback()

        created_summary.append({
            "competitor_id": str(competitor.id),
            "name": competitor.name,
            "sources_added": len(created_sources),
        })

    return {
        "status": "success",
        "message": f"Successfully processed {len(created_summary)} competitor(s)",
        "added": created_summary,
    }
