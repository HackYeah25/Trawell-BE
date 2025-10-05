#!/usr/bin/env python3
"""
Simulate a complete profiling session to test database saving
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase first
from app.services.supabase_service import init_supabase
init_supabase()

# Import after loading env
from app.services.session_service import session_service
from app.models.profiling import ProfilingStatus

async def simulate_complete_session():
    """Simulate a complete profiling session"""
    
    session_id = "prof_test_complete"
    
    # Create session data
    session_data = {
        "session_id": session_id,
        "user_id": None,  # Anonymous user
        "status": "completed",
        "current_question_index": 13,  # All questions answered
        "profile_completeness": 1.0,  # 100% complete
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "responses": [
            {
                "question_id": "traveler_type",
                "user_answer": "I love actively exploring new places, trying local food, and going on adventures",
                "validation_status": "sufficient",
                "extracted_value": "explorer",
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "activity_level",
                "user_answer": "I prefer high activity - hiking all day, walking tours, multiple activities",
                "validation_status": "sufficient",
                "extracted_value": "high",
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "accommodation",
                "user_answer": "I like boutique hotels with character and unique experiences",
                "validation_status": "sufficient",
                "extracted_value": "boutique",
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "environment",
                "user_answer": "I love mountains and nature, but also enjoy exploring cities",
                "validation_status": "sufficient",
                "extracted_value": "mixed",
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "budget_sensitivity",
                "user_answer": "Budget is somewhat important, I balance cost with good experiences",
                "validation_status": "sufficient",
                "extracted_value": "medium",
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "culture_interest",
                "user_answer": "I love museums, historical sites, and learning about local culture",
                "validation_status": "sufficient",
                "extracted_value": "high",
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "food_importance",
                "user_answer": "Food is a highlight! I love trying local cuisine and food experiences",
                "validation_status": "sufficient",
                "extracted_value": "high",
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "dietary_restrictions",
                "user_answer": "No dietary restrictions",
                "validation_status": "sufficient",
                "extracted_value": [],
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "mobility_accessibility",
                "user_answer": "No mobility limitations",
                "validation_status": "sufficient",
                "extracted_value": [],
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "climate_preference",
                "user_answer": "I prefer mild temperate weather, like spring or fall",
                "validation_status": "sufficient",
                "extracted_value": ["mild_temperate"],
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "past_destinations",
                "user_answer": "I've loved trips to Japan (amazing food and culture), Iceland (stunning nature), and Italy (perfect mix of everything)",
                "validation_status": "sufficient",
                "extracted_value": ["Japan", "Iceland", "Italy"],
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "wishlist_regions",
                "user_answer": "I'd love to visit Patagonia for hiking, Norway for fjords, and New Zealand for nature",
                "validation_status": "sufficient",
                "extracted_value": ["Patagonia", "Norway", "New Zealand"],
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            },
            {
                "question_id": "language_comfort",
                "user_answer": "I'm comfortable with language barriers, I enjoy the challenge",
                "validation_status": "sufficient",
                "extracted_value": [],
                "follow_up_count": 0,
                "answered_at": datetime.now().isoformat()
            }
        ]
    }
    
    print(f"Creating session {session_id} in Redis...")
    await session_service.create_session(session_data)
    
    # Add conversation messages
    conversation = [
        {
            "role": "assistant",
            "content": "Welcome! Ready to discover your perfect destination?",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "user",
            "content": "I love actively exploring new places",
            "timestamp": datetime.now().isoformat()
        },
    ]
    
    for msg in conversation:
        await session_service.add_message_to_conversation(session_id, msg)
    
    print(f"✅ Created session with {len(session_data['responses'])} responses")
    print(f"✅ Added {len(conversation)} conversation messages")
    
    # Now save to Supabase
    print(f"\nSaving session to Supabase database...")
    success = await session_service.save_session_to_database(session_id)
    
    if success:
        print("\n" + "="*80)
        print("✅ SUCCESS! Session saved to Supabase")
        print("="*80)
        print(f"\nSession ID: {session_id}")
        print(f"Completeness: 100%")
        print(f"Responses: {len(session_data['responses'])}")
        print("\nRun this to see the saved data:")
        print("  python check_sessions.py")
    else:
        print("\n❌ Failed to save session to Supabase")

if __name__ == "__main__":
    asyncio.run(simulate_complete_session())

