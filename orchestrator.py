#!/usr/bin/env python3
"""
Orchestrator for WordPress Content Generator

This orchestrates the workflow between different agents in the content generation pipeline.
"""

import argparse
import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any

from dotenv import load_dotenv
from supabase import create_client

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Create and return a Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file{ENDC}")
        sys.exit(1)
    
    return create_client(url, key)

def create_strategic_plan(supabase_client, domain, audience, tone, niche, goal):
    """Create a new strategic plan."""
    try:
        plan = {
            "domain": domain,
            "audience": audience,
            "tone": tone,
            "niche": niche,
            "goal": goal
        }
        
        response = supabase_client.table("strategic_plans").insert(plan).execute()
        
        if not response.data:
            print(f"{RED}Failed to create strategic plan{ENDC}")
            return None
        
        plan_id = response.data[0]["id"]
        print(f"{GREEN}Created strategic plan: {plan_id}{ENDC}")
        
        return plan_id
    
    except Exception as e:
        print(f"{RED}Error creating strategic plan: {e}{ENDC}")
        return None

def run_seo_agent(plan_id, supabase_client, use_ai=False):
    """
    Run the SEO agent for a given strategic plan.

    Args:
        plan_id (str): Strategic plan UUID.
        supabase_client: Initialized Supabase client.
        use_ai (bool): Whether to call OpenAI (default True).
    Returns:
        list[str]: IDs of created content pieces.
    """
    print(f"{BLUE}Running SEO agent for plan: {plan_id}{ENDC}")
    # -------------------------------------------------
    # Debug statement 1 – entering function
    # -------------------------------------------------
    print(f"{YELLOW}DEBUG: Starting run_seo_agent with plan_id: {plan_id}{ENDC}")
    
    cmd = ["python", "enhanced_seo_agent.py", "--plan-id", plan_id]
    
    if not use_ai:
        cmd.append("--no-ai")
    
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # -------------------------------------------------
        # Debug statement 2 – after subprocess completes
        # -------------------------------------------------
        print(f"{YELLOW}DEBUG: SEO agent process completed with return code: {process.returncode}{ENDC}")

        if process.returncode != 0:
            print(f"{RED}SEO agent failed with code {process.returncode}{ENDC}")
            print(f"{RED}Error: {process.stderr}{ENDC}")
            return []
        
        print(f"{GREEN}SEO agent completed successfully{ENDC}")
        
        # Extract content piece IDs from the output
        content_pieces = []
        
        # Look for JSON files created by the SEO agent
        seo_files = Path(".").glob(f"seo_analysis_{plan_id.split('-')[0]}*.json")
        
        for file in seo_files:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    # Content piece IDs would be returned by the SEO agent in future versions
            except Exception:
                continue
        
        # Get content pieces from the database
        try:
            # -------------------------------------------------
            # Debug statement 3 – about to hit database
            # -------------------------------------------------
            print(f"{YELLOW}DEBUG: About to query database for content pieces{ENDC}")
            # (Supabase-py does not expose raw SQL, so we log the high-level query.)

            response = supabase_client.table("content_pieces").select("id").eq("strategic_plan_id", plan_id).execute()
            
            if response.data:
                content_pieces = [item["id"] for item in response.data]
                # -------------------------------------------------
                # Debug statement 5 – content pieces retrieved
                # -------------------------------------------------
                print(f"{YELLOW}DEBUG: Retrieved content_pieces: {content_pieces}{ENDC}")
                print(f"{GREEN}Found {len(content_pieces)} content pieces in database{ENDC}")
            else:
                print(f"{YELLOW}No content pieces found in database for plan: {plan_id}{ENDC}")
        except Exception as e:
            print(f"{RED}Error retrieving content pieces: {e}{ENDC}")
        
        return content_pieces
    
    except Exception as e:
        print(f"{RED}Error running SEO agent: {e}{ENDC}")
        return []

