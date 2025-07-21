"""Unit tests for the draft assembly agent."""

import sys
import os
import unittest
import importlib.util

# Dynamically load the agent module from its new location
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "draft_assembly_agent",
    os.path.join(REPO_ROOT, "agents", "draft-assembly-agent", "index.py"),
)
draft_assembly_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(draft_assembly_agent)
sys.modules["draft_assembly_agent"] = draft_assembly_agent

from draft_assembly_agent import assemble_content


class TestDraftAssemblyAgent(unittest.TestCase):
    def test_assemble_content_basic(self):
        piece = {"title": "My Post", "draft_text": "Body"}
        headline = {"selected_title": "Better Title"}
        hooks = {"main_hook": "Read this!", "micro_hooks": ["Tip1", "Tip2"]}

        result = assemble_content(piece, headline, hooks)

        self.assertIn("# Better Title", result)
        self.assertIn("Read this!", result)
        self.assertIn("- Tip1", result)
        self.assertIn("Body", result)


if __name__ == "__main__":
    unittest.main()
