#!/usr/bin/env python3
"""
Run Supabase migration for group conversations
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY not found in .env")
    exit(1)

# Create client
supabase = create_client(supabase_url, supabase_key)

# Read migration
migration_path = Path(__file__).parent / "supabase" / "migrations" / "001_group_conversations.sql"
with open(migration_path, 'r') as f:
    migration_sql = f.read()

print("🚀 Running migration: 001_group_conversations.sql")
print("-" * 60)

try:
    # Execute migration
    # Note: Supabase Python client doesn't have direct SQL execution
    # You need to use the REST API or use supabase CLI

    print("⚠️  Python Supabase client doesn't support raw SQL execution.")
    print("\n📋 Options to run migration:\n")

    print("1. **Supabase Dashboard (Recommended):**")
    print(f"   - Go to: {supabase_url.replace('supabase.co', 'supabase.com/dashboard/project')}")
    print("   - Navigate to: SQL Editor")
    print(f"   - Copy contents from: {migration_path}")
    print("   - Execute the SQL\n")

    print("2. **Supabase CLI:**")
    print("   supabase link --project-ref <your-project-ref>")
    print("   supabase db push\n")

    print("3. **Manual psql:**")
    print("   Get connection string from Supabase dashboard")
    print(f"   psql <connection-string> < {migration_path}\n")

    print("-" * 60)
    print("📄 Migration SQL preview (first 500 chars):")
    print(migration_sql[:500] + "...\n")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
