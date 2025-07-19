#!/usr/bin/env python3
"""
Create Tables Using Admin Privileges

This script uses the service role key to create tables in Supabase.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import json

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Load environment variables
load_dotenv()

def get_admin_supabase_client():
    """Create and return a Supabase client with admin privileges."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin privileges
    
    if not url or not key:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file{ENDC}")
        sys.exit(1)
    
    print(f"Connecting to {url} with service role key")
    return create_client(url, key)

def check_available_tables(supabase):
    """Check what tables are currently available."""
    try:
        # Query for strategic_plans to verify connection
        response = supabase.table("strategic_plans").select("count", count="exact").execute()
        print(f"{GREEN}Successfully connected to strategic_plans table{ENDC}")
        print(f"Found {response.count} records")
        
        print(f"\n{BLUE}Checking for other tables...{ENDC}")
        tables_to_check = ["content_pieces", "keywords", "agent_status"]
        
        for table in tables_to_check:
            try:
                response = supabase.table(table).select("count", count="exact").execute()
                print(f"  {table}: {GREEN}exists{ENDC} ({response.count} rows)")
            except Exception as e:
                print(f"  {table}: {RED}does not exist{ENDC}")
    
    except Exception as e:
        print(f"{RED}Error checking tables: {e}{ENDC}")

def create_tables(supabase):
    """Create necessary tables using direct SQL."""
    print(f"\n{BLUE}Creating tables...{ENDC}")
    
    # Table creation SQL
    tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS public.content_pieces (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            strategic_plan_id UUID REFERENCES public.strategic_plans(id),
            title TEXT,
            slug TEXT,
            status TEXT NOT NULL DEFAULT 'draft',
            draft_text TEXT,
            final_text TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS public.keywords (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            content_id UUID REFERENCES public.content_pieces(id) ON DELETE CASCADE,
            focus_keyword TEXT NOT NULL,
            supporting_keywords TEXT[] DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS public.agent_status (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            agent TEXT NOT NULL,
            content_id UUID REFERENCES public.content_pieces(id) ON DELETE CASCADE,
            input JSONB DEFAULT '{}',
            output JSONB DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'queued',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    # Try different methods of executing SQL
    try:
        # Method 1: Using RPC with SQL
        for i, sql in enumerate(tables_sql):
            table_name = sql.split("CREATE TABLE IF NOT EXISTS public.")[1].split(" ")[0]
            print(f"Creating {table_name}...")
            
            try:
                # First try directly using a raw PostgreSQL query
                response = supabase.postgrest.schema("public").execute(sql)
                print(f"  {GREEN}Table created successfully (Method 1){ENDC}")
            except Exception as e1:
                print(f"  {YELLOW}Method 1 failed: {e1}{ENDC}")
                
                try:
                    # Try using the pg_execute RPC function if available
                    response = supabase.rpc("pg_execute", {"command": sql}).execute()
                    print(f"  {GREEN}Table created successfully (Method 2){ENDC}")
                except Exception as e2:
                    print(f"  {YELLOW}Method 2 failed: {e2}{ENDC}")
                    
                    try:
                        # Try using a custom RPC function (if you've created one)
                        response = supabase.rpc("execute_sql", {"sql": sql}).execute()
                        print(f"  {GREEN}Table created successfully (Method 3){ENDC}")
                    except Exception as e3:
                        print(f"  {RED}Failed to create table using all methods{ENDC}")
                        print(f"  Error details: {e1}, {e2}, {e3}")
    
    except Exception as e:
        print(f"{RED}Error executing SQL: {e}{ENDC}")
        print("This suggests that direct SQL execution might not be allowed.")
        print("Try creating tables through the Supabase dashboard SQL Editor.")

def main():
    print(f"{BOLD}WordPress Content Generator - Create Tables with Admin Privileges{ENDC}")
    print("=" * 60)
    
    try:
        # Get admin Supabase client
        supabase = get_admin_supabase_client()
        
        # Check what tables are available
        check_available_tables(supabase)
        
        # Attempt to create tables
        create_tables(supabase)
        
        # Check tables again to see if they were created
        print(f"\n{BLUE}Checking if tables were created...{ENDC}")
        check_available_tables(supabase)
        
    except Exception as e:
        print(f"{RED}Error: {e}{ENDC}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
