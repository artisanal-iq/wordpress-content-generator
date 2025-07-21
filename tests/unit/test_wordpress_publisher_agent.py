#!/usr/bin/env python3
"""
Unit tests for WordPress Publisher Agent
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import importlib.util
import json
import uuid
import base64
from datetime import datetime
from io import StringIO
from pathlib import Path

# Dynamically load the agent module from its new location
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "wordpress_publisher_agent",
    os.path.join(REPO_ROOT, "agents", "wordpress-publisher-agent", "index.py"),
)
wordpress_publisher_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wordpress_publisher_agent)
sys.modules["wordpress_publisher_agent"] = wordpress_publisher_agent

class TestWordPressPublisherAgent(unittest.TestCase):
    """Test cases for WordPress Publisher Agent."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock content piece data
        self.content_piece = {
            "id": "test-content-123",
            "title": "Test Article",
            "status": "image_generated",
            "draft_text": "<h1>Test Article</h1><p>This is a test article about WordPress publishing.</p>",
            "slug": "test-article",
            "featured_image_id": "test-image-456",
            "strategic_plan_id": "test-plan-789"
        }
        
        # Mock keywords data
        self.keywords = {
            "content_id": "test-content-123",
            "focus_keyword": "WordPress publishing",
            "supporting_keywords": ["content automation", "WordPress API", "publishing workflow"]
        }
        
        # Mock image data
        self.image_data = {
            "id": "test-image-456",
            "content_id": "test-content-123",
            "file_path": "/tmp/test-image.png",
            "metadata": {
                "prompt": "Test image prompt",
                "model": "dall-e-3"
            }
        }
        
        # Mock WordPress credentials
        self.wp_credentials = {
            "url": "https://example.com/wp-json/wp/v2/",
            "user": "testuser",
            "password": "testpass"
        }
        
        # Mock WordPress API responses
        self.wp_media_response = {
            "id": 123,
            "source_url": "https://example.com/wp-content/uploads/2023/07/test-image.png",
            "title": {"rendered": "Test Image"}
        }
        
        self.wp_post_response = {
            "id": 456,
            "link": "https://example.com/test-article/",
            "title": {"rendered": "Test Article"},
            "status": "publish"
        }
        
        self.wp_tag_response = {
            "id": 789,
            "name": "WordPress publishing",
            "slug": "wordpress-publishing"
        }
        
        # Mock Supabase client
        self.mock_supabase = MagicMock()
        
        # Set up patch for open function to avoid actual file operations
        self.mock_open = mock_open(read_data=b'test image data')

    @patch('wordpress_publisher_agent.get_supabase_client')
    @patch('wordpress_publisher_agent.get_wordpress_credentials')
    @patch('requests.post')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('wordpress_publisher_agent.Path.exists')
    def test_main_functionality(self, mock_path_exists, mock_file_open, mock_get, mock_post, mock_get_wp_creds, mock_get_supabase):
        """Test the main functionality of the WordPress Publisher Agent."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_get_wp_creds.return_value = self.wp_credentials
        mock_path_exists.return_value = True
        mock_file_open.return_value.read.return_value = b'test image data'
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.image_data])      # get_content_image
        ]
        
        # Set up WordPress API responses
        mock_post.side_effect = [
            MagicMock(status_code=201, json=lambda: self.wp_media_response),  # upload_image_to_wordpress
            MagicMock(status_code=201, json=lambda: self.wp_post_response)    # create_wordpress_post
        ]
        
        mock_get.return_value = MagicMock(status_code=200, json=lambda: [])  # get_or_create_tag (empty list, tag not found)
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function with test arguments
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            try:
                wordpress_publisher_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify Supabase interactions
        self.mock_supabase.table.assert_any_call("content_pieces")
        self.mock_supabase.table.assert_any_call("keywords")
        self.mock_supabase.table.assert_any_call("images")
        self.mock_supabase.table.assert_any_call("agent_status")
        
        # Verify WordPress API interactions
        mock_post.assert_any_call(
            f"{self.wp_credentials['url']}media",
            headers=unittest.mock.ANY,
            data=b'test image data',
            auth=(self.wp_credentials['user'], self.wp_credentials['password'])
        )
        
        mock_post.assert_any_call(
            f"{self.wp_credentials['url']}posts",
            headers=unittest.mock.ANY,
            json=unittest.mock.ANY,
            auth=(self.wp_credentials['user'], self.wp_credentials['password'])
        )
        
        # Verify content piece was updated with new status and WordPress post info
        update_call = self.mock_supabase.table.return_value.update.call_args[0][0]
        self.assertEqual(update_call["status"], "published")
        self.assertEqual(update_call["wordpress_post_id"], self.wp_post_response["id"])
        self.assertEqual(update_call["wordpress_post_url"], self.wp_post_response["link"])
        
        # Verify agent status was logged
        agent_status_call = self.mock_supabase.table.return_value.insert.call_args[0][0]
        self.assertEqual(agent_status_call["agent"], "wordpress-publisher-agent")
        self.assertEqual(agent_status_call["status"], "completed")
        
        # Check output for success message
        output = captured_output.getvalue()
        self.assertIn("WordPress Publisher Agent completed successfully", output)

    @patch('wordpress_publisher_agent.get_supabase_client')
    @patch('wordpress_publisher_agent.get_wordpress_credentials')
    @patch('requests.post')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('wordpress_publisher_agent.Path.exists')
    def test_preview_mode(self, mock_path_exists, mock_file_open, mock_get, mock_post, mock_get_wp_creds, mock_get_supabase):
        """Test the preview mode functionality."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_get_wp_creds.return_value = self.wp_credentials
        mock_path_exists.return_value = True
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.image_data])      # get_content_image
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function with preview flag
        test_args = ["--content-id", "test-content-123", "--preview"]
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            try:
                wordpress_publisher_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify WordPress API was not called to create post
        mock_post.assert_not_called()
        
        # Verify content piece status was not updated
        self.mock_supabase.table.return_value.update.assert_not_called()
        
        # Check output for preview message
        output = captured_output.getvalue()
        self.assertIn("=== WordPress Post Preview ===", output)
        self.assertIn("Preview mode: Post was not published to WordPress", output)

    @patch('wordpress_publisher_agent.get_supabase_client')
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
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            with self.assertRaises(SystemExit) as cm:
                wordpress_publisher_agent.main()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn(f"Error: Content piece with ID nonexistent-id not found", captured_output.getvalue())
        
        # Verify exit code
        self.assertEqual(cm.exception.code, 1)

    @patch('wordpress_publisher_agent.get_supabase_client')
    @patch('wordpress_publisher_agent.get_wordpress_credentials')
    @patch('builtins.open', new_callable=mock_open)
    @patch('wordpress_publisher_agent.Path.exists')
    def test_image_upload_error(self, mock_path_exists, mock_file_open, mock_get_wp_creds, mock_get_supabase):
        """Test handling of image upload errors."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_get_wp_creds.return_value = self.wp_credentials
        mock_path_exists.return_value = False  # Image file doesn't exist
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.image_data])      # get_content_image
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            with patch('requests.post') as mock_post:
                # Make post creation succeed even without image
                mock_post.return_value = MagicMock(
                    status_code=201, 
                    json=lambda: self.wp_post_response
                )
                try:
                    wordpress_publisher_agent.main()
                except SystemExit:
                    pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn(f"Error: Image file not found at {self.image_data['file_path']}", captured_output.getvalue())
        
        # Verify WordPress post was still created without the image
        self.assertIn("Successfully created WordPress post", captured_output.getvalue())

    @patch('wordpress_publisher_agent.get_supabase_client')
    @patch('wordpress_publisher_agent.get_wordpress_credentials')
    @patch('requests.post')
    @patch('builtins.open', new_callable=mock_open)
    @patch('wordpress_publisher_agent.Path.exists')
    def test_post_creation_error(self, mock_path_exists, mock_file_open, mock_post, mock_get_wp_creds, mock_get_supabase):
        """Test handling of post creation errors."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_get_wp_creds.return_value = self.wp_credentials
        mock_path_exists.return_value = True
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.image_data])      # get_content_image
        ]
        
        # Make post creation fail
        mock_post.side_effect = [
            MagicMock(status_code=201, json=lambda: self.wp_media_response),  # upload_image_to_wordpress
            MagicMock(status_code=400, text="Bad request", json=lambda: {"code": "rest_invalid_param"})  # create_wordpress_post
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            with self.assertRaises(SystemExit) as cm:
                wordpress_publisher_agent.main()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error creating post: 400", captured_output.getvalue())
        
        # Verify exit code
        self.assertEqual(cm.exception.code, 1)
        
        # Verify content piece status was not updated
        self.mock_supabase.table.return_value.update.assert_not_called()

    @patch('wordpress_publisher_agent.get_supabase_client')
    @patch('wordpress_publisher_agent.get_wordpress_credentials')
    @patch('requests.post')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('wordpress_publisher_agent.Path.exists')
    def test_tag_handling(self, mock_path_exists, mock_file_open, mock_get, mock_post, mock_get_wp_creds, mock_get_supabase):
        """Test tag creation and handling."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_get_wp_creds.return_value = self.wp_credentials
        mock_path_exists.return_value = True
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.image_data])      # get_content_image
        ]
        
        # Set up WordPress API responses for tag handling
        # First, tag search returns empty (tag not found)
        # Then, tag creation succeeds
        mock_get.return_value = MagicMock(status_code=200, json=lambda: [])
        
        # Set up post responses
        mock_post.side_effect = [
            MagicMock(status_code=201, json=lambda: self.wp_media_response),  # upload_image_to_wordpress
            MagicMock(status_code=201, json=lambda: self.wp_tag_response),    # create tag
            MagicMock(status_code=201, json=lambda: self.wp_post_response)    # create_wordpress_post
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            try:
                wordpress_publisher_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify tag API was called
        mock_get.assert_called_with(
            f"{self.wp_credentials['url']}tags",
            params={'search': 'WordPress publishing'},
            auth=(self.wp_credentials['user'], self.wp_credentials['password'])
        )
        
        # Verify tag creation API was called
        mock_post.assert_any_call(
            f"{self.wp_credentials['url']}tags",
            headers={'Content-Type': 'application/json'},
            json={'name': 'WordPress publishing', 'slug': 'wordpress-publishing'},
            auth=(self.wp_credentials['user'], self.wp_credentials['password'])
        )
        
        # Now test with existing tag
        mock_get.return_value = MagicMock(
            status_code=200, 
            json=lambda: [{'id': 789, 'name': 'WordPress publishing', 'slug': 'wordpress-publishing'}]
        )
        
        mock_post.side_effect = [
            MagicMock(status_code=201, json=lambda: self.wp_media_response),  # upload_image_to_wordpress
            MagicMock(status_code=201, json=lambda: self.wp_post_response)    # create_wordpress_post
        ]
        
        # Reset stdout capture
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function again
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            try:
                wordpress_publisher_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify tag API was called but not tag creation
        self.assertEqual(mock_post.call_count, 2)  # Only media upload and post creation

    @patch('wordpress_publisher_agent.get_supabase_client')
    @patch('wordpress_publisher_agent.get_wordpress_credentials')
    @patch('requests.post')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('wordpress_publisher_agent.Path.exists')
    def test_database_error_handling(self, mock_path_exists, mock_file_open, mock_get, mock_post, mock_get_wp_creds, mock_get_supabase):
        """Test handling of database errors when updating content status."""
        # Set up mocks
        mock_get_supabase.return_value = self.mock_supabase
        mock_get_wp_creds.return_value = self.wp_credentials
        mock_path_exists.return_value = True
        
        # Set up Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[self.content_piece]),  # get_content_piece
            MagicMock(data=[self.keywords]),       # get_content_keywords
            MagicMock(data=[self.image_data])      # get_content_image
        ]
        
        # Make database update fail
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        
        # Set up WordPress API responses
        mock_get.return_value = MagicMock(status_code=200, json=lambda: [])
        mock_post.side_effect = [
            MagicMock(status_code=201, json=lambda: self.wp_media_response),  # upload_image_to_wordpress
            MagicMock(status_code=201, json=lambda: self.wp_tag_response),    # create tag
            MagicMock(status_code=201, json=lambda: self.wp_post_response)    # create_wordpress_post
        ]
        
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the main function
        test_args = ["--content-id", "test-content-123"]
        with patch('sys.argv', ['wordpress_publisher_agent.py'] + test_args):
            try:
                wordpress_publisher_agent.main()
            except SystemExit:
                pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Verify error message was printed
        self.assertIn("Error updating content piece status", captured_output.getvalue())
        
        # Verify agent status was logged with error
        agent_status_call = self.mock_supabase.table.return_value.insert.call_args[0][0]
        self.assertEqual(agent_status_call["agent"], "wordpress-publisher-agent")
        self.assertEqual(agent_status_call["status"], "failed")
        self.assertIn("error", agent_status_call)

    def test_get_wordpress_credentials(self):
        """Test WordPress credentials retrieval."""
        # Set environment variables
        with patch.dict(os.environ, {
            "WORDPRESS_URL": "https://example.com/",
            "WORDPRESS_USER": "testuser",
            "WORDPRESS_APP_PASSWORD": "testpass"
        }):
            credentials = wordpress_publisher_agent.get_wordpress_credentials()
            
            self.assertEqual(credentials["url"], "https://example.com/wp-json/wp/v2/")
            self.assertEqual(credentials["user"], "testuser")
            self.assertEqual(credentials["password"], "testpass")
        
        # Test with URL already having wp-json path
        with patch.dict(os.environ, {
            "WORDPRESS_URL": "https://example.com/wp-json/wp/v2/",
            "WORDPRESS_USER": "testuser",
            "WORDPRESS_APP_PASSWORD": "testpass"
        }):
            credentials = wordpress_publisher_agent.get_wordpress_credentials()
            
            self.assertEqual(credentials["url"], "https://example.com/wp-json/wp/v2/")
        
        # Test with missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                wordpress_publisher_agent.get_wordpress_credentials()


if __name__ == '__main__':
    unittest.main()
