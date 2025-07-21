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
    run_flow_editor_agent,
    run_line_editor_agent,
    run_draft_assembly_agent,
    run_image_generator_agent,
    run_wordpress_publisher_agent,  # Added this import
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
        plan_id = create_strategic_plan(mock_supabase, **plan_args)
        
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
        result = run_seo_agent(self.mock_plan_id, mock_supabase)
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertIn("agents/enhanced-seo-agent/index.py", mock_subprocess.call_args[0][0][1])
        self.assertIn("--plan-id", mock_subprocess.call_args[0][0][2])
        self.assertIn(self.mock_plan_id, mock_subprocess.call_args[0][0][3])

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_research_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the research agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0
        
        # Call the function
        result = run_research_agent(self.mock_content_id, MagicMock())
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertIn("agents/research-agent/index.py", mock_subprocess.call_args[0][0][1])
        self.assertIn("--content-id", mock_subprocess.call_args[0][0][2])
        self.assertIn(self.mock_content_id, mock_subprocess.call_args[0][0][3])
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_image_generator_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the image generator agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0

        # Call the function
        result = run_image_generator_agent(self.mock_content_id, MagicMock())

        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertIn("agents/image-generator-agent/index.py", mock_subprocess.call_args[0][0][1])
        self.assertIn("--content-id", mock_subprocess.call_args[0][0][2])
        self.assertIn(self.mock_content_id, mock_subprocess.call_args[0][0][3])
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_wordpress_publisher_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the WordPress publisher agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0
        
        # Call the function
        result = run_wordpress_publisher_agent(self.mock_content_id, MagicMock())
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertIn("agents/wordpress-publisher-agent/index.py", mock_subprocess.call_args[0][0][1])
        self.assertIn("--content-id", mock_subprocess.call_args[0][0][2])
        self.assertIn(self.mock_content_id, mock_subprocess.call_args[0][0][3])
        self.assertTrue(result)
        
        # Test with preview flag
        mock_subprocess.reset_mock()
        result = run_wordpress_publisher_agent(self.mock_content_id, MagicMock(), preview=True)
        self.assertIn("--preview", mock_subprocess.call_args[0][0])
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_draft_writer_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the draft writer agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0
        
        # Call the function
        result = run_draft_writer_agent(self.mock_content_id, MagicMock())
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertIn("agents/draft-writer-agent/index.py", mock_subprocess.call_args[0][0][1])
        self.assertIn("--content-id", mock_subprocess.call_args[0][0][2])
        self.assertIn(self.mock_content_id, mock_subprocess.call_args[0][0][3])
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_flow_editor_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the flow editor agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0
        
        # Call the function
        result = run_flow_editor_agent(self.mock_content_id, MagicMock())
        
        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertIn("agents/flow-editor-agent/index.py", mock_subprocess.call_args[0][0][1])
        self.assertIn("--content-id", mock_subprocess.call_args[0][0][2])
        self.assertIn(self.mock_content_id, mock_subprocess.call_args[0][0][3])
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    @patch("orchestrator.subprocess.run")
    def test_run_line_editor_agent(self, mock_subprocess, mock_get_supabase, mock_print):
        """Test running the line editor agent."""
        # Mock subprocess
        mock_subprocess.return_value.returncode = 0

        # Call the function
        result = run_line_editor_agent(self.mock_content_id, MagicMock())

        # Verify the agent was run
        mock_subprocess.assert_called_once()
        self.assertIn("agents/line-editor-agent/index.py", mock_subprocess.call_args[0][0][1])
        self.assertIn("--content-id", mock_subprocess.call_args[0][0][2])
        self.assertIn(self.mock_content_id, mock_subprocess.call_args[0][0][3])
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("orchestrator.run_research_agent")
    @patch("orchestrator.run_draft_writer_agent")
    @patch("orchestrator.run_flow_editor_agent")
    @patch("orchestrator.run_line_editor_agent")
    @patch("orchestrator.run_draft_assembly_agent")
    @patch("orchestrator.run_image_generator_agent")
    @patch("orchestrator.run_wordpress_publisher_agent")
    def test_process_content_piece(self, mock_wordpress_publisher, mock_image_gen, mock_draft_assembly,
                                   mock_line_editor, mock_flow_editor,
                                   mock_draft_writer, mock_research, mock_print):
        """Test processing a content piece through the pipeline."""
        # Mock agent results
        mock_research.return_value = True
        mock_draft_writer.return_value = True
        mock_flow_editor.return_value = True
        mock_line_editor.return_value = True
        mock_image_gen.return_value = True
        mock_wordpress_publisher.return_value = True
        
        # Setup content piece with different statuses to test each step
        content_piece_draft = {**self.mock_content_piece, "status": "draft"}
        content_piece_researched = {**self.mock_content_piece, "status": "researched"}
        content_piece_written = {**self.mock_content_piece, "status": "written"}
        content_piece_flow = {**self.mock_content_piece, "status": "flow_edited"}
        content_piece_line = {**self.mock_content_piece, "status": "line_edited"}
        content_piece_assembled = {**self.mock_content_piece, "status": "assembled"}
        content_piece_image = {**self.mock_content_piece, "status": "image_generated"}
        
        # Test processing a draft content piece
        result_draft = process_content_piece(content_piece_draft, MagicMock())
        mock_research.assert_called_once_with(self.mock_content_id, MagicMock(), True)
        self.assertTrue(result_draft)
        
        # Reset mocks
        mock_research.reset_mock()
        mock_draft_writer.reset_mock()
        mock_flow_editor.reset_mock()
        
        # Test processing a researched content piece
        result_researched = process_content_piece(content_piece_researched, MagicMock())
        mock_draft_writer.assert_called_once_with(self.mock_content_id, MagicMock(), True)
        self.assertTrue(result_researched)
        
        # Reset mocks
        mock_research.reset_mock()
        mock_draft_writer.reset_mock()
        mock_flow_editor.reset_mock()
        
        # Test processing a written content piece
        result_written = process_content_piece(content_piece_written, MagicMock())
        mock_flow_editor.assert_called_once_with(self.mock_content_id, MagicMock(), True)
        self.assertTrue(result_written)

        # Reset mocks
        mock_research.reset_mock()
        mock_draft_writer.reset_mock()
        mock_flow_editor.reset_mock()
        mock_line_editor.reset_mock()

        # Test processing a flow_edited content piece
        result_flow = process_content_piece(content_piece_flow, MagicMock())
        mock_line_editor.assert_called_once_with(self.mock_content_id, MagicMock(), True)
        self.assertTrue(result_flow)
        
        # Reset mocks
        mock_line_editor.reset_mock()
        mock_draft_assembly.reset_mock()
        
        # Test processing a line_edited content piece
        result_line = process_content_piece(content_piece_line, MagicMock())
        mock_draft_assembly.assert_called_once_with(self.mock_content_id, MagicMock(), True)
        self.assertTrue(result_line)

        # Reset mocks
        mock_draft_assembly.reset_mock()
        mock_image_gen.reset_mock()

        # Test processing an assembled content piece
        result_assembled = process_content_piece(content_piece_assembled, MagicMock())
        mock_image_gen.assert_called_once_with(self.mock_content_id, MagicMock(), True)
        self.assertTrue(result_assembled)

        # Reset mocks
        mock_image_gen.reset_mock()
        mock_wordpress_publisher.reset_mock()

        # Test processing an image_generated content piece
        result_image = process_content_piece(content_piece_image, MagicMock())
        mock_wordpress_publisher.assert_called_once_with(self.mock_content_id, MagicMock(), True, False)
        self.assertTrue(result_image)

    @patch("builtins.print")
    @patch("orchestrator.get_supabase_client")
    def test_get_content_pieces_by_plan(self, mock_get_supabase, mock_print):
        """Test retrieving content pieces for a strategic plan."""
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock RPC method
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


    # ------------------------------------------------------------------ #
    # Full-pipeline smoke test with all agents mocked                    #
    # ------------------------------------------------------------------ #
    @patch("builtins.print")  # silence orchestrator prints
    @patch("orchestrator.run_wordpress_publisher_agent")
    @patch("orchestrator.run_line_editor_agent")
    @patch("orchestrator.run_draft_assembly_agent")
    @patch("orchestrator.run_image_generator_agent")
    @patch("orchestrator.run_flow_editor_agent")
    @patch("orchestrator.run_draft_writer_agent")
    @patch("orchestrator.run_research_agent")
    @patch("orchestrator.run_seo_agent")
    @patch("orchestrator.get_supabase_client")
    def test_full_pipeline_with_mocks(
        self,
        mock_get_supabase,
        mock_run_seo,
        mock_run_research,
        mock_run_draft,
        mock_run_flow,
        mock_run_line,
        mock_run_assemble,
        mock_run_image,
        mock_run_publisher,
        mock_print,
    ):
        """
        Ensure full_pipeline executes each step in order and returns success.
        Specifically verifies that the Line-Editor agent step is reached.
        """
        from types import SimpleNamespace
        import orchestrator  # local import to keep patch-decorator targets clear

        # 1. mock the Supabase client (not used in test body)
        mock_get_supabase.return_value = MagicMock()

        # 2. prepare deterministic data
        mock_run_seo.return_value = [self.mock_content_id]
        mock_run_research.return_value = True
        mock_run_draft.return_value = True
        mock_run_flow.return_value = True
        mock_run_line.return_value = True
        mock_run_image.return_value = True
        mock_run_publisher.return_value = True

        # also record the call sequence for verification
        call_order = []

        def _record(name):
            def _wrapper(*_a, **_kw):
                call_order.append(name)
                if name == "seo":
                    return [self.mock_content_id]
                return True

            return _wrapper

        mock_run_seo.side_effect = _record("seo")
        mock_run_research.side_effect = _record("research")
        mock_run_draft.side_effect = _record("draft")
        mock_run_flow.side_effect = _record("flow")
        mock_run_line.side_effect = _record("line")
        mock_run_assemble.side_effect = _record("assemble")
        mock_run_image.side_effect = _record("image")
        mock_run_publisher.side_effect = _record("publish")

        # 3. Build args namespace identical to CLI parsing
        args = SimpleNamespace(
            plan_id=self.mock_plan_id,
            create_plan=False,
            domain=None,
            audience=None,
            tone=None,
            niche=None,
            goal=None,
            no_ai=True,  # use mock/no-ai mode
        )

        # 4. Execute pipeline
        result_code = orchestrator.full_pipeline(args)

        # 5. Assertions
        self.assertEqual(result_code, 0)

        # Agent invocation counts
        mock_run_seo.assert_called_once_with(self.mock_plan_id, mock_get_supabase.return_value, True)
        mock_run_research.assert_called_once()
        mock_run_draft.assert_called_once()
        mock_run_flow.assert_called_once()
        mock_run_line.assert_called_once()
        mock_run_assemble.assert_called_once()
        mock_run_image.assert_called_once()
        mock_run_publisher.assert_called_once()

        # Order: seo -> research -> draft -> flow -> line -> assemble -> image -> publish
        self.assertEqual(call_order, ["seo", "research", "draft", "flow", "line", "assemble", "image", "publish"])


if __name__ == "__main__":
    unittest.main()
