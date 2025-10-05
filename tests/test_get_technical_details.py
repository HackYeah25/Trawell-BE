#!/usr/bin/env python3
"""
Test script for Planning API technical details functionality
Tests the prompt loader and technical details generation
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.prompts.loader import get_prompt_loader

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def test_prompt_loader_initialization():
    """Test prompt loader initialization"""
    print("\n" + "=" * 60)
    print("TEST 1: Prompt Loader Initialization")
    print("=" * 60)

    try:
        prompt_loader = get_prompt_loader()
        
        if prompt_loader:
            print("✅ Prompt loader initialized successfully")
            print(f"   Loader type: {type(prompt_loader)}")
            return True
        else:
            print("❌ Prompt loader is None")
            return False

    except Exception as e:
        print(f"❌ Prompt loader initialization failed: {e}")
        return False


def test_technical_details_krakow():
    """Test technical details for Krakow"""
    print("\n" + "=" * 60)
    print("TEST 2: Technical Details - Krakow")
    print("=" * 60)

    try:
        prompt_loader = get_prompt_loader()
        result = prompt_loader.load_template(
            module="planning",
            prompt_name="location_technical_details",
            destination="Krakow"
        )
        
        if result:
            print("✅ Technical details generated successfully")
            print(f"   Result type: {type(result)}")
            
            # Check if result contains expected content
            if isinstance(result, str):
                print(f"   Content length: {len(result)} characters")
                
                # Check for key technical details
                content_lower = result.lower()
                expected_terms = ["weather", "timezone", "currency", "language", "climate", "safety"]
                found_terms = [term for term in expected_terms if term in content_lower]
                
                print(f"   Found technical terms: {found_terms}")
                print(f"   Missing terms: {[term for term in expected_terms if term not in content_lower]}")
                
                # Show preview of content
                preview = result[:200] + "..." if len(result) > 200 else result
                print(f"   Content preview: {preview}")
                
                return len(found_terms) >= 3
            else:
                print(f"   ⚠️  Unexpected result type: {type(result)}")
                return False
        else:
            print("❌ No result returned")
            return False

    except Exception as e:
        print(f"❌ Technical details test failed: {e}")
        return False


def test_technical_details_paris():
    """Test technical details for Paris"""
    print("\n" + "=" * 60)
    print("TEST 3: Technical Details - Paris")
    print("=" * 60)

    try:
        prompt_loader = get_prompt_loader()
        result = prompt_loader.load_template(
            module="planning",
            prompt_name="location_technical_details",
            destination="Paris, France"
        )
        
        if result:
            print("✅ Technical details generated successfully")
            print(f"   Result type: {type(result)}")
            
            if isinstance(result, str):
                print(f"   Content length: {len(result)} characters")
                
                # Check for Paris-specific content
                content_lower = result.lower()
                if "euro" in content_lower or "eur" in content_lower:
                    print("   ✅ Contains currency information")
                if "french" in content_lower:
                    print("   ✅ Contains language information")
                if "france" in content_lower:
                    print("   ✅ Contains location information")
                
                # Show preview
                preview = result[:200] + "..." if len(result) > 200 else result
                print(f"   Content preview: {preview}")
                
                return len(result) > 50  # Should have substantial content
            else:
                print(f"   ⚠️  Unexpected result type: {type(result)}")
                return False
        else:
            print("❌ No result returned")
            return False

    except Exception as e:
        print(f"❌ Paris technical details test failed: {e}")
        return False


def test_technical_details_tokyo():
    """Test technical details for Tokyo"""
    print("\n" + "=" * 60)
    print("TEST 4: Technical Details - Tokyo")
    print("=" * 60)

    try:
        prompt_loader = get_prompt_loader()
        result = prompt_loader.load_template(
            module="planning",
            prompt_name="location_technical_details",
            destination="Tokyo, Japan"
        )
        
        if result:
            print("✅ Technical details generated successfully")
            print(f"   Result type: {type(result)}")
            
            if isinstance(result, str):
                print(f"   Content length: {len(result)} characters")
                
                # Check for Japan-specific content
                content_lower = result.lower()
                if "yen" in content_lower or "jpy" in content_lower:
                    print("   ✅ Contains currency information")
                if "japanese" in content_lower:
                    print("   ✅ Contains language information")
                if "japan" in content_lower:
                    print("   ✅ Contains location information")
                
                return len(result) > 50
            else:
                print(f"   ⚠️  Unexpected result type: {type(result)}")
                return False
        else:
            print("❌ No result returned")
            return False

    except Exception as e:
        print(f"❌ Tokyo technical details test failed: {e}")
        return False


def test_technical_details_invalid_destination():
    """Test technical details with unusual destination"""
    print("\n" + "=" * 60)
    print("TEST 5: Technical Details - Unusual Destination")
    print("=" * 60)

    try:
        prompt_loader = get_prompt_loader()
        result = prompt_loader.load_template(
            module="planning",
            prompt_name="location_technical_details",
            destination="Mars Colony Alpha"
        )
        
        if result:
            print("✅ Technical details generated (even for unusual destination)")
            print(f"   Result type: {type(result)}")
            
            if isinstance(result, str):
                print(f"   Content length: {len(result)} characters")
                
                # Even for unusual destinations, should return something
                preview = result[:200] + "..." if len(result) > 200 else result
                print(f"   Content preview: {preview}")
                
                return len(result) > 10  # Should return some content
            else:
                print(f"   ⚠️  Unexpected result type: {type(result)}")
                return False
        else:
            print("❌ No result returned")
            return False

    except Exception as e:
        print(f"❌ Unusual destination test failed: {e}")
        return False


def test_prompt_template_validation():
    """Test that the prompt template exists and is valid"""
    print("\n" + "=" * 60)
    print("TEST 6: Prompt Template Validation")
    print("=" * 60)

    try:
        prompt_loader = get_prompt_loader()
        
        # Test if we can load the specific template
        result = prompt_loader.load_template(
            module="planning",
            prompt_name="location_technical_details",
            destination="Test Destination"
        )
        
        if result:
            print("✅ Prompt template loaded successfully")
            print(f"   Template returns: {type(result)}")
            
            # Check if template contains expected placeholders
            if isinstance(result, str):
                if "{destination}" in result:
                    print("   ✅ Template contains destination placeholder")
                else:
                    print("   ⚠️  Template may not have destination placeholder")
                
                # Check for expected technical detail sections
                content_lower = result.lower()
                expected_sections = ["weather", "timezone", "currency", "language", "climate", "safety"]
                found_sections = [section for section in expected_sections if section in content_lower]
                
                print(f"   Found sections: {found_sections}")
                print(f"   Missing sections: {[s for s in expected_sections if s not in content_lower]}")
                
                return len(found_sections) >= 3
            else:
                print(f"   ⚠️  Template returns unexpected type: {type(result)}")
                return False
        else:
            print("❌ Template loading failed")
            return False

    except Exception as e:
        print(f"❌ Template validation failed: {e}")
        return False


def main():
    """Run all technical details tests"""
    print("🚀 Starting Technical Details Tests...")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_prompt_loader_initialization,
        test_technical_details_krakow,
        test_technical_details_paris,
        test_technical_details_tokyo,
        test_technical_details_invalid_destination,
        test_prompt_template_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
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
    success = main()
    sys.exit(0 if success else 1)
