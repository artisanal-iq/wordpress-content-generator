"""Tests for the site scaffold agent."""

import os
import sys
import unittest

# Ensure parent path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from agents.site_scaffold_agent import run


class TestSiteScaffoldAgent(unittest.TestCase):
    def test_run_basic(self):
        input_data = {
            "plan_id": "test-plan",
            "categories": ["news", "updates"],
        }
        result = run(input_data)
        self.assertEqual(result["status"], "done")
        self.assertEqual(
            result["output"]["scaffold"]["categories_created"], ["news", "updates"]
        )


if __name__ == "__main__":
    unittest.main()
