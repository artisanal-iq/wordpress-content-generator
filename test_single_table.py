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

print(f"{BOLD}Testing connection to Supabase...{ENDC}")
print(f"URL: {url}")

# Connect to Supabase
supabase = create_client(url, key)

# Test strategic_plans table
try:
    response = supabase.table("strategic_plans").select("*").execute()
    print(f"{GREEN}Successfully connected to strategic_plans table!{ENDC}")
    print(f"Found {len(response.data)} records")
    
    # Show the first record
    if response.data:
        print("\nFirst record:")
        for key, value in response.data[0].items():
            print(f"- {key}: {value}")
            
except Exception as e:
    print(f"{RED}Error: {e}{ENDC}")
