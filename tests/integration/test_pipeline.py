"""
Integration tests for the full content generation pipeline.
"""

import os
import json
import sys
import uuid
import unittest
from unittest.mock import patch, MagicMock

import pytest

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import modules to test
from orchestrator import (
    create_strategic_plan,
    run_seo_agent,
    run_research_agent,
    run_draft_writer_agent,
    process_content_piece,
    get_content_pieces_by_plan
)


class TestContentPipeline(unittest.TestCase):
    """Test cases for the full content pipeline."""

    def setUp(self):
        """Set up test case."""
        # Mock strategic plan
        self.mock_plan_id = str(uuid.uuid4())
        self.mock_plan = {
            "id": self.mock_plan_id,
            "domain": "example.com",
            "audience": "test audience",
            "tone": "informative",
            "niche": "technology",
            "goal": "educate readers"
        }
        
        # Mock content pieces
        self.mock_content_id = str(uuid.uuid4())
        self.mock_content_piece = {
            "id": self.mock_content_id,
            "strategic_plan_id": self.mock_plan_id,
            "title": "Test Article Title",
            "slug": "test-article-title",
            "status": "draft"
        }

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    def test_create_strategic_plan(self, mock_get_supabase, mock_print):
        """Test creating a strategic plan."""
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock insert operation
        mock_insert_response = MagicMock(data=[{"id": self.mock_plan_id}])
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_response
        
        # Call the function
        plan_args = {
            "domain": "example.com",
            "audience": "test audience",
            "tone": "informative",
            "niche": "technology",
            "goal": "educate readers"
        }
        plan_id = create_strategic_plan(plan_args)
        
        # Verify the plan was created
        mock_supabase.table.assert_called_once_with("strategic_plans")
        mock_supabase.table.return_value.insert.assert_called_once()
        self.assertEqual(plan_id, self.mock_plan_id)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_seo_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the SEO agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        # Call the function
        result = run_seo_agent(self.mock_plan_id)
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_research_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the research agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0
        
        # Call the function
        result = run_research_agent(self.mock_content_id)
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_draft_writer_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the draft writer agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0
        
        # Call the function
        result = run_draft_writer_agent(self.mock_content_id)
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.run_research_agent")
    @patch("orchestrator.run_draft_writer_agent")
    def test_process_content_piece(self, mock_draft_writer, mock_research, mock_print):
        """Test processing a content piece through the pipeline."""
        # Mock agent results
        mock_research.return_value = True
        mock_draft_writer.return_value = True
        
        # Setup content piece with different statuses to test each step
        content_piece_draft = {**self.mock_content_piece, "status": "draft"}
        content_piece_researched = {**self.mock_content_piece, "status": "researched"}
        
        # Test processing a draft content piece
        result_draft = process_content_piece(content_piece_draft, 1, 1)
        mock_research.assert_called_once_with(self.mock_content_id)
        self.assertTrue(result_draft)
        
        # Reset mocks
        mock_research.reset_mock()
        mock_draft_writer.reset_mock()
        
        # Test processing a researched content piece
        result_researched = process_content_piece(content_piece_researched, 1, 1)
        mock_draft_writer.assert_called_once_with(self.mock_content_id)
        self.assertTrue(result_researched)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    def test_get_content_pieces_by_plan(self, mock_get_supabase, mock_print):
        """Test retrieving content pieces for a strategic plan."""
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock RPC call for select_content_pieces_by_plan function
        mock_rpc_response = MagicMock(data=[self.mock_content_piece])
        mock_supabase.rpc.return_value.execute.return_value = mock_rpc_response
        
        # Test the RPC method
        content_pieces_rpc = get_content_pieces_by_plan(self.mock_plan_id)
        mock_supabase.rpc.assert_called_once_with("select_content_pieces_by_plan", {"plan_id_param": self.mock_plan_id})
        self.assertEqual(len(content_pieces_rpc), 1)
        self.assertEqual(content_pieces_rpc[0]["id"], self.mock_content_id)
        
        # Reset and mock the RPC method failing
        mock_supabase.reset_mock()
        mock_supabase.rpc.return_value.execute.side_effect = Exception("RPC failed")
        
        # Mock direct query as fallback
        mock_table_response = MagicMock(data=[self.mock_content_piece])
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_table_response
        
        # Test the fallback method
        content_pieces_fallback = get_content_pieces_by_plan(self.mock_plan_id)
        mock_supabase.table.assert_called_once_with("content_pieces")
        self.assertEqual(len(content_pieces_fallback), 1)
        self.assertEqual(content_pieces_fallback[0]["id"], self.mock_content_id)


if __name__ == "__main__":
    unittest.main()
