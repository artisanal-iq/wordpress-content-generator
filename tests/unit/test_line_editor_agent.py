#!/usr/bin/env python3
"""
Unit tests for Line Editor Agent
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
from datetime import datetime
from io import StringIO

# Add the parent directory to the path so we can import the line_editor_agent module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import line_editor_agent

class TestLineEditorAgent(unittest.TestCase):
    """Test cases for Line Editor Agent."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock content piece data
        self.content_piece = {
            "id": "test-content-123",
            "title": "Test Article",
            "status": "flow_edited",
            "draft_text": "This is a test article. It needs better grammar and style.",
            "strategic_plan_id": "test-plan-456"
        }
        
        # Mock keywords data
        self.keywords = {
            "focus_keyword": "test keyword",
            "supporting_keywords": ["grammar", "style", "editing"]
        }
        
        # Mock research data
        self.research = [
            {"title": "Research Item 1", "content": "Some research content"}
        ]
        
        # Mock strategic plan data
        self.plan = {
            "id": "test-plan-456",
            "domain": "example.com",
            "audience": "general readers",
            "tone": "informative",
            "niche": "technology",
            "goal": "educate readers"
        }
        
        # Mock OpenAI response
        self.openai_response = MagicMock()
        self.openai_response.choices = [MagicMock()]
        self.openai_response.choices[0].message.content = "This is an improved test article. It has better grammar and style."
        
        # Mock Supabase client
        self.mock_supabase = MagicMock()
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [self.content_piece]
        
        # Set up patch for open function to avoid actual file operations
        self.mock_open = mock_open()
        
    @patch('line_editor_agent.get_supabase_client')
    @patch('line_editor_agent.setup_openai')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_functionality(self, mock_file_open, mock_setup_openai, mock_get_supabase):
        """Test the main functionality of the Line Editor Agent."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_openai_client = MagicMock()
        mock_openai_client.chat.completions.create.return_value = self.openai_response
        mock_setup_openai.return_value = mock_openai_client
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=self.research),         # get_content_research
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function with test arguments
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['line_editor_agent.py'] + test_args):
            try:
                line_editor_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify Supabase interactions
        self.mock_supabase.table.assert_any_call("content_pieces")
        self.mock_supabase.table.assert_any_call("keywords")
        self.mock_supabase.table.assert_any_call("research")
        self.mock_supabase.table.assert_any_call("strategic_plans")
        
        # Verify OpenAI was called with appropriate parameters
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4")
        self.assertEqual(len(call_args["messages"]), 2)
        
        # Verify content piece was updated with new status
        update_call = self.mock_supabase.table.return_value.update.call_args[0][0]
        self.assertEqual(update_call["status"], "line_edited")
        self.assertIn("draft_text", update_call)
        
        # Verify agent status was logged
        insert_call = self.mock_supabase.table.return_value.insert.call_args[0][0]
        self.assertEqual(insert_call["agent"], "line-editor-agent")
        self.assertEqual(insert_call["status"], "completed")
        
        # Verify file was saved
        mock_file_open.assert_called()
        
        # Check output for success message
        output = captured_output.getvalue()
        self.assertIn("Line Editor Agent completed successfully", output)

    @patch('line_editor_agent.get_supabase_client')
    @patch('builtins.open', new_callable=mock_open)
    def test_mock_data_mode(self, mock_file_open, mock_get_supabase):
        """Test the agent with --no-ai flag to use mock data."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=self.research),         # get_content_research
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function with --no-ai flag
        test_args = ["--content-id", "test-content-123", "--no-ai"]
        with patch('sys.argv', ['line_editor_agent.py'] + test_args):
            try:
                line_editor_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify OpenAI was not used (no setup_openai call)
        self.assertIn("Using mock data (--no-ai flag set)", captured_output.getvalue())
        
        # Verify content piece was updated with new status
        update_call = self.mock_supabase.table.return_value.update.call_args[0][0]
        self.assertEqual(update_call["status"], "line_edited")
        
        # Verify file was saved
        mock_file_open.assert_called()

    @patch('line_editor_agent.get_supabase_client')
    def test_no_content_pieces_found(self, mock_get_supabase):
        """Test handling of no content pieces found."""
        # Set up mock to return empty data
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_get_supabase.return_value = mock_supabase
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "nonexistent-id"]
        with patch('sys.argv', ['line_editor_agent.py'] + test_args):
            with self.assertRaises(SystemExit) as cm:
                line_editor_agent.main()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error: Content piece with ID nonexistent-id not found", captured_output.getvalue())
        
        # Verify exit code
        self.assertEqual(cm.exception.code, 1)

    @patch('line_editor_agent.get_supabase_client')
    @patch('line_editor_agent.setup_openai')
    def test_openai_error_handling(self, mock_setup_openai, mock_get_supabase):
        """Test handling of OpenAI API errors."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_openai_client = MagicMock()
        mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI API error")
        mock_setup_openai.return_value = mock_openai_client
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=self.research),         # get_content_research
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['line_editor_agent.py'] + test_args):
            with self.assertRaises(SystemExit) as cm:
                line_editor_agent.main()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error using OpenAI to improve grammar and style", captured_output.getvalue())
        
        # Verify exit code
        self.assertEqual(cm.exception.code, 1)

    @patch('line_editor_agent.get_supabase_client')
    @patch('line_editor_agent.setup_openai')
    @patch('builtins.open', new_callable=mock_open)
    def test_database_error_handling(self, mock_file_open, mock_setup_openai, mock_get_supabase):
        """Test handling of database errors when saving results."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_openai_client = MagicMock()
        mock_openai_client.chat.completions.create.return_value = self.openai_response
        mock_setup_openai.return_value = mock_openai_client
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=self.research),         # get_content_research
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Make the update method raise an exception
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['line_editor_agent.py'] + test_args):
            try:
                line_editor_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error saving line-edited article to database", captured_output.getvalue())
        
        # Verify file was still saved despite database error
        mock_file_open.assert_called()

    def test_generate_mock_line_edited(self):
        """Test the mock data generation function."""
        # Test with empty content piece
        empty_content = {}
        mock_result = line_editor_agent.generate_mock_line_edited(empty_content)
        self.assertIn("Mock Line-Edited Article", mock_result)
        
        # Test with actual content
        content_with_text = {
            "draft_text": "This is a test article with some common errors.  There are double spaces, and dont forget about apostrophes."
        }
        mock_result = line_editor_agent.generate_mock_line_edited(content_with_text)
        self.assertIn("This is a test article with some common errors.", mock_result)
        self.assertIn("don't", mock_result)  # Should fix apostrophe
        self.assertNotIn("  ", mock_result)  # Should fix double spaces


if __name__ == '__main__':
    unittest.main()
