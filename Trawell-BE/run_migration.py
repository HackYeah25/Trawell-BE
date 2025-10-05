#!/usr/bin/env python3
"""
Run Supabase migrations
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    sys.exit(1)

print(f"🔗 Supabase URL: {SUPABASE_URL}")
print(f"🔑 Service Key: {SUPABASE_SERVICE_KEY[:20]}...")

# Get migration files
migrations_dir = Path(__file__).parent / "supabase" / "migrations"
migration_files = sorted(migrations_dir.glob("*.sql"))

if not migration_files:
    print("⚠️  No migration files found")
    sys.exit(0)

print(f"\n📁 Found {len(migration_files)} migration file(s):\n")

for migration_file in migration_files:
    print(f"   • {migration_file.name}")

print("\n" + "="*60)
print("📋 MANUAL MIGRATION REQUIRED")
print("="*60)
print("""
The Supabase Python client doesn't support direct SQL execution.
Please run migrations manually using one of these methods:

METHOD 1: Supabase SQL Editor (Recommended)
────────────────────────────────────────────
1. Go to: https://supabase.com/dashboard/project/khuuhyyeyajujqdpzqyz/sql/new

2. Copy & paste SQL from each file:
""")

for i, migration_file in enumerate(migration_files, 1):
    print(f"\n   Step {i}: {migration_file.name}")
    print(f"   File: {migration_file}")

print("""
3. Click "Run" for each migration

METHOD 2: Supabase CLI
────────────────────────────────────────────
$ supabase link --project-ref khuuhyyeyajujqdpzqyz
$ supabase db push

METHOD 3: Direct PostgreSQL Connection
────────────────────────────────────────────
Use the connection string from Supabase dashboard > Project Settings > Database
Then run: psql <connection_string> < migration_file.sql
""")

# Show SQL content if requested
if len(sys.argv) > 1 and sys.argv[1] == "--show-sql":
    for migration_file in migration_files:
        print("\n" + "="*60)
        print(f"SQL: {migration_file.name}")
        print("="*60 + "\n")
        with open(migration_file, 'r', encoding='utf-8') as f:
            print(f.read())
        print("\n")

print("\n💡 Run with --show-sql flag to see SQL content")
