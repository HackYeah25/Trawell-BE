#!/bin/bash
# Test script for profile skip functionality

echo "==================================================================="
echo "Testing Profile Skip Functionality"
echo "==================================================================="
echo ""

API_BASE="http://localhost:8000/api/profiling"

echo "1. Checking profile status (should have profile if seed data loaded)..."
echo "-------------------------------------------------------------------"
curl -s "${API_BASE}/status" | python -m json.tool
echo ""
echo ""

echo "2. Testing profile reset..."
echo "-------------------------------------------------------------------"
curl -s -X DELETE "${API_BASE}/profile/reset" | python -m json.tool
echo ""
echo ""

echo "3. Checking profile status again (should NOT have profile after reset)..."
echo "-------------------------------------------------------------------"
curl -s "${API_BASE}/status" | python -m json.tool
echo ""
echo ""

echo "==================================================================="
echo "Test Summary:"
echo "==================================================================="
echo "1. If seed data is loaded: First check should return has_profile=true"
echo "2. After reset: Profile should be deleted"
echo "3. Second check should return has_profile=false"
echo ""
echo "To reload seed data:"
echo "  - Run the SQL in supabase/seeds/001_test_user_profile.sql"
echo "  - Or use: psql <database_url> -f supabase/seeds/001_test_user_profile.sql"
echo ""
