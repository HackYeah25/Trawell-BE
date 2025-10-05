#!/usr/bin/env python3
"""
Push seed data to Supabase using REST API
"""
import os
import requests
from pathlib import Path

# Read seed SQL file
seed_file = Path(__file__).parent / "Trawell-BE/supabase/seeds/001_test_user_profile.sql"
with open(seed_file, 'r') as f:
    sql_content = f.read()

# Get Supabase credentials from .env
env_file = Path(__file__).parent / "Trawell-BE/.env"
env_vars = {}
with open(env_file, 'r') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key] = value

supabase_url = env_vars.get('SUPABASE_URL')
supabase_key = env_vars.get('SUPABASE_KEY')  # Service role key needed for direct SQL

if not supabase_url or not supabase_key:
    print("ERROR: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

print(f"Supabase URL: {supabase_url}")
print(f"Executing seed file: {seed_file}")
print("=" * 60)

# Note: We can't execute arbitrary SQL via REST API with anon key
# We need to use the service_role key or direct database connection

print("\nOPTION 1: Use Supabase Dashboard SQL Editor")
print("-" * 60)
print(f"1. Go to: https://supabase.com/dashboard/project/khuuhyyeyajujqdpzqyz/sql")
print(f"2. Copy the contents of: {seed_file}")
print("3. Paste and run in the SQL Editor")
print("")

print("\nOPTION 2: Use psql with connection string")
print("-" * 60)
print("Run this command (replace [PASSWORD] with your DB password):")
print("")
print(f"psql 'postgresql://postgres:[PASSWORD]@db.khuuhyyeyajujqdpzqyz.supabase.co:5432/postgres' -f {seed_file}")
print("")

print("\nOPTION 3: Copy SQL content to clipboard")
print("-" * 60)
try:
    import pyperclip
    pyperclip.copy(sql_content)
    print("✅ SQL content copied to clipboard!")
    print("Paste it into Supabase SQL Editor")
except ImportError:
    print("Install pyperclip to auto-copy: pip install pyperclip")
    print("\nSQL Content:")
    print("=" * 60)
    print(sql_content[:500] + "\n... (truncated)")

print("")
print("After running the seed:")
print("  - Test user ID: a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
print("  - Test endpoint: http://localhost:8000/api/profiling/status")
