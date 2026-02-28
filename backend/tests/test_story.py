"""Tests for story generation endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_continue_story_success():
    """Test successful story continuation."""
    response = client.post(
        "/api/v1/story/continue",
        json={
            "text": "Once upon a time, there was a brave knight",
            "max_length": 100,
            "temperature": 0.8
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "generated_text" in data["data"]


def test_continue_story_empty_text():
    """Test story continuation with empty text."""
    response = client.post(
        "/api/v1/story/continue",
        json={"text": ""}
    )
    assert response.status_code == 400


def test_continue_story_short_text():
    """Test story continuation with too short text."""
    response = client.post(
        "/api/v1/story/continue",
        json={"text": "short"}
    )
    assert response.status_code == 400
