#!/usr/bin/env python3
"""
Create test user with completed profiling session
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Initialize Supabase
from app.services.supabase_service import init_supabase
init_supabase()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

TEST_USER_ID = "test-user-123-with-profile"

print("Creating test user with completed profiling session...")
print(f"User ID: {TEST_USER_ID}\n")

# Create completed profiling session
try:
    result = supabase.table("profiling_sessions").insert({
        "session_id": "prof_test_user_123",
        "user_id": TEST_USER_ID,
        "status": "completed",
        "current_question_index": 13,
        "profile_completeness": 1.0,
        "completed_at": "2025-10-04T18:00:00+00:00"
    }).execute()
    
    print("✅ Created completed profiling session")
    print(f"   Session ID: prof_test_user_123")
    print(f"   Status: completed")
    print(f"   Completeness: 100%")
    
except Exception as e:
    if "duplicate" in str(e).lower():
        print("⚠️  Session already exists - updating...")
        supabase.table("profiling_sessions").update({
            "status": "completed",
            "profile_completeness": 1.0,
            "completed_at": "2025-10-04T18:00:00+00:00"
        }).eq("session_id", "prof_test_user_123").execute()
        print("✅ Updated existing session")
    else:
        print(f"❌ Error: {e}")

print("\n" + "="*80)
print("Test User Created!")
print("="*80)
print(f"\nUser ID: {TEST_USER_ID}")
print("\nThis user has a COMPLETED profiling session.")
print("Frontend should SKIP onboarding for this user.\n")
print("Test with:")
print(f'  curl "http://localhost:8000/api/profiling/status" \\')
print(f'    -H "Authorization: Bearer <token_with_user_id={TEST_USER_ID}>"')
print("\nExpected response:")
print("""  {
    "has_completed_profiling": true,
    "should_skip_onboarding": true,
    "profile_completeness": 100,
    "last_session_id": "prof_test_user_123"
  }
""")

