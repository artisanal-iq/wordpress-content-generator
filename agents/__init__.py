"""
WordPress Content Generator - Agents Package

This package contains all the specialized agents used in the content generation pipeline.
Each agent is responsible for a specific task in the content creation process, such as
SEO keyword generation, research, writing, editing, etc.

Agents are designed to be:
1. Stateless - They don't maintain state between invocations
2. Idempotent - Running the same agent with the same input produces the same output
3. Focused - Each agent has a single, well-defined responsibility
4. Interoperable - Agents communicate through standardized input/output contracts

The shared module provides common utilities, schemas, and helper functions used across agents.
"""

# Import shared modules for easier access
from .shared import schemas, utils

# Import agent modules
try:
    from . import seo_agent, site_scaffold_agent
except ImportError:
    pass  # Agent may not be fully implemented yet

# Define public API
__all__ = [
    "schemas",
    "utils",
    "seo_agent",
    "site_scaffold_agent",
]

# Alias common agent functions for convenience
try:
    from .seo_agent import run as run_seo_agent

    __all__.append("run_seo_agent")
    from .site_scaffold_agent import run as run_site_scaffold_agent

    __all__.append("run_site_scaffold_agent")
except ImportError:
    pass
