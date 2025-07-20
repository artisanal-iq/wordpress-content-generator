#!/usr/bin/env python3
"""
WordPress Publisher Agent

This agent publishes content to WordPress using the WordPress REST API by:
1. Taking content pieces with status "image_generated"
2. Uploading any associated images to WordPress media library
3. Creating a new post with the content, categories, tags, and featured image
4. Updating the content piece status to "published"
5. Storing the WordPress post URL in the database

Input: Content piece with status "image_generated"
Output: Published WordPress post and updated content piece
Status transition: "image_generated" → "published"
"""

import os
import sys
import json
import uuid
import argparse
import base64
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

try:
    from supabase import create_client
except ImportError:
    print("Error: Required packages not installed. Run 'pip install supabase requests'")
    sys.exit(1)


def get_supabase_client():
    """Initialize Supabase client with URL and key from environment variables."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        sys.exit(1)
    
    return create_client(url, key)


def get_wordpress_credentials():
    """Get WordPress API credentials from environment variables."""
    wp_url = os.getenv("WORDPRESS_URL")
    wp_user = os.getenv("WORDPRESS_USER")
    wp_app_password = os.getenv("WORDPRESS_APP_PASSWORD")
    
    if not wp_url or not wp_user or not wp_app_password:
        print("Error: WORDPRESS_URL, WORDPRESS_USER, and WORDPRESS_APP_PASSWORD environment variables must be set")
        sys.exit(1)
    
    # Ensure the URL ends with a trailing slash
    if not wp_url.endswith('/'):
        wp_url += '/'
    
    # Add wp-json/wp/v2/ to the URL if it's not already there
    if 'wp-json/wp/v2/' not in wp_url:
        wp_url += 'wp-json/wp/v2/'
    
    return {
        "url": wp_url,
        "user": wp_user,
        "password": wp_app_password
    }


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
        # Get the first content piece with status "image_generated"
        result = supabase.table("content_pieces").select("*").eq("status", "image_generated").limit(1).execute()
        if not result.data:
            print("Error: No content pieces with status 'image_generated' found")
            sys.exit(1)
        return result.data[0]


def get_content_keywords(supabase, content_id):
    """Retrieve keywords for a content piece."""
    result = supabase.table("keywords").select("*").eq("content_id", content_id).execute()
    if not result.data:
        print(f"Warning: No keywords found for content piece {content_id}")
        return None
    return result.data[0]


def get_content_image(supabase, image_id):
    """Retrieve image data for a content piece."""
    result = supabase.table("images").select("*").eq("id", image_id).execute()
    if not result.data:
        print(f"Warning: No image found with ID {image_id}")
        return None
    return result.data[0]


def upload_image_to_wordpress(wp_credentials, image_path, image_title):
    """
    Upload an image to the WordPress media library.
    
    Args:
        wp_credentials: WordPress credentials
        image_path: Path to the image file
        image_title: Title for the image
        
    Returns:
        Media ID if successful, None otherwise
    """
    try:
        # Check if the image file exists
        if not Path(image_path).exists():
            print(f"Error: Image file not found at {image_path}")
            return None
        
        # Read the image file
        with open(image_path, 'rb') as img:
            image_data = img.read()
        
        # Prepare the request
        url = f"{wp_credentials['url']}media"
        headers = {
            'Content-Disposition': f'attachment; filename="{Path(image_path).name}"',
            'Content-Type': 'image/png'  # Assuming PNG, adjust as needed
        }
        auth = (wp_credentials['user'], wp_credentials['password'])
        
        # Upload the image
        response = requests.post(url, headers=headers, data=image_data, auth=auth)
        
        if response.status_code not in (200, 201):
            print(f"Error uploading image: {response.status_code} - {response.text}")
            return None
        
        # Get the media ID
        media_data = response.json()
        media_id = media_data.get('id')
        
        if not media_id:
            print("Error: Failed to get media ID from WordPress response")
            return None
        
        print(f"Successfully uploaded image to WordPress with ID: {media_id}")
        return media_id
    
    except Exception as e:
        print(f"Error uploading image to WordPress: {str(e)}")
        return None


def create_wordpress_post(wp_credentials, content_piece, media_id=None, keywords=None, preview=False):
    """
    Create a new post in WordPress.
    
    Args:
        wp_credentials: WordPress credentials
        content_piece: Content piece data
        media_id: Optional media ID for featured image
        keywords: Optional keywords data
        preview: Whether to preview the post without publishing
        
    Returns:
        Post ID and URL if successful, (None, None) otherwise
    """
    try:
        title = content_piece.get("title", "")
        content = content_piece.get("draft_text", "")
        slug = content_piece.get("slug", "")
        
        # Prepare tags and categories
        tags = []
        categories = []
        
        if keywords:
            # Add focus keyword as a tag
            focus_keyword = keywords.get("focus_keyword", "")
            if focus_keyword:
                tags.append(focus_keyword)
            
            # Add supporting keywords as tags
            supporting_keywords = keywords.get("supporting_keywords", [])
            tags.extend(supporting_keywords)
        
        # Prepare the post data
        post_data = {
            "title": title,
            "content": content,
            "status": "publish",  # or "draft" if preview
            "slug": slug
        }
        
        # Add featured image if available
        if media_id:
            post_data["featured_media"] = media_id
        
        # Add tags if available
        if tags:
            # First, check if tags exist or create them
            tag_ids = []
            for tag_name in tags:
                tag_id = get_or_create_tag(wp_credentials, tag_name)
                if tag_id:
                    tag_ids.append(tag_id)
            
            if tag_ids:
                post_data["tags"] = tag_ids
        
        # If in preview mode, just print the post data and return
        if preview:
            print("\n=== WordPress Post Preview ===")
            print(f"Title: {title}")
            print(f"Slug: {slug}")
            print(f"Status: publish")
            print(f"Featured Image ID: {media_id}")
            print(f"Tags: {tags}")
            print(f"Categories: {categories}")
            print(f"Content (first 200 chars): {content[:200]}...")
            print("=== End Preview ===\n")
            return None, None
        
        # Prepare the request
        url = f"{wp_credentials['url']}posts"
        headers = {
            'Content-Type': 'application/json'
        }
        auth = (wp_credentials['user'], wp_credentials['password'])
        
        # Create the post
        response = requests.post(url, headers=headers, json=post_data, auth=auth)
        
        if response.status_code not in (200, 201):
            print(f"Error creating post: {response.status_code} - {response.text}")
            return None, None
        
        # Get the post ID and URL
        post_data = response.json()
        post_id = post_data.get('id')
        post_url = post_data.get('link')
        
        if not post_id or not post_url:
            print("Error: Failed to get post ID or URL from WordPress response")
            return None, None
        
        print(f"Successfully created WordPress post with ID: {post_id}")
        print(f"Post URL: {post_url}")
        return post_id, post_url
    
    except Exception as e:
        print(f"Error creating WordPress post: {str(e)}")
        return None, None


def get_or_create_tag(wp_credentials, tag_name):
    """
    Get or create a tag in WordPress.
    
    Args:
        wp_credentials: WordPress credentials
        tag_name: Tag name
        
    Returns:
        Tag ID if successful, None otherwise
    """
    try:
        # First, check if the tag exists
        url = f"{wp_credentials['url']}tags"
        params = {
            'search': tag_name
        }
        auth = (wp_credentials['user'], wp_credentials['password'])
        
        response = requests.get(url, params=params, auth=auth)
        
        if response.status_code == 200:
            tags = response.json()
            for tag in tags:
                if tag.get('name') == tag_name:
                    return tag.get('id')
        
        # If not found, create the tag
        tag_data = {
            'name': tag_name,
            'slug': tag_name.lower().replace(' ', '-')
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=tag_data, auth=auth)
        
        if response.status_code not in (200, 201):
            print(f"Error creating tag: {response.status_code} - {response.text}")
            return None
        
        tag_data = response.json()
        return tag_data.get('id')
    
    except Exception as e:
        print(f"Error getting or creating tag: {str(e)}")
        return None


def update_content_piece_status(supabase, content_id, post_id, post_url):
    """
    Update the content piece status to "published" and store WordPress post info.
    
    Args:
        supabase: Supabase client
        content_id: Content piece ID
        post_id: WordPress post ID
        post_url: WordPress post URL
        
    Returns:
        Boolean indicating success
    """
    try:
        # Update content piece with WordPress post info and new status
        supabase.table("content_pieces").update({
            "status": "published",
            "wordpress_post_id": post_id,
            "wordpress_post_url": post_url,
            "published_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", content_id).execute()
        
        # Log agent status
        supabase.table("agent_status").insert({
            "id": str(uuid.uuid4()),
            "content_id": content_id,
            "agent": "wordpress-publisher-agent",
            "status": "completed",
            "input": {"content_id": content_id},
            "output": {
                "status": "success", 
                "wordpress_post_id": post_id,
                "wordpress_post_url": post_url,
                "timestamp": datetime.utcnow().isoformat()
            },
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        print(f"Successfully updated content piece status to 'published' for ID: {content_id}")
        return True
    
    except Exception as e:
        print(f"Error updating content piece status: {str(e)}")
        
        # Log error in agent status
        try:
            supabase.table("agent_status").insert({
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "agent": "wordpress-publisher-agent",
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
    parser = argparse.ArgumentParser(description="WordPress Publisher Agent - Publish content to WordPress")
    parser.add_argument("--content-id", help="ID of the content piece to process")
    parser.add_argument("--preview", action="store_true", help="Preview the post without publishing")
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Initialize clients
    supabase = get_supabase_client()
    wp_credentials = get_wordpress_credentials()
    
    # Get content piece
    content_piece = get_content_piece(supabase, args.content_id)
    content_id = content_piece["id"]
    
    print(f"Processing content piece: {content_piece['title']} (ID: {content_id})")
    
    # Get keywords for tags
    keywords = get_content_keywords(supabase, content_id)
    
    # Get featured image if available
    media_id = None
    featured_image_id = content_piece.get("featured_image_id")
    
    if featured_image_id:
        image_data = get_content_image(supabase, featured_image_id)
        
        if image_data:
            image_path = image_data.get("file_path")
            image_title = content_piece.get("title", "Featured Image")
            
            if image_path:
                # Upload image to WordPress
                media_id = upload_image_to_wordpress(wp_credentials, image_path, image_title)
    
    # Create WordPress post
    post_id, post_url = create_wordpress_post(wp_credentials, content_piece, media_id, keywords, args.preview)
    
    # If in preview mode, exit here
    if args.preview:
        print("Preview mode: Post was not published to WordPress")
        return
    
    # Update content piece status
    if post_id and post_url:
        update_content_piece_status(supabase, content_id, post_id, post_url)
        print("WordPress Publisher Agent completed successfully")
    else:
        print("Error: Failed to publish content to WordPress")
        sys.exit(1)


if __name__ == "__main__":
    main()
