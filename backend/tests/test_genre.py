"""Tests for genre detection endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_detect_genre_success():
    """Test successful genre detection."""
    response = client.post(
        "/api/v1/genre/detect",
        json={"text": "ghost in dark house with scary shadows"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "genre" in data["data"]


def test_detect_genre_empty_text():
    """Test genre detection with empty text."""
    response = client.post(
        "/api/v1/genre/detect",
        json={"text": ""}
    )
    assert response.status_code == 400
