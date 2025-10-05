#!/usr/bin/env python3
"""
Test script for Google Places API integration
Tests place search and photo retrieval functionality
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.google_places_service import GooglePlacesService

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


async def test_place_search():
    """Test basic place search functionality"""
    print("\n" + "=" * 60)
    print("TEST 1: Place Search")
    print("=" * 60)

    try:
        service = GooglePlacesService()
        result = await service.search_place("Kraków Poland")

        if result:
            print(f"✅ Place search successful")
            print(f"   Name: {result.name}")
            print(f"   Address: {result.formatted_address}")
            print(f"   Location: {result.location['latitude']:.4f}, {result.location['longitude']:.4f}")
            print(f"   Rating: {result.rating}")
            print(f"   User ratings: {result.user_rating_count}")
            return True
        else:
            print("❌ No results found")
            return False

    except Exception as e:
        print(f"❌ Place search failed: {e}")
        return False


async def test_photo_retrieval():
    """Test photo retrieval functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Photo Retrieval")
    print("=" * 60)

    try:
        service = GooglePlacesService()
        
        # First search for a place to get photo name
        place_result = await service.search_place("Kraków Poland")
        
        if not place_result or not place_result.photos:
            print("❌ No place or photos found for photo test")
            return False
        
        photo_name = place_result.photos[0].name
        print(f"   Found photo: {photo_name}")
        
        # Get photo details
        photo_result = await service.get_place_photo(photo_name)
        
        if photo_result:
            print(f"✅ Photo retrieval successful")
            print(f"   Photo URI: {photo_result.photo_uri}")
            print(f"   Dimensions: {photo_result.width_px}x{photo_result.height_px}")
            return True
        else:
            print("❌ Photo retrieval failed")
            return False

    except Exception as e:
        print(f"❌ Photo retrieval failed: {e}")
        return False


async def test_complete_flow():
    """Test complete flow: search place and get photo"""
    print("\n" + "=" * 60)
    print("TEST 3: Complete Flow (Search + Photo)")
    print("=" * 60)

    try:
        service = GooglePlacesService()
        result = await service.search_place_with_photo("Kraków Poland")

        if result:
            print(f"✅ Complete flow successful")
            print(f"   Place: {result.name}")
            print(f"   Address: {result.formatted_address}")
            print(f"   Location: {result.location['latitude']:.4f}, {result.location['longitude']:.4f}")
            
            if result.photos:
                photo = result.photos[0]
                print(f"   📸 Photo URI: {photo.photo_uri}")
                print(f"   📐 Photo dimensions: {photo.width_px}x{photo.height_px}")
            else:
                print("   ⚠️  No photos found")
            
            return True
        else:
            print("❌ Complete flow failed - no results")
            return False

    except Exception as e:
        print(f"❌ Complete flow failed: {e}")
        return False


async def test_error_handling():
    """Test error handling with invalid queries"""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling")
    print("=" * 60)

    try:
        service = GooglePlacesService()
        
        # Test with non-existent place
        result = await service.search_place("NonExistentPlace12345XYZ")
        
        if result is None:
            print("✅ Error handling works - no results for invalid query")
            return True
        else:
            print("⚠️  Unexpected result for invalid query")
            return False

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def test_krakow_specific():
    """Test specific Krakow search with photo URI"""
    print("\n" + "=" * 60)
    print("TEST 5: Krakow Photo URI Test")
    print("=" * 60)

    try:
        service = GooglePlacesService()
        result = await service.search_place_with_photo("Kraków Poland")

        if result:
            print(f"✅ Krakow search successful")
            print(f"   Place: {result.name}")
            print(f"   Address: {result.formatted_address}")
            
            # Validate it's actually Krakow
            if "kraków" in result.name.lower() or "krakow" in result.name.lower():
                print("   ✅ Correctly identified as Krakow")
            else:
                print("   ⚠️  Place name doesn't contain 'Krakow'")
            
            if result.photos:
                photo = result.photos[0]
                print(f"   📸 Photo URI: {photo.photo_uri}")
                
                # Validate photo URI format
                if photo.photo_uri.startswith("https://"):
                    print("   ✅ Photo URI is valid HTTPS URL")
                else:
                    print("   ⚠️  Photo URI format unexpected")
                
                print(f"   📐 Dimensions: {photo.width_px}x{photo.height_px}")
                return True
            else:
                print("   ❌ No photos found for Krakow")
                return False
        else:
            print("❌ Krakow search failed")
            return False

    except Exception as e:
        print(f"❌ Krakow test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Google Places API Tests...")
    print("=" * 60)
    
    # Check if API key is available
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in environment")
        print("   Please set your Google Maps API key in .env file")
        return False
    
    print(f"✓ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    # Run tests
    tests = [
        test_place_search,
        test_photo_retrieval,
        test_complete_flow,
        test_error_handling,
        test_krakow_specific
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
