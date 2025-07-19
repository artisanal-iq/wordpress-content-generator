"""
WordPress Content Generator

An autonomous, agent-based system that plans, writes, edits, illustrates and publishes 
long-form, SEO-optimised articles directly to WordPress.

This package provides a modular framework for content generation using specialized agents,
each responsible for a specific part of the content creation pipeline.

Usage:
    from wordpress_content_generator import run_agent, orchestrator
    from wordpress_content_generator.agents.seo_agent import run as run_seo_agent
"""

__version__ = "0.1.0"
__author__ = "Jay Jordan"

# Import main components for easier access
try:
    from .agents.shared import schemas, utils
    from .agents.seo_agent import run as run_seo_agent
    from .run_agent import main as run_agent
    from .orchestrator import main as run_orchestrator
    
    # Define public API
    __all__ = [
        "schemas",
        "utils",
        "run_seo_agent",
        "run_agent",
        "run_orchestrator",
    ]
except ImportError:
    # This allows the package to be imported even if some dependencies
    # are not installed yet (useful during installation)
    pass
