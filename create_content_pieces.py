#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Get credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"{BOLD}Creating content_pieces table in Supabase...{ENDC}")
print(f"URL: {url}")

try:
    # Connect to Supabase
    supabase = create_client(url, key)
    
    # Try to get strategic_plans table to confirm it exists
    response = supabase.table("strategic_plans").select("id").limit(1).execute()
    print(f"{GREEN}Successfully connected to strategic_plans table!{ENDC}")
    
    # Use Supabase REST API to create the content_pieces table
    # Note: This is not the preferred way, but we're trying a direct approach
    try:
        # We'll use a REST POST request to the rpc endpoint
        response = supabase.rpc(
            "create_content_pieces",
            {
                "query": """
                CREATE TABLE IF NOT EXISTS content_pieces (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    strategic_plan_id UUID REFERENCES strategic_plans(id),
                    title TEXT,
                    slug TEXT,
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                """
            }
        ).execute()
        print(f"{GREEN}Content pieces table created successfully!{ENDC}")
    except Exception as e:
        print(f"{RED}Error creating content_pieces table: {e}{ENDC}")
        print("You'll need to create the tables via the Supabase SQL Editor or Table Editor interface.")
        
except Exception as e:
    print(f"{RED}Connection error: {e}{ENDC}")
