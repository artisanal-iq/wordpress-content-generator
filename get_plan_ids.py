#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Connect to Supabase
supabase = create_client(url, key)

# Get strategic plans
response = supabase.table("strategic_plans").select("*").execute()

# Print each plan ID and domain
for plan in response.data:
    print(f"{plan['id']}: {plan['domain']} - {plan['niche']}")
