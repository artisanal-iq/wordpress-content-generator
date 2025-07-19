#!/usr/bin/env python3
"""
Script to list available tables in Supabase

This script tries to list all available tables that are accessible
using the current Supabase credentials.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"{BOLD}Checking available tables in Supabase...{ENDC}")
print(f"URL: {url}")

# Make a request to list all tables using the REST API
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

try:
    # Request to get schema information
    # Note: This is a direct HTTP request to the Supabase API
    tables_endpoint = f"{url}/rest/v1/"
    response = requests.get(tables_endpoint, headers=headers)
    
    if response.status_code == 200:
        print(f"{GREEN}Successfully retrieved schema information!{ENDC}")
        print(f"Response: {response.text}")
    else:
        print(f"{RED}Error retrieving schema information. Status code: {response.status_code}{ENDC}")
        print(f"Response: {response.text}")
    
    # Try to access known tables
    tables_to_check = ["strategic_plans", "content_pieces", "keywords", "agent_status"]
    print(f"\n{BOLD}Checking specific tables:{ENDC}")
    
    for table in tables_to_check:
        table_endpoint = f"{url}/rest/v1/{table}?select=count"
        response = requests.get(table_endpoint, headers=headers)
        
        if response.status_code == 200:
            print(f"  {table}: {GREEN}accessible{ENDC}")
        else:
            print(f"  {table}: {RED}not accessible{ENDC} (Status: {response.status_code})")
    
    print(f"\n{YELLOW}If you see 'not accessible' for tables that should exist, you may need to:{ENDC}")
    print("1. Check your Supabase permissions")
    print("2. Make sure Row Level Security is configured correctly")
    print("3. Use the Supabase web interface to create the tables")
    
except Exception as e:
    print(f"{RED}Error: {e}{ENDC}")
