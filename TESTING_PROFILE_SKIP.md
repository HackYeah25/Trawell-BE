# Testing Profile Skip Functionality

This guide explains how to test the profile skip feature where users with complete profiles automatically skip the onboarding process.

## Overview

- **Test User ID**: `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`
- When this user has a complete profile → onboarding is skipped → redirects to `/app/brainstorm`
- When this user has NO profile → goes through onboarding normally

## Setup: Load Test Data

### Option 1: Direct SQL (Recommended)

Connect to your Supabase database and run:

```bash
psql <your_supabase_connection_string> -f Trawell-BE/supabase/seeds/001_test_user_profile.sql
```

### Option 2: Supabase Dashboard

1. Go to Supabase Dashboard → SQL Editor
2. Copy contents of `Trawell-BE/supabase/seeds/001_test_user_profile.sql`
3. Paste and run

### What Gets Created

The seed script creates:

1. **Test User with Complete Profile**
   - `user_id`: `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`
   - Complete profiling session
   - 13 answered questions
   - Profile in `user_profiles` table
   - **Should skip onboarding**

2. **Test User WITHOUT Profile**
   - `user_id`: `b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22`
   - Incomplete session (23% complete)
   - No profile in database
   - **Should go through onboarding**

## Testing Workflow

### 1. Test Profile Skip (User HAS Profile)

```bash
# Run test script
./test_profile_skip.sh

# Or manual testing:
curl http://localhost:8000/api/profiling/status | jq .
```

**Expected Response:**
```json
{
  "has_profile": true,
  "profile_completeness": 100,
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
}
```

**Frontend Behavior:**
- Opens `/onboarding`
- Calls `GET /api/profiling/status`
- Sees `has_profile: true`
- **Auto-redirects to `/app/brainstorm`**
- Skips onboarding entirely

### 2. Test Onboarding Flow (User NO Profile)

```bash
# Reset the profile
curl -X DELETE http://localhost:8000/api/profiling/profile/reset | jq .

# Check status again
curl http://localhost:8000/api/profiling/status | jq .
```

**Expected Response After Reset:**
```json
{
  "has_profile": false,
  "profile_completeness": 0,
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
}
```

**Frontend Behavior:**
- Opens `/onboarding`
- Calls `GET /api/profiling/status`
- Sees `has_profile: false`
- **Stays on onboarding page**
- Starts profiling session normally

### 3. Reset Profile for Re-testing

```bash
# Delete profile to test onboarding again
curl -X DELETE http://localhost:8000/api/profiling/profile/reset | jq .
```

**Or reload seed data:**
```bash
psql <connection_string> -f Trawell-BE/supabase/seeds/001_test_user_profile.sql
```

## API Endpoints

### GET `/api/profiling/status`
Checks if user has completed profile.

**Response:**
```json
{
  "has_profile": true,
  "profile_completeness": 100,
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
}
```

### DELETE `/api/profiling/profile/reset`
Deletes user profile from database.

**Response:**
```json
{
  "success": true,
  "message": "Profile reset successfully. You can now complete onboarding again.",
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
}
```

## Frontend Implementation

The frontend uses these hooks:

```typescript
// Check profile status on mount
const { data: profileStatus } = useProfileStatus();

// Auto-skip if profile exists
useEffect(() => {
  if (profileStatus?.has_profile && profileStatus?.profile_completeness === 100) {
    navigate('/app/brainstorm');
  }
}, [profileStatus]);

// Reset profile
const resetMutation = useResetProfile();
await resetMutation.mutateAsync();
```

## Development Notes

- **No Auth Required**: The backend uses test user ID `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11` when not authenticated
- **Brainstorm Integration**: User profile is injected into brainstorm sessions automatically
- **Profile Data**: Includes travel preferences, past destinations, wishlist regions, constraints

## Troubleshooting

### Profile skip not working?

1. Check seed data loaded: `SELECT * FROM user_profiles WHERE user_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';`
2. Check backend logs for "DEBUG: No auth, using test user_id"
3. Verify frontend redirects in console logs

### Profile reset not working?

1. Check Supabase RLS policies allow DELETE
2. Verify `supabase.client` is initialized
3. Check backend logs for "✅ Deleted profile"

## Database Tables

- `user_profiles` - User profile data
- `profiling_sessions` - Profiling session tracking
- `profiling_responses` - Individual question responses
- `profiling_messages` - Full conversation history
