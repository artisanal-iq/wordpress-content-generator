"""
Pytest fixtures for WordPress Content Generator tests

This module contains fixtures that can be used across all test files.
Fixtures provide reusable test data, mocked services, and utility functions.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv

# Try to load environment variables from .env file
load_dotenv()

# Sample test data
@pytest.fixture
def sample_strategic_plan():
    """Return a sample strategic plan for testing."""
    return {
        "id": str(uuid.uuid4()),
        "domain": "fitness-blog.com",
        "audience": "fitness enthusiasts aged 25-45",
        "tone": "motivational and informative",
        "niche": "weight training",
        "goal": "educate beginners on proper weight training techniques",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

@pytest.fixture
def sample_content_piece(sample_strategic_plan):
    """Return a sample content piece for testing."""
    return {
        "id": str(uuid.uuid4()),
        "strategic_plan_id": sample_strategic_plan["id"],
        "title": None,
        "slug": None,
        "status": "draft",
        "draft_text": None,
        "final_text": None,
        "wp_post_id": None,
        "featured_image_id": None,
        "scheduled_at": None,
        "published_at": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

@pytest.fixture
def sample_keywords():
    """Return sample keywords for testing."""
    return {
        "focus_keyword": "beginner weight training program",
        "supporting_keywords": [
            "weight training for beginners",
            "strength training basics",
            "gym workout plan",
            "free weight exercises"
        ],
        "internal_links": [
            "protein nutrition guide",
            "recovery techniques"
        ],
        "cluster_target": "strength training"
    }

@pytest.fixture
def sample_research():
    """Return sample research data for testing."""
    return [
        {
            "excerpt": "According to a 2022 study, beginners who followed a structured weight training program for 12 weeks saw an average strength increase of 30%.",
            "url": "https://example.com/study1",
            "type": "study",
            "confidence": 0.9
        },
        {
            "excerpt": "The American College of Sports Medicine recommends that beginners start with 1-3 sets of 8-12 repetitions.",
            "url": "https://example.com/recommendation1",
            "type": "fact",
            "confidence": 0.95
        }
    ]

@pytest.fixture
def sample_hooks():
    """Return sample hooks for testing."""
    return {
        "main_hook": "Discover the scientifically-backed weight training program that helped complete beginners increase their strength by 30% in just 12 weeks.",
        "micro_hooks": [
            "The #1 mistake that sabotages beginner gains",
            "Why 90% of gym newcomers quit within 3 months",
            "The 5 essential exercises that build more muscle in less time"
        ]
    }

@pytest.fixture
def sample_agent_task(sample_content_piece):
    """Return a sample agent task for testing."""
    return {
        "id": str(uuid.uuid4()),
        "agent": "seo-agent",
        "content_id": sample_content_piece["id"],
        "input": {
            "domain": "fitness-blog.com",
            "niche": "weight training"
        },
        "output": {},
        "status": "queued",
        "errors": [],
        "retry_count": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

@pytest.fixture
def sample_seo_agent_output(sample_keywords):
    """Return sample SEO agent output for testing."""
    return {
        "agent": "seo-agent",
        "output": {
            "seo": sample_keywords
        },
        "status": "done",
        "errors": []
    }

# Mock fixtures
@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    mock = MagicMock()
    
    # Configure the mock to return empty data by default
    table_mock = MagicMock()
    select_mock = MagicMock()
    execute_mock = MagicMock()
    execute_mock.data = []
    execute_mock.count = 0
    select_mock.execute.return_value = execute_mock
    table_mock.select.return_value = select_mock
    mock.table.return_value = table_mock
    
    return mock

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing."""
    class MockChoice:
        def __init__(self, text):
            self.message = MagicMock()
            self.message.content = text
    
    class MockResponse:
        def __init__(self, text):
            self.choices = [MockChoice(text)]
    
    return MockResponse

@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    mock = MagicMock()
    chat_mock = MagicMock()
    completions_mock = MagicMock()
    
    # Configure the mock to return a default response
    completions_mock.create.return_value = mock_openai_response()(
        """
        {
            "focus_keyword": "test keyword",
            "supporting_keywords": ["keyword1", "keyword2"],
            "internal_links": ["link1", "link2"],
            "cluster_target": "test cluster"
        }
        """
    )
    
    chat_mock.completions = completions_mock
    mock.chat = chat_mock
    
    return mock

@pytest.fixture
def patch_openai():
    """Patch OpenAI client for testing."""
    with patch("openai.OpenAI") as mock:
        mock.return_value = mock_openai()
        yield mock

@pytest.fixture
def patch_supabase():
    """Patch Supabase client for testing."""
    with patch("agents.shared.utils.create_client") as mock:
        mock.return_value = mock_supabase()
        yield mock

# Environment helpers
@pytest.fixture
def temp_env_vars():
    """
    Temporarily set environment variables for testing.
    
    Usage:
        def test_something(temp_env_vars):
            temp_env_vars({
                "SUPABASE_URL": "https://test.supabase.co",
                "OPENAI_API_KEY": "test-key"
            })
            # Test code here
    """
    original_environ = os.environ.copy()
    
    def _set_env_vars(env_vars):
        for key, value in env_vars.items():
            os.environ[key] = value
    
    yield _set_env_vars
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_environ)

# Agent testing helpers
@pytest.fixture
def run_agent():
    """
    Helper to run an agent with test input.
    
    Usage:
        def test_seo_agent(run_agent):
            result = run_agent("seo-agent", {"domain": "test.com", "niche": "test"})
            assert result["status"] == "done"
    """
    def _run_agent(agent_name, input_data):
        try:
            # Try to import the agent module
            if "-" in agent_name:
                module_name = f"agents.{agent_name.replace('-', '_')}"
            else:
                module_name = f"agents.{agent_name}"
            
            agent_module = __import__(module_name, fromlist=["run"])
            
            # Run the agent
            return agent_module.run(input_data)
        except ImportError:
            # Try importing from index module
            try:
                module_name = f"agents.{agent_name}.index"
                agent_module = __import__(module_name, fromlist=["run"])
                return agent_module.run(input_data)
            except ImportError:
                pytest.fail(f"Could not import agent module: {agent_name}")
    
    return _run_agent

@pytest.fixture
def load_test_json():
    """
    Load JSON test data from a file.
    
    Usage:
        def test_with_data(load_test_json):
            data = load_test_json("tests/data/test_input.json")
            # Test code here
    """
    def _load_json(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            pytest.fail(f"Error loading test data from {file_path}: {e}")
    
    return _load_json