def run_research_agent(content_id, supabase_client, use_ai=False):
    """
    Run the research agent for a given content piece.

    Args:
        content_id (str): Content piece UUID.
        supabase_client: Initialized Supabase client (currently unused, placeholder for future needs).
        use_ai (bool): Whether to call OpenAI (default True).
    Returns:
        bool: True on success, False on failure.
    """
    print(f"{BLUE}Running research agent for content: {content_id}{ENDC}")
    
    cmd = ["python", "research_agent.py", "--content-id", content_id]
    
    if not use_ai:
        cmd.append("--no-ai")
    
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            print(f"{RED}Research agent failed with code {process.returncode}{ENDC}")
            print(f"{RED}Error: {process.stderr}{ENDC}")
            return False
        
        print(f"{GREEN}Research agent completed successfully{ENDC}")
        return True
    
    except Exception as e:
        print(f"{RED}Error running research agent: {e}{ENDC}")
        return False

# --------------------------------------------------------------------------- #
# Flow-Editor Agent                                                           #
# --------------------------------------------------------------------------- #

def run_flow_editor_agent(content_id, supabase_client, use_ai=False):
    """
    Run the Flow-Editor agent for a given content piece.

    Args:
        content_id (str): Content piece UUID.
        supabase_client: Initialized Supabase client (currently unused, placeholder for future needs).
        use_ai (bool): Whether to call OpenAI (default True).
    Returns:
        bool: True on success, False on failure.
    """
    print(f"{BLUE}Running flow editor agent for content: {content_id}{ENDC}")

    cmd = ["python", "flow_editor_agent.py", "--content-id", content_id]

    if not use_ai:
        cmd.append("--no-ai")

    try:
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode != 0:
            print(f"{RED}Flow editor agent failed with code {process.returncode}{ENDC}")
            print(f"{RED}Error: {process.stderr}{ENDC}")
            return False

        print(f"{GREEN}Flow editor agent completed successfully{ENDC}")
        return True

    except Exception as e:
        print(f"{RED}Error running flow editor agent: {e}{ENDC}")
        return False

def run_draft_writer_agent(content_id, supabase_client, use_ai=False):
# --------------------------------------------------------------------------- #
# Content Piece Processor                                                     #
# --------------------------------------------------------------------------- #

def process_content_piece(
    content_piece: Dict[str, Any],
    supabase_client,
    use_ai: bool = True,
) -> bool:
    """
    Process a single content piece according to its current status.

    The processing rules are:
        - status == "draft"      -> run research agent
        - status == "researched" -> run draft-writer agent
        - status == "written"    -> run flow-editor agent

    Args:
        content_piece: Row dict from `content_pieces` table.
        supabase_client: Supabase client (passed through to sub-functions).
        use_ai: Whether agents should call OpenAI (default True).

    Returns:
        True if the corresponding agent finished successfully, else False.
    """
    cid = content_piece["id"]
    status = content_piece.get("status", "").lower()

    print(f"{YELLOW}DEBUG: process_content_piece → id={cid} status={status}{ENDC}")

    if status == "draft":
        return run_research_agent(cid, supabase_client, use_ai)
    elif status == "researched":
        return run_draft_writer_agent(cid, supabase_client, use_ai)
    elif status == "written":
        return run_flow_editor_agent(cid, supabase_client, use_ai)
    else:
        # Unknown or already processed status – nothing to do
        print(
            f"{YELLOW}Skipping content piece {cid}: "
            f"status '{status}' not actionable{ENDC}"
        )
        return False


    """
    Run the Draft-Writer agent for a given content piece.

    Args:
        content_id (str): Content piece UUID.
        supabase_client: Initialized Supabase client (currently unused, placeholder for future needs).
        use_ai (bool): Whether to call OpenAI (default True).
    Returns:
        bool: True on success, False on failure.
    """
    print(f"{BLUE}Running draft writer agent for content: {content_id}{ENDC}")
    
    cmd = ["python", "draft_writer_agent.py", "--content-id", content_id]
    
    if not use_ai:
        cmd.append("--no-ai")
    
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            print(f"{RED}Draft writer agent failed with code {process.returncode}{ENDC}")
            print(f"{RED}Error: {process.stderr}{ENDC}")
            return False
        
        print(f"{GREEN}Draft writer agent completed successfully{ENDC}")
        return True
    
    except Exception as e:
        print(f"{RED}Error running draft writer agent: {e}{ENDC}")
        return False

