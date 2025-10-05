#!/usr/bin/env python3
"""
Test /api/profiling/status endpoint
"""
import requests

# Test 1: Anonymous user (no auth)
print("="*80)
print("Test 1: Anonymous User (No Authentication)")
print("="*80)

response = requests.get("http://localhost:8000/api/profiling/status")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test 2: Simulate user with completed session
# We'll create a mock test by checking our existing session
print("="*80)
print("Test 2: Check existing completed session")
print("="*80)

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Check what sessions we have
sessions = supabase.table("profiling_sessions").select("*").eq(
    "status", "completed"
).execute()

if sessions.data:
    print(f"Found {len(sessions.data)} completed session(s):\n")
    for session in sessions.data:
        print(f"Session ID: {session['session_id']}")
        print(f"User ID: {session['user_id']}")
        print(f"Completeness: {session['profile_completeness'] * 100:.0f}%")
        print(f"Completed: {session.get('completed_at')}")
        
        if session['user_id']:
            print(f"\n✅ This user ({session['user_id']}) SHOULD SKIP onboarding")
            print(f"   because they have completed profiling session: {session['session_id']}")
        else:
            print(f"\n⚠️  This is anonymous session (no user_id)")
        print()
else:
    print("No completed sessions found")

print("\n" + "="*80)
print("Frontend Integration")
print("="*80)
print("""
When user logs in, frontend should:

1. Call GET /api/profiling/status
   
2. Check response.should_skip_onboarding:
   
   if (response.should_skip_onboarding === true) {
     // User has completed profiling - go to main app
     router.push('/brainstorm');
   } else if (response.status === 'in_progress') {
     // Resume incomplete profiling
     router.push(`/profiling/resume/${response.last_session_id}`);
   } else {
     // New user - start profiling
     router.push('/profiling/start');
   }

3. Example responses:

   Completed profiling:
   {
     "has_completed_profiling": true,
     "should_skip_onboarding": true,
     "profile_completeness": 100,
     "last_session_id": "prof_test_complete"
   }
   
   In progress:
   {
     "has_completed_profiling": false,
     "should_skip_onboarding": false,
     "profile_completeness": 45,
     "last_session_id": "prof_xyz123",
     "status": "in_progress"
   }
   
   New user:
   {
     "has_completed_profiling": false,
     "should_skip_onboarding": false,
     "profile_completeness": 0,
     "last_session_id": null
   }
""")

