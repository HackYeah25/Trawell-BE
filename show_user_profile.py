#!/usr/bin/env python3
"""
Show complete user profile from profiling session
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 90)
print("🧳 TRAVELER PROFILE - First User")
print("=" * 90)

# Get the session
session = supabase.table("profiling_sessions").select("*").eq(
    "session_id", "prof_test_complete"
).execute().data[0]

# Get all responses
responses = supabase.table("profiling_responses").select("*").eq(
    "session_id", "prof_test_complete"
).execute().data

# Organize responses by question_id
answers = {resp['question_id']: resp for resp in responses}

print(f"\n📊 Profile Summary")
print("-" * 90)
print(f"   Session ID: {session['session_id']}")
print(f"   Status: {session['status'].upper()}")
print(f"   Completeness: {session['profile_completeness'] * 100:.0f}%")
print(f"   Questions Answered: {len(responses)}/13")

print("\n\n🎯 TRAVEL STYLE")
print("=" * 90)

# Traveler Type
traveler = answers.get('traveler_type', {})
print(f"\n🏃 Traveler Type: {traveler.get('extracted_value', 'N/A').upper()}")
print(f"   → {traveler.get('user_answer', 'N/A')}")

# Activity Level
activity = answers.get('activity_level', {})
print(f"\n⚡ Activity Level: {activity.get('extracted_value', 'N/A').upper()}")
print(f"   → {activity.get('user_answer', 'N/A')}")

# Environment Preference
env = answers.get('environment', {})
print(f"\n🌍 Preferred Environment: {env.get('extracted_value', 'N/A').upper()}")
print(f"   → {env.get('user_answer', 'N/A')}")

# Accommodation
accom = answers.get('accommodation', {})
print(f"\n🏨 Accommodation Style: {accom.get('extracted_value', 'N/A').upper()}")
print(f"   → {accom.get('user_answer', 'N/A')}")

print("\n\n💰 PRIORITIES & INTERESTS")
print("=" * 90)

# Budget
budget = answers.get('budget_sensitivity', {})
print(f"\n💵 Budget Sensitivity: {budget.get('extracted_value', 'N/A').upper()}")
print(f"   → {budget.get('user_answer', 'N/A')}")

# Culture
culture = answers.get('culture_interest', {})
print(f"\n🏛️  Culture Interest: {culture.get('extracted_value', 'N/A').upper()}")
print(f"   → {culture.get('user_answer', 'N/A')}")

# Food
food = answers.get('food_importance', {})
print(f"\n🍜 Food Importance: {food.get('extracted_value', 'N/A').upper()}")
print(f"   → {food.get('user_answer', 'N/A')}")

print("\n\n⚠️  CONSTRAINTS & REQUIREMENTS")
print("=" * 90)

# Dietary
dietary = answers.get('dietary_restrictions', {})
dietary_list = dietary.get('extracted_value', [])
print(f"\n🥗 Dietary Restrictions:")
if dietary_list:
    for item in dietary_list:
        print(f"   • {item}")
else:
    print(f"   ✓ None")

# Mobility
mobility = answers.get('mobility_accessibility', {})
mobility_list = mobility.get('extracted_value', [])
print(f"\n♿ Mobility/Accessibility:")
if mobility_list:
    for item in mobility_list:
        print(f"   • {item}")
else:
    print(f"   ✓ None")

# Climate
climate = answers.get('climate_preference', {})
climate_list = climate.get('extracted_value', [])
print(f"\n🌤️  Climate Preference:")
if climate_list:
    for item in climate_list:
        print(f"   • {item}")
else:
    print(f"   • No specific preference")

# Language
lang = answers.get('language_comfort', {})
print(f"\n🗣️  Language Comfort:")
print(f"   → {lang.get('user_answer', 'N/A')}")

print("\n\n✈️  TRAVEL EXPERIENCE")
print("=" * 90)

# Past destinations
past = answers.get('past_destinations', {})
past_list = past.get('extracted_value', [])
print(f"\n📍 Past Favorite Destinations:")
if past_list:
    for dest in past_list:
        print(f"   ✓ {dest}")
else:
    print(f"   (No previous trips recorded)")
print(f"\n   Context: {past.get('user_answer', 'N/A')}")

# Wishlist
wishlist = answers.get('wishlist_regions', {})
wishlist_list = wishlist.get('extracted_value', [])
print(f"\n🌟 Dream Destinations (Wishlist):")
if wishlist_list:
    for region in wishlist_list:
        print(f"   ⭐ {region}")
else:
    print(f"   (No wishlist recorded)")
print(f"\n   Context: {wishlist.get('user_answer', 'N/A')}")

print("\n\n🎯 RECOMMENDED DESTINATIONS BASED ON THIS PROFILE")
print("=" * 90)
print("""
Based on this traveler's profile, ideal destinations would include:

1. **Patagonia, Chile/Argentina** ⭐ (Wishlist Match!)
   - High activity hiking ✓
   - Stunning nature & mountains ✓
   - Boutique lodges available ✓
   - Temperate climate (spring/fall) ✓

2. **Norwegian Fjords** ⭐ (Wishlist Match!)
   - Active exploration with hiking ✓
   - Dramatic natural scenery ✓
   - Cultural heritage sites ✓
   - Spring/fall ideal for visits ✓

3. **Peru (Inca Trail & Cusco)**
   - High activity trekking ✓
   - Rich cultural experiences ✓
   - Amazing local cuisine ✓
   - Similar to loved destinations (Japan culture, Iceland nature) ✓

4. **New Zealand** ⭐ (Wishlist Match!)
   - Ultimate nature & adventure ✓
   - Mix of mountains & coastline ✓
   - Excellent food scene ✓
   - Temperate climate ✓

5. **Slovenia & Croatia**
   - Boutique accommodations in charming towns ✓
   - Mix of nature (Julian Alps) & culture (historic cities) ✓
   - Excellent food ✓
   - Budget-friendly yet high-quality experiences ✓
""")

print("\n" + "=" * 90)
print("✅ Profile Analysis Complete!")
print("=" * 90)

