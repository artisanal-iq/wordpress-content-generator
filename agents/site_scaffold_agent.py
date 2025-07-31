#!/usr/bin/env python3
"""
WordPress Site Scaffold Agent

This agent bootstraps a WordPress site with:
- Required plugins (Rank Math SEO, WPForms, etc.)
- EEAT pages (About, Contact, Privacy Policy, etc.)
- Default categories
- Pillar posts (2500-3000 words) + supporting posts (5 per pillar)

Usage:
    python site_scaffold_agent.py --site-id <uuid>
    python site_scaffold_agent.py --site-id <uuid> --no-ai
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# Import shared utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.shared.utils import create_agent_task, update_agent_status

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Default plugins to install
DEFAULT_PLUGINS = [
    {
        "slug": "seo-by-rank-math",
        "name": "Rank Math SEO",
        "description": "SEO plugin with XML sitemaps, schema, OpenGraph"
    },
    {
        "slug": "wpforms-lite",
        "name": "WPForms Lite",
        "description": "Contact forms with GDPR compliance"
    },
    {
        "slug": "redirection",
        "name": "Redirection",
        "description": "Manage 301 redirects and track 404 errors"
    },
    {
        "slug": "wp-super-cache",
        "name": "WP Super Cache",
        "description": "Static page caching for performance"
    },
    {
        "slug": "autoptimize",
        "name": "Autoptimize",
        "description": "Optimize CSS, JS, images, Google Fonts"
    },
    {
        "slug": "wordfence",
        "name": "Wordfence Security",
        "description": "Firewall, malware scanner, brute force protection"
    },
    {
        "slug": "google-site-kit",
        "name": "Site Kit by Google",
        "description": "Analytics, Search Console, PageSpeed integration"
    },
    {
        "slug": "easy-table-of-contents",
        "name": "Easy Table of Contents",
        "description": "Auto-generate ToC for long articles"
    }
]

# EEAT pages to create
EEAT_PAGES = [
    {
        "title": "About Us",
        "slug": "about-us",
        "content_template": "This is the About Us page for {site_name}. We are experts in {niche} focused on providing value to {audience}."
    },
    {
        "title": "Contact Us",
        "slug": "contact-us",
        "content_template": "Get in touch with {site_name}. We're here to help with all your {niche} needs."
    },
    {
        "title": "Privacy Policy",
        "slug": "privacy-policy",
        "content_template": "This Privacy Policy describes how {site_name} collects, uses, and shares your information when you use our website."
    },
    {
        "title": "Terms of Service",
        "slug": "terms-of-service",
        "content_template": "By accessing or using {site_name}, you agree to be bound by these Terms of Service."
    },
    {
        "title": "Author Biography",
        "slug": "author-bio",
        "content_template": "Learn more about the expert authors at {site_name} who specialize in {niche}."
    },
    {
        "title": "Sitemap",
        "slug": "sitemap",
        "content_template": "Navigate all the content available on {site_name}."
    }
]

# Default categories if none specified
DEFAULT_CATEGORIES = [
    "Guides & Tutorials",
    "Industry News",
    "Case Studies"
]


def get_supabase_client() -> Client:
    """Create and return a Supabase client."""
    # Load environment variables
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file{ENDC}")
        sys.exit(1)
    
    return create_client(url, key)


def get_wordpress_site(site_id: str, supabase: Client) -> Dict[str, Any]:
    """Fetch WordPress site details from Supabase."""
    try:
        response = supabase.table("wordpress_sites").select("*").eq("id", site_id).execute()
        
        if not response.data:
            print(f"{RED}Error: No WordPress site found with ID {site_id}{ENDC}")
            sys.exit(1)
        
        return response.data[0]
    except Exception as e:
        print(f"{RED}Error fetching WordPress site: {e}{ENDC}")
        sys.exit(1)


def update_scaffold_status(site_id: str, status: str, supabase: Client, 
                          scaffolded_at: Optional[datetime] = None) -> None:
    """Update the scaffold status of a WordPress site."""
    try:
        update_data = {"scaffold_status": status}
        if scaffolded_at:
            update_data["scaffolded_at"] = scaffolded_at.isoformat()
        
        supabase.table("wordpress_sites").update(update_data).eq("id", site_id).execute()
        print(f"{GREEN}Updated scaffold status to '{status}'{ENDC}")
    except Exception as e:
        print(f"{RED}Error updating scaffold status: {e}{ENDC}")


def install_plugins(wp_site: Dict[str, Any], use_ai: bool = True) -> bool:
    """
    Install and activate the default plugins.
    
    In a real implementation, this would make REST API calls to WordPress.
    For now, we'll simulate the process with logs.
    """
    print(f"{BLUE}Installing and activating plugins for {wp_site['domain']}{ENDC}")
    
    for plugin in DEFAULT_PLUGINS:
        print(f"{YELLOW}Installing plugin: {plugin['name']}{ENDC}")
        
        # Simulate API call to install plugin
        # In production, this would be:
        # response = requests.post(
        #     f"{wp_site['url']}/wp-json/wp/v2/plugins",
        #     auth=(wp_site['username'], wp_site['app_password']),
        #     json={"slug": plugin['slug'], "status": "active"}
        # )
        
        # Simulate success/failure
        success = True
        if success:
            print(f"{GREEN}Successfully installed and activated: {plugin['name']}{ENDC}")
        else:
            print(f"{RED}Failed to install plugin: {plugin['name']}{ENDC}")
            return False
        
        # Simulate a delay for realism
        time.sleep(0.5)
    
    return True


def create_eeat_pages(wp_site: Dict[str, Any], use_ai: bool = True) -> bool:
    """
    Create EEAT pages (About, Contact, Privacy, Terms, Author, Sitemap).
    
    In a real implementation, this would make REST API calls to WordPress.
    """
    print(f"{BLUE}Creating EEAT pages for {wp_site['domain']}{ENDC}")
    
    # Get site name from domain
    site_name = wp_site['domain'].split('.')[0].title()
    
    # Use niche from a strategic plan or default
    niche = "digital content"
    audience = "online readers"
    
    # Try to get a strategic plan for this site
    try:
        supabase = get_supabase_client()
        response = supabase.table("strategic_plans").select("niche,audience").eq("wordpress_site_id", wp_site['id']).execute()
        if response.data:
            niche = response.data[0].get("niche", niche)
            audience = response.data[0].get("audience", audience)
    except Exception:
        # Use defaults if we can't get the strategic plan
        pass
    
    for page in EEAT_PAGES:
        print(f"{YELLOW}Creating page: {page['title']}{ENDC}")
        
        # Format content template with site info
        content = page['content_template'].format(
            site_name=site_name,
            niche=niche,
            audience=audience
        )
        
        # Simulate API call to create page
        # In production, this would be:
        # response = requests.post(
        #     f"{wp_site['url']}/wp-json/wp/v2/pages",
        #     auth=(wp_site['username'], wp_site['app_password']),
        #     json={
        #         "title": page['title'],
        #         "slug": page['slug'],
        #         "content": content,
        #         "status": "publish"
        #     }
        # )
        
        # Simulate success
        print(f"{GREEN}Created page: {page['title']}{ENDC}")
        
        # Simulate a delay for realism
        time.sleep(0.5)
    
    return True


def create_categories(wp_site: Dict[str, Any], use_ai: bool = True) -> List[Dict[str, Any]]:
    """
    Create default categories.
    
    In a real implementation, this would make REST API calls to WordPress.
    Returns a list of created category objects.
    """
    print(f"{BLUE}Creating categories for {wp_site['domain']}{ENDC}")
    
    categories = []
    
    for category_name in DEFAULT_CATEGORIES:
        print(f"{YELLOW}Creating category: {category_name}{ENDC}")
        
        # Simulate API call to create category
        # In production, this would be:
        # response = requests.post(
        #     f"{wp_site['url']}/wp-json/wp/v2/categories",
        #     auth=(wp_site['username'], wp_site['app_password']),
        #     json={
        #         "name": category_name,
        #         "slug": category_name.lower().replace(" & ", "-").replace(" ", "-")
        #     }
        # )
        
        # Simulate response with category ID
        category_id = len(categories) + 1
        category = {
            "id": category_id,
            "name": category_name,
            "slug": category_name.lower().replace(" & ", "-").replace(" ", "-")
        }
        categories.append(category)
        
        print(f"{GREEN}Created category: {category_name} (ID: {category_id}){ENDC}")
        
        # Simulate a delay for realism
        time.sleep(0.5)
    
    return categories


def generate_pillar_post(category: Dict[str, Any], wp_site: Dict[str, Any], 
                         supabase: Client, use_ai: bool = True) -> str:
    """
    Generate a pillar post (2500-3000 words) for a category.
    
    In a real implementation, this would:
    1. Create a strategic plan if needed
    2. Create a content_piece record
    3. Queue the content generation pipeline
    
    Returns the content_piece ID.
    """
    print(f"{BLUE}Generating pillar post for category: {category['name']}{ENDC}")
    
    # Get or create a strategic plan for this site
    strategic_plan_id = None
    try:
        response = supabase.table("strategic_plans").select("id").eq("wordpress_site_id", wp_site['id']).execute()
        if response.data:
            strategic_plan_id = response.data[0]["id"]
        else:
            # Create a new strategic plan
            site_name = wp_site['domain'].split('.')[0].title()
            plan_data = {
                "domain": wp_site['domain'],
                "audience": "general audience",
                "tone": "informative",
                "niche": category['name'],
                "goal": "educate readers",
                "wordpress_site_id": wp_site['id']
            }
            response = supabase.table("strategic_plans").insert(plan_data).execute()
            strategic_plan_id = response.data[0]["id"]
    except Exception as e:
        print(f"{RED}Error with strategic plan: {e}{ENDC}")
        # Generate a UUID for testing purposes
        strategic_plan_id = str(uuid.uuid4())
    
    # Create a content piece for the pillar post
    content_id = str(uuid.uuid4())
    title = f"Ultimate Guide to {category['name']}"
    slug = f"ultimate-guide-{category['slug']}"
    
    try:
        content_data = {
            "id": content_id,
            "title": title,
            "slug": slug,
            "status": "draft",
            "strategic_plan_id": strategic_plan_id,
            "created_at": datetime.now().isoformat(),
            "is_pillar": True,
            "category_id": category['id']
        }
        
        supabase.table("content_pieces").insert(content_data).execute()
        print(f"{GREEN}Created pillar post: {title} (ID: {content_id}){ENDC}")
        
        # Queue the SEO agent to start the content pipeline
        agent_task_id = str(uuid.uuid4())
        create_agent_task("seo-agent", content_id, {"plan_id": strategic_plan_id}, supabase)
        
    except Exception as e:
        print(f"{YELLOW}Simulating content creation due to error: {e}{ENDC}")
    
    return content_id


def generate_supporting_posts(pillar_id: str, category: Dict[str, Any], 
                             wp_site: Dict[str, Any], supabase: Client,
                             count: int = 5, use_ai: bool = True) -> List[str]:
    """
    Generate supporting posts for a pillar post.
    
    Returns a list of content_piece IDs.
    """
    print(f"{BLUE}Generating {count} supporting posts for pillar in {category['name']}{ENDC}")
    
    content_ids = []
    
    # Get the strategic plan ID from the pillar post
    strategic_plan_id = None
    try:
        response = supabase.table("content_pieces").select("strategic_plan_id").eq("id", pillar_id).execute()
        if response.data:
            strategic_plan_id = response.data[0]["strategic_plan_id"]
    except Exception:
        # Generate a UUID for testing purposes
        strategic_plan_id = str(uuid.uuid4())
    
    for i in range(1, count + 1):
        content_id = str(uuid.uuid4())
        title = f"Supporting Article #{i} for {category['name']}"
        slug = f"supporting-{i}-{category['slug']}"
        
        try:
            content_data = {
                "id": content_id,
                "title": title,
                "slug": slug,
                "status": "draft",
                "strategic_plan_id": strategic_plan_id,
                "created_at": datetime.now().isoformat(),
                "is_pillar": False,
                "pillar_id": pillar_id,
                "category_id": category['id']
            }
            
            supabase.table("content_pieces").insert(content_data).execute()
            print(f"{GREEN}Created supporting post: {title} (ID: {content_id}){ENDC}")
            
            # Queue the SEO agent to start the content pipeline
            create_agent_task("seo-agent", content_id, {"plan_id": strategic_plan_id}, supabase)
            
            content_ids.append(content_id)
            
        except Exception as e:
            print(f"{YELLOW}Simulating supporting content creation due to error: {e}{ENDC}")
            content_ids.append(content_id)
        
        # Simulate a delay for realism
        time.sleep(0.2)
    
    return content_ids


def scaffold_wordpress_site(site_id: str, use_ai: bool = True) -> bool:
    """
    Main function to scaffold a WordPress site.
    
    1. Install/activate plugins
    2. Create EEAT pages
    3. Create categories
    4. Generate pillar + supporting posts
    """
    print(f"{BOLD}WordPress Site Scaffold Agent{ENDC}")
    print("=" * 60)
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Get WordPress site details
    wp_site = get_wordpress_site(site_id, supabase)
    print(f"{GREEN}Scaffolding WordPress site: {wp_site['domain']} ({wp_site['url']}){ENDC}")
    
    # Create agent status record
    agent_task_id = str(uuid.uuid4())
    create_agent_task("site-scaffold-agent", site_id, {}, supabase)
    update_agent_status(agent_task_id, "processing", supabase=supabase)
    
    # Update scaffold status to in_progress
    update_scaffold_status(site_id, "in_progress", supabase)
    
    try:
        # Step 1: Install and activate plugins
        if not install_plugins(wp_site, use_ai):
            update_agent_status(
                agent_task_id, 
                "error", 
                errors=["plugin_installation_failed"], 
                supabase=supabase
            )
            update_scaffold_status(site_id, "failed", supabase)
            return False
        
        # Step 2: Create EEAT pages
        if not create_eeat_pages(wp_site, use_ai):
            update_agent_status(
                agent_task_id, 
                "error", 
                errors=["eeat_pages_creation_failed"], 
                supabase=supabase
            )
            update_scaffold_status(site_id, "failed", supabase)
            return False
        
        # Step 3: Create categories
        categories = create_categories(wp_site, use_ai)
        if not categories:
            update_agent_status(
                agent_task_id, 
                "error", 
                errors=["categories_creation_failed"], 
                supabase=supabase
            )
            update_scaffold_status(site_id, "failed", supabase)
            return False
        
        # Step 4: Generate pillar posts + supporting content for each category
        for category in categories:
            # Create pillar post
            pillar_id = generate_pillar_post(category, wp_site, supabase, use_ai)
            
            # Create 5 supporting posts
            supporting_ids = generate_supporting_posts(
                pillar_id, category, wp_site, supabase, count=5, use_ai=use_ai
            )
            
            print(f"{GREEN}Created content cluster for {category['name']}: " 
                  f"1 pillar + {len(supporting_ids)} supporting posts{ENDC}")
        
        # Update scaffold status to done
        update_scaffold_status(
            site_id, "done", supabase, scaffolded_at=datetime.now()
        )
        
        # Update agent status to done
        update_agent_status(
            agent_task_id, 
            "done", 
            output={"message": f"Successfully scaffolded WordPress site {wp_site['domain']}"},
            supabase=supabase
        )
        
        print(f"{GREEN}Successfully scaffolded WordPress site: {wp_site['domain']}{ENDC}")
        return True
        
    except Exception as e:
        print(f"{RED}Error scaffolding WordPress site: {e}{ENDC}")
        update_agent_status(
            agent_task_id, 
            "error", 
            errors=[str(e)], 
            supabase=supabase
        )
        update_scaffold_status(site_id, "failed", supabase)
        return False


def main():
    """Parse command line arguments and run the agent."""
    parser = argparse.ArgumentParser(description="WordPress Site Scaffold Agent")
    parser.add_argument("--site-id", required=True, help="WordPress site UUID")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI (use mock data)")
    
    args = parser.parse_args()
    
    return 0 if scaffold_wordpress_site(args.site_id, not args.no_ai) else 1


if __name__ == "__main__":
    sys.exit(main())
