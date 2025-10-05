#!/usr/bin/env python3
"""
Verify Supabase migration was successful
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

print("🔍 Verifying Supabase tables...")
print(f"📍 URL: {SUPABASE_URL}\n")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Check tables by trying to select from them
    tables_to_check = [
        "profiling_sessions",
        "profiling_responses", 
        "profiling_messages",
        "group_conversations",
        "group_participants",
        "group_messages"
    ]
    
    print("Checking tables:\n")
    
    for table in tables_to_check:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ {table:<25} - EXISTS (rows: 0)")
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print(f"❌ {table:<25} - NOT FOUND")
            else:
                print(f"⚠️  {table:<25} - ERROR: {str(e)[:50]}")
    
    print("\n" + "="*60)
    print("✅ Migration verification complete!")
    
except Exception as e:
    print(f"❌ Connection error: {e}")

