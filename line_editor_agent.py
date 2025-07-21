#!/usr/bin/env python3
"""
Line Editor Agent

This agent improves the grammar, style, and readability of article drafts by:
1. Correcting grammar, spelling, and punctuation errors
2. Improving sentence structure and readability
3. Ensuring consistent style (e.g., active voice, formatting)
4. Optimizing keyword placement for SEO

Input: Content piece with status "flow_edited"
Output: Improved article with better grammar, style, and readability
Status transition: "flow_edited" → "line_edited"
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
        # Get the first content piece with status "flow_edited"
        result = supabase.table("content_pieces").select("*").eq("status", "flow_edited").limit(1).execute()
        if not result.data:
            logger.info("Error: No content pieces with status 'flow_edited' found")
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


def improve_grammar_style_with_ai(client, content_piece, keywords, research, plan, seo_output=None):
    """
    Use OpenAI to improve grammar, style, and readability of an article.
    
    Args:
        client: OpenAI client
        content_piece: Content piece data
        keywords: Keywords data
        research: Research data
        plan: Strategic plan data
        seo_output: Optional SEO agent output
        
    Returns:
        Line-edited article text
    """
    logger.info(f"Improving grammar and style for article: {content_piece['title']}")
    
    # Extract existing draft text
    draft_text = content_piece.get("draft_text", "")
    if not draft_text:
        logger.info("Error: Content piece has no draft text")
        sys.exit(1)
    
    # Extract keywords
    focus_keyword = keywords.get("focus_keyword", "") if keywords else ""
    supporting_keywords = keywords.get("supporting_keywords", []) if keywords else []
    
    # Build prompt for OpenAI
    system_prompt = """You are a professional line editor specializing in grammar, style, and readability improvements.
Your task is to edit the provided article to ensure:
1. Perfect grammar, spelling, and punctuation
2. Clear, concise, and readable sentences
3. Consistent style and tone throughout
4. Active voice where appropriate
5. Proper keyword placement and density for SEO

Maintain the overall structure and content organization.
Keep all factual information and citations from the original draft.
Preserve headings, links, and formatting in the Markdown.
Ensure the focus keyword appears in the first paragraph and is used naturally throughout.
Supporting keywords should be incorporated where they fit naturally.
The overall article should read professionally and flow smoothly."""

    user_prompt = f"""# Article Information
- Title: {content_piece['title']}
- Focus Keyword: {focus_keyword}
- Supporting Keywords: {', '.join(supporting_keywords)}
- Target Audience: {plan['audience']}
- Tone: {plan['tone']}

# Original Draft
{draft_text}

Please improve the grammar, style, and readability of this article while maintaining its structure and factual content.
Return the complete line-edited article in Markdown format.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better editing capabilities
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,  # Lower temperature for more consistent editing
            max_tokens=4000
        )
        
        line_edited_text = response.choices[0].message.content
        logger.info("Successfully improved grammar and style")
        return line_edited_text
    
    except Exception as e:
        logger.info(f"Error using OpenAI to improve grammar and style: {str(e)}")
        sys.exit(1)


def generate_mock_line_edited(content_piece):
    """
    Generate mock line-edited article for testing without OpenAI.
    
    Args:
        content_piece: Content piece data
        
    Returns:
        Mock line-edited article text
    """
    draft_text = content_piece.get("draft_text", "")
    if not draft_text:
        return "# Mock Line-Edited Article\n\nThis is a mock line-edited article for testing."
    
    # Apply some simple mock edits to simulate grammar and style improvements
    edited_text = draft_text
    
    # Fix common grammatical issues (simple replacements)
    replacements = {
        "  ": " ",  # Double spaces to single
        " ,": ",",  # Space before comma
        " .": ".",  # Space before period
        "dont": "don't",
        "cant": "can't",
        "wont": "won't",
        "its": "it's",  # Note: This is simplified and would cause issues with possessive "its"
        "thier": "their",
        "the the": "the"
    }
    
    for old, new in replacements.items():
        edited_text = edited_text.replace(old, new)
    
    # Add SEO improvements note
    edited_text += "\n\n*Note: This article has been edited for grammar, style, and SEO optimization.*"
    
    return edited_text


def save_line_edited_to_database(supabase, content_id, line_edited_text):
    """
    Save the line-edited article to the database.
    
    Args:
        supabase: Supabase client
        content_id: Content piece ID
        line_edited_text: Line-edited article text
        
    Returns:
        Boolean indicating success
    """
    try:
        # Update content piece with line-edited text and new status
        supabase.table("content_pieces").update({
            "draft_text": line_edited_text,
            "status": "line_edited",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", content_id).execute()
        
        # Log agent status
        supabase.table("agent_status").insert({
            "id": str(uuid.uuid4()),
            "content_id": content_id,
            "agent": "line-editor-agent",
            "status": "completed",
            "input": {"content_id": content_id},
            "output": {"status": "success", "timestamp": datetime.utcnow().isoformat()},
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        logger.info(f"Successfully saved line-edited article to database with ID: {content_id}")
        return True
    
    except Exception as e:
        logger.info(f"Error saving line-edited article to database: {str(e)}")
        
        # Log error in agent status
        try:
            supabase.table("agent_status").insert({
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "agent": "line-editor-agent",
                "status": "failed",
                "input": {"content_id": content_id},
                "error": {"message": str(e), "timestamp": datetime.utcnow().isoformat()},
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as log_error:
            logger.info(f"Error logging agent status: {str(log_error)}")
        
        return False


def save_line_edited_to_file(content_id, content_title, line_edited_text):
    """
    Save the line-edited article to a file.
    
    Args:
        content_id: Content piece ID
        content_title: Content piece title
        line_edited_text: Line-edited article text
        
    Returns:
        Filename
    """
    # Create a filename based on content ID
    filename = f"line_edited_{content_id[:8]}.md"
    
    # Write to file
    with open(filename, "w") as f:
        f.write(line_edited_text)
    
    logger.info(f"Saved line-edited article to file: {filename}")
    return filename


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Line Editor Agent - Improve grammar, style, and readability")
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
    
    # Improve grammar and style
    if args.no_ai:
        logger.info("Using mock data (--no-ai flag set)")
        line_edited_text = generate_mock_line_edited(content_piece)
    else:
        openai_client = setup_openai()
        line_edited_text = improve_grammar_style_with_ai(
            openai_client,
            content_piece,
            keywords,
            research,
            plan,
            seo_output
        )
    
    # Save results
    save_line_edited_to_database(supabase, content_id, line_edited_text)
    save_line_edited_to_file(content_id, content_piece["title"], line_edited_text)
    
    logger.info("Line Editor Agent completed successfully")


if __name__ == "__main__":
    main()
