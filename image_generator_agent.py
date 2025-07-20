#!/usr/bin/env python3
"""
Image Generator Agent

This agent generates featured images for articles using OpenAI's DALL-E API by:
1. Analyzing article content to create relevant image prompts
2. Generating high-quality images using DALL-E
3. Saving images to disk and updating the database with image metadata
4. Preparing the content for WordPress publishing

Input: Content piece with status "line_edited"
Output: Generated image and updated content piece
Status transition: "line_edited" → "image_generated"
"""

import os
import sys
import json
import uuid
import argparse
import base64
import re
from datetime import datetime
from pathlib import Path
import io
from typing import Dict, Any, Optional, List, Tuple

try:
    import openai
    from openai import OpenAI
    from supabase import create_client
    from PIL import Image
except ImportError:
    print("Error: Required packages not installed. Run 'pip install openai supabase pillow'")
    sys.exit(1)


def setup_openai():
    """Initialize OpenAI client with API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    return OpenAI(api_key=api_key)


def get_supabase_client():
    """Initialize Supabase client with URL and key from environment variables."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
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
            print(f"Error: Content piece with ID {content_id} not found")
            sys.exit(1)
        return result.data[0]
    else:
        # Get the first content piece with status "line_edited"
        result = supabase.table("content_pieces").select("*").eq("status", "line_edited").limit(1).execute()
        if not result.data:
            print("Error: No content pieces with status 'line_edited' found")
            sys.exit(1)
        return result.data[0]


def get_content_keywords(supabase, content_id):
    """Retrieve keywords for a content piece."""
    result = supabase.table("keywords").select("*").eq("content_id", content_id).execute()
    if not result.data:
        print(f"Warning: No keywords found for content piece {content_id}")
        return None
    return result.data[0]


def get_strategic_plan(supabase, plan_id):
    """Retrieve strategic plan data."""
    result = supabase.table("strategic_plans").select("*").eq("id", plan_id).execute()
    if not result.data:
        print(f"Error: Strategic plan with ID {plan_id} not found")
        sys.exit(1)
    return result.data[0]


def create_image_prompt(content_piece, keywords=None):
    """
    Create a prompt for image generation based on content piece and keywords.
    
    Args:
        content_piece: Content piece data
        keywords: Optional keywords data
        
    Returns:
        String prompt for DALL-E
    """
    title = content_piece.get("title", "")
    draft_text = content_piece.get("draft_text", "")
    
    # Extract first paragraph (likely contains the main topic)
    first_paragraph = ""
    if draft_text:
        paragraphs = draft_text.split("\n\n")
        if paragraphs:
            # Remove markdown headers if present
            first_paragraph = re.sub(r'^#+ ', '', paragraphs[0]).strip()
    
    # Use focus keyword if available
    focus_keyword = ""
    if keywords and "focus_keyword" in keywords:
        focus_keyword = keywords["focus_keyword"]
    
    # Create a descriptive prompt for DALL-E
    prompt = f"Create a professional, high-quality featured image for an article titled '{title}'"
    
    if focus_keyword:
        prompt += f" about {focus_keyword}"
    
    # Add style guidance
    prompt += ". The image should be visually appealing, modern, and suitable for a professional blog. "
    prompt += "Use a clean composition with balanced elements, good lighting, and a color palette that conveys trust and expertise. "
    prompt += "The image should work well as a featured image at the top of a WordPress article."
    
    return prompt


def generate_image_with_dalle(client, prompt, size="1024x1024", quality="standard", n=1):
    """
    Generate an image using DALL-E API.
    
    Args:
        client: OpenAI client
        prompt: Text prompt for image generation
        size: Image size (default: 1024x1024)
        quality: Image quality (default: standard)
        n: Number of images to generate (default: 1)
        
    Returns:
        Tuple of (image_data, response_metadata)
    """
    print(f"Generating image with prompt: {prompt}")
    
    try:
        response = client.images.generate(
            model="dall-e-3",  # Using the latest DALL-E model
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
            response_format="b64_json"  # Get base64 encoded image
        )
        
        # Extract image data and metadata
        image_data = base64.b64decode(response.data[0].b64_json)
        image_metadata = {
            "prompt": prompt,
            "revised_prompt": response.data[0].revised_prompt,
            "model": "dall-e-3",
            "size": size,
            "quality": quality,
            "created": datetime.utcnow().isoformat()
        }
        
        print("Successfully generated image with DALL-E")
        return image_data, image_metadata
    
    except Exception as e:
        print(f"Error generating image with DALL-E: {str(e)}")
        sys.exit(1)


