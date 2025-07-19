#!/usr/bin/env python3
"""
Supabase Connection Test Script for WordPress Content Generator

This script tests the connection to your Supabase project and runs simple queries
to verify that the database schema is correctly set up.

Usage:
    python test_supabase.py [--verbose]
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Any, Optional

import dotenv
from supabase import create_client, Client

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

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

def load_env_vars() -> Dict[str, Optional[str]]:
    """Load environment variables and return Supabase credentials."""
    # Try to load .env file
    dotenv.load_dotenv()
    
    # Get Supabase credentials
    credentials = {
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_KEY"),
        "service_key": os.getenv("SUPABASE_SERVICE_KEY")
    }
    
    return credentials

def connect_to_supabase(url: str, key: str) -> Client:
    """Create and return a Supabase client."""
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    return create_client(url, key)

def test_connection(supabase: Client) -> bool:
    """Test basic connection to Supabase."""
    try:
        # Simple query to test connection
        response = supabase.table("strategic_plans").select("count", count="exact").limit(1).execute()
        return True
    except Exception as e:
        print(f"{RED}Connection error: {e}{ENDC}")
        return False

def test_tables(supabase: Client, verbose: bool = False) -> Dict[str, bool]:
    """Test if the required tables exist."""
    required_tables = [
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
    
    results = {}
    
    for table in required_tables:
        try:
            response = supabase.table(table).select("count", count="exact").limit(1).execute()
            count = response.count
            results[table] = True
            
            if verbose:
                print(f"  {table}: {GREEN}OK{ENDC} ({count} rows)")
        except Exception as e:
            results[table] = False
            if verbose:
                print(f"  {table}: {RED}ERROR{ENDC} ({str(e)})")
    
    return results

def run_sample_queries(supabase: Client, verbose: bool = False) -> Dict[str, Any]:
    """Run sample queries on the database."""
    results = {}
    
    # Query strategic plans
    try:
        response = supabase.table("strategic_plans").select("*").limit(5).execute()
        results["strategic_plans"] = {
            "success": True,
            "count": len(response.data),
            "data": response.data if verbose else None
        }
    except Exception as e:
        results["strategic_plans"] = {
            "success": False,
            "error": str(e)
        }
    
    # Query content pieces
    try:
        response = supabase.table("content_pieces").select("*").limit(5).execute()
        results["content_pieces"] = {
            "success": True,
            "count": len(response.data),
            "data": response.data if verbose else None
        }
    except Exception as e:
        results["content_pieces"] = {
            "success": False,
            "error": str(e)
        }
    
    # Query agent status
    try:
        response = supabase.table("agent_status").select("*").limit(5).execute()
        results["agent_status"] = {
            "success": True,
            "count": len(response.data),
            "data": response.data if verbose else None
        }
    except Exception as e:
        results["agent_status"] = {
            "success": False,
            "error": str(e)
        }
    
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Supabase connection")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    args = parser.parse_args()
    
    print(f"\n{BOLD}WordPress Content Generator - Supabase Connection Test{ENDC}")
    print("=" * 60)
    
    # Load environment variables
    credentials = load_env_vars()
    
    if not credentials["url"] or not credentials["key"]:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file{ENDC}")
        print(f"{YELLOW}Tip: Copy .env.example to .env and fill in your Supabase credentials{ENDC}")
        return 1
    
    print(f"Supabase URL: {credentials['url']}")
    
    try:
        # Connect to Supabase
        start_time = time.time()
        supabase = connect_to_supabase(credentials["url"], credentials["key"])
        connection_time = time.time() - start_time
        print_status("Connection to Supabase", "OK", args.verbose, f"Connected in {connection_time:.2f}s")
        
        # Test tables
        print("\nChecking required tables:")
        table_results = test_tables(supabase, args.verbose)
        
        missing_tables = [table for table, exists in table_results.items() if not exists]
        if missing_tables:
            print_status(f"Tables check ({len(table_results) - len(missing_tables)}/{len(table_results)})", "WARNING", 
                        True, f"Missing tables: {', '.join(missing_tables)}")
        else:
            print_status(f"Tables check ({len(table_results)}/{len(table_results)})", "OK")
        
        # Run sample queries
        print("\nRunning sample queries:")
        query_results = run_sample_queries(supabase, args.verbose)
        
        for table, result in query_results.items():
            if result["success"]:
                print_status(f"Query {table}", "OK", args.verbose, f"Found {result['count']} rows")
            else:
                print_status(f"Query {table}", "ERROR", args.verbose, result["error"])
        
        # Summary
        print("\n" + "=" * 60)
        all_tables_ok = all(table_results.values())
        all_queries_ok = all(result["success"] for result in query_results.values())
        
        if all_tables_ok and all_queries_ok:
            print(f"\n{GREEN}✅ All tests passed! Your Supabase connection is working correctly.{ENDC}")
        else:
            print(f"\n{YELLOW}⚠️ Some tests failed. Please check the issues above.{ENDC}")
        
        return 0
        
    except Exception as e:
        print(f"{RED}Error: {e}{ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
