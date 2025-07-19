#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Load environment variables
load_dotenv()

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file{ENDC}")
    sys.exit(1)

print(f"{BOLD}Testing Supabase connection...{ENDC}")
print(f"URL: {url}")

try:
    # Connect to Supabase
    supabase = create_client(url, key)
    
    # Try a simple query
    response = supabase.table("strategic_plans").select("*").limit(5).execute()
    
    print(f"{GREEN}Connection successful!{ENDC}")
    print(f"Found {len(response.data)} strategic plans")
    
except Exception as e:
    print(f"{RED}Error: {e}{ENDC}")
    print("Have you created the tables using the SQL script?")
    print("Go to the Supabase dashboard, SQL Editor, and run the schema script")
    sys.exit(1)

print("\nAvailable tables:")
tables = [
    "strategic_plans",
    "content_pieces",
    "keywords",
    "agent_status"
]

for table in tables:
    try:
        response = supabase.table(table).select("count", count="exact").execute()
        print(f"- {table}: {GREEN}OK{ENDC} ({response.count} rows)")
    except Exception as e:
        print(f"- {table}: {RED}ERROR{ENDC}")

print(f"\n{BOLD}Test completed. You're ready to use Supabase with the WordPress Content Generator!{ENDC}")
