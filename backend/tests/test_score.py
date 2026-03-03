"""Tests for story scoring endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_score_story_success():
    """Test successful story scoring."""
    response = client.post(
        "/api/v1/score/story",
        json={"text": "This is a test story with multiple sentences. It has characters and plot."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "total_score" in data["data"]
    assert 0 <= data["data"]["total_score"] <= 100


def test_extract_characters_success():
    """Test successful character extraction."""
    response = client.post(
        "/api/v1/score/characters",
        json={"text": "John and Mary went to the park. They met Sarah there."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "characters" in data["data"]


def test_extract_characters_lowercase_named_and_with_patterns():
    response = client.post(
        "/api/v1/score/characters",
        json={
            "text": "once upon a time there was a girl named she was student, "
            "she had a boyfriend named mayank but she cheated on him with naitik"
        },
    )
    assert response.status_code == 200
    data = response.json()
    chars = [c.lower() for c in data["data"]["characters"]]
    assert "mayank" in chars
    assert "naitik" in chars
