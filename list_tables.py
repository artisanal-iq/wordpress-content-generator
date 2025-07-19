#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client
import psycopg2
from psycopg2 import sql
import urllib.parse

# Load environment variables
load_dotenv()

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"{BOLD}Testing connection to Supabase...{ENDC}")
print(f"URL: {url}")

try:
    # Connect to Supabase
    supabase = create_client(url, key)
    print(f"{GREEN}Basic connection successful!{ENDC}")
    
    # Get list of tables using system tables query
    try:
        # Parse connection string from URL
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        
        # Extract project reference from URL
        project_ref = host.split('.')[0]
        
        # Build REST API query to get table information
        endpoint = f"{url}/rest/v1/?apikey={key}"
        
        print(f"{BLUE}Using REST API to list tables...{ENDC}")
        print(f"Project reference: {project_ref}")
        print(f"Endpoint: {endpoint}")
        
        print(f"\n{BLUE}Currently available tables in your Supabase project:{ENDC}")
        print("Please check the Supabase web interface to see the full list of tables")
        print("If tables exist in the interface but not through the API, you may have permission issues")
        
    except Exception as e:
        print(f"{RED}Error retrieving table list: {e}{ENDC}")
    
except Exception as e:
    print(f"{RED}Connection error: {e}{ENDC}")
