"""
Unit tests for the draft writer agent.
"""

import os
import json
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import importlib.util

import pytest

# Dynamically load the agent module from its new location
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "draft_writer_agent",
    os.path.join(REPO_ROOT, "agents", "draft-writer-agent", "index.py"),
)
draft_writer_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(draft_writer_agent)
sys.modules["draft_writer_agent"] = draft_writer_agent

# Import functions to test
from draft_writer_agent import (
    setup_openai,
    get_supabase_client,
    get_content_piece,
    get_content_keywords,
    get_content_research,
    get_strategic_plan,
    get_seo_agent_output,
    write_draft_with_ai,
    save_draft_to_database,
    save_draft_to_file
)


class TestDraftWriterAgent(unittest.TestCase):
    """Test cases for the draft writer agent functions."""

    def setUp(self):
        """Set up test case."""
        self.mock_content_piece = {
            "id": "test-content-id",
            "strategic_plan_id": "test-plan-id",
            "title": "Test Article Title",
            "slug": "test-article-title",
            "status": "researched",
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
        
        self.mock_research = [
            {
                "id": "test-research-id-001",
                "content_id": "test-content-id",
                "excerpt": "This is a test fact about technology.",
                "url": "https://example.com/fact",
                "type": "fact",
                "confidence": 0.9
            },
            {
                "id": "test-research-id-002",
                "content_id": "test-content-id",
                "excerpt": "This is a test quote from an expert in technology.",
                "url": "https://example.com/quote",
                "type": "quote",
                "confidence": 0.85
            }
        ]
        
        self.mock_seo_output = {
            "content_idea": {
                "title": "Test Article Title",
                "focus_keyword": "test keyword",
                "description": "This is a test description.",
                "estimated_word_count": 1500,
                "suggested_sections": ["Introduction", "Section 1", "Conclusion"]
            },
            "keywords": {
                "focus": "test keyword",
                "supporting": ["support1", "support2"]
            }
        }
        
        self.mock_draft_text = """
# Test Article Title

## Introduction
This is a test introduction about test keyword.

## Section 1
This is the first section discussing test keyword in detail.

## Conclusion
In conclusion, test keyword is important for test audience.
"""

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
        
        with patch("draft_writer_agent.create_client") as mock_create_client:
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
        """Test retrieving a researched content piece."""
        mock_supabase = MagicMock()
        mock_limit = MagicMock()
        mock_limit.execute.return_value = MagicMock(data=[self.mock_content_piece])
        mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value = mock_limit
        
        content_piece = get_content_piece(mock_supabase)
        
        mock_supabase.table.assert_called_once_with("content_pieces")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("status", "researched")
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

    def test_get_content_research(self):
        """Test retrieving research for a content piece."""
        mock_supabase = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=self.mock_research)
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_execute
        
        research = get_content_research(mock_supabase, "test-content-id")
        
        mock_supabase.table.assert_called_once_with("research")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("content_id", "test-content-id")
        self.assertEqual(research, self.mock_research)

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

    def test_get_seo_agent_output(self):
        """Test retrieving SEO agent output for a content piece."""
        mock_supabase = MagicMock()
        mock_execute = MagicMock()
        mock_agent_status = {"output": self.mock_seo_output}
        mock_execute.execute.return_value = MagicMock(data=[mock_agent_status])
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value = mock_execute
        
        seo_output = get_seo_agent_output(mock_supabase, "test-content-id")
        
        mock_supabase.table.assert_called_once_with("agent_status")
        mock_supabase.table.return_value.select.assert_called_once_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("content_id", "test-content-id")
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.assert_called_once_with("agent", "seo-agent")
        self.assertEqual(seo_output, self.mock_seo_output)

    @patch("builtins.print")
    def test_write_draft_with_ai(self, mock_print):
        """Test writing a draft with OpenAI."""
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=self.mock_draft_text))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = write_draft_with_ai(
            mock_openai_client, 
            self.mock_content_piece, 
            self.mock_keywords, 
            self.mock_research, 
            self.mock_plan, 
            self.mock_seo_output
        )
        
        mock_openai_client.chat.completions.create.assert_called_once()
        self.assertEqual(result, self.mock_draft_text)

    @patch("builtins.print")
    def test_save_draft_to_database(self, mock_print):
        """Test saving draft to the database."""
        mock_supabase = MagicMock()
        
        # Mock the update operation
        mock_update_execute = MagicMock()
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_execute
        
        # Mock the insert operation
        mock_insert_response = MagicMock(data=[{"id": "new-agent-status-id"}])
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_response
        
        # Call the function to test
        result = save_draft_to_database(mock_supabase, "test-content-id", self.mock_draft_text)
        
        # Verify content piece update
        mock_supabase.table.assert_any_call("content_pieces")
        mock_supabase.table.return_value.update.assert_called_once()
        
        # Verify agent status insert
        mock_supabase.table.assert_any_call("agent_status")
        mock_supabase.table.return_value.insert.assert_called_once()
        
        self.assertTrue(result)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_draft_to_file(self, mock_file_open):
        """Test saving draft to a file."""
        content_id = "test-content-id"
        content_title = "Test Article Title"
        
        filename = save_draft_to_file(content_id, content_title, self.mock_draft_text)
        
        mock_file_open.assert_called_once_with(filename, "w")
        handle = mock_file_open()
        handle.write.assert_called_once_with(self.mock_draft_text)
        self.assertTrue(filename.startswith("draft_"))


if __name__ == "__main__":
    unittest.main()
