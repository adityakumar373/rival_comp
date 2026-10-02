# tests/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "scheduler_enabled" in data


def test_autocomplete_endpoint():
    response = client.get("/discovery/autocomplete?q=Open")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["name"] == "OpenAI" for item in data)


def test_dashboard_analytics_endpoint():
    response = client.get("/dashboard/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_insights" in data
    assert "total_changes" in data
    assert "total_alerts" in data
    assert "category_breakdown" in data
    assert "competitor_activity" in data


def test_alerts_endpoint():
    response = client.get("/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_insights_endpoint():
    response = client.get("/insights/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_scheduler_status_endpoint():
    response = client.get("/scraper/scheduler/status")
    assert response.status_code == 200
    data = response.json()
    assert "enabled" in data
    assert "interval_seconds" in data
