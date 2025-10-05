#!/usr/bin/env python3
"""
Create a test user with a completed profiling session and real profile data

This script:
1. Creates a user with email/password
2. Creates a completed profiling session linked to that user
3. Creates a user profile with real preferences
4. Prints the user_id and login credentials for testing

Usage:
    python create_test_user_with_real_profile.py
"""

import os
import sys
from datetime import datetime
from passlib.context import CryptContext

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.supabase_service import get_supabase, init_supabase

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user_with_profile():
    """Create a test user with completed profile"""
    
    # Initialize Supabase
    init_supabase()
    supabase = get_supabase()
    
    if not supabase.client:
        print("❌ Error: Supabase client not initialized")
        print("   Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
        return
    
    # Test user credentials
    test_email = "testuser@trawell.com"
    test_password = "TestPassword123!"
    test_name = "Test User with Profile"
    
    print("\n" + "="*60)
    print("  Creating Test User with Real Profile")
    print("="*60)
    
    try:
        # 1. Check if user already exists
        print(f"\n1. Checking if user {test_email} exists...")
        existing = supabase.client.table("users").select("*").eq("email", test_email).execute()
        
        if existing.data:
            user_id = existing.data[0]["id"]
            print(f"   ✅ User already exists: {user_id}")
        else:
            # Create user
            print(f"   Creating new user...")
            password_hash = pwd_context.hash(test_password)
            
            user_result = supabase.client.table("users").insert({
                "email": test_email,
                "name": test_name,
                "password_hash": password_hash
            }).execute()
            
            user_id = user_result.data[0]["id"]
            print(f"   ✅ Created user: {user_id}")
        
        # 2. Create profiling session (if doesn't exist)
        print(f"\n2. Creating profiling session...")
        session_id = f"prof_test_{user_id[:8]}"
        
        existing_session = supabase.client.table("profiling_sessions").select("*").eq(
            "session_id", session_id
        ).execute()
        
        if not existing_session.data:
            supabase.client.table("profiling_sessions").insert({
                "session_id": session_id,
                "user_id": user_id,
                "status": "completed",
                "current_question_index": 13,
                "profile_completeness": 1.0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat()
            }).execute()
            print(f"   ✅ Created profiling session: {session_id}")
        else:
            print(f"   ✅ Profiling session already exists: {session_id}")
        
        # 3. Create user profile (if doesn't exist)
        print(f"\n3. Creating user profile...")
        existing_profile = supabase.client.table("user_profiles").select("*").eq(
            "user_id", user_id
        ).execute()
        
        if not existing_profile.data:
            profile_data = {
                "user_id": user_id,
                "travel_style": "explorer",
                "budget_level": "medium",
                "preferred_climate": ["warm", "tropical", "temperate"],
                "activity_preferences": ["adventure", "culture", "food", "nature"],
                "dietary_restrictions": [],
                "accessibility_needs": [],
                "travel_pace": "moderate",
                "profile_completed": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            supabase.client.table("user_profiles").insert(profile_data).execute()
            print(f"   ✅ Created user profile")
        else:
            print(f"   ✅ User profile already exists")
        
        # Print summary
        print("\n" + "="*60)
        print("  ✅ TEST USER CREATED SUCCESSFULLY")
        print("="*60)
        print(f"\n📧 Email: {test_email}")
        print(f"🔑 Password: {test_password}")
        print(f"🆔 User ID: {user_id}")
        print(f"✅ Profile Status: Completed")
        
        print("\n" + "="*60)
        print("  HOW TO USE")
        print("="*60)
        
        print(f"\n1. Login to get JWT token:")
        print(f'''
curl -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"email":"{test_email}","password":"{test_password}"}}'
''')
        
        print(f"\n2. Or use the user_id directly in requests:")
        print(f"   user_id={user_id}")
        
        print(f"\n3. Test brainstorm with this user:")
        print(f'''
curl -X POST http://localhost:8000/api/brainstorm/start \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{}}'
''')
        
        print(f"\n4. WebSocket connections will use real profile data!")
        print(f"   No more fallback profiles 🎉")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_user_with_profile()
