"""Unit tests for the hook agent."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch
import importlib.util

# Dynamically load the agent module from its new location
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "hook_agent",
    os.path.join(REPO_ROOT, "agents", "hook-agent", "index.py"),
)
hook_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_agent)
sys.modules["hook_agent"] = hook_agent

from hook_agent import (generate_hooks_with_ai, get_content_keywords,
                        get_content_piece, get_strategic_plan,
                        get_supabase_client, save_hooks_to_database,
                        save_results_to_file, setup_openai)


class TestHookAgent(unittest.TestCase):
    def setUp(self):
        self.content_piece = {
            "id": "test-content-id",
            "strategic_plan_id": "test-plan-id",
            "title": "Test Title",
        }
        self.keywords = {
            "focus_keyword": "test keyword",
            "supporting_keywords": ["a", "b"],
        }
        self.plan = {
            "id": "test-plan-id",
            "audience": "developers",
            "niche": "testing",
        }
        self.hooks = {
            "main_hook": "Main hook",
            "micro_hooks": [f"Hook {i}" for i in range(7)],
        }

    @patch("os.getenv")
    def test_setup_openai(self, mock_getenv):
        mock_getenv.return_value = "key"
        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value = "client"
            client = setup_openai()
            mock_openai.assert_called_once_with(api_key="key")
            self.assertEqual(client, "client")

    @patch("os.getenv")
    def test_get_supabase_client(self, mock_getenv):
        mock_getenv.side_effect = lambda x: "url" if x == "SUPABASE_URL" else "key"
        with patch("hook_agent.create_client") as mock_create:
            mock_create.return_value = "client"
            client = get_supabase_client()
            mock_create.assert_called_once_with("url", "key")
            self.assertEqual(client, "client")

    def test_get_content_piece(self):
        mock_supabase = MagicMock()
        mock_exec = MagicMock()
        mock_exec.execute.return_value = MagicMock(data=[self.content_piece])
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_exec
        result = get_content_piece(mock_supabase, "test-content-id")
        self.assertEqual(result, self.content_piece)

    def test_get_content_keywords(self):
        mock_supabase = MagicMock()
        mock_exec = MagicMock()
        mock_exec.execute.return_value = MagicMock(data=[self.keywords])
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_exec
        result = get_content_keywords(mock_supabase, "test-content-id")
        self.assertEqual(result, self.keywords)

    def test_get_strategic_plan(self):
        mock_supabase = MagicMock()
        mock_exec = MagicMock()
        mock_exec.execute.return_value = MagicMock(data=[self.plan])
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_exec
        result = get_strategic_plan(mock_supabase, "test-plan-id")
        self.assertEqual(result, self.plan)

    def test_generate_hooks_with_ai(self):
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.choices = [
            MagicMock(message=MagicMock(content=json.dumps(self.hooks)))
        ]
        mock_client.chat.completions.create.return_value = mock_resp
        main_hook, micro_hooks = generate_hooks_with_ai(
            mock_client, self.keywords, self.plan
        )
        mock_client.chat.completions.create.assert_called_once()
        self.assertEqual(main_hook, self.hooks["main_hook"])
        self.assertEqual(micro_hooks, self.hooks["micro_hooks"])

    def test_save_hooks_to_database(self):
        mock_supabase = MagicMock()
        save_hooks_to_database(mock_supabase, "test-content-id", "Main", ["a"])
        mock_supabase.table.assert_called_once_with("hooks")
        mock_supabase.table.return_value.insert.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_results_to_file(self, mock_dump, mock_file):
        filename = save_results_to_file("abc12345", "Main", ["a"])
        mock_file.assert_called_once()
        mock_dump.assert_called_once()
        self.assertTrue(filename.startswith("hooks_"))


if __name__ == "__main__":
    unittest.main()
