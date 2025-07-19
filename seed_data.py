#!/usr/bin/env python3
"""
Seed Data Script for WordPress Content Generator

This script populates the Supabase database with test data for development and testing.
It creates sample strategic plans, content pieces, keywords, and agent tasks.

Usage:
    python seed_data.py [--reset]
    
Options:
    --reset    Delete existing data before inserting new data
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List

import dotenv
from supabase import create_client

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
dotenv.load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample data
STRATEGIC_PLANS = [
    {
        "domain": "fitness-blog.com",
        "audience": "fitness enthusiasts aged 25-45",
        "tone": "motivational and informative",
        "niche": "weight training",
        "goal": "educate beginners on proper weight training techniques"
    },
    {
        "domain": "recipe-heaven.com",
        "audience": "home cooks of all skill levels",
        "tone": "friendly and approachable",
        "niche": "vegetarian recipes",
        "goal": "provide easy vegetarian recipes for weeknight dinners"
    },
    {
        "domain": "tech-insights.org",
        "audience": "technology professionals and enthusiasts",
        "tone": "analytical and forward-thinking",
        "niche": "artificial intelligence",
        "goal": "explain complex AI concepts in accessible terms"
    }
]

# Sample keywords
SAMPLE_KEYWORDS = {
    "fitness-blog.com": {
        "focus_keyword": "beginner weight training program",
        "supporting_keywords": [
            "weight training for beginners",
            "strength training basics",
            "gym workout plan",
            "free weight exercises",
            "resistance training fundamentals",
            "weight lifting form"
        ],
        "cluster_target": "strength training",
        "internal_links": [
            "protein nutrition guide",
            "recovery techniques",
            "gym equipment essentials",
            "workout schedule planning"
        ]
    },
    "recipe-heaven.com": {
        "focus_keyword": "easy vegetarian dinner recipes",
        "supporting_keywords": [
            "quick vegetarian meals",
            "plant-based dinner ideas",
            "30-minute vegetarian recipes",
            "meat-free weeknight dinners",
            "simple vegetarian cooking",
            "vegetarian protein sources"
        ],
        "cluster_target": "vegetarian cooking",
        "internal_links": [
            "vegetarian meal prep",
            "plant-based protein guide",
            "seasonal vegetable guide",
            "vegetarian substitutes"
        ]
    },
    "tech-insights.org": {
        "focus_keyword": "artificial intelligence explained",
        "supporting_keywords": [
            "AI for beginners",
            "machine learning basics",
            "how AI works",
            "neural networks explained",
            "AI vs machine learning",
            "future of artificial intelligence"
        ],
        "cluster_target": "artificial intelligence",
        "internal_links": [
            "machine learning applications",
            "data science fundamentals",
            "ethical AI considerations",
            "AI in business"
        ]
    }
}

# Sample research data
SAMPLE_RESEARCH = {
    "fitness-blog.com": [
        {
            "excerpt": "According to a 2022 study in the Journal of Strength and Conditioning Research, beginners who followed a structured weight training program for 12 weeks saw an average strength increase of 30%.",
            "url": "https://journals.lww.com/nsca-jscr/abstract/2022/05000/effects_of_structured_training_on_novice_lifters.8.aspx",
            "type": "study"
        },
        {
            "excerpt": "The American College of Sports Medicine recommends that beginners start with 1-3 sets of 8-12 repetitions for each major muscle group, 2-3 times per week.",
            "url": "https://www.acsm.org/all-blog-posts/certification-blog/acsm-certified-blog/2019/07/31/resistance-training-for-health-and-fitness",
            "type": "fact"
        },
        {
            "excerpt": "\"The most common mistake I see with beginners is trying to lift too heavy too soon. Focus on form first, then gradually increase the weight,\" says certified strength coach Michael Johnson.",
            "url": "https://www.strengthcoachjournal.com/beginner-mistakes",
            "type": "quote"
        }
    ],
    "recipe-heaven.com": [
        {
            "excerpt": "A 2021 survey by the Vegetarian Resource Group found that 6% of Americans identify as vegetarian, with an additional 8% saying they follow a semi-vegetarian or flexitarian diet.",
            "url": "https://www.vrg.org/nutshell/Polls/2021_adults_veg.htm",
            "type": "statistic"
        },
        {
            "excerpt": "Legumes such as beans, lentils, and chickpeas are excellent sources of plant-based protein, providing approximately 15 grams of protein per cooked cup.",
            "url": "https://www.hsph.harvard.edu/nutritionsource/what-should-you-eat/protein/",
            "type": "fact"
        },
        {
            "excerpt": "\"The key to satisfying vegetarian meals is umami-rich ingredients like mushrooms, tomatoes, and fermented foods that provide depth of flavor,\" explains chef Linda Green.",
            "url": "https://www.vegetariancooking.com/umami-secrets",
            "type": "quote"
        }
    ],
    "tech-insights.org": [
        {
            "excerpt": "According to Stanford University's 2023 AI Index Report, investment in AI startups reached $91.9 billion in 2022, a 48% increase from 2021.",
            "url": "https://aiindex.stanford.edu/report/",
            "type": "statistic"
        },
        {
            "excerpt": "Machine learning is a subset of artificial intelligence that focuses on developing systems that learn from data without being explicitly programmed.",
            "url": "https://www.ibm.com/cloud/learn/machine-learning",
            "type": "definition"
        },
        {
            "excerpt": "\"The most significant risk of advanced AI isn't that it will become malevolent, but that it will become extremely competent at pursuing goals that aren't fully aligned with our own,\" states AI researcher Dr. Stuart Russell.",
            "url": "https://www.nature.com/articles/d41586-021-00530-0",
            "type": "quote"
        }
    ]
}

# Sample hooks
SAMPLE_HOOKS = {
    "fitness-blog.com": {
        "main_hook": "Discover the scientifically-backed weight training program that helped complete beginners increase their strength by 30% in just 12 weeks—without spending hours in the gym or risking injury.",
        "micro_hooks": [
            "The #1 mistake that sabotages beginner gains (and how to avoid it)",
            "Why 90% of gym newcomers quit within 3 months—and the simple mindset shift that keeps you consistent",
            "The 5 essential exercises that build more muscle in less time than complicated routines",
            "How to know exactly when to increase weight (without a personal trainer)",
            "The recovery secret elite athletes use that beginners completely overlook",
            "Why 'feeling the burn' might actually be slowing your progress",
            "The science-backed rep range that maximizes results for novice lifters"
        ]
    },
    "recipe-heaven.com": {
        "main_hook": "Transform your weeknight dinners with these 15-minute vegetarian recipes that even dedicated meat-eaters can't resist—using ingredients already hiding in your pantry.",
        "micro_hooks": [
            "The 'umami secret' that makes vegetarian meals taste satisfyingly rich",
            "How to create restaurant-quality vegetarian dishes without specialty ingredients",
            "The simple protein-pairing trick that keeps you full for hours",
            "Why most vegetarian recipes fail (and how these are different)",
            "The 3-ingredient flavor boost that transforms bland vegetables",
            "How to make vegetables the star without feeling like you're 'just eating sides'",
            "The meal-prep shortcut that turns one cooking session into 5 different dinners"
        ]
    },
    "tech-insights.org": {
        "main_hook": "Beyond the buzzwords: Here's what artificial intelligence actually is, how it's already affecting your daily life, and what you need to know before it transforms your career.",
        "micro_hooks": [
            "The counterintuitive way AI actually creates jobs instead of eliminating them",
            "Why most 'AI products' aren't using real AI at all (and how to spot the difference)",
            "The surprisingly simple concept behind neural networks that anyone can understand",
            "How AI makes decisions—and why it sometimes gets things catastrophically wrong",
            "The ethical blindspot even AI experts are overlooking",
            "Why the 'human vs. machine' narrative misses the most important point about AI",
            "The one skill that will remain valuable no matter how advanced AI becomes"
        ]
    }
}

def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())

def delete_all_data():
    """Delete all existing data from the database."""
    print("Deleting existing data...")
    
    # Delete in reverse order of dependencies
    tables = [
        "agent_status",
        "publishing_metadata",
        "editing_feedback",
        "headlines",
        "images",
        "hooks",
        "research",
        "content_sections",
        "keywords",
        "content_pieces",
        "strategic_plans"
    ]
    
    for table in tables:
        try:
            response = supabase.table(table).delete().execute()
            print(f"Deleted all records from {table}")
        except Exception as e:
            print(f"Error deleting from {table}: {e}")

def create_strategic_plans():
    """Create sample strategic plans."""
    print("\nCreating strategic plans...")
    plan_ids = {}
    
    for plan in STRATEGIC_PLANS:
        try:
            response = supabase.table("strategic_plans").insert(plan).execute()
            plan_id = response.data[0]["id"]
            domain = plan["domain"]
            plan_ids[domain] = plan_id
            print(f"Created strategic plan for {domain} with ID: {plan_id}")
        except Exception as e:
            print(f"Error creating strategic plan for {domain}: {e}")
    
    return plan_ids

def create_content_pieces(plan_ids):
    """Create sample content pieces for each strategic plan."""
    print("\nCreating content pieces...")
    content_ids = {}
    
    for domain, plan_id in plan_ids.items():
        # Create two content pieces for each domain
        for i in range(1, 3):
            content_data = {
                "strategic_plan_id": plan_id,
                "status": "draft",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            try:
                response = supabase.table("content_pieces").insert(content_data).execute()
                content_id = response.data[0]["id"]
                
                if domain not in content_ids:
                    content_ids[domain] = []
                
                content_ids[domain].append(content_id)
                print(f"Created content piece {i} for {domain} with ID: {content_id}")
            except Exception as e:
                print(f"Error creating content piece for {domain}: {e}")
    
    return content_ids

def create_keywords(content_ids):
    """Create sample keywords for each content piece."""
    print("\nCreating keywords...")
    
    for domain, ids in content_ids.items():
        keyword_data = SAMPLE_KEYWORDS.get(domain, {})
        
        if not keyword_data:
            continue
        
        for content_id in ids:
            # Add some variation for the second content piece
            if content_id == ids[1] and len(ids) > 1:
                focus_keyword = f"advanced {keyword_data['focus_keyword']}"
            else:
                focus_keyword = keyword_data["focus_keyword"]
            
            data = {
                "content_id": content_id,
                "focus_keyword": focus_keyword,
                "supporting_keywords": keyword_data["supporting_keywords"],
                "cluster_target": keyword_data["cluster_target"],
                "internal_links": keyword_data["internal_links"]
            }
            
            try:
                response = supabase.table("keywords").insert(data).execute()
                print(f"Created keywords for content ID: {content_id}")
            except Exception as e:
                print(f"Error creating keywords for content ID {content_id}: {e}")

def create_research(content_ids):
    """Create sample research data for each content piece."""
    print("\nCreating research data...")
    
    for domain, ids in content_ids.items():
        research_data = SAMPLE_RESEARCH.get(domain, [])
        
        if not research_data:
            continue
        
        for content_id in ids:
            for research in research_data:
                data = {
                    "content_id": content_id,
                    "excerpt": research["excerpt"],
                    "url": research["url"],
                    "type": research["type"],
                    "confidence": 0.9
                }
                
                try:
                    response = supabase.table("research").insert(data).execute()
                    print(f"Created research entry for content ID: {content_id}")
                except Exception as e:
                    print(f"Error creating research for content ID {content_id}: {e}")

def create_hooks(content_ids):
    """Create sample hooks for each content piece."""
    print("\nCreating hooks...")
    
    for domain, ids in content_ids.items():
        hook_data = SAMPLE_HOOKS.get(domain, {})
        
        if not hook_data:
            continue
        
        for content_id in ids:
            # Add some variation for the second content piece
            if content_id == ids[1] and len(ids) > 1:
                main_hook = f"Advanced guide: {hook_data['main_hook']}"
            else:
                main_hook = hook_data["main_hook"]
            
            data = {
                "content_id": content_id,
                "main_hook": main_hook,
                "micro_hooks": hook_data["micro_hooks"]
            }
            
            try:
                response = supabase.table("hooks").insert(data).execute()
                print(f"Created hooks for content ID: {content_id}")
            except Exception as e:
                print(f"Error creating hooks for content ID {content_id}: {e}")

def create_agent_tasks(content_ids):
    """Create sample agent tasks for each content piece."""
    print("\nCreating agent tasks...")
    
    # Define agents in execution order
    agents = ["seo-agent", "research-agent", "hook-agent", "writer-agent", 
              "flow-editor-agent", "line-editor-agent", "headline-agent", 
              "image-agent", "publisher-agent"]
    
    # For the first content piece of each domain, create all tasks with different statuses
    for domain, ids in content_ids.items():
        content_id = ids[0]
        
        for i, agent in enumerate(agents):
            # Set different statuses based on position
            if i == 0:
                status = "done"  # First agent (seo) is done
            elif i == 1:
                status = "processing"  # Second agent (research) is processing
            elif i == 2:
                status = "queued"  # Third agent (hook) is queued
            else:
                status = "queued"  # Rest are queued
            
            # Create task data
            task_data = {
                "agent": agent,
                "content_id": content_id,
                "status": status,
                "input": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Add sample output for completed tasks
            if status == "done":
                if agent == "seo-agent":
                    keyword_data = SAMPLE_KEYWORDS.get(domain, {})
                    task_data["output"] = {
                        "seo": {
                            "focus_keyword": keyword_data.get("focus_keyword", ""),
                            "supporting_keywords": keyword_data.get("supporting_keywords", []),
                            "cluster_target": keyword_data.get("cluster_target", ""),
                            "internal_links": keyword_data.get("internal_links", [])
                        }
                    }
            
            try:
                response = supabase.table("agent_status").insert(task_data).execute()
                print(f"Created {status} task for {agent} on content ID: {content_id}")
            except Exception as e:
                print(f"Error creating task for {agent} on content ID {content_id}: {e}")
        
        # For the second content piece, just create the first task (seo-agent)
        if len(ids) > 1:
            content_id = ids[1]
            task_data = {
                "agent": "seo-agent",
                "content_id": content_id,
                "status": "queued",
                "input": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            try:
                response = supabase.table("agent_status").insert(task_data).execute()
                print(f"Created queued task for seo-agent on content ID: {content_id}")
            except Exception as e:
                print(f"Error creating task for seo-agent on content ID {content_id}: {e}")

def main():
    """Main function to seed the database."""
    parser = argparse.ArgumentParser(description="Seed the database with test data")
    parser.add_argument("--reset", action="store_true", help="Delete existing data before inserting new data")
    args = parser.parse_args()
    
    print("WordPress Content Generator - Database Seed Script")
    print("=" * 50)
    
    if args.reset:
        delete_all_data()
    
    # Create data in the correct order
    plan_ids = create_strategic_plans()
    content_ids = create_content_pieces(plan_ids)
    create_keywords(content_ids)
    create_research(content_ids)
    create_hooks(content_ids)
    create_agent_tasks(content_ids)
    
    print("\nSeed data creation complete!")
    print(f"Created {len(plan_ids)} strategic plans")
    total_content = sum(len(ids) for ids in content_ids.values())
    print(f"Created {total_content} content pieces")

if __name__ == "__main__":
    main()
