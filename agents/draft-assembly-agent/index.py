#!/usr/bin/env python3
"""Draft Assembly Agent

Merge outputs from other agents into a final article draft.
"""
import argparse
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
ENDC = "\033[0m"


def get_supabase_client():
    """Return configured Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set{ENDC}")
        sys.exit(1)
    return create_client(url, key)


def get_content_piece(supabase, content_id: str) -> Dict[str, Any]:
    """Fetch content piece data."""
    result = supabase.table("content_pieces").select("*").eq("id", content_id).execute()
    if not result.data:
        print(f"{RED}Content piece {content_id} not found{ENDC}")
        sys.exit(1)
    return result.data[0]


def get_headline(supabase, content_id: str) -> Optional[Dict[str, Any]]:
    """Fetch headline record if available."""
    result = supabase.table("headlines").select("*").eq("content_id", content_id).execute()
    return result.data[0] if result.data else None


def get_hooks(supabase, content_id: str) -> Optional[Dict[str, Any]]:
    """Fetch hook record if available."""
    result = supabase.table("hooks").select("*").eq("content_id", content_id).execute()
    return result.data[0] if result.data else None


def assemble_content(piece: Dict[str, Any], headline: Optional[Dict[str, Any]], hooks: Optional[Dict[str, Any]]) -> str:
    """Merge line-edited draft with headline and hooks."""
    title = piece.get("title", "")
    if headline and headline.get("selected_title"):
        title = headline["selected_title"]
    final = f"# {title}\n\n"
    if hooks and hooks.get("main_hook"):
        final += f"> {hooks['main_hook']}\n\n"
    final += piece.get("draft_text", "")
    if hooks and hooks.get("micro_hooks"):
        final += "\n\n<!-- START: hook-agent.micro-hooks -->\n"
        for h in hooks["micro_hooks"]:
            final += f"- {h}\n"
        final += "<!-- END: hook-agent.micro-hooks -->\n"
    return final


def save_final_text(supabase, content_id: str, text: str) -> None:
    """Persist final article to database and log status."""
    supabase.table("content_pieces").update({
        "final_text": text,
        "status": "assembled",
        "updated_at": datetime.utcnow().isoformat(),
    }).eq("id", content_id).execute()
    supabase.table("agent_status").insert({
        "id": str(uuid.uuid4()),
        "content_id": content_id,
        "agent": "draft-assembly-agent",
        "status": "done",
        "input": {"content_id": content_id},
        "output": {"length": len(text)},
        "created_at": datetime.utcnow().isoformat(),
    }).execute()


def save_final_to_file(content_id: str, text: str) -> str:
    """Write final article to disk."""
    filename = f"final_{content_id[:8]}.md"
    with open(filename, "w") as f:
        f.write(text)
    print(f"{GREEN}Saved final draft to {filename}{ENDC}")
    return filename


def main() -> int:
    parser = argparse.ArgumentParser(description="Draft Assembly Agent")
    parser.add_argument("--content-id", required=True, help="Content piece ID")
    args = parser.parse_args()

    supabase = get_supabase_client()
    piece = get_content_piece(supabase, args.content_id)
    headline = get_headline(supabase, args.content_id)
    hooks = get_hooks(supabase, args.content_id)

    final_text = assemble_content(piece, headline, hooks)
    save_final_text(supabase, piece["id"], final_text)
    save_final_to_file(piece["id"], final_text)

    print(f"{BOLD}Draft assembly complete{ENDC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
