"""
SEO Agent Package for WordPress Content Generator

This package provides functionality to generate SEO-optimized keyword clusters
based on a domain and content niche. It produces focus keywords, supporting keywords,
and internal link targets to guide content creation.

Example usage:
    from agents.seo_agent import run
    
    result = run({
        "domain": "fitness-blog.com",
        "niche": "weight training"
    })
"""

from .index import run, validate, generate_keyword_cluster
from .validate import validate_input, validate_output, validate_keyword_quality, validate_keyword_cluster

__all__ = [
    'run',
    'validate',
    'generate_keyword_cluster',
    'validate_input',
    'validate_output',
    'validate_keyword_quality',
    'validate_keyword_cluster'
]
