#!/usr/bin/env python3
"""
Demo: How onboarding skip works with profiling_sessions
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("="*90)
print("ONBOARDING SKIP LOGIC - Demo")
print("="*90)

print("""
CORE LOGIC:
-----------
1. User logs in → Frontend calls GET /api/profiling/status

2. Backend checks profiling_sessions table:
   - Query: WHERE user_id = {logged_in_user} AND status = 'completed'
   
3. If FOUND completed session:
   → should_skip_onboarding = TRUE
   → Redirect to /brainstorm (main app)
   
4. If NOT FOUND:
   → should_skip_onboarding = FALSE
   → Start profiling questionnaire


CURRENT DATABASE STATE:
""")

# Show all sessions
all_sessions = supabase.table("profiling_sessions").select("*").execute()

print(f"\n📊 Total profiling sessions in database: {len(all_sessions.data)}\n")

for i, session in enumerate(all_sessions.data, 1):
    print(f"Session #{i}:")
    print(f"  ID: {session['session_id']}")
    print(f"  User ID: {session['user_id'] or 'Anonymous'}")
    print(f"  Status: {session['status']}")
    print(f"  Completeness: {session['profile_completeness'] * 100:.0f}%")
    
    if session['status'] == 'completed' and session['user_id']:
        print(f"  ✅ This user WILL SKIP onboarding!")
    elif session['status'] == 'completed' and not session['user_id']:
        print(f"  ⚠️  Anonymous - needs user_id to skip")
    elif session['status'] == 'in_progress':
        print(f"  🔄 In progress - can resume")
    
    print()

print("="*90)
print("IMPLEMENTATION SUMMARY:")
print("="*90)
print("""
✅ We DON'T need user_profiles table for skip logic
✅ We ONLY check profiling_sessions.status = 'completed'  
✅ Works as long as session has user_id set

When user completes profiling via WebSocket:
1. Session status → 'completed' ✓
2. Session saved to Supabase ✓ (via save_session_to_database)
3. Next login → /status returns should_skip_onboarding=true ✓

FRONTEND CODE:
--------------
async function checkOnboardingStatus() {
  const response = await fetch('/api/profiling/status', {
    headers: { 'Authorization': `Bearer ${userToken}` }
  });
  
  const data = await response.json();
  
  if (data.should_skip_onboarding) {
    // User completed profiling - go to main app
    router.push('/brainstorm');
  } else if (data.status === 'in_progress') {
    // Resume incomplete session
    router.push(`/profiling/resume/${data.last_session_id}`);
  } else {
    // New user - start profiling
    router.push('/profiling/start');
  }
}
""")

print("\n" + "="*90)

