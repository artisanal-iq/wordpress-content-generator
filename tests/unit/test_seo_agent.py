"""
Unit tests for the enhanced SEO agent.
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

# Import functions to test (adjust these imports based on your actual file structure)
from enhanced_seo_agent import (
    setup_openai,
    get_supabase_client,
    get_strategic_plan,
    analyze_seo_keywords_with_ai,
    generate_content_ideas_with_ai,
    save_results_to_database,
    save_results_to_file
)


class TestSEOAgent(unittest.TestCase):
    """Test cases for the SEO agent functions."""

    def setUp(self):
        """Set up test case."""
        self.mock_plan = {
            "id": "test-plan-id",
            "domain": "example.com",
            "audience": "test audience",
            "tone": "informative",
            "niche": "technology",
            "goal": "educate readers"
        }
        
        self.mock_keywords = {
            "focus_keyword": "test keyword",
            "supporting_keywords": ["support1", "support2"],
            "search_volume": {
                "test keyword": 1000,
                "support1": 500,
                "support2": 300
            }
        }
        
        self.mock_content_ideas = [
            {
                "title": "Test Article Title",
                "focus_keyword": "test keyword",
                "description": "This is a test description.",
                "estimated_word_count": 1500,
                "suggested_sections": ["Intro", "Section 1", "Conclusion"]
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
        
        with patch("enhanced_seo_agent.create_client") as mock_create_client:
            mock_create_client.return_value = "mock-supabase-client"
            client = get_supabase_client()
            
            mock_create_client.assert_called_once_with("fake-url", "fake-key")
            self.assertEqual(client, "mock-supabase-client")

    def test_get_strategic_plan_with_id(self):
        """Test retrieving a strategic plan with a specific ID."""
        mock_supabase = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[self.mock_plan])
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_execute
        
        plan = get_strategic_plan(mock_supabase, "test-plan-id")
        
        mock_supabase.table.assert_called_once_with("strategic_plans")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("id", "test-plan-id")
        self.assertEqual(plan, self.mock_plan)

    def test_get_strategic_plan_no_id(self):
        """Test retrieving the most recent strategic plan."""
        mock_supabase = MagicMock()
        mock_limit = MagicMock()
        mock_limit.execute.return_value = MagicMock(data=[self.mock_plan])
        mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value = mock_limit
        
        plan = get_strategic_plan(mock_supabase)
        
        mock_supabase.table.assert_called_once_with("strategic_plans")
        mock_supabase.table.return_value.select.return_value.order.assert_called_once()
        mock_supabase.table.return_value.select.return_value.order.return_value.limit.assert_called_once_with(1)
        self.assertEqual(plan, self.mock_plan)

    @patch("builtins.print")
    def test_analyze_seo_keywords_with_ai(self, mock_print):
        """Test analyzing SEO keywords with OpenAI."""
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(self.mock_keywords)))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = analyze_seo_keywords_with_ai(mock_openai_client, self.mock_plan)
        
        mock_openai_client.chat.completions.create.assert_called_once()
        self.assertEqual(result, self.mock_keywords)

    @patch("builtins.print")
    def test_generate_content_ideas_with_ai(self, mock_print):
        """Test generating content ideas with OpenAI."""
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps({"content_ideas": self.mock_content_ideas})))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = generate_content_ideas_with_ai(mock_openai_client, self.mock_plan, self.mock_keywords)
        
        mock_openai_client.chat.completions.create.assert_called_once()
        self.assertEqual(result, self.mock_content_ideas)

    @patch("builtins.print")
    def test_save_results_to_database(self, mock_print):
        """Test saving SEO results to the database."""
        mock_supabase = MagicMock()
        mock_insert_response = MagicMock(data=[{"id": "new-content-id"}])
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_response
        
        result = save_results_to_database(mock_supabase, "test-plan-id", self.mock_keywords, self.mock_content_ideas)
        
        # Should call table().insert().execute() for each content idea
        self.assertEqual(mock_supabase.table.call_count, 3)  # Once for content_piece, keywords, and agent_status
        self.assertEqual(len(result), 1)  # Should return one content piece ID

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_results_to_file(self, mock_json_dump, mock_file_open):
        """Test saving SEO results to a file."""
        plan_id = "test-plan-id"
        
        filename = save_results_to_file(plan_id, self.mock_keywords, self.mock_content_ideas)
        
        mock_file_open.assert_called_once()
        mock_json_dump.assert_called_once()
        self.assertTrue(filename.startswith("seo_analysis_"))


if __name__ == "__main__":
    unittest.main()
