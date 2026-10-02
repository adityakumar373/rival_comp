# tests/test_ai_service.py
import pytest
from app.services.ai_service import _parse_response, InsightCategory


def test_parse_valid_json_response():
    raw_json = '''
    {
        "category": "pricing",
        "summary": "Increased Pro plan price from $29 to $49/mo",
        "reasoning": "Signals a shift upmarket to capture higher ARPU",
        "impact_score": 85,
        "confidence_score": 0.95
    }
    '''
    parsed = _parse_response(raw_json)
    assert parsed is not None
    assert parsed["category"] == "pricing"
    assert parsed["impact_score"] == 85
    assert parsed["confidence_score"] == 0.95
    assert "Pro plan" in parsed["summary"]


def test_parse_json_with_markdown_fences():
    raw_markdown = '''```json
    {
        "category": "hiring",
        "summary": "Added 12 new AI research scientist openings",
        "reasoning": "Heavy investment in proprietary LLM development",
        "impact_score": 75,
        "confidence_score": 0.90
    }
    ```'''
    parsed = _parse_response(raw_markdown)
    assert parsed is not None
    assert parsed["category"] == "hiring"
    assert parsed["impact_score"] == 75


def test_parse_invalid_category_fallback():
    raw_json = '''
    {
        "category": "unknown_future_event",
        "summary": "Changed CEO statement",
        "reasoning": "Executive statement update",
        "impact_score": 30,
        "confidence_score": 0.8
    }
    '''
    parsed = _parse_response(raw_json)
    assert parsed is not None
    assert parsed["category"] == "other"


def test_score_clamping():
    raw_json = '''
    {
        "category": "product",
        "summary": "Out of bounds scores",
        "reasoning": "Clamping check",
        "impact_score": 150,
        "confidence_score": 2.5
    }
    '''
    parsed = _parse_response(raw_json)
    assert parsed is not None
    assert parsed["impact_score"] == 100
    assert parsed["confidence_score"] == 1.0