def full_pipeline(args):
    """Run the full pipeline from strategic plan to research."""
    print(f"{BOLD}WordPress Content Generator - Full Pipeline{ENDC}")
    print("=" * 60)
    
    # Connect to Supabase
    supabase_client = get_supabase_client()
    
    # Create strategic plan if requested
    plan_id = args.plan_id
    
    if not plan_id and args.create_plan:
        domain = args.domain or "example.com"
        audience = args.audience or "general audience"
        tone = args.tone or "informative"
        niche = args.niche or "technology"
        goal = args.goal or "educate readers"
        
        plan_id = create_strategic_plan(supabase_client, domain, audience, tone, niche, goal)
        
        if not plan_id:
            print(f"{RED}Failed to create strategic plan. Cannot proceed.{ENDC}")
            return 1
    
    # Check if we have a plan ID
    if not plan_id:
        print(f"{RED}No strategic plan ID provided. Use --plan-id or --create-plan{ENDC}")
        return 1
    
    # Step 1: Run the SEO agent
    print(f"{BOLD}Step 1: Running SEO Agent{ENDC}")
    content_pieces = run_seo_agent(plan_id, supabase_client, not args.no_ai)
    
    if not content_pieces:
        print(f"{RED}No content pieces generated. Cannot proceed.{ENDC}")
        return 1
    
    # Step 2: Run the research agent for each content piece
    print(f"{BOLD}Step 2: Running Research Agent for {len(content_pieces)} content pieces{ENDC}")
    
    research_success_count = 0
    for i, content_id in enumerate(content_pieces):
        print(f"{BLUE}Processing content piece {i+1} of {len(content_pieces)} with Research Agent{ENDC}")
        
        if run_research_agent(content_id, supabase_client, not args.no_ai):
            research_success_count += 1
        
        if i < len(content_pieces) - 1:
            # Sleep a bit between requests to avoid rate limiting
            time.sleep(1)
    
    # Step 3: Run the draft writer agent for each content piece
    print(f"{BOLD}Step 3: Running Draft Writer Agent for {len(content_pieces)} content pieces{ENDC}")
    
    draft_success_count = 0
    for i, content_id in enumerate(content_pieces):
        print(f"{BLUE}Processing content piece {i+1} of {len(content_pieces)} with Draft Writer Agent{ENDC}")
        
        if run_draft_writer_agent(content_id, supabase_client, not args.no_ai):
            draft_success_count += 1
        
        if i < len(content_pieces) - 1:
            # Sleep a bit between requests to avoid rate limiting
            time.sleep(1)

    # Step 4: Run the flow editor agent for each content piece
    print(f"{BOLD}Step 4: Running Flow Editor Agent for {len(content_pieces)} content pieces{ENDC}")
    
    flow_success_count = 0
    for i, content_id in enumerate(content_pieces):
        print(f"{BLUE}Processing content piece {i+1} of {len(content_pieces)} with Flow Editor Agent{ENDC}")
        
        if run_flow_editor_agent(content_id, supabase_client, not args.no_ai):
            flow_success_count += 1
        
        if i < len(content_pieces) - 1:
            # Sleep a bit between requests to avoid rate limiting
            time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print(f"{BOLD}Pipeline Summary:{ENDC}")
    print(f"Strategic Plan: {plan_id}")
    print(f"Content Pieces: {len(content_pieces)} generated")
    print(f"Research: {research_success_count} of {len(content_pieces)} completed")
    print(f"Draft Writing: {draft_success_count} of {len(content_pieces)} completed")
    print(f"Flow Editing: {flow_success_count} of {len(content_pieces)} completed")
    
    return 0

def main():
    parser = argparse.ArgumentParser(description="WordPress Content Generator Orchestrator")
    parser.add_argument("--plan-id", help="ID of the strategic plan to use")
    parser.add_argument("--create-plan", action="store_true", help="Create a new strategic plan")
    parser.add_argument("--domain", help="Domain for new strategic plan")
    parser.add_argument("--audience", help="Target audience for new strategic plan")
    parser.add_argument("--tone", help="Content tone for new strategic plan")
    parser.add_argument("--niche", help="Content niche for new strategic plan")
    parser.add_argument("--goal", help="Content goal for new strategic plan")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI and use mock data instead")
    
    args = parser.parse_args()
    
    return full_pipeline(args)

if __name__ == "__main__":
    sys.exit(main())