def generate_mock_image(prompt):
    """
    Generate a mock image for testing without OpenAI.
    
    Args:
        prompt: Text prompt that would be used for image generation
        
    Returns:
        Tuple of (image_data, metadata)
    """
    print(f"Generating mock image for prompt: {prompt}")
    
    # Create a simple colored image with text
    width, height = 1024, 1024
    color = (240, 248, 255)  # Light blue background
    
    # Create a blank image
    img = Image.new('RGB', (width, height), color)
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Create mock metadata
    image_metadata = {
        "prompt": prompt,
        "revised_prompt": prompt,
        "model": "mock-image-generator",
        "size": f"{width}x{height}",
        "quality": "standard",
        "created": datetime.utcnow().isoformat()
    }
    
    return image_data, image_metadata


def save_image_to_file(image_data, content_id, content_title):
    """
    Save image data to a file.
    
    Args:
        image_data: Binary image data
        content_id: Content piece ID
        content_title: Content piece title
        
    Returns:
        Path to the saved image file
    """
    # Create images directory if it doesn't exist
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)
    
    # Create a filename based on content title and ID
    safe_title = re.sub(r'[^\w\-_]', '_', content_title.lower())
    filename = f"{safe_title}_{content_id[:8]}.png"
    filepath = images_dir / filename
    
    # Write image data to file
    with open(filepath, "wb") as f:
        f.write(image_data)
    
    print(f"Saved image to file: {filepath}")
    return str(filepath)


def update_database_with_image(supabase, content_id, image_path, image_metadata):
    """
    Update the database with image information.
    
    Args:
        supabase: Supabase client
        content_id: Content piece ID
        image_path: Path to the saved image
        image_metadata: Image metadata
        
    Returns:
        Boolean indicating success
    """
    try:
        # Create a new image record
        image_id = str(uuid.uuid4())
        image_record = {
            "id": image_id,
            "content_id": content_id,
            "file_path": image_path,
            "metadata": image_metadata,
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("images").insert(image_record).execute()
        
        # Update content piece with image reference and new status
        supabase.table("content_pieces").update({
            "featured_image_id": image_id,
            "status": "image_generated",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", content_id).execute()
        
        # Log agent status
        supabase.table("agent_status").insert({
            "id": str(uuid.uuid4()),
            "content_id": content_id,
            "agent": "image-generator-agent",
            "status": "completed",
            "input": {"content_id": content_id},
            "output": {
                "status": "success", 
                "image_path": image_path,
                "timestamp": datetime.utcnow().isoformat()
            },
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        print(f"Successfully updated database with image for content piece: {content_id}")
        return True
    
    except Exception as e:
        print(f"Error updating database with image: {str(e)}")
        
        # Log error in agent status
        try:
            supabase.table("agent_status").insert({
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "agent": "image-generator-agent",
                "status": "failed",
                "input": {"content_id": content_id},
                "error": {"message": str(e), "timestamp": datetime.utcnow().isoformat()},
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as log_error:
            print(f"Error logging agent status: {str(log_error)}")
        
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Image Generator Agent - Create featured images for articles")
    parser.add_argument("--content-id", help="ID of the content piece to process")
    parser.add_argument("--no-ai", action="store_true", help="Use mock data instead of OpenAI")
    parser.add_argument("--size", default="1024x1024", choices=["1024x1024", "1792x1024", "1024x1792"], 
                        help="Image size (default: 1024x1024)")
    parser.add_argument("--quality", default="standard", choices=["standard", "hd"], 
                        help="Image quality (default: standard)")
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Initialize clients
    supabase = get_supabase_client()
    
    # Get content piece
    content_piece = get_content_piece(supabase, args.content_id)
    content_id = content_piece["id"]
    
    print(f"Processing content piece: {content_piece['title']} (ID: {content_id})")
    
    # Get keywords for better image prompts
    keywords = get_content_keywords(supabase, content_id)
    
    # Create image prompt
    prompt = create_image_prompt(content_piece, keywords)
    
    # Generate image
    if args.no_ai:
        print("Using mock image generator (--no-ai flag set)")
        image_data, image_metadata = generate_mock_image(prompt)
    else:
        openai_client = setup_openai()
        image_data, image_metadata = generate_image_with_dalle(
            openai_client, 
            prompt,
            size=args.size,
            quality=args.quality
        )
    
    # Save image to file
    image_path = save_image_to_file(image_data, content_id, content_piece["title"])
    
    # Update database
    update_database_with_image(supabase, content_id, image_path, image_metadata)
    
    print("Image Generator Agent completed successfully")


if __name__ == "__main__":
    main()
