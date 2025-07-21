#!/usr/bin/env python3
"""
Enhanced SEO Agent for WordPress Content Generator

This agent analyzes a strategic plan, generates SEO keywords and content ideas using OpenAI,
and stores the results in the database.
"""

import argparse
import json
import os
import sys
import uuid
import time
from typing import Dict, List, Any
from datetime import datetime

from dotenv import load_dotenv

from agents.shared.utils import logger
from supabase import create_client
import openai

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Load environment variables
load_dotenv()

def setup_openai():
    """Set up OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.info(f"{RED}Error: OPENAI_API_KEY must be set in .env file{ENDC}")
        sys.exit(1)
    
    # Set up OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    return client

def get_supabase_client():
    """Create and return a Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        logger.info(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file{ENDC}")
        sys.exit(1)
    
    return create_client(url, key)

def get_strategic_plan(supabase, plan_id=None):
    """Get a strategic plan from Supabase."""
    try:
        if plan_id:
            response = supabase.table("strategic_plans").select("*").eq("id", plan_id).execute()
        else:
            # Get the most recent plan if no ID is provided
            response = supabase.table("strategic_plans").select("*").order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            logger.info(f"{RED}No strategic plan found{ENDC}")
            sys.exit(1)
        
        return response.data[0]
    
    except Exception as e:
        logger.info(f"{RED}Error retrieving strategic plan: {e}{ENDC}")
        sys.exit(1)

def analyze_seo_keywords_with_ai(openai_client, plan: Dict[str, Any]):
    """
    Analyze the strategic plan and generate SEO keywords using OpenAI.
    """
    logger.info(f"{BLUE}Analyzing strategic plan for SEO keywords using AI...{ENDC}")
    logger.info(f"  Domain: {plan['domain']}")
    logger.info(f"  Audience: {plan['audience']}")
    logger.info(f"  Niche: {plan['niche']}")
    
    try:
        # Craft a prompt for OpenAI
        prompt = f"""
        Generate SEO keywords for a website with the following details:
        
        Domain: {plan['domain']}
        Audience: {plan['audience']}
        Tone: {plan['tone']}
        Niche: {plan['niche']}
        Goal: {plan['goal']}
        
        Provide:
        1. One focus keyword (highest search volume)
        2. 5-8 supporting keywords
        3. Estimated search volume for each keyword (numerical values)
        
        Format the response as a valid JSON object with these keys:
        - focus_keyword (string)
        - supporting_keywords (array of strings)
        - search_volume (object mapping each keyword to its estimated monthly search volume as a number)
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o, adjust based on your needs
            messages=[
                {"role": "system", "content": "You are an SEO expert specialized in keyword research. Provide realistic, researched keywords with good search volume that would be valuable for content creation. Format your response as valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        result_text = response.choices[0].message.content
        keywords = json.loads(result_text)
        
        logger.info(f"{GREEN}Generated {len(keywords['supporting_keywords'])} supporting keywords{ENDC}")
        
        return keywords
    
    except Exception as e:
        logger.info(f"{RED}Error generating keywords with AI: {e}{ENDC}")
        # Fall back to mock data if AI fails
        logger.info(f"{YELLOW}Falling back to mock keyword generation{ENDC}")
        
        keywords = {
            "focus_keyword": f"best {plan['niche']} guide",
            "supporting_keywords": [
                f"{plan['niche']} tips",
                f"{plan['niche']} for {plan['audience']}",
                f"how to {plan['goal'].split()[0]} {plan['niche']}",
                f"{plan['tone']} advice on {plan['niche']}",
                f"{plan['niche']} best practices"
            ],
            "search_volume": {
                f"best {plan['niche']} guide": 1200,
                f"{plan['niche']} tips": 880,
                f"{plan['niche']} for {plan['audience']}": 590,
                f"how to {plan['goal'].split()[0]} {plan['niche']}": 320,
                f"{plan['tone']} advice on {plan['niche']}": 210,
                f"{plan['niche']} best practices": 430
            }
        }
        
        return keywords

def generate_content_ideas_with_ai(openai_client, plan: Dict[str, Any], keywords: Dict[str, Any]):
    """
    Generate content ideas based on the strategic plan and keywords using OpenAI.
    """
    logger.info(f"{BLUE}Generating content ideas using AI...{ENDC}")
    
    try:
        # Craft a prompt for OpenAI
        prompt = f"""
        Generate content ideas for a website with the following details:
        
        Domain: {plan['domain']}
        Audience: {plan['audience']}
        Tone: {plan['tone']}
        Niche: {plan['niche']}
        Goal: {plan['goal']}
        
        Focus Keyword: {keywords['focus_keyword']}
        Supporting Keywords: {', '.join(keywords['supporting_keywords'][:5])}
        
        Provide 3 content ideas that would rank well for these keywords.
        For each idea include:
        1. A catchy title that includes the keyword
        2. Which keyword it targets
        3. A brief description (1-2 sentences)
        4. Estimated word count
        5. 5-6 section headings that would be included in the article
        
        Format the response as a valid JSON array, where each item is an object with these keys:
        - title (string)
        - focus_keyword (string)
        - description (string)
        - estimated_word_count (number)
        - suggested_sections (array of strings)
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o, adjust based on your needs
            messages=[
                {"role": "system", "content": "You are a content strategist specialized in creating SEO-optimized content plans. Provide engaging, valuable content ideas that would rank well and serve the target audience."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        result_text = response.choices[0].message.content
        result_json = json.loads(result_text)
        content_ideas = result_json.get("content_ideas", [])
        if not content_ideas and isinstance(result_json, list):
            content_ideas = result_json
        
        logger.info(f"{GREEN}Generated {len(content_ideas)} content ideas{ENDC}")
        
        return content_ideas
    
    except Exception as e:
        logger.info(f"{RED}Error generating content ideas with AI: {e}{ENDC}")
        # Fall back to mock data if AI fails
        logger.info(f"{YELLOW}Falling back to mock content generation{ENDC}")
        
        content_ideas = [
            {
                "title": f"The Ultimate Guide to {plan['niche'].title()}",
                "focus_keyword": keywords["focus_keyword"],
                "description": f"A comprehensive guide to {plan['niche']} for {plan['audience']}.",
                "estimated_word_count": 2500,
                "suggested_sections": [
                    "Introduction to " + plan['niche'],
                    "Key Benefits of " + plan['niche'],
                    "How to Get Started with " + plan['niche'],
                    "Best Practices for " + plan['niche'],
                    "Case Studies",
                    "Conclusion"
                ]
            },
            {
                "title": f"10 Essential {plan['niche'].title()} Tips for {plan['audience'].title()}",
                "focus_keyword": keywords["supporting_keywords"][0] if keywords["supporting_keywords"] else "tips",
                "description": f"Practical tips to help {plan['audience']} with {plan['niche']}.",
                "estimated_word_count": 1800,
                "suggested_sections": [
                    "Why " + plan['niche'] + " Matters",
                    "Tip 1: Getting Started",
                    "Tip 2: Optimizing Your Approach",
                    "Tip 3-10: Various Strategies",
                    "Implementation Guide"
                ]
            },
            {
                "title": f"How to {plan['goal'].split()[0].title()} {plan['niche'].title()} Like a Pro",
                "focus_keyword": keywords["supporting_keywords"][2] if len(keywords["supporting_keywords"]) > 2 else "how-to",
                "description": f"Step-by-step guide to {plan['goal']} through {plan['niche']}.",
                "estimated_word_count": 2200,
                "suggested_sections": [
                    "Understanding " + plan['niche'],
                    "Step 1: Assessment",
                    "Step 2: Strategy Development",
                    "Step 3: Implementation",
                    "Step 4: Measurement",
                    "Success Stories"
                ]
            }
        ]
        
        return content_ideas

def save_results_to_database(supabase, plan_id: str, keywords: Dict[str, Any], content_ideas: List[Dict[str, Any]]):
    """Save SEO analysis results to the database."""
    logger.info(f"{BLUE}Saving results to database...{ENDC}")
    
    try:
        # Create content pieces for each content idea
        created_content_pieces = []
        
        for idea in content_ideas:
            # Create content piece
            content_piece = {
                "strategic_plan_id": plan_id,
                "title": idea["title"],
                "slug": idea["title"].lower().replace(" ", "-"),
                "status": "draft",
                "draft_text": idea["description"]
            }
            
            content_response = supabase.table("content_pieces").insert(content_piece).execute()
            
            if not content_response.data:
                logger.info(f"{RED}Failed to create content piece: {idea['title']}{ENDC}")
                continue
            
            content_id = content_response.data[0]["id"]
            created_content_pieces.append(content_id)
            logger.info(f"{GREEN}Created content piece: {idea['title']}{ENDC}")
            
            # Create keyword entry
            keyword_data = {
                "content_id": content_id,
                "focus_keyword": idea["focus_keyword"],
                "supporting_keywords": idea.get("supporting_keywords", [])
            }
            
            keyword_response = supabase.table("keywords").insert(keyword_data).execute()
            
            if not keyword_response.data:
                logger.info(f"{YELLOW}Failed to create keyword entry for: {idea['title']}{ENDC}")
            
            # Create agent status entry
            agent_status_data = {
                "agent": "seo-agent",
                "content_id": content_id,
                "status": "done",
                "input": {
                    "strategic_plan_id": plan_id,
                    "timestamp": datetime.now().isoformat()
                },
                "output": {
                    "content_idea": idea,
                    "keywords": {
                        "focus": idea["focus_keyword"],
                        "supporting": idea.get("supporting_keywords", [])
                    },
                    "sections": idea["suggested_sections"],
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            agent_response = supabase.table("agent_status").insert(agent_status_data).execute()
            
            if not agent_response.data:
                logger.info(f"{YELLOW}Failed to create agent status entry for: {idea['title']}{ENDC}")
        
        logger.info(f"{GREEN}Successfully created {len(created_content_pieces)} content pieces{ENDC}")
        
        return created_content_pieces
    
    except Exception as e:
        logger.info(f"{RED}Error saving results to database: {e}{ENDC}")
        return []

def save_results_to_file(plan_id: str, keywords: Dict[str, Any], content_ideas: List[Dict[str, Any]]):
    """Save SEO analysis results to a file (for backup/viewing)."""
    results = {
        "plan_id": plan_id,
        "keywords": keywords,
        "content_ideas": content_ideas,
        "timestamp": datetime.now().isoformat()
    }
    
    filename = f"seo_analysis_{plan_id.split('-')[0]}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"{GREEN}Results also saved to {filename}{ENDC}")
    
    return filename

def main():
    parser = argparse.ArgumentParser(description="Enhanced SEO Agent for WordPress Content Generator")
    parser.add_argument("--plan-id", help="ID of the strategic plan to analyze")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI and use mock data instead")
    args = parser.parse_args()
    
    logger.info(f"{BOLD}WordPress Content Generator - Enhanced SEO Agent{ENDC}")
    logger.info("=" * 60)
    
    # Connect to Supabase
    supabase = get_supabase_client()
    
    # Set up OpenAI if AI is enabled
    openai_client = None
    if not args.no_ai:
        try:
            openai_client = setup_openai()
            logger.info(f"{GREEN}Connected to OpenAI API{ENDC}")
        except Exception as e:
            logger.info(f"{RED}Error connecting to OpenAI API: {e}{ENDC}")
            logger.info(f"{YELLOW}Falling back to mock data generation{ENDC}")
            args.no_ai = True
    
    # Get the strategic plan
    plan = get_strategic_plan(supabase, args.plan_id)
    logger.info(f"{GREEN}Retrieved strategic plan: {plan['domain']}{ENDC}")
    
    # Analyze for SEO keywords
    if args.no_ai:
        # Use mock data if AI is disabled
        keywords = {
            "focus_keyword": f"best {plan['niche']} guide",
            "supporting_keywords": [
                f"{plan['niche']} tips",
                f"{plan['niche']} for {plan['audience']}",
                f"how to {plan['goal'].split()[0]} {plan['niche']}",
                f"{plan['tone']} advice on {plan['niche']}",
                f"{plan['niche']} best practices"
            ],
            "search_volume": {
                f"best {plan['niche']} guide": 1200,
                f"{plan['niche']} tips": 880,
                f"{plan['niche']} for {plan['audience']}": 590,
                f"how to {plan['goal'].split()[0]} {plan['niche']}": 320,
                f"{plan['tone']} advice on {plan['niche']}": 210,
                f"{plan['niche']} best practices": 430
            }
        }
        logger.info(f"{YELLOW}Using mock data for keywords{ENDC}")
    else:
        # Use OpenAI to generate keywords
        keywords = analyze_seo_keywords_with_ai(openai_client, plan)
    
    logger.info(f"{GREEN}Generated {len(keywords['supporting_keywords'])} supporting keywords{ENDC}")
    
    # Generate content ideas
    if args.no_ai:
        # Use mock data if AI is disabled
        content_ideas = [
            {
                "title": f"The Ultimate Guide to {plan['niche'].title()}",
                "focus_keyword": keywords["focus_keyword"],
                "description": f"A comprehensive guide to {plan['niche']} for {plan['audience']}.",
                "estimated_word_count": 2500,
                "suggested_sections": [
                    "Introduction to " + plan['niche'],
                    "Key Benefits of " + plan['niche'],
                    "How to Get Started with " + plan['niche'],
                    "Best Practices for " + plan['niche'],
                    "Case Studies",
                    "Conclusion"
                ]
            },
            {
                "title": f"10 Essential {plan['niche'].title()} Tips for {plan['audience'].title()}",
                "focus_keyword": keywords["supporting_keywords"][0],
                "description": f"Practical tips to help {plan['audience']} with {plan['niche']}.",
                "estimated_word_count": 1800,
                "suggested_sections": [
                    "Why " + plan['niche'] + " Matters",
                    "Tip 1: Getting Started",
                    "Tip 2: Optimizing Your Approach",
                    "Tip 3-10: Various Strategies",
                    "Implementation Guide"
                ]
            },
            {
                "title": f"How to {plan['goal'].split()[0].title()} {plan['niche'].title()} Like a Pro",
                "focus_keyword": keywords["supporting_keywords"][2] if len(keywords["supporting_keywords"]) > 2 else keywords["supporting_keywords"][0],
                "description": f"Step-by-step guide to {plan['goal']} through {plan['niche']}.",
                "estimated_word_count": 2200,
                "suggested_sections": [
                    "Understanding " + plan['niche'],
                    "Step 1: Assessment",
                    "Step 2: Strategy Development",
                    "Step 3: Implementation",
                    "Step 4: Measurement",
                    "Success Stories"
                ]
            }
        ]
        logger.info(f"{YELLOW}Using mock data for content ideas{ENDC}")
    else:
        # Use OpenAI to generate content ideas
        content_ideas = generate_content_ideas_with_ai(openai_client, plan, keywords)
    
    logger.info(f"{GREEN}Generated {len(content_ideas)} content ideas{ENDC}")
    
    # Save results to file (for backup/viewing)
    filename = save_results_to_file(plan["id"], keywords, content_ideas)
    
    # Save results to database
    content_pieces = save_results_to_database(supabase, plan["id"], keywords, content_ideas)
    
    logger.info(f"\n{BOLD}SEO Analysis Complete!{ENDC}")
    logger.info(f"Created {len(content_pieces)} content pieces in the database")
    logger.info(f"You can also view the results in {filename}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
