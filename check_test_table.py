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

try:
    # Connect to Supabase
    supabase = create_client(url, key)
    
    # Test if test_table exists
    try:
        response = supabase.table("test_table").select("*").execute()
        print(f"{GREEN}Successfully connected to test_table!{ENDC}")
        print(f"Found {len(response.data)} records")
        
        # Show the records
        if response.data:
            print("\nRecords:")
            for record in response.data:
                print(f"- {record['id']}: {record['name']} (created: {record['created_at']})")
                
    except Exception as e:
        print(f"{RED}Error accessing test_table: {e}{ENDC}")
        
except Exception as e:
    print(f"{RED}Connection error: {e}{ENDC}")
