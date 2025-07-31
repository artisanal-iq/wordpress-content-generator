"""Headline Agent

Generates multiple headline options and selects the best one
based on simple clickability and SEO heuristics.

Input fields:
- seed_title: starting title or topic
- focus_keyword: main SEO keyword

Output fields:
- headline.title_options: list of generated titles
- headline.selected_title: chosen headline with best score
- headline.subheaders: short subheaders for article sections
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..shared.utils import format_agent_response, log_agent_error

logger = logging.getLogger("headline-agent")
logging.basicConfig(level=logging.INFO)

CLICKABLE_WORDS = {"how", "why", "top", "best", "easy", "guide", "tips", "tricks"}


def validate(input_data: Dict[str, Any]) -> bool:
    """Validate agent input."""
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
    if "seed_title" not in input_data:
        raise ValueError("Input must contain 'seed_title'")
    if "focus_keyword" not in input_data:
        raise ValueError("Input must contain 'focus_keyword'")
    seed = input_data["seed_title"]
    keyword = input_data["focus_keyword"]
    if not isinstance(seed, str) or len(seed.strip()) < 3:
        raise ValueError("seed_title must be a non-empty string")
    if not isinstance(keyword, str) or len(keyword.strip()) < 2:
        raise ValueError("focus_keyword must be a non-empty string")
    return True


def generate_headline_options(seed_title: str, focus_keyword: str) -> List[str]:
    """Generate a list of headline suggestions."""
    base = seed_title.strip()
    return [
        f"{base}: {focus_keyword.title()} Guide",
        f"{base} - Top Tips for {focus_keyword}",
        f"How to {focus_keyword} with {base}",
        f"{focus_keyword.title()} Made Easy: {base}",
        f"Why {focus_keyword.title()} Matters for {base}",
    ]


def score_headline(headline: str, focus_keyword: str) -> int:
    """Score a headline for clickability and SEO."""
    score = 0
    if focus_keyword.lower() in headline.lower():
        score += 2
    words = headline.split()
    if 6 <= len(words) <= 12:
        score += 2
    elif 4 <= len(words) <= 14:
        score += 1
    if any(word in headline.lower() for word in CLICKABLE_WORDS):
        score += 1
    if "?" in headline or "!" in headline:
        score += 1
    return score


def select_best_headline(options: List[str], focus_keyword: str) -> str:
    """Select the headline with the highest score."""
    scored = [(score_headline(opt, focus_keyword), opt) for opt in options]
    scored.sort(key=lambda t: t[0], reverse=True)
    return scored[0][1]


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate and evaluate headline options."""
    agent_name = "headline-agent"
    try:
        validate(input_data)
        seed = input_data["seed_title"]
        keyword = input_data["focus_keyword"]
        options = generate_headline_options(seed, keyword)
        selected = select_best_headline(options, keyword)
        subheaders = [f"{seed} Overview", f"{keyword.title()} Tips", "Final Thoughts"]
        output = {
            "headline": {
                "title_options": options,
                "selected_title": selected,
                "subheaders": subheaders,
            }
        }
        return format_agent_response(agent_name, output)
    except Exception as exc:
        log_agent_error(agent_name, exc)
        return format_agent_response(
            agent_name,
            {},
            status="error",
            errors=[f"HEADLINE_FAIL: {exc}"],
        )


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        params = {"seed_title": "Mastering Python", "focus_keyword": "python programming"}
    print(json.dumps(run(params), indent=2))
