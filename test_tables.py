#!/usr/bin/env python3
"""
Table Existence Test Script for WordPress Content Generator

This script tests the connection to your Supabase project and checks if all 
required tables for the WordPress Content Generator have been created.

Usage:
    python test_tables.py [--verbose]
"""

import argparse
import os
import sys
from typing import Dict, List, Any

from dotenv import load_dotenv
from supabase import create_client

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Required tables based on schema
REQUIRED_TABLES = [
    "strategic_plans",
    "content_pieces",
    "keywords",
    "research",
    "hooks",
    "images",
    "headlines",
    "editing_feedback",
    "publishing_metadata",
    "agent_status",
    "content_sections"
]

def print_status(message: str, status: str, verbose: bool = False, details: str = None):
    """Print a status message with color coding."""
    status_color = {
        "OK": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "INFO": BLUE
    }.get(status, "")
    
    print(f"{message:<50} [{status_color}{status}{ENDC}]")
    
    if verbose and details:
        print(f"  {details}")

def check_table_exists(supabase, table_name: str, verbose: bool = False) -> bool:
    """Check if a table exists by running a simple query."""
    try:
        # Try to select a single row with count
        response = supabase.table(table_name).select("count", count="exact").limit(1).execute()
        count = response.count
        
        if verbose:
            print(f"  Table '{table_name}': {GREEN}exists{ENDC} ({count} rows)")
        
        return True
    except Exception as e:
        if verbose:
            error_msg = str(e)
            if "does not exist" in error_msg:
                print(f"  Table '{table_name}': {RED}does not exist{ENDC}")
            else:
                print(f"  Table '{table_name}': {RED}error{ENDC} - {error_msg}")
        
        return False

def main():
    """Main function to check table existence."""
    parser = argparse.ArgumentParser(
        description="Check if required tables exist in Supabase"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information"
    )
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file{ENDC}")
        return 1
    
    print(f"\n{BOLD}WordPress Content Generator - Supabase Table Check{ENDC}")
    print("=" * 60)
    print(f"Supabase URL: {url}")
    
    try:
        # Connect to Supabase
        supabase = create_client(url, key)
        print_status("Connection to Supabase", "OK")
        
        # Check each required table
        print(f"\n{BOLD}Checking required tables:{ENDC}")
        existing_tables = []
        missing_tables = []
        
        for table in REQUIRED_TABLES:
            exists = check_table_exists(supabase, table, args.verbose)
            if exists:
                existing_tables.append(table)
            else:
                missing_tables.append(table)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"{BOLD}Summary:{ENDC}")
        print(f"  Tables found: {len(existing_tables)}/{len(REQUIRED_TABLES)}")
        
        if missing_tables:
            print(f"\n{YELLOW}Missing tables:{ENDC}")
            for table in missing_tables:
                print(f"  - {table}")
            
            print(f"\n{YELLOW}To create the missing tables, run the SQL script:{ENDC}")
            print("  1. Go to Supabase SQL Editor")
            print("  2. Create a new query")
            print("  3. Copy the SQL from supabase_schema.sql")
            print("  4. Run the script")
        else:
            print(f"\n{GREEN}All required tables exist! Your database is ready.{ENDC}")
        
        return 0
    
    except Exception as e:
        print(f"{RED}Error connecting to Supabase: {e}{ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
