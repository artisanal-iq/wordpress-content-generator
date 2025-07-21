#!/usr/bin/env python3
"""Hook Agent

Generates a main hook and micro hooks for a content piece. The results
are stored in the ``hooks`` table in Supabase.

Input:
    --content-id CONTENT_ID  ID of the content piece
    --no-ai                  Use mock data instead of OpenAI
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

try:
    import openai  # noqa: F401
except ImportError:  # pragma: no cover - handled in tests
    openai = None  # type: ignore

from agents.shared.utils import get_supabase_client, setup_openai

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_content_piece(supabase, content_id: str) -> Dict[str, Any]:
    """Retrieve a content piece."""
    result = supabase.table("content_pieces").select("*").eq("id", content_id).execute()
    if not result.data:
        raise ValueError(f"Content piece {content_id} not found")
    return result.data[0]


def get_content_keywords(supabase, content_id: str) -> Dict[str, Any]:
    """Retrieve keywords for a content piece."""
    result = (
        supabase.table("keywords").select("*").eq("content_id", content_id).execute()
    )
    if not result.data:
        raise ValueError(f"Keywords for {content_id} not found")
    return result.data[0]


def get_strategic_plan(supabase, plan_id: str) -> Dict[str, Any]:
    """Retrieve a strategic plan."""
    result = supabase.table("strategic_plans").select("*").eq("id", plan_id).execute()
    if not result.data:
        raise ValueError(f"Strategic plan {plan_id} not found")
    return result.data[0]


def generate_hooks_with_ai(
    client, keywords: Dict[str, Any], plan: Dict[str, Any]
) -> Tuple[str, List[str]]:
    """Generate a main hook and seven micro hooks using OpenAI."""
    prompt = (
        "Generate a JSON object with a short 'main_hook' and an array 'micro_hooks'\n"
        "of exactly seven catchy phrases for an article about '{focus}' aimed at\n"
        "{audience} in the {niche} niche."
    ).format(
        focus=keywords["focus_keyword"],
        audience=plan["audience"],
        niche=plan["niche"],
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative copywriter."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    text = response.choices[0].message.content
    if "```" in text:
        text = text.split("```")[1].strip()
    data = json.loads(text)
    return data.get("main_hook", ""), data.get("micro_hooks", [])


def generate_mock_hooks(keywords: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Return deterministic mock hooks."""
    main = f"Discover {keywords['focus_keyword']} in minutes!"
    micros = [f"Tip {i+1} about {keywords['focus_keyword']}" for i in range(7)]
    return main, micros


def save_hooks_to_database(
    supabase, content_id: str, main_hook: str, micro_hooks: List[str]
) -> None:
    """Insert hooks into the database."""
    data = {
        "content_id": content_id,
        "main_hook": main_hook,
        "micro_hooks": micro_hooks,
        "created_at": datetime.utcnow().isoformat(),
    }
    supabase.table("hooks").insert(data).execute()


def save_results_to_file(
    content_id: str, main_hook: str, micro_hooks: List[str]
) -> str:
    """Write hooks to a JSON file. Returns filename."""
    filename = f"hooks_{content_id[:8]}.json"
    with open(filename, "w") as f:
        json.dump({"main_hook": main_hook, "micro_hooks": micro_hooks}, f)
    return filename


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Hook Agent")
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--no-ai", action="store_true", help="use mock data")
    args = parser.parse_args()

    supabase = get_supabase_client()
    piece = get_content_piece(supabase, args.content_id)
    keywords = get_content_keywords(supabase, args.content_id)
    plan = get_strategic_plan(supabase, piece["strategic_plan_id"])

    if args.no_ai:
        main_hook, micro_hooks = generate_mock_hooks(keywords)
    else:
        client = setup_openai()
        try:
            main_hook, micro_hooks = generate_hooks_with_ai(client, keywords, plan)
        except Exception:
            main_hook, micro_hooks = generate_mock_hooks(keywords)

    save_hooks_to_database(supabase, args.content_id, main_hook, micro_hooks)
    save_results_to_file(args.content_id, main_hook, micro_hooks)
    print("Hook Agent completed successfully")


if __name__ == "__main__":
    main()
