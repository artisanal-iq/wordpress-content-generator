"""
Shared Utility Functions for WordPress Content Generator

This module provides utility functions used across all agents in the content
generation pipeline. It includes helpers for database interactions, LLM API calls,
text processing, error handling, and more.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import openai
import requests
import tiktoken
from dotenv import load_dotenv
from slugify import slugify
from supabase import Client, create_client
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("wordpress-content-generator")


# Initialize Supabase client
def get_supabase_client() -> Client:
    """
    Create and return a Supabase client using environment variables.

    Returns:
        Client: Configured Supabase client
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL and SUPABASE_KEY environment variables must be set"
        )

    return create_client(url, key)


# OpenAI/LLM utilities
def get_openai_client():
    """
    Create and return an OpenAI client using environment variables.

    Returns:
        OpenAI client instance
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable must be set")

    return openai.OpenAI(api_key=api_key)


def setup_openai():
    """Backward compatible wrapper for obtaining an OpenAI client."""
    return get_openai_client()


@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def generate_completion(
    prompt: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    system_message: str = "You are a helpful assistant.",
) -> str:
    """
    Generate text completion using OpenAI's API with retry logic.

    Args:
        prompt: The user prompt to send to the model
        model: The OpenAI model to use
        temperature: Controls randomness (0-1)
        max_tokens: Maximum tokens in the response
        system_message: System message for context

    Returns:
        str: Generated text response
    """
    client = get_openai_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating completion: {e}")
        raise


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text string for a specific model.

    Args:
        text: The text to count tokens for
        model: The model to use for counting

    Returns:
        int: Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Error counting tokens: {e}. Using approximate count.")
        # Fallback to approximate count (1 token ≈ 4 chars)
        return len(text) // 4


# Text processing utilities
def create_slug(text: str) -> str:
    """
    Create a URL-friendly slug from text.

    Args:
        text: Text to convert to slug

    Returns:
        str: URL-friendly slug
    """
    return slugify(text)


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract potential keywords from a text.

    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return

    Returns:
        List[str]: Extracted keywords
    """
    # This is a simple implementation
    # In a real system, you might use NLP libraries or LLM APIs
    words = re.findall(r"\b[a-zA-Z]{3,15}\b", text.lower())
    word_freq = {}

    for word in words:
        if word not in word_freq:
            word_freq[word] = 0
        word_freq[word] += 1

    # Filter out common words (very basic stopwords)
    stopwords = {
        "the",
        "and",
        "is",
        "in",
        "to",
        "of",
        "for",
        "with",
        "on",
        "at",
        "from",
        "by",
    }
    word_freq = {
        word: freq for word, freq in word_freq.items() if word not in stopwords
    }

    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    # Return top keywords
    return [word for word, _ in sorted_words[:max_keywords]]


def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        add_ellipsis: Whether to add "..." at the end

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length].rsplit(" ", 1)[0]
    if add_ellipsis:
        truncated += "..."

    return truncated


# Error handling and logging
def log_agent_error(
    agent_name: str, error: Exception, content_id: str = None
) -> Dict[str, Any]:
    """
    Log an agent error and format it for storage.

    Args:
        agent_name: Name of the agent
        error: Exception that occurred
        content_id: ID of the content piece (if applicable)

    Returns:
        Dict with error information
    """
    error_info = {
        "agent": agent_name,
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": datetime.now().isoformat(),
    }

    if content_id:
        error_info["content_id"] = content_id

    logger.error(f"Agent error: {agent_name} - {error}")
    return error_info


def format_agent_response(
    agent_name: str,
    output: Dict[str, Any],
    status: str = "done",
    errors: List[str] = None,
) -> Dict[str, Any]:
    """
    Format agent response according to the standard schema.

    Args:
        agent_name: Name of the agent
        output: Output data from the agent
        status: Task status
        errors: List of error messages

    Returns:
        Dict with formatted response
    """
    return {
        "agent": agent_name,
        "output": output,
        "status": status,
        "errors": errors or [],
        "updated_at": datetime.now().isoformat(),
    }


# WordPress API utilities
def wordpress_api_request(
    endpoint: str,
    method: str = "GET",
    data: Dict = None,
    auth: Tuple[str, str] = None,
) -> Dict:
    """
    Make a request to the WordPress REST API.

    Args:
        endpoint: API endpoint (without base URL)
        method: HTTP method
        data: Request data
        auth: (username, password) tuple for authentication

    Returns:
        Dict: API response
    """
    wp_api_url = os.getenv("WP_API_URL")
    if not wp_api_url:
        raise EnvironmentError("WP_API_URL environment variable must be set")

    url = f"{wp_api_url}/{endpoint.lstrip('/')}"

    if not auth and os.getenv("WP_USERNAME") and os.getenv("WP_APP_PASSWORD"):
        auth = (os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))

    try:
        response = requests.request(
            method=method,
            url=url,
            json=data,
            auth=auth,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"WordPress API error: {e}")
        raise


