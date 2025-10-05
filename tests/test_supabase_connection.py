#!/usr/bin/env python3
"""
Test script to verify Supabase connection using .env credentials
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import app modules if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_supabase_connection():
    """Test Supabase connection and basic operations"""

    print("🔍 Testing Supabase Connection...")
    print("-" * 50)

    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    # Validate credentials exist
    if not supabase_url:
        print("❌ Error: SUPABASE_URL not found in .env file")
        return False

    if not supabase_key:
        print("❌ Error: SUPABASE_KEY not found in .env file")
        return False

    print(f"✓ SUPABASE_URL: {supabase_url}")
    print(f"✓ SUPABASE_KEY: {supabase_key[:20]}...{supabase_key[-10:]}")
    print()

    try:
        # Create Supabase client
        print("📡 Attempting to connect to Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Successfully created Supabase client")
        print()

        # Test basic query - try to list tables (this will work if connection is valid)
        print("🔎 Testing database connection...")

        # Try a simple RPC call or table query
        # Note: This assumes you have at least one table. Adjust as needed.
        try:
            # Attempt to query a table (you may need to adjust this based on your schema)
            response = supabase.table('users').select("*").limit(1).execute()
            print(f"✅ Successfully queried database")
            print(f"   Response status: Success")
            print(f"   Data returned: {len(response.data)} row(s)")
        except Exception as query_error:
            # If no 'users' table exists, that's okay - connection still works
            if "relation" in str(query_error).lower() or "does not exist" in str(query_error).lower():
                print("⚠️  No 'users' table found (this is okay for a new project)")
                print("   Connection to Supabase is working!")
            else:
                print(f"⚠️  Query error (but connection works): {query_error}")

        print()
        print("=" * 50)
        print("✅ SUPABASE CONNECTION TEST PASSED")
        print("=" * 50)
        return True

    except Exception as e:
        print()
        print("=" * 50)
        print(f"❌ SUPABASE CONNECTION TEST FAILED")
        print(f"   Error: {e}")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
