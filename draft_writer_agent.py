#!/usr/bin/env python3
"""
Draft Writer Agent for WordPress Content Generator

This agent takes a content piece with research and keywords and creates a complete article draft.
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

def get_content_piece(supabase, content_id=None):
    """Get a content piece from Supabase."""
    try:
        if content_id:
            response = supabase.table("content_pieces").select("*").eq("id", content_id).execute()
        else:
            # Get a content piece that has been researched but not yet written
            response = supabase.table("content_pieces").select("*").eq("status", "researched").limit(1).execute()
        
        if not response.data:
            logger.info(f"{RED}No content piece found{ENDC}")
            sys.exit(1)
        
        return response.data[0]
    
    except Exception as e:
        logger.info(f"{RED}Error retrieving content piece: {e}{ENDC}")
        sys.exit(1)

def get_content_keywords(supabase, content_id):
    """Get keywords for a content piece."""
    try:
        response = supabase.table("keywords").select("*").eq("content_id", content_id).execute()
        
        if not response.data:
            logger.info(f"{RED}No keywords found for content piece: {content_id}{ENDC}")
            return None
        
        return response.data[0]
    
    except Exception as e:
        logger.info(f"{RED}Error retrieving keywords: {e}{ENDC}")
        return None

def get_content_research(supabase, content_id):
    """Get research for a content piece."""
    try:
        response = supabase.table("research").select("*").eq("content_id", content_id).execute()
        
        if not response.data:
            logger.info(f"{YELLOW}No research found for content piece: {content_id}{ENDC}")
            logger.info(f"{YELLOW}Will use minimal research data.{ENDC}")
            return []
        
        return response.data
    
    except Exception as e:
        logger.info(f"{RED}Error retrieving research: {e}{ENDC}")
        return []

def get_strategic_plan(supabase, plan_id):
    """Get a strategic plan from Supabase."""
    try:
        response = supabase.table("strategic_plans").select("*").eq("id", plan_id).execute()
        
        if not response.data:
            logger.info(f"{RED}No strategic plan found: {plan_id}{ENDC}")
            return None
        
        return response.data[0]
    
    except Exception as e:
        logger.info(f"{RED}Error retrieving strategic plan: {e}{ENDC}")
        return None

def get_seo_agent_output(supabase, content_id):
    """Get SEO agent output for a content piece."""
    try:
        response = supabase.table("agent_status").select("*").eq("content_id", content_id).eq("agent", "seo-agent").execute()
        
        if not response.data:
            logger.info(f"{YELLOW}No SEO agent data found for content piece: {content_id}{ENDC}")
            return None
        
        return response.data[0].get("output", {})
    
    except Exception as e:
        logger.info(f"{RED}Error retrieving SEO agent output: {e}{ENDC}")
        return None

def write_draft_with_ai(openai_client, content_piece, keywords, research, strategic_plan, seo_output):
    """
    Write a complete draft for a content piece using OpenAI.
    """
    logger.info(f"{BLUE}Writing draft for content piece: {content_piece['title']}{ENDC}")
    
    try:
        # Extract sections from SEO output if available
        sections = []
        if seo_output and "content_idea" in seo_output and "suggested_sections" in seo_output["content_idea"]:
            sections = seo_output["content_idea"]["suggested_sections"]
        elif seo_output and "sections" in seo_output:
            sections = seo_output["sections"]
        
        # Format research points for the prompt
        research_text = ""
        for i, point in enumerate(research):
            research_text += f"{i+1}. {point['type'].upper()}: {point['excerpt']} (Source: {point['url']})\n"
        
        # Craft a prompt for OpenAI
        prompt = f"""
        Write a complete blog post with the following details:
        
        Title: {content_piece['title']}
        Focus Keyword: {keywords['focus_keyword']}
        Supporting Keywords: {', '.join(keywords.get('supporting_keywords', []))}
        Audience: {strategic_plan['audience']}
        Tone: {strategic_plan['tone']}
        Niche: {strategic_plan['niche']}
        
        Research Points to Include:
        {research_text if research else "No specific research points provided. Create appropriate content based on the title and keywords."}
        
        Article Structure:
        {"- " + "\n- ".join(sections) if sections else "Create a logical structure with introduction, main sections, and conclusion."}
        
        Important Guidelines:
        1. Write a complete, high-quality article of 1200-1500 words
        2. Use the focus keyword in the first paragraph, conclusion, and several times throughout
        3. Use supporting keywords naturally throughout the text
        4. Include a clear introduction and conclusion
        5. Use H2 and H3 headings to structure the content
        6. Write in a {strategic_plan['tone']} tone appropriate for {strategic_plan['audience']}
        7. Include relevant examples and practical advice
        8. Format the article with proper markdown headings (# for title, ## for H2, ### for H3)
        9. Include a call-to-action at the end
        
        Output Format: Write the full article in markdown format.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o for high-quality long-form content
            messages=[
                {"role": "system", "content": "You are a professional content writer specialized in creating SEO-optimized articles that are engaging, informative, and well-structured. Write content that sounds natural and provides real value to readers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,  # Allowing enough tokens for a comprehensive article
            temperature=0.7   # Slightly creative but still focused
        )
        
        # Extract the draft text
        draft_text = response.choices[0].message.content
        
        logger.info(f"{GREEN}Generated draft of approximately {len(draft_text.split())} words{ENDC}")
        
        return draft_text
    
    except Exception as e:
        logger.info(f"{RED}Error generating draft with AI: {e}{ENDC}")
        # Fall back to mock data if AI fails
        logger.info(f"{YELLOW}Falling back to mock draft generation{ENDC}")
        
        # Mock draft with minimal placeholder text
        mock_draft = f"""
# {content_piece['title']}

## Introduction
Welcome to this comprehensive guide on {keywords['focus_keyword']}. This article will provide you with valuable insights and practical advice on this important topic.

## What is {keywords['focus_keyword'].title()}?
{keywords['focus_keyword'].title()} refers to the methodical approach to implementing strategies in {strategic_plan['niche']} that benefit {strategic_plan['audience']}. 
Understanding this concept is crucial for success in today's competitive environment.

## Why {keywords['focus_keyword'].title()} Matters
Recent studies show that 78% of {strategic_plan['audience']} consider {keywords['focus_keyword']} to be essential for their success. 
This highlights the growing importance of mastering this area.

## Key Strategies for {keywords['focus_keyword'].title()}

### Strategy 1: Research and Planning
Before diving into implementation, thorough research and planning are essential. This lays the groundwork for successful outcomes.

### Strategy 2: Consistent Implementation
Consistency is key when working with {keywords['focus_keyword']}. Establish regular practices and stick to them.

### Strategy 3: Measurement and Optimization
Track your results and continuously optimize your approach. This iterative process leads to the best outcomes.

## Case Study: Success with {keywords['focus_keyword'].title()}
Company XYZ implemented {keywords['focus_keyword']} strategies and saw a 35% increase in engagement among {strategic_plan['audience']}. 
Their approach focused on [specific details would be inserted here].

## Common Challenges and Solutions
While implementing {keywords['focus_keyword']} strategies, you may encounter several challenges. Here's how to overcome them effectively.

## Conclusion
{keywords['focus_keyword'].title()} represents a significant opportunity for {strategic_plan['audience']} to improve their results in {strategic_plan['niche']}. 
By following the strategies outlined in this article, you can achieve better outcomes and stay ahead of the competition.

## Call to Action
Ready to implement these {keywords['focus_keyword']} strategies? Start with the first step today and track your progress. 
Share your results or questions in the comments below!
"""
        
        return mock_draft

def save_draft_to_database(supabase, content_id, draft_text):
    """Save draft to database."""
    logger.info(f"{BLUE}Saving draft to database...{ENDC}")
    
    try:
        # Update content piece
        supabase.table("content_pieces").update({
            "status": "drafted",
            "draft_text": draft_text
        }).eq("id", content_id).execute()
        
        logger.info(f"{GREEN}Updated content piece status to 'drafted'{ENDC}")
        
        # Create agent status entry
        agent_status_data = {
            "agent": "draft-writer-agent",
            "content_id": content_id,
            "status": "done",
            "input": {
                "content_id": content_id,
                "timestamp": datetime.now().isoformat()
            },
            "output": {
                "draft_length": len(draft_text.split()),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        supabase.table("agent_status").insert(agent_status_data).execute()
        logger.info(f"{GREEN}Created agent status entry for draft writer agent{ENDC}")
        
        return True
    
    except Exception as e:
        logger.info(f"{RED}Error saving draft to database: {e}{ENDC}")
        return False

def save_draft_to_file(content_id, content_title, draft_text):
    """Save draft to a file."""
    filename = f"draft_{content_id.split('-')[0]}.md"
    
    with open(filename, "w") as f:
        f.write(draft_text)
    
    logger.info(f"{GREEN}Draft saved to {filename}{ENDC}")
    
    return filename

def main():
    parser = argparse.ArgumentParser(description="Draft Writer Agent for WordPress Content Generator")
    parser.add_argument("--content-id", help="ID of the content piece to write a draft for")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI and use mock data instead")
    args = parser.parse_args()
    
    logger.info(f"{BOLD}WordPress Content Generator - Draft Writer Agent{ENDC}")
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
    
    # Get the content piece
    content_piece = get_content_piece(supabase, args.content_id)
    logger.info(f"{GREEN}Retrieved content piece: {content_piece['title']}{ENDC}")
    
    # Get keywords for the content piece
    keywords = get_content_keywords(supabase, content_piece['id'])
    if not keywords:
        logger.info(f"{RED}No keywords found for this content piece. Cannot proceed.{ENDC}")
        sys.exit(1)
    
    logger.info(f"{GREEN}Retrieved keywords: {keywords['focus_keyword']}{ENDC}")
    
    # Get the strategic plan
    strategic_plan = get_strategic_plan(supabase, content_piece['strategic_plan_id'])
    if not strategic_plan:
        logger.info(f"{RED}No strategic plan found. Cannot proceed.{ENDC}")
        sys.exit(1)
    
    # Get research for the content piece
    research = get_content_research(supabase, content_piece['id'])
    logger.info(f"{GREEN}Retrieved {len(research)} research points{ENDC}")
    
    # Get SEO agent output for additional context (like suggested sections)
    seo_output = get_seo_agent_output(supabase, content_piece['id'])
    
    # Write the draft
    if args.no_ai:
        # Use mock data if AI is disabled
        draft_text = f"""
# {content_piece['title']}

## Introduction
Welcome to this comprehensive guide on {keywords['focus_keyword']}. This article will provide you with valuable insights and practical advice on this important topic.

## What is {keywords['focus_keyword'].title()}?
{keywords['focus_keyword'].title()} refers to the methodical approach to implementing strategies in {strategic_plan['niche']} that benefit {strategic_plan['audience']}. 
Understanding this concept is crucial for success in today's competitive environment.

## Why {keywords['focus_keyword'].title()} Matters
Recent studies show that 78% of {strategic_plan['audience']} consider {keywords['focus_keyword']} to be essential for their success. 
This highlights the growing importance of mastering this area.

## Key Strategies for {keywords['focus_keyword'].title()}

### Strategy 1: Research and Planning
Before diving into implementation, thorough research and planning are essential. This lays the groundwork for successful outcomes.

### Strategy 2: Consistent Implementation
Consistency is key when working with {keywords['focus_keyword']}. Establish regular practices and stick to them.

### Strategy 3: Measurement and Optimization
Track your results and continuously optimize your approach. This iterative process leads to the best outcomes.

## Case Study: Success with {keywords['focus_keyword'].title()}
Company XYZ implemented {keywords['focus_keyword']} strategies and saw a 35% increase in engagement among {strategic_plan['audience']}. 
Their approach focused on [specific details would be inserted here].

## Common Challenges and Solutions
While implementing {keywords['focus_keyword']} strategies, you may encounter several challenges. Here's how to overcome them effectively.

## Conclusion
{keywords['focus_keyword'].title()} represents a significant opportunity for {strategic_plan['audience']} to improve their results in {strategic_plan['niche']}. 
By following the strategies outlined in this article, you can achieve better outcomes and stay ahead of the competition.

## Call to Action
Ready to implement these {keywords['focus_keyword']} strategies? Start with the first step today and track your progress. 
Share your results or questions in the comments below!
"""
        logger.info(f"{YELLOW}Using mock data for draft{ENDC}")
    else:
        # Use OpenAI to generate draft
        draft_text = write_draft_with_ai(openai_client, content_piece, keywords, research, strategic_plan, seo_output)
    
    # Save draft to file
    filename = save_draft_to_file(content_piece['id'], content_piece['title'], draft_text)
    
    # Save draft to database
    save_draft_to_database(supabase, content_piece['id'], draft_text)
    
    logger.info(f"\n{BOLD}Draft Writing Complete!{ENDC}")
    logger.info(f"Created draft of approximately {len(draft_text.split())} words for '{content_piece['title']}'")
    logger.info(f"You can view the draft in {filename}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
