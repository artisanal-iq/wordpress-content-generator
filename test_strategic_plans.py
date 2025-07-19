#!/usr/bin/env python3

import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Get credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"{BOLD}Testing strategic_plans table in Supabase...{ENDC}")
print(f"URL: {url}")

try:
    # Connect to Supabase
    supabase = create_client(url, key)
    
    # Read existing data
    response = supabase.table("strategic_plans").select("*").execute()
    print(f"{BLUE}Current records in strategic_plans: {len(response.data)}{ENDC}")
    
    for i, record in enumerate(response.data):
        print(f"  Record {i+1}: {record['domain']} - {record['niche']} - {record['goal']}")
    
    # Insert a new test record
    new_record = {
        "domain": f"test-domain-{uuid.uuid4().hex[:8]}.com",
        "audience": "tech professionals",
        "tone": "professional",
        "niche": "cloud computing",
        "goal": "educate about cloud security"
    }
    
    insert_response = supabase.table("strategic_plans").insert(new_record).execute()
    
    if insert_response.data:
        print(f"{GREEN}Successfully inserted a new record!{ENDC}")
        print(f"  New record ID: {insert_response.data[0]['id']}")
        print(f"  Domain: {insert_response.data[0]['domain']}")
    else:
        print(f"{RED}Failed to insert a new record{ENDC}")
    
    # Read the updated data
    response = supabase.table("strategic_plans").select("*").execute()
    print(f"{BLUE}Updated records in strategic_plans: {len(response.data)}{ENDC}")
    
    for i, record in enumerate(response.data):
        print(f"  Record {i+1}: {record['domain']} - {record['niche']} - {record['goal']}")
    
except Exception as e:
    print(f"{RED}Error: {e}{ENDC}")
