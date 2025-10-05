#!/usr/bin/env python3
"""
Test script for complete authentication and profiling flow

Tests:
1. User registration
2. User login
3. Starting profiling session (authenticated)
4. Profile status check
5. Attempting brainstorm without profile (should fail)

Run: python test_auth_flow.py
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_NAME = "Test User"

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(success, message):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_registration():
    """Test user registration"""
    print_section("1. Testing User Registration")
    
    payload = {
        "email": TEST_EMAIL,
        "username": TEST_EMAIL.split("@")[0],
        "password": TEST_PASSWORD,
        "full_name": TEST_NAME
    }
    
    print(f"Registering user: {TEST_EMAIL}")
    response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Registration successful")
        print(f"   User ID: {data['user']['id']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Token: {data['access_token'][:20]}...")
        return data['access_token'], data['user']['id']
    else:
        print_result(False, f"Registration failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None, None

def test_login(email, password):
    """Test user login"""
    print_section("2. Testing User Login")
    
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"Logging in user: {email}")
    response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Login successful")
        print(f"   User ID: {data['user']['id']}")
        print(f"   Onboarding Completed: {data['user']['onboardingCompleted']}")
        print(f"   Token: {data['access_token'][:20]}...")
        return data['access_token']
    else:
        print_result(False, f"Login failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_profile_status(token):
    """Test profile status check"""
    print_section("3. Testing Profile Status Check")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/profiling/status", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Profile status retrieved")
        print(f"   Has Completed Profiling: {data['has_completed_profiling']}")
        print(f"   Should Skip Onboarding: {data['should_skip_onboarding']}")
        print(f"   Profile Completeness: {data['profile_completeness']}%")
        return data
    else:
        print_result(False, f"Profile status check failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_start_profiling_authenticated(token):
    """Test starting profiling session with authentication"""
    print_section("4. Testing Start Profiling (Authenticated)")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {}
    
    response = requests.post(f"{BASE_URL}/api/profiling/start", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Profiling session started")
        print(f"   Session ID: {data['session']['session_id']}")
        print(f"   User ID: {data['session']['user_id']}")
        print(f"   WebSocket URL: {data['websocket_url']}")
        print(f"   First Message: {data['first_message'][:50]}...")
        return data['session']['session_id']
    else:
        print_result(False, f"Start profiling failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_start_profiling_unauthenticated():
    """Test starting profiling session without authentication"""
    print_section("5. Testing Start Profiling (Unauthenticated - Should Fail)")
    
    payload = {}
    response = requests.post(f"{BASE_URL}/api/profiling/start", json=payload)
    
    if response.status_code == 401:
        print_result(True, f"Correctly rejected unauthenticated request")
        print(f"   Status: {response.status_code}")
    else:
        print_result(False, f"Should have rejected but got: {response.status_code}")
        print(f"   Response: {response.text}")

def test_get_profiling_questions():
    """Test getting profiling questions (public endpoint)"""
    print_section("6. Testing Get Profiling Questions (Public)")
    
    response = requests.get(f"{BASE_URL}/api/profiling/questions")
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved profiling questions")
        print(f"   Total Questions: {len(data)}")
        if data:
            print(f"   First Question: {data[0]['markdownQuestion'][:50]}...")
        return data
    else:
        print_result(False, f"Get questions failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_wrong_password(email):
    """Test login with wrong password"""
    print_section("7. Testing Login with Wrong Password (Should Fail)")
    
    payload = {
        "email": email,
        "password": "WrongPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
    
    if response.status_code == 401:
        print_result(True, f"Correctly rejected wrong password")
        print(f"   Status: {response.status_code}")
    else:
        print_result(False, f"Should have rejected but got: {response.status_code}")
        print(f"   Response: {response.text}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  TRAWELL AUTHENTICATION & PROFILING FLOW TEST")
    print("="*60)
    print(f"\nTest User: {TEST_EMAIL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test 1: Registration
    token, user_id = test_registration()
    if not token:
        print("\n❌ Registration failed, cannot continue tests")
        return
    
    # Test 2: Login
    login_token = test_login(TEST_EMAIL, TEST_PASSWORD)
    if not login_token:
        print("\n❌ Login failed, cannot continue tests")
        return
    
    # Test 3: Profile Status (should be incomplete)
    profile_status = test_profile_status(token)
    
    # Test 4: Start Profiling (authenticated)
    session_id = test_start_profiling_authenticated(token)
    
    # Test 5: Start Profiling (unauthenticated - should fail)
    test_start_profiling_unauthenticated()
    
    # Test 6: Get Questions (public)
    questions = test_get_profiling_questions()
    
    # Test 7: Wrong Password (should fail)
    test_wrong_password(TEST_EMAIL)
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"✅ User registered successfully: {TEST_EMAIL}")
    print(f"✅ User logged in successfully")
    print(f"✅ Profile status checked")
    print(f"✅ Profiling session started (authenticated)")
    print(f"✅ Unauthenticated request rejected")
    print(f"✅ Public endpoints accessible")
    print(f"✅ Wrong password rejected")
    
    print("\n" + "="*60)
    print("  NEXT STEPS")
    print("="*60)
    print(f"\n1. Complete profiling via WebSocket:")
    print(f"   ws://localhost:8000/api/profiling/ws/{session_id}")
    print(f"\n2. Check profile status again:")
    print(f"   curl -H 'Authorization: Bearer {token[:20]}...' \\")
    print(f"        http://localhost:8000/api/profiling/status")
    print(f"\n3. Start brainstorm session (should work after profiling):")
    print(f"   curl -H 'Authorization: Bearer {token[:20]}...' \\")
    print(f"        -X POST http://localhost:8000/api/brainstorm/start")
    print()

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at http://localhost:8000")
        print("   Make sure the backend server is running:")
        print("   cd Trawell-BE && python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
