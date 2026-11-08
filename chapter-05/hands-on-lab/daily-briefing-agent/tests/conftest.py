"""
Shared test fixtures for the Daily Briefing Agent.

This module provides common fixtures used across all test categories.
Follow the patterns defined in tech.md and structure.md.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest

# Set test environment before importing application modules
os.environ["FLASK_ENV"] = "testing"
os.environ["USE_LOCALSTACK"] = "false"


# ===========================================
# Configuration Fixtures
# ===========================================


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Provide test configuration values."""
    return {
        "database_url": "sqlite:///:memory:",
        "aws_region": "us-east-1",
        # Unit tests mock Bedrock, so this value is never invoked. Keep it in sync
        # with BEDROCK_MODEL_ID in .env.example anyway, so the fixture stays honest.
        "bedrock_model_id": "global.anthropic.claude-haiku-5-5",
        "s3_bucket": "test-briefings",
    }


# ===========================================
# Story Fixtures
# ===========================================


@pytest.fixture
def sample_story_data() -> Dict[str, Any]:
    """Provide sample story data for testing."""
    return {
        "id": "test-story-001",
        "title": "New AI Framework Released: Actually Does What It Claims",
        "original_url": "https://news.ycombinator.com/item?id=12345",
        "source": "hackernews",
        "published_at": datetime.utcnow() - timedelta(hours=2),
        "collected_at": datetime.utcnow(),
        "content": "A new AI framework has been released that actually delivers on its promises.",
        "summary": "",
        "score": 150.0,
        "is_breaking": False,
        "hn_score": 150,
        "hn_comments": 45,
    }


@pytest.fixture
def sample_stories(sample_story_data: Dict[str, Any]) -> list:
    """Provide a list of sample stories for testing."""
    stories = []
    for i in range(5):
        story = sample_story_data.copy()
        story["id"] = f"test-story-{i:03d}"
        story["title"] = f"Test Story {i}: {story['title']}"
        story["score"] = 100 + (i * 20)
        stories.append(story)
    return stories


@pytest.fixture
def breaking_news_story(sample_story_data: Dict[str, Any]) -> Dict[str, Any]:
    """Provide a breaking news story for testing."""
    story = sample_story_data.copy()
    story["id"] = "breaking-001"
    story["title"] = "BREAKING: Major Tech Company Makes Significant Announcement"
    story["is_breaking"] = True
    story["score"] = 500.0
    story["published_at"] = datetime.utcnow() - timedelta(minutes=30)
    return story


# ===========================================
# Mock AWS Services
# ===========================================


@pytest.fixture
def mock_bedrock_client() -> Generator[MagicMock, None, None]:
    """Provide a mocked Bedrock client for testing."""
    with patch("boto3.client") as mock_client:
        bedrock_mock = MagicMock()
        bedrock_mock.invoke_model.return_value = {
            "body": MagicMock(
                read=MagicMock(return_value=b'{"content": [{"type": "thinking", "thinking": "", "signature": "sig"}, {"type": "text", "text": "A witty summary."}], "stop_reason": "end_turn"}')
            )
        }
        mock_client.return_value = bedrock_mock
        yield bedrock_mock


@pytest.fixture
def mock_s3_client() -> Generator[MagicMock, None, None]:
    """Provide a mocked S3 client for testing."""
    with patch("boto3.client") as mock_client:
        s3_mock = MagicMock()
        s3_mock.put_object.return_value = {"ETag": '"abc123"'}
        s3_mock.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"# Daily Briefing\n"))
        }
        mock_client.return_value = s3_mock
        yield s3_mock


# ===========================================
# HTTP Mock Fixtures
# ===========================================


@pytest.fixture
def mock_hn_response() -> str:
    """Provide a sample Hacker News HTML response."""
    return """
    <html>
    <body>
        <table class="itemlist">
            <tr class="athing" id="12345">
                <td class="title">
                    <span class="titleline">
                        <a href="https://example.com/story">Test Story Title</a>
                    </span>
                </td>
            </tr>
            <tr>
                <td class="subtext">
                    <span class="score" id="score_12345">150 points</span>
                    <a href="item?id=12345">45 comments</a>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ===========================================
# Database Fixtures
# ===========================================


@pytest.fixture
def in_memory_db():
    """Provide an in-memory SQLite database for testing."""
    # This fixture will be expanded when SQLAlchemy models are implemented
    pass


# ===========================================
# Flask App Fixtures
# ===========================================


@pytest.fixture
def flask_app():
    """Provide a Flask test application."""
    # This fixture will be expanded when Flask app is implemented
    pass


@pytest.fixture
def flask_client(flask_app):
    """Provide a Flask test client."""
    # This fixture will be expanded when Flask app is implemented
    pass


# ===========================================
# Utility Functions
# ===========================================


def create_test_story(**kwargs) -> Dict[str, Any]:
    """Factory function to create test story data with custom attributes.

    Usage:
        story = create_test_story(title="Custom Title", score=200)
    """
    defaults = {
        "id": "test-story-factory",
        "title": "Factory Generated Test Story",
        "original_url": "https://example.com/test",
        "source": "hackernews",
        "published_at": datetime.utcnow(),
        "collected_at": datetime.utcnow(),
        "content": "Test content for story.",
        "summary": "",
        "score": 100.0,
        "is_breaking": False,
        "hn_score": 100,
        "hn_comments": 20,
    }
    defaults.update(kwargs)
    return defaults
