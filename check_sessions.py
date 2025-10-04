#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("🔍 Checking all profiling sessions...\n")

# Check sessions
sessions = supabase.table("profiling_sessions").select("*").order("created_at", desc=True).execute()

print(f"Found {len(sessions.data)} session(s):\n")

for session in sessions.data:
    print(f"Session: {session['session_id']}")
    print(f"  Status: {session['status']}")
    print(f"  User ID: {session['user_id']}")
    print(f"  Question: {session['current_question_index']}/13")
    print(f"  Completeness: {session['profile_completeness']*100:.0f}%")
    print(f"  Created: {session['created_at']}")
    
    # Check responses
    responses = supabase.table("profiling_responses").select("*").eq(
        "session_id", session['session_id']
    ).execute()
    
    print(f"  Responses: {len(responses.data)}")
    
    # Check messages
    messages = supabase.table("profiling_messages").select("*").eq(
        "session_id", session['session_id']
    ).execute()
    
    print(f"  Messages: {len(messages.data)}")
    print()

