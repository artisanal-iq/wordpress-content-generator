#!/usr/bin/env python3
"""
Flow Editor Agent

This agent improves the structure and flow of article drafts by:
1. Analyzing the logical structure of the content
2. Reorganizing sections for better narrative progression
3. Adding transition sentences between sections
4. Ensuring consistent tone throughout the article

Input: Content piece with status "written"
Output: Improved article with better flow and structure
Status transition: "written" → "flow_edited"
"""

import os
import sys
import json
import uuid
import argparse

from agents.shared.utils import logger
from datetime import datetime
import re

try:
    import openai
    from openai import OpenAI
    from supabase import create_client
except ImportError:
    logger.info("Error: Required packages not installed. Run 'pip install openai supabase'")
    sys.exit(1)


def setup_openai():
    """Initialize OpenAI client with API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.info("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    return OpenAI(api_key=api_key)


def get_supabase_client():
    """Initialize Supabase client with URL and key from environment variables."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        logger.info("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        sys.exit(1)
    
    return create_client(url, key)


def get_content_piece(supabase, content_id=None):
    """
    Retrieve a content piece from the database.
    
    Args:
        supabase: Supabase client
        content_id: Optional ID of the content piece to retrieve
        
    Returns:
        Content piece data as a dictionary
    """
    if content_id:
        # Get specific content piece by ID
        result = supabase.table("content_pieces").select("*").eq("id", content_id).execute()
        if not result.data:
            logger.info(f"Error: Content piece with ID {content_id} not found")
            sys.exit(1)
        return result.data[0]
    else:
        # Get the first content piece with status "written"
        result = supabase.table("content_pieces").select("*").eq("status", "written").limit(1).execute()
        if not result.data:
            logger.info("Error: No content pieces with status 'written' found")
            sys.exit(1)
        return result.data[0]


def get_content_keywords(supabase, content_id):
    """Retrieve keywords for a content piece."""
    result = supabase.table("keywords").select("*").eq("content_id", content_id).execute()
    if not result.data:
        logger.info(f"Warning: No keywords found for content piece {content_id}")
        return None
    return result.data[0]


def get_content_research(supabase, content_id):
    """Retrieve research data for a content piece."""
    result = supabase.table("research").select("*").eq("content_id", content_id).execute()
    if not result.data:
        logger.info(f"Warning: No research found for content piece {content_id}")
        return []
    return result.data


def get_strategic_plan(supabase, plan_id):
    """Retrieve strategic plan data."""
    result = supabase.table("strategic_plans").select("*").eq("id", plan_id).execute()
    if not result.data:
        logger.info(f"Error: Strategic plan with ID {plan_id} not found")
        sys.exit(1)
    return result.data[0]


def get_seo_agent_output(supabase, content_id):
    """Retrieve SEO agent output for a content piece."""
    result = supabase.table("agent_status").select("*").eq("content_id", content_id).eq("agent", "seo-agent").execute()
    if not result.data:
        logger.info(f"Warning: No SEO agent output found for content piece {content_id}")
        return None
    return result.data[0].get("output", {})


