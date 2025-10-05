#!/usr/bin/env python3
"""
Create user with properly completed profiling session (with valid UUID)
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import uuid

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Generate proper UUID
TEST_USER_UUID = str(uuid.uuid4())
TEST_SESSION_ID = f"prof_{uuid.uuid4().hex[:12]}"

print("="*80)
print("Creating Test User with Completed Profiling")
print("="*80)
print(f"\nUser ID (UUID): {TEST_USER_UUID}")
print(f"Session ID: {TEST_SESSION_ID}\n")

try:
    # 1. Create profiling session with user_id
    supabase.table("profiling_sessions").insert({
        "session_id": TEST_SESSION_ID,
        "user_id": TEST_USER_UUID,
        "status": "completed",
        "current_question_index": 13,
        "profile_completeness": 1.0,
        "completed_at": "2025-10-04T20:00:00+00:00",
        "created_at": "2025-10-04T19:00:00+00:00",
        "updated_at": "2025-10-04T20:00:00+00:00"
    }).execute()
    
    print("✅ Created completed profiling session")
    
    # 2. Add some responses
    supabase.table("profiling_responses").insert({
        "session_id": TEST_SESSION_ID,
        "question_id": "traveler_type",
        "user_answer": "I'm an active explorer who loves adventures",
        "validation_status": "sufficient",
        "extracted_value": "explorer"
    }).execute()
    
    print("✅ Added sample responses")
    
    # 3. Add some messages
    supabase.table("profiling_messages").insert({
        "session_id": TEST_SESSION_ID,
        "role": "assistant",
        "content": "Welcome! Let's discover your travel style."
    }).execute()
    
    print("✅ Added conversation messages")
    
    print("\n" + "="*80)
    print("✅ SUCCESS! Test user created")
    print("="*80)
    
    print(f"""
Test this user:

User UUID: {TEST_USER_UUID}
Session ID: {TEST_SESSION_ID}

To test /api/profiling/status endpoint, you would need to:
1. Create a JWT token with user_id = {TEST_USER_UUID}
2. Call GET /api/profiling/status with Authorization header

Expected response:
{{
  "has_completed_profiling": true,
  "should_skip_onboarding": true,
  "profile_completeness": 100.0,
  "last_session_id": "{TEST_SESSION_ID}",
  "user_id": "{TEST_USER_UUID}"
}}

Save this info for testing!
    """)
    
    # Save to file for reference
    with open("test_user_info.txt", "w") as f:
        f.write(f"TEST_USER_UUID={TEST_USER_UUID}\n")
        f.write(f"TEST_SESSION_ID={TEST_SESSION_ID}\n")
    
    print("💾 Saved to test_user_info.txt")
    
except Exception as e:
    print(f"❌ Error: {e}")

