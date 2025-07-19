"""
Shared pytest fixtures for both unit and integration tests.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_supabase_client():
    """
    Create a mock Supabase client for testing.
    """
    mock_client = MagicMock()
    
    # Configure the mock to return predictable values
    mock_select = MagicMock()
    mock_eq = MagicMock()
    mock_execute = MagicMock()
    
    # Setup the method chain
    mock_client.table.return_value.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.execute.return_value = mock_execute
    
    # For direct execute on table operations
    mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": "mock-id-123"}])
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
    
    return mock_client

@pytest.fixture
def mock_openai_client():
    """
    Create a mock OpenAI client for testing.
    """
    mock_client = MagicMock()
    
    # Configure the mock to return predictable values for chat completions
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "focus_keyword": "test keyword",
                        "supporting_keywords": ["support1", "support2"],
                        "search_volume": {
                            "test keyword": 1000,
                            "support1": 500,
                            "support2": 300
                        }
                    })
                )
            )
        ]
    )
    
    return mock_client

@pytest.fixture
def sample_strategic_plan():
    """
    Provide a sample strategic plan for testing.
    """
    return {
        "id": "test-plan-id-123",
        "domain": "example.com",
        "audience": "test audience",
        "tone": "informative",
        "niche": "technology",
        "goal": "educate readers"
    }

@pytest.fixture
def sample_content_piece():
    """
    Provide a sample content piece for testing.
    """
    return {
        "id": "test-content-id-456",
        "strategic_plan_id": "test-plan-id-123",
        "title": "Test Article Title",
        "slug": "test-article-title",
        "status": "draft",
        "draft_text": "This is a sample draft text."
    }

@pytest.fixture
def sample_keywords():
    """
    Provide sample keywords for testing.
    """
    return {
        "id": "test-keywords-id-789",
        "content_id": "test-content-id-456",
        "focus_keyword": "test keyword",
        "supporting_keywords": ["support1", "support2"]
    }

@pytest.fixture
def sample_research():
    """
    Provide sample research data for testing.
    """
    return [
        {
            "id": "test-research-id-001",
            "content_id": "test-content-id-456",
            "excerpt": "This is a test fact.",
            "url": "https://example.com/fact",
            "type": "fact",
            "confidence": 0.9
        },
        {
            "id": "test-research-id-002",
            "content_id": "test-content-id-456",
            "excerpt": "This is a test quote from an expert.",
            "url": "https://example.com/quote",
            "type": "quote",
            "confidence": 0.8
        }
    ]
