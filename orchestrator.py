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

def create_strategic_plan(supabase, domain, audience, tone, niche, goal):
    """Create a new strategic plan."""
    try:
        plan = {
            "domain": domain,
            "audience": audience,
            "tone": tone,
            "niche": niche,
            "goal": goal
        }
        
        response = supabase.table("strategic_plans").insert(plan).execute()
        
        if not response.data:
            print(f"{RED}Failed to create strategic plan{ENDC}")
            return None
        
        plan_id = response.data[0]["id"]
        print(f"{GREEN}Created strategic plan: {plan_id}{ENDC}")
        
        return plan_id
    
    except Exception as e:
        print(f"{RED}Error creating strategic plan: {e}{ENDC}")
        return None

def run_seo_agent(plan_id, use_ai=False):
    """Run the SEO agent for a given strategic plan."""
    print(f"{BLUE}Running SEO agent for plan: {plan_id}{ENDC}")
    
    cmd = ["python", "enhanced_seo_agent.py", "--plan-id", plan_id]
    
    if not use_ai:
        cmd.append("--no-ai")
    
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
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
            response = supabase.table("content_pieces").select("id").eq("strategic_plan_id", plan_id).execute()
            
            if response.data:
                content_pieces = [item["id"] for item in response.data]
                print(f"{GREEN}Found {len(content_pieces)} content pieces in database{ENDC}")
            else:
                print(f"{YELLOW}No content pieces found in database for plan: {plan_id}{ENDC}")
        except Exception as e:
            print(f"{RED}Error retrieving content pieces: {e}{ENDC}")
        
        return content_pieces
    
    except Exception as e:
        print(f"{RED}Error running SEO agent: {e}{ENDC}")
        return []

def run_research_agent(content_id, use_ai=False):
    """Run the research agent for a given content piece."""
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

def full_pipeline(args):
    """Run the full pipeline from strategic plan to research."""
    print(f"{BOLD}WordPress Content Generator - Full Pipeline{ENDC}")
    print("=" * 60)
    
    # Connect to Supabase
    supabase = get_supabase_client()
    
    # Create strategic plan if requested
    plan_id = args.plan_id
    
    if not plan_id and args.create_plan:
        domain = args.domain or "example.com"
        audience = args.audience or "general audience"
        tone = args.tone or "informative"
        niche = args.niche or "technology"
        goal = args.goal or "educate readers"
        
        plan_id = create_strategic_plan(supabase, domain, audience, tone, niche, goal)
        
        if not plan_id:
            print(f"{RED}Failed to create strategic plan. Cannot proceed.{ENDC}")
            return 1
    
    # Check if we have a plan ID
    if not plan_id:
        print(f"{RED}No strategic plan ID provided. Use --plan-id or --create-plan{ENDC}")
        return 1
    
    # Run the SEO agent
    print(f"{BOLD}Step 1: Running SEO Agent{ENDC}")
    content_pieces = run_seo_agent(plan_id, not args.no_ai)
    
    if not content_pieces:
        print(f"{RED}No content pieces generated. Cannot proceed.{ENDC}")
        return 1
    
    # Run the research agent for each content piece
    print(f"{BOLD}Step 2: Running Research Agent for {len(content_pieces)} content pieces{ENDC}")
    
    success_count = 0
    for i, content_id in enumerate(content_pieces):
        print(f"{BLUE}Processing content piece {i+1} of {len(content_pieces)}{ENDC}")
        
        if run_research_agent(content_id, not args.no_ai):
            success_count += 1
        
        if i < len(content_pieces) - 1:
            # Sleep a bit between requests to avoid rate limiting
            time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"{BOLD}Pipeline Summary:{ENDC}")
    print(f"Strategic Plan: {plan_id}")
    print(f"Content Pieces: {len(content_pieces)} generated")
    print(f"Research: {success_count} of {len(content_pieces)} completed")
    
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
