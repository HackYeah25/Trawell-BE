#!/usr/bin/env python3
"""
Test complete profiling flow and check saved data
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 80)
print("PROFILING SESSIONS - Summary")
print("=" * 80)

# Get all profiling sessions
sessions = supabase.table("profiling_sessions").select("*").execute()

if not sessions.data:
    print("\n⚠️  No profiling sessions found yet.")
    print("\nTo test the flow:")
    print("1. Start a session: POST /api/profiling/start")
    print("2. Connect via WebSocket: ws://localhost:8000/api/profiling/ws/{session_id}")
    print("3. Answer questions interactively")
else:
    print(f"\n📊 Found {len(sessions.data)} session(s):\n")
    
    for i, session in enumerate(sessions.data, 1):
        print(f"\nSession #{i}")
        print("-" * 80)
        print(f"  Session ID: {session['session_id']}")
        print(f"  User ID: {session['user_id'] or 'Anonymous'}")
        print(f"  Status: {session['status']}")
        print(f"  Current Question: {session['current_question_index'] + 1}/13")
        print(f"  Completeness: {session['profile_completeness'] * 100:.1f}%")
        print(f"  Created: {session['created_at']}")
        print(f"  Updated: {session['updated_at']}")
        
        # Get responses for this session
        responses = supabase.table("profiling_responses").select("*").eq(
            "session_id", session['session_id']
        ).execute()
        
        print(f"\n  📝 Responses: {len(responses.data)}")
        
        if responses.data:
            print("\n  Question Answers:")
            for resp in responses.data:
                status_emoji = {
                    'sufficient': '✅',
                    'complete': '✅',
                    'insufficient': '⚠️',
                    'not_answered': '❌'
                }.get(resp['validation_status'], '❓')
                
                print(f"    {status_emoji} {resp['question_id']}")
                print(f"       Answer: {resp['user_answer'][:60]}...")
                print(f"       Status: {resp['validation_status']}")
                if resp['extracted_value']:
                    print(f"       Extracted: {resp['extracted_value']}")
                print()
        
        # Get messages for this session
        messages = supabase.table("profiling_messages").select("*").eq(
            "session_id", session['session_id']
        ).order("created_at").execute()
        
        print(f"  💬 Conversation: {len(messages.data)} messages")
        
        if messages.data and len(messages.data) > 0:
            print("\n  Last 5 messages:")
            for msg in messages.data[-5:]:
                role_emoji = "🤖" if msg['role'] == 'assistant' else "👤"
                content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
                print(f"    {role_emoji} {msg['role']}: {content}")

print("\n" + "=" * 80)
print("USER PROFILES - From Completed Sessions")
print("=" * 80)

# Check if any profiles were created
profiles = supabase.table("user_profiles").select("*").execute()

if not profiles.data:
    print("\n⚠️  No user profiles created yet.")
    print("Profiles are created when profiling session reaches 80%+ completion.")
else:
    print(f"\n✅ Found {len(profiles.data)} profile(s):\n")
    
    for i, profile in enumerate(profiles.data, 1):
        print(f"\nProfile #{i}")
        print("-" * 80)
        print(f"  User ID: {profile['user_id']}")
        print(f"  Created: {profile['created_at']}")
        print(f"  Updated: {profile['updated_at']}")
        
        print("\n  🎯 Preferences:")
        prefs = profile.get('preferences', {})
        for key, value in prefs.items():
            print(f"    • {key}: {value}")
        
        print("\n  ⚠️  Constraints:")
        constraints = profile.get('constraints', {})
        for key, value in constraints.items():
            if value:  # Only show non-empty
                print(f"    • {key}: {value}")
        
        print("\n  ✈️  Travel History:")
        past = profile.get('past_destinations', [])
        if past:
            for dest in past:
                print(f"    • {dest}")
        else:
            print("    (none recorded)")
        
        print("\n  🌟 Wishlist:")
        wishlist = profile.get('wishlist_regions', [])
        if wishlist:
            for region in wishlist:
                print(f"    • {region}")
        else:
            print("    (none recorded)")

print("\n" + "=" * 80)
print("\n💡 Next Steps:")
print("   • Start new session: curl -X POST http://localhost:8000/api/profiling/start")
print("   • View API docs: http://localhost:8000/docs#tag/Profiling")
print("   • Complete profiling via WebSocket to generate profile")
print()

