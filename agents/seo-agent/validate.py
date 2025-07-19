"""
Validation Module for SEO Agent

This module provides validation functions for the SEO agent's input and output data.
It ensures that all required fields are present and properly formatted.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seo-agent-validator")


def validate_input(input_data: Dict[str, Any]) -> bool:
    """
    Validate the input data for the SEO agent.
    
    Args:
        input_data: Dictionary containing input parameters
        
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
        
    # Check required fields
    if "domain" not in input_data:
        raise ValueError("Input must contain 'domain' field")
        
    if "niche" not in input_data:
        raise ValueError("Input must contain 'niche' field")
    
    # Validate domain format
    domain = input_data["domain"]
    if not isinstance(domain, str):
        raise ValueError("Domain must be a string")
    
    # Basic domain validation (simplified)
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
    if not re.match(domain_pattern, domain):
        raise ValueError(f"Invalid domain format: {domain}")
    
    # Validate niche
    niche = input_data["niche"]
    if not isinstance(niche, str):
        raise ValueError("Niche must be a string")
    
    if len(niche.strip()) < 3:
        raise ValueError("Niche must be at least 3 characters long")
    
    # Optional fields validation
    if "content_id" in input_data and not isinstance(input_data["content_id"], str):
        raise ValueError("content_id must be a string (UUID)")
    
    if "strategic_plan_id" in input_data and not isinstance(input_data["strategic_plan_id"], str):
        raise ValueError("strategic_plan_id must be a string (UUID)")
        
    return True


def validate_output(output_data: Dict[str, Any]) -> bool:
    """
    Validate the output data from the SEO agent.
    
    Args:
        output_data: Dictionary containing output parameters
        
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    if not isinstance(output_data, dict):
        raise ValueError("Output must be a dictionary")
    
    # Check if seo key exists
    if "seo" not in output_data:
        raise ValueError("Output must contain 'seo' field")
    
    seo_data = output_data["seo"]
    
    # Validate focus keyword
    if "focus_keyword" not in seo_data:
        raise ValueError("SEO output must contain 'focus_keyword' field")
    
    focus_keyword = seo_data["focus_keyword"]
    if not isinstance(focus_keyword, str) or len(focus_keyword.strip()) < 2:
        raise ValueError("focus_keyword must be a non-empty string")
    
    # Validate supporting keywords
    if "supporting_keywords" not in seo_data:
        raise ValueError("SEO output must contain 'supporting_keywords' field")
    
    supporting_keywords = seo_data["supporting_keywords"]
    if not isinstance(supporting_keywords, list):
        raise ValueError("supporting_keywords must be a list")
    
    if len(supporting_keywords) < 1:
        raise ValueError("supporting_keywords must contain at least one keyword")
    
    for keyword in supporting_keywords:
        if not isinstance(keyword, str) or len(keyword.strip()) < 2:
            raise ValueError("Each supporting keyword must be a non-empty string")
    
    # Validate internal links
    if "internal_links" in seo_data:
        internal_links = seo_data["internal_links"]
        if not isinstance(internal_links, list):
            raise ValueError("internal_links must be a list")
        
        for link in internal_links:
            if not isinstance(link, str) or len(link.strip()) < 2:
                raise ValueError("Each internal link must be a non-empty string")
    
    # Validate cluster target
    if "cluster_target" in seo_data:
        cluster_target = seo_data["cluster_target"]
        if not isinstance(cluster_target, str) or len(cluster_target.strip()) < 2:
            raise ValueError("cluster_target must be a non-empty string")
    
    return True


def validate_keyword_quality(keyword: str) -> Dict[str, Any]:
    """
    Evaluate the quality of a keyword or phrase.
    
    Args:
        keyword: The keyword to evaluate
        
    Returns:
        Dict with quality metrics
    """
    metrics = {
        "length": len(keyword),
        "word_count": len(keyword.split()),
        "has_numbers": any(char.isdigit() for char in keyword),
        "quality_score": 0  # Default score
    }
    
    # Basic quality scoring (can be expanded)
    word_count = metrics["word_count"]
    
    # Long-tail keywords (3-5 words) are often better
    if 3 <= word_count <= 5:
        metrics["quality_score"] += 3
    elif 2 == word_count:
        metrics["quality_score"] += 2
    elif word_count > 5:
        metrics["quality_score"] += 1
    else:
        # Single word keywords are often highly competitive
        metrics["quality_score"] += 0
    
    # Keywords with numbers often perform well
    if metrics["has_numbers"]:
        metrics["quality_score"] += 1
    
    # Keywords that are too long might be too specific
    if len(keyword) > 50:
        metrics["quality_score"] -= 1
    
    return metrics


def validate_keyword_cluster(
    focus_keyword: str, 
    supporting_keywords: List[str]
) -> Dict[str, Any]:
    """
    Validate the semantic coherence of a keyword cluster.
    
    Args:
        focus_keyword: The main keyword
        supporting_keywords: List of related keywords
        
    Returns:
        Dict with validation results
    """
    results = {
        "is_valid": True,
        "warnings": [],
        "suggestions": []
    }
    
    # Check if supporting keywords are too similar to each other
    for i, kw1 in enumerate(supporting_keywords):
        for j, kw2 in enumerate(supporting_keywords[i+1:], i+1):
            if kw1.lower() == kw2.lower():
                results["is_valid"] = False
                results["warnings"].append(f"Duplicate supporting keywords: '{kw1}' and '{kw2}'")
    
    # Check if supporting keywords contain the focus keyword
    focus_words = set(focus_keyword.lower().split())
    supporting_contains_focus = 0
    
    for kw in supporting_keywords:
        kw_words = set(kw.lower().split())
        if focus_words.issubset(kw_words):
            supporting_contains_focus += 1
    
    # If too many supporting keywords contain the exact focus keyword
    if supporting_contains_focus > len(supporting_keywords) / 2:
        results["warnings"].append(
            "Too many supporting keywords contain the exact focus keyword. "
            "Consider more diverse variations."
        )
    
    # Check keyword length distribution
    long_keywords = [kw for kw in supporting_keywords if len(kw.split()) >= 4]
    if len(long_keywords) == 0:
        results["suggestions"].append(
            "Consider adding some longer-tail keywords (4+ words) "
            "to capture more specific search intent."
        )
    
    return results