# Image utilities
def download_image(url: str, save_path: str = None) -> bytes:
    """
    Download an image from a URL.

    Args:
        url: Image URL
        save_path: Path to save the image (if provided)

    Returns:
        bytes: Image data
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        if save_path:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        return response.content
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        raise


def search_stock_images(
    query: str, provider: str = "pexels", per_page: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for stock images using Pexels or Unsplash API.

    Args:
        query: Search query
        provider: "pexels" or "unsplash"
        per_page: Number of results to return

    Returns:
        List of image data dictionaries
    """
    if provider.lower() == "pexels":
        api_key = os.getenv("PEXELS_API_KEY")
        if not api_key:
            raise EnvironmentError("PEXELS_API_KEY environment variable must be set")

        url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"
        headers = {"Authorization": api_key}

    elif provider.lower() == "unsplash":
        api_key = os.getenv("UNSPLASH_API_KEY")
        if not api_key:
            raise EnvironmentError("UNSPLASH_API_KEY environment variable must be set")

        url = (
            f"https://api.unsplash.com/search/photos?query={query}&per_page={per_page}"
        )
        headers = {"Authorization": f"Client-ID {api_key}"}

    else:
        raise ValueError("Provider must be 'pexels' or 'unsplash'")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Normalize response format
        if provider.lower() == "pexels":
            return [
                {
                    "id": photo["id"],
                    "url": photo["src"]["original"],
                    "width": photo["width"],
                    "height": photo["height"],
                    "alt": photo.get("alt", ""),
                    "photographer": photo["photographer"],
                    "source": "pexels",
                    "thumbnail": photo["src"]["medium"],
                }
                for photo in data.get("photos", [])
            ]
        else:  # unsplash
            return [
                {
                    "id": photo["id"],
                    "url": photo["urls"]["full"],
                    "width": photo["width"],
                    "height": photo["height"],
                    "alt": photo.get("alt_description", ""),
                    "photographer": photo["user"]["name"],
                    "source": "unsplash",
                    "thumbnail": photo["urls"]["thumb"],
                }
                for photo in data.get("results", [])
            ]

    except Exception as e:
        logger.error(f"Error searching stock images: {e}")
        raise


# Database interaction helpers
def get_content_piece(content_id: str, supabase: Client = None) -> Dict[str, Any]:
    """
    Get a content piece from the database.

    Args:
        content_id: ID of the content piece
        supabase: Supabase client (optional)

    Returns:
        Dict: Content piece data
    """
    if supabase is None:
        supabase = get_supabase_client()

    response = (
        supabase.table("content_pieces").select("*").eq("id", content_id).execute()
    )

    if not response.data:
        raise ValueError(f"Content piece with ID {content_id} not found")

    return response.data[0]


def update_agent_status(
    task_id: str,
    status: str,
    output: Dict = None,
    errors: List[str] = None,
    supabase: Client = None,
) -> Dict[str, Any]:
    """
    Update the status of an agent task in the database.

    Args:
        task_id: ID of the agent task
        status: New status
        output: Task output data
        errors: List of error messages
        supabase: Supabase client (optional)

    Returns:
        Dict: Updated task data
    """
    if supabase is None:
        supabase = get_supabase_client()

    update_data = {"status": status, "updated_at": datetime.now().isoformat()}

    if output is not None:
        update_data["output"] = output

    if errors is not None:
        update_data["errors"] = errors

    response = (
        supabase.table("agent_status").update(update_data).eq("id", task_id).execute()
    )

    if not response.data:
        raise ValueError(f"Agent task with ID {task_id} not found")

    return response.data[0]


def create_agent_task(
    agent: str, content_id: str, input_data: Dict[str, Any], supabase: Client = None
) -> Dict[str, Any]:
    """
    Create a new agent task in the database.

    Args:
        agent: Name of the agent
        content_id: ID of the content piece
        input_data: Task input data
        supabase: Supabase client (optional)

    Returns:
        Dict: Created task data
    """
    if supabase is None:
        supabase = get_supabase_client()

    task_data = {
        "agent": agent,
        "content_id": content_id,
        "input": input_data,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    response = supabase.table("agent_status").insert(task_data).execute()

    return response.data[0]
