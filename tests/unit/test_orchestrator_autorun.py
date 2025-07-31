import sys
import os
import unittest
from types import SimpleNamespace

# Ensure parent path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from orchestrator import get_next_agent


class TestOrchestratorAutoRun(unittest.TestCase):
    def test_get_next_agent(self):
        self.assertEqual(get_next_agent("seo-agent"), "research-agent")
        self.assertEqual(get_next_agent("image-generator-agent"), "wordpress-publisher-agent")
        self.assertIsNone(get_next_agent("wordpress-publisher-agent"))


if __name__ == "__main__":
    unittest.main()
