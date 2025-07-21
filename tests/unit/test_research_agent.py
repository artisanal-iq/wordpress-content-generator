"""
Unit tests for the research agent.
"""

import os
import json
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

import pytest

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import functions to test
from research_agent import (
    setup_openai,
    get_supabase_client,
    get_content_piece,
    get_content_keywords,
    get_strategic_plan,
    perform_research_with_ai,
    save_research_to_database,
    save_results_to_file
)


class TestResearchAgent(unittest.TestCase):
    """Test cases for the research agent functions."""

    def setUp(self):
        """Set up test case."""
        self.mock_content_piece = {
            "id": "test-content-id",
            "strategic_plan_id": "test-plan-id",
            "title": "Test Article Title",
            "slug": "test-article-title",
            "status": "draft",
            "draft_text": "This is a sample draft text."
        }
        
        self.mock_keywords = {
            "id": "test-keywords-id",
            "content_id": "test-content-id",
            "focus_keyword": "test keyword",
            "supporting_keywords": ["support1", "support2"]
        }
        
        self.mock_plan = {
            "id": "test-plan-id",
            "domain": "example.com",
            "audience": "test audience",
            "tone": "informative",
            "niche": "technology",
            "goal": "educate readers"
        }
        
        self.mock_research_points = [
            {
                "excerpt": "This is a test fact about technology.",
                "url": "https://example.com/fact",
                "type": "fact",
                "confidence": 0.9
            },
            {
                "excerpt": "This is a test quote from an expert in technology.",
                "url": "https://example.com/quote",
                "type": "quote",
                "confidence": 0.85
            }
        ]

    @patch("os.getenv")
    def test_setup_openai(self, mock_getenv):
        """Test OpenAI setup with valid API key."""
        mock_getenv.return_value = "fake-api-key"
        
        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value = "mock-openai-client"
            client = setup_openai()
            
            mock_openai.assert_called_once_with(api_key="fake-api-key")
            self.assertEqual(client, "mock-openai-client")

    @patch("os.getenv")
    def test_get_supabase_client(self, mock_getenv):
        """Test Supabase client creation with valid credentials."""
        mock_getenv.side_effect = lambda x: "fake-url" if x == "SUPABASE_URL" else "fake-key"
        
        with patch("research_agent.create_client") as mock_create_client:
            mock_create_client.return_value = "mock-supabase-client"
            client = get_supabase_client()
            
            mock_create_client.assert_called_once_with("fake-url", "fake-key")
            self.assertEqual(client, "mock-supabase-client")

    def test_get_content_piece_with_id(self):
        """Test retrieving a content piece with a specific ID."""
        mock_supabase = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[self.mock_content_piece])
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_execute
        
        content_piece = get_content_piece(mock_supabase, "test-content-id")
        
        mock_supabase.table.assert_called_once_with("content_pieces")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("id", "test-content-id")
        self.assertEqual(content_piece, self.mock_content_piece)

    def test_get_content_piece_no_id(self):
        """Test retrieving a draft content piece."""
        mock_supabase = MagicMock()
        mock_limit = MagicMock()
        mock_limit.execute.return_value = MagicMock(data=[self.mock_content_piece])
        mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value = mock_limit
        
        content_piece = get_content_piece(mock_supabase)
        
        mock_supabase.table.assert_called_once_with("content_pieces")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("status", "draft")
        mock_supabase.table.return_value.select.return_value.eq.return_value.limit.assert_called_once_with(1)
        self.assertEqual(content_piece, self.mock_content_piece)

    def test_get_content_keywords(self):
        """Test retrieving keywords for a content piece."""
        mock_supabase = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[self.mock_keywords])
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_execute
        
        keywords = get_content_keywords(mock_supabase, "test-content-id")
        
        mock_supabase.table.assert_called_once_with("keywords")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("content_id", "test-content-id")
        self.assertEqual(keywords, self.mock_keywords)

    def test_get_strategic_plan(self):
        """Test retrieving a strategic plan."""
        mock_supabase = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[self.mock_plan])
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_execute
        
        plan = get_strategic_plan(mock_supabase, "test-plan-id")
        
        mock_supabase.table.assert_called_once_with("strategic_plans")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("id", "test-plan-id")
        self.assertEqual(plan, self.mock_plan)

    @patch("research_agent.logger")
    def test_perform_research_with_ai(self, mock_print):
        """Test performing research with OpenAI."""
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps({"research_points": self.mock_research_points})))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = perform_research_with_ai(mock_openai_client, self.mock_content_piece, self.mock_keywords, self.mock_plan)
        
        mock_openai_client.chat.completions.create.assert_called_once()
        self.assertEqual(result, self.mock_research_points)

    @patch("research_agent.logger")
    def test_save_research_to_database(self, mock_print):
        """Test saving research to the database."""
        mock_supabase = MagicMock()
        
        # Mock the research table check
        mock_test_query = MagicMock()
        mock_test_query.execute.return_value = MagicMock()  # Table exists
        mock_supabase.table.return_value.select.return_value.limit.return_value = mock_test_query
        
        # Mock the insert operations
        mock_insert_response = MagicMock(data=[{"id": "new-research-id"}])
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_response
        
        # Call the function to test
        save_research_to_database(mock_supabase, "test-content-id", self.mock_research_points)
        
        # Verify table exists check was made
        mock_supabase.table.assert_any_call("research")
        mock_supabase.table.return_value.select.assert_any_call("count", count="exact")
        
        # Verify content piece status update
        mock_supabase.table.assert_any_call("content_pieces")
        mock_supabase.table.return_value.update.assert_called_once_with({"status": "researched"})
        
        # Verify research inserts (one for each research point)
        self.assertEqual(mock_supabase.table.return_value.insert.call_count, 3)  # 2 research points + 1 agent status entry

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_results_to_file(self, mock_json_dump, mock_file_open):
        """Test saving research results to a file."""
        content_id = "test-content-id"
        content_title = "Test Article Title"
        
        filename = save_results_to_file(content_id, content_title, self.mock_research_points)
        
        mock_file_open.assert_called_once()
        mock_json_dump.assert_called_once()
        self.assertTrue(filename.startswith("research_"))


if __name__ == "__main__":
    unittest.main()
