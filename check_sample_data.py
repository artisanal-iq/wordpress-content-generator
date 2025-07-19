#!/usr/bin/env python3
"""
Check Sample Data in Supabase Tables

This script checks the sample data in all Supabase tables.
"""

import os
import json
import sys
from dotenv import load_dotenv
from supabase import create_client

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Create and return a Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file{ENDC}")
        sys.exit(1)
    
    return create_client(url, key)

def display_table_data(supabase, table_name, limit=5):
    """Display data from a table."""
    try:
        response = supabase.table(table_name).select("*").limit(limit).execute()
        print(f"{BOLD}{table_name}{ENDC} ({len(response.data)} records):")
        
        if not response.data:
            print(f"  {YELLOW}No data found{ENDC}")
            return
        
        # Determine columns to display (skip large text fields)
        skip_columns = ["draft_text", "final_text"]
        sample_record = response.data[0]
        columns = [col for col in sample_record.keys() if col not in skip_columns]
        
        # Display each record
        for i, record in enumerate(response.data):
            print(f"\n  {BLUE}Record #{i+1}:{ENDC}")
            for col in columns:
                # Format the value nicely
                value = record.get(col)
                if isinstance(value, dict) or isinstance(value, list):
                    value = json.dumps(value)
                elif value is None:
                    value = f"{YELLOW}NULL{ENDC}"
                
                # Truncate long values
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                    
                print(f"    {col}: {value}")
    
    except Exception as e:
        print(f"  {RED}Error: {e}{ENDC}")

def main():
    print(f"{BOLD}WordPress Content Generator - Check Sample Data{ENDC}")
    print("=" * 60)
    
    try:
        # Connect to Supabase
        supabase = get_supabase_client()
        print(f"{GREEN}Connected to Supabase{ENDC}")
        
        # Check data in each table
        print("\n")
        display_table_data(supabase, "strategic_plans")
        print("\n")
        display_table_data(supabase, "content_pieces")
        print("\n")
        display_table_data(supabase, "keywords")
        print("\n")
        display_table_data(supabase, "agent_status")
        
        print(f"\n{GREEN}Data check complete!{ENDC}")
        
    except Exception as e:
        print(f"{RED}Error: {e}{ENDC}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
