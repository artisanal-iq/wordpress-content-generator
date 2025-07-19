"""
SEO Agent for WordPress Content Generator

This agent generates SEO keyword clusters based on a domain and niche.
It produces focus keywords, supporting keywords, and internal link targets
to guide content creation.

Input:
    - domain: The website domain (e.g., "fitness-blog.com")
    - niche: The content niche (e.g., "weight training")

Output:
    - focus_keyword: Primary keyword for the content
    - supporting_keywords: List of related keywords
    - cluster_target: Category/cluster this content belongs to
    - internal_links: Suggested internal link targets
"""

import json
import logging
import sys
from typing import Dict, Any, List

from ..shared.schemas import AgentTask, KeywordCluster
from ..shared.utils import (
    generate_completion,
    format_agent_response,
    log_agent_error,
    extract_keywords
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seo-agent")

# Define system prompt for keyword generation
KEYWORD_SYSTEM_PROMPT = """
You are an expert SEO strategist. Your task is to analyze a website domain and content niche,
then generate a strategic keyword cluster for a new piece of content.

Focus on:
1. Identifying a primary keyword with good search volume and moderate competition
2. Supporting keywords that enhance the semantic relevance
3. Internal linking opportunities within the same domain
4. Ensuring the keyword cluster is cohesive and targeted

Provide only JSON output with no additional text.
"""

def validate(input_data: Dict[str, Any]) -> bool:
    """
    Validate the input data for the SEO agent.
    
    Args:
        input_data: Dictionary containing input parameters
        
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
        
    if "domain" not in input_data:
        raise ValueError("Input must contain 'domain' field")
        
    if "niche" not in input_data:
        raise ValueError("Input must contain 'niche' field")
        
    return True


def generate_keyword_cluster(domain: str, niche: str) -> Dict[str, Any]:
    """
    Generate a keyword cluster using OpenAI's API.
    
    Args:
        domain: Website domain
        niche: Content niche
        
    Returns:
        Dict: Generated keyword data
    """
    prompt = f"""
    Please generate an SEO keyword cluster for a new article on {domain}, which focuses on {niche}.
    
    I need:
    1. A primary focus keyword (moderately competitive, good search intent)
    2. 5-7 supporting keywords that enhance the article's semantic relevance
    3. 3-5 internal link suggestions (topics that would make sense to link to)
    4. A cluster/category name this content belongs to
    
    Return your response as a JSON object with these keys:
    - focus_keyword
    - supporting_keywords (array)
    - internal_links (array)
    - cluster_target
    """
    
    try:
        response = generate_completion(
            prompt=prompt,
            system_message=KEYWORD_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=800
        )
        
        # Parse the JSON response
        try:
            # Handle potential markdown code block formatting
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            keyword_data = json.loads(response)
            
            # Validate required fields
            required_fields = ["focus_keyword", "supporting_keywords", "internal_links", "cluster_target"]
            for field in required_fields:
                if field not in keyword_data:
                    raise ValueError(f"Missing required field in response: {field}")
                    
            return keyword_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            
            # Fallback: Try to extract keywords directly from the text
            focus_keyword = niche
            supporting_keywords = extract_keywords(response, max_keywords=7)
            
            return {
                "focus_keyword": focus_keyword,
                "supporting_keywords": supporting_keywords,
                "internal_links": [f"{niche} guide", f"{niche} tips", f"{niche} examples"],
                "cluster_target": niche
            }
            
    except Exception as e:
        logger.error(f"Error generating keyword cluster: {e}")
        raise


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the SEO agent.
    
    Args:
        input_data: Dictionary with 'domain' and 'niche' keys
        
    Returns:
        Dict: Agent response with status and output
    """
    agent_name = "seo-agent"
    
    try:
        # Validate input
        validate(input_data)
        
        domain = input_data["domain"]
        niche = input_data["niche"]
        
        logger.info(f"Generating keyword cluster for domain: {domain}, niche: {niche}")
        
        # Generate keyword cluster
        keyword_data = generate_keyword_cluster(domain, niche)
        
        # Format output according to the standard schema
        output = {
            "seo": {
                "focus_keyword": keyword_data["focus_keyword"],
                "supporting_keywords": keyword_data["supporting_keywords"],
                "internal_links": keyword_data["internal_links"],
                "cluster_target": keyword_data["cluster_target"]
            }
        }
        
        return format_agent_response(agent_name, output)
        
    except Exception as e:
        error_info = log_agent_error(agent_name, e)
        return format_agent_response(
            agent_name, 
            {}, 
            status="error",
            errors=[f"SEO_GENERATION_FAIL: {str(e)}"]
        )


if __name__ == "__main__":
    """
    Command-line interface for testing the agent.
    
    Usage:
        python -m agents.seo-agent.index '{"domain": "example.com", "niche": "gardening"}'
    """
    if len(sys.argv) > 1:
        try:
            input_json = json.loads(sys.argv[1])
            result = run(input_json)
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError:
            print("Error: Input must be valid JSON")
            sys.exit(1)
    else:
        print("Error: No input provided")
        print("Usage: python -m agents.seo-agent.index '{\"domain\": \"example.com\", \"niche\": \"gardening\"}'")
        sys.exit(1)