def improve_flow_with_ai(client, content_piece, keywords, research, plan, seo_output=None):
    """
    Use OpenAI to improve the structure and flow of an article draft.
    
    Args:
        client: OpenAI client
        content_piece: Content piece data
        keywords: Keywords data
        research: Research data
        plan: Strategic plan data
        seo_output: Optional SEO agent output
        
    Returns:
        Improved article text
    """
    logger.info(f"Analyzing and improving flow for article: {content_piece['title']}")
    
    # Extract existing draft text
    draft_text = content_piece.get("draft_text", "")
    if not draft_text:
        logger.info("Error: Content piece has no draft text")
        sys.exit(1)
    
    # Extract keywords
    focus_keyword = keywords.get("focus_keyword", "") if keywords else ""
    supporting_keywords = keywords.get("supporting_keywords", []) if keywords else []
    
    # Build research context
    research_context = ""
    for item in research:
        research_context += f"- {item['type'].capitalize()}: {item['excerpt']} (Source: {item['url']})\n"
    
    # Build prompt for OpenAI
    system_prompt = """You are a professional editor specializing in improving article flow and structure.
Your task is to analyze and enhance the provided article draft to ensure:
1. Logical progression of ideas
2. Smooth transitions between sections
3. Consistent tone throughout
4. Clear narrative structure (introduction, body, conclusion)
5. Proper use of keywords for SEO without keyword stuffing

Maintain all factual information and citations from the original draft.
Add transition sentences between sections where needed.
Reorganize sections if it improves the logical flow.
Keep the same overall topic and focus."""

    user_prompt = f"""# Article Information
- Title: {content_piece['title']}
- Focus Keyword: {focus_keyword}
- Supporting Keywords: {', '.join(supporting_keywords)}
- Target Audience: {plan['audience']}
- Tone: {plan['tone']}

# Original Draft
{draft_text}

Please improve the flow and structure of this article while maintaining all factual content and citations.
Return the complete improved article in Markdown format.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better editing capabilities
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        improved_text = response.choices[0].message.content
        logger.info("Successfully improved article flow and structure")
        return improved_text
    
    except Exception as e:
        logger.info(f"Error using OpenAI to improve article flow: {str(e)}")
        sys.exit(1)


def generate_mock_improved_flow(content_piece):
    """
    Generate mock improved article flow for testing without OpenAI.
    
    Args:
        content_piece: Content piece data
        
    Returns:
        Mock improved article text
    """
    draft_text = content_piece.get("draft_text", "")
    if not draft_text:
        return "# Mock Improved Article\n\nThis is a mock improved article for testing."
    
    # Extract sections
    sections = re.split(r'(?m)^#{1,2} ', draft_text)
    
    # Add transition sentences between sections
    improved_text = ""
    for i, section in enumerate(sections):
        if i == 0:  # First part might be empty due to split
            improved_text += section
            continue
            
        # Add section header back
        if i == 1:
            improved_text += "# " + section
        else:
            # Add transition sentence before section
            transition_phrases = [
                "Moving on to another important aspect,",
                "Now, let's explore",
                "Having covered the basics, we can now discuss",
                "This brings us to the topic of",
                "With that foundation in place, let's examine"
            ]
            transition = transition_phrases[(i-1) % len(transition_phrases)]
            improved_text += f"\n\n{transition}\n\n## " + section
    
    # Add improved conclusion
    if "conclusion" not in improved_text.lower():
        improved_text += "\n\n## Conclusion\n\nIn summary, this article has covered several key points. The insights provided should help readers better understand the topic and apply this knowledge effectively."
    
    return improved_text


def save_flow_edited_to_database(supabase, content_id, improved_text):
    """
    Save the flow-edited article to the database.
    
    Args:
        supabase: Supabase client
        content_id: Content piece ID
        improved_text: Improved article text
        
    Returns:
        Boolean indicating success
    """
    try:
        # Update content piece with improved text and new status
        supabase.table("content_pieces").update({
            "draft_text": improved_text,
            "status": "flow_edited",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", content_id).execute()
        
        # Log agent status
        supabase.table("agent_status").insert({
            "id": str(uuid.uuid4()),
            "content_id": content_id,
            "agent": "flow-editor-agent",
            "status": "completed",
            "input": {"content_id": content_id},
            "output": {"status": "success", "timestamp": datetime.utcnow().isoformat()},
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        logger.info(f"Successfully saved flow-edited article to database with ID: {content_id}")
        return True
    
    except Exception as e:
        logger.info(f"Error saving flow-edited article to database: {str(e)}")
        
        # Log error in agent status
        try:
            supabase.table("agent_status").insert({
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "agent": "flow-editor-agent",
                "status": "failed",
                "input": {"content_id": content_id},
                "error": {"message": str(e), "timestamp": datetime.utcnow().isoformat()},
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as log_error:
            logger.info(f"Error logging agent status: {str(log_error)}")
        
        return False


def save_flow_edited_to_file(content_id, content_title, improved_text):
    """
    Save the flow-edited article to a file.
    
    Args:
        content_id: Content piece ID
        content_title: Content piece title
        improved_text: Improved article text
        
    Returns:
        Filename
    """
    # Create a filename based on content ID
    filename = f"flow_edited_{content_id[:8]}.md"
    
    # Write to file
    with open(filename, "w") as f:
        f.write(improved_text)
    
    logger.info(f"Saved flow-edited article to file: {filename}")
    return filename


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Flow Editor Agent - Improve article structure and flow")
    parser.add_argument("--content-id", help="ID of the content piece to process")
    parser.add_argument("--no-ai", action="store_true", help="Use mock data instead of OpenAI")
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Initialize clients
    supabase = get_supabase_client()
    
    # Get content piece
    content_piece = get_content_piece(supabase, args.content_id)
    content_id = content_piece["id"]
    
    logger.info(f"Processing content piece: {content_piece['title']} (ID: {content_id})")
    
    # Get related data
    keywords = get_content_keywords(supabase, content_id)
    research = get_content_research(supabase, content_id)
    plan = get_strategic_plan(supabase, content_piece["strategic_plan_id"])
    seo_output = get_seo_agent_output(supabase, content_id)
    
    # Improve article flow
    if args.no_ai:
        logger.info("Using mock data (--no-ai flag set)")
        improved_text = generate_mock_improved_flow(content_piece)
    else:
        openai_client = setup_openai()
        improved_text = improve_flow_with_ai(
            openai_client,
            content_piece,
            keywords,
            research,
            plan,
            seo_output
        )
    
    # Save results
    save_flow_edited_to_database(supabase, content_id, improved_text)
    save_flow_edited_to_file(content_id, content_piece["title"], improved_text)
    
    logger.info("Flow Editor Agent completed successfully")


if __name__ == "__main__":
    main()
