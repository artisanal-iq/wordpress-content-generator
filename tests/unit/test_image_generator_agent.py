#!/usr/bin/env python3
"""
Unit tests for Image Generator Agent
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
import base64
from datetime import datetime
from io import StringIO, BytesIO
from pathlib import Path

# Add the parent directory to the path so we can import the image_generator_agent module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import image_generator_agent

class TestImageGeneratorAgent(unittest.TestCase):
    """Test cases for Image Generator Agent."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock content piece data
        self.content_piece = {
            "id": "test-content-123",
            "title": "Test Article",
            "status": "line_edited",
            "draft_text": "This is a test article about artificial intelligence.",
            "strategic_plan_id": "test-plan-456"
        }
        
        # Mock keywords data
        self.keywords = {
            "focus_keyword": "artificial intelligence",
            "supporting_keywords": ["AI", "machine learning", "neural networks"]
        }
        
        # Mock strategic plan data
        self.plan = {
            "id": "test-plan-456",
            "domain": "example.com",
            "audience": "technology enthusiasts",
            "tone": "informative",
            "niche": "technology",
            "goal": "educate readers"
        }
        
        # Mock OpenAI DALL-E response
        self.mock_image_data = b'test_image_data'
        self.mock_image_base64 = base64.b64encode(self.mock_image_data).decode('utf-8')
        
        self.openai_response = MagicMock()
        self.openai_response.data = [MagicMock()]
        self.openai_response.data[0].b64_json = self.mock_image_base64
        self.openai_response.data[0].revised_prompt = "A professional image depicting artificial intelligence concepts"
        
        # Mock Supabase client
        self.mock_supabase = MagicMock()
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [self.content_piece]
        
        # Set up patch for open function to avoid actual file operations
        self.mock_open = mock_open()
        
        # Mock Path.mkdir to avoid creating directories
        self.mock_mkdir = MagicMock()
        
    @patch('image_generator_agent.get_supabase_client')
    @patch('image_generator_agent.setup_openai')
    @patch('builtins.open', new_callable=mock_open)
    @patch('image_generator_agent.Path.mkdir')
    def test_main_functionality(self, mock_mkdir, mock_file_open, mock_setup_openai, mock_get_supabase):
        """Test the main functionality of the Image Generator Agent."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_openai_client = MagicMock()
        mock_openai_client.images.generate.return_value = self.openai_response
        mock_setup_openai.return_value = mock_openai_client
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function with test arguments
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['image_generator_agent.py'] + test_args):
            try:
                image_generator_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify Supabase interactions
        self.mock_supabase.table.assert_any_call("content_pieces")
        self.mock_supabase.table.assert_any_call("keywords")
        self.mock_supabase.table.assert_any_call("strategic_plans")
        self.mock_supabase.table.assert_any_call("images")
        
        # Verify OpenAI was called with appropriate parameters
        mock_openai_client.images.generate.assert_called_once()
        call_args = mock_openai_client.images.generate.call_args[1]
        self.assertEqual(call_args["model"], "dall-e-3")
        self.assertIn("artificial intelligence", call_args["prompt"])
        
        # Verify content piece was updated with new status and image reference
        update_call = self.mock_supabase.table.return_value.update.call_args[0][0]
        self.assertEqual(update_call["status"], "image_generated")
        self.assertIn("featured_image_id", update_call)
        
        # Verify image record was created
        insert_call = self.mock_supabase.table.return_value.insert.call_args_list[0][0][0]
        self.assertEqual(insert_call["content_id"], "test-content-123")
        self.assertIn("file_path", insert_call)
        self.assertIn("metadata", insert_call)
        
        # Verify agent status was logged
        agent_status_call = self.mock_supabase.table.return_value.insert.call_args_list[1][0][0]
        self.assertEqual(agent_status_call["agent"], "image-generator-agent")
        self.assertEqual(agent_status_call["status"], "completed")
        
        # Verify image directory was created
        mock_mkdir.assert_called_once_with(exist_ok=True)
        
        # Verify image was saved to file
        mock_file_open.assert_called()
        mock_file_open.return_value.write.assert_called_with(self.mock_image_data)
        
        # Check output for success message
        output = captured_output.getvalue()
        self.assertIn("Image Generator Agent completed successfully", output)

    @patch('image_generator_agent.get_supabase_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('image_generator_agent.Path.mkdir')
    def test_mock_data_mode(self, mock_mkdir, mock_file_open, mock_get_supabase):
        """Test the agent with --no-ai flag to use mock data."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function with --no-ai flag
        test_args = ["--content-id", "test-content-123", "--no-ai"]
        with patch('sys.argv', ['image_generator_agent.py'] + test_args):
            try:
                image_generator_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify OpenAI was not used (no setup_openai call)
        self.assertIn("Using mock image generator (--no-ai flag set)", captured_output.getvalue())
        
        # Verify content piece was updated with new status
        update_call = self.mock_supabase.table.return_value.update.call_args[0][0]
        self.assertEqual(update_call["status"], "image_generated")
        
        # Verify image was saved to file
        mock_file_open.assert_called()
        mock_mkdir.assert_called_once_with(exist_ok=True)

    @patch('image_generator_agent.get_supabase_client')
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
        with patch('sys.argv', ['image_generator_agent.py'] + test_args):
            with self.assertRaises(SystemExit) as cm:
                image_generator_agent.main()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error: Content piece with ID nonexistent-id not found", captured_output.getvalue())
        
        # Verify exit code
        self.assertEqual(cm.exception.code, 1)

    @patch('image_generator_agent.get_supabase_client')
    @patch('image_generator_agent.setup_openai')
    def test_openai_error_handling(self, mock_setup_openai, mock_get_supabase):
        """Test handling of OpenAI API errors."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_openai_client = MagicMock()
        mock_openai_client.images.generate.side_effect = Exception("DALL-E API error")
        mock_setup_openai.return_value = mock_openai_client
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['image_generator_agent.py'] + test_args):
            with self.assertRaises(SystemExit) as cm:
                image_generator_agent.main()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error generating image with DALL-E", captured_output.getvalue())
        
        # Verify exit code
        self.assertEqual(cm.exception.code, 1)

    @patch('image_generator_agent.get_supabase_client')
    @patch('image_generator_agent.setup_openai')
    @patch('builtins.open', new_callable=mock_open)
    @patch('image_generator_agent.Path.mkdir')
    def test_database_error_handling(self, mock_mkdir, mock_file_open, mock_setup_openai, mock_get_supabase):
        """Test handling of database errors when saving results."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_openai_client = MagicMock()
        mock_openai_client.images.generate.return_value = self.openai_response
        mock_setup_openai.return_value = mock_openai_client
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.plan])            # get_strategic_plan
        ]
        
        # Make the insert method raise an exception
        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['image_generator_agent.py'] + test_args):
            try:
                image_generator_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error updating database with image", captured_output.getvalue())
        
        # Verify file was still saved despite database error
        mock_file_open.assert_called()

    def test_create_image_prompt(self):
        """Test the image prompt generation function."""
        # Test with title and keywords
        prompt = image_generator_agent.create_image_prompt(self.content_piece, self.keywords)
        self.assertIn(self.content_piece["title"], prompt)
        self.assertIn(self.keywords["focus_keyword"], prompt)
        
        # Test with title only (no keywords)
        prompt_no_keywords = image_generator_agent.create_image_prompt(self.content_piece, None)
        self.assertIn(self.content_piece["title"], prompt_no_keywords)
        self.assertNotIn("about artificial intelligence", prompt_no_keywords)
        
        # Test with empty content piece
        empty_content = {"title": "", "draft_text": ""}
        prompt_empty = image_generator_agent.create_image_prompt(empty_content, None)
        self.assertIn("Create a professional", prompt_empty)
        
    def test_generate_mock_image(self):
        """Test the mock image generation function."""
        prompt = "Test prompt for mock image"
        image_data, metadata = image_generator_agent.generate_mock_image(prompt)
        
        # Verify image data is bytes
        self.assertIsInstance(image_data, bytes)
        
        # Verify metadata contains expected keys
        self.assertEqual(metadata["prompt"], prompt)
        self.assertEqual(metadata["revised_prompt"], prompt)
        self.assertEqual(metadata["model"], "mock-image-generator")
        self.assertEqual(metadata["size"], "1024x1024")
        self.assertEqual(metadata["quality"], "standard")
        self.assertIn("created", metadata)


if __name__ == '__main__':
    unittest.main()
