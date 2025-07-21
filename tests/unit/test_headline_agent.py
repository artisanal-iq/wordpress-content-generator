#!/usr/bin/env python3
"""Unit tests for the headline agent."""

import os
import sys
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.headline_agent import (
    run,
    validate,
    generate_headline_options,
    score_headline,
    select_best_headline,
)
from agents.shared.schemas import TaskStatus


class TestHeadlineAgent(unittest.TestCase):
    """Tests for headline generation and scoring."""

    def setUp(self):
        self.valid_input = {
            "seed_title": "Mastering Python",
            "focus_keyword": "python programming",
        }

    def test_validate_valid(self):
        self.assertTrue(validate(self.valid_input))

    def test_validate_missing_field(self):
        with self.assertRaises(ValueError):
            validate({"seed_title": "title only"})

    def test_generate_options(self):
        options = generate_headline_options("Learn Python", "python")
        self.assertEqual(len(options), 5)
        self.assertTrue(any("python" in o.lower() for o in options))

    def test_score_headline(self):
        high = score_headline("How to learn python fast", "python")
        low = score_headline("learn", "python")
        self.assertGreater(high, low)

    def test_run(self):
        result = run(self.valid_input)
        self.assertEqual(result["status"], TaskStatus.DONE)
        headlines = result["output"]["headline"]
        self.assertIn(headlines["selected_title"], headlines["title_options"])
        self.assertEqual(len(headlines["subheaders"]), 3)


if __name__ == "__main__":
    unittest.main()
