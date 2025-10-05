# ADR: Add User Authentication and Profile Persistence

## Status
Implemented - October 5, 2025

## Context
Previously, the Trawell application allowed anonymous usage with fallback test profiles when user profiling data was missing. This created several issues:

1. **No Profile Persistence**: Users couldn't save their profiling responses across sessions
2. **Fallback Profiles Everywhere**: Brainstorm and planning endpoints used hardcoded fallback profiles when real data was missing
3. **No User Identity**: No way to track which user owns which profiling session, trip, or conversation
4. **Poor UX**: Users had to re-do profiling every time they started a new session

## Decision
We implemented a complete authentication and profile persistence system:

### 1. Database Schema Changes
- Added `password_hash` column to `users` table for bcrypt-hashed passwords
- Added `name` column to `users` table for display names
- Created index on `email` for faster lookups
- Ensured `profiling_sessions.user_id` properly links to `users.id`

### 2. Authentication Endpoints
Implemented mock authentication in `/api/auth`:

- **POST /api/auth/register**: Register new user with email/password
  - Validates email uniqueness
  - Hashes password with bcrypt
  - Creates user record in database
  - Returns JWT token and user data

- **POST /api/auth/login**: Login existing user
  - Validates credentials
  - Checks profiling completion status
  - Returns JWT token with `onboardingCompleted` flag

### 3. Profiling Session Persistence
Updated `/api/profiling` endpoints:

- **POST /api/profiling/start**: Now requires authentication
  - Links session to authenticated user via `user_id`
  - Prevents duplicate profiling (checks for existing completed sessions)
  - Stores session in Redis temporarily, then persists to Supabase on completion

- **DELETE /api/profiling/profile/reset**: Now requires authentication
  - Properly cascades deletion of profiling_sessions, profiling_responses, profiling_messages
  - Allows users to re-do profiling

### 4. Removed All Fallback Profiles
Updated these endpoints to **require** real user profiles:

- `/api/brainstorm/ws/{session_id}`: Closes WebSocket if no profile found
- `/api/planning/ws/{recommendation_id}`: Closes WebSocket if no profile found

**No more hardcoded fallback profiles** - users must complete profiling first.

### 5. Profile Retrieval
Updated `SupabaseService.get_user_profile()`:
- Returns `None` if profile doesn't exist
- No fallback logic in service layer
- Callers must handle missing profiles appropriately

Added `SupabaseService.has_completed_profiling()`:
- Helper to check if user has completed profiling
- Used by login endpoint to set `onboardingCompleted` flag

## Consequences

### Positive
✅ **Profile Persistence**: Users can now register, complete profiling once, and use the app across sessions
✅ **Data Integrity**: All profiling data properly linked to user accounts
✅ **Better UX**: Users don't need to re-do profiling every time
✅ **Proper Error Handling**: Clear error messages when profile is missing instead of silent fallbacks
✅ **Security**: Password hashing with bcrypt, JWT-based authentication

### Negative
⚠️ **Breaking Change**: Existing anonymous sessions won't work anymore
⚠️ **Requires Migration**: Need to run database migration for `password_hash` and `name` columns
⚠️ **Frontend Changes Required**: Frontend must implement login/register flows

### Migration Path
For existing users/sessions:
1. Run migration: `add_password_to_users.sql`
2. Existing users without passwords cannot login (they need to re-register)
3. Existing profiling sessions without `user_id` will be orphaned (acceptable for MVP)

## Implementation Details

### Authentication Flow
```
1. User registers: POST /api/auth/register
   → Creates user with hashed password
   → Returns JWT token

2. User logs in: POST /api/auth/login
   → Validates credentials
   → Checks profiling status
   → Returns JWT with onboardingCompleted flag

3. User starts profiling: POST /api/profiling/start (with JWT)
   → Creates session linked to user_id
   → Stores in Redis for real-time updates
   → Persists to Supabase on completion

4. User uses brainstorm/planning: (with JWT)
   → Fetches real profile from user_profiles table
   → Fails gracefully if profile missing
```

### WebSocket Authentication
WebSockets don't directly use JWT in headers, but they:
1. Verify session exists before accepting connection
2. Session contains `user_id` from authenticated user
3. Load user profile from database using `user_id`
4. Close connection if profile not found

### Data Flow
```
Registration → Login → Profiling → Profile Saved → Brainstorm/Planning
     ↓           ↓          ↓             ↓                ↓
   users      JWT      profiling_    user_profiles    Uses real
   table      token    sessions                       profile data
```

## Testing
Required test scenarios:
1. ✅ Register new user
2. ✅ Login with correct credentials
3. ✅ Login with wrong credentials (should fail)
4. ✅ Start profiling (authenticated)
5. ✅ Start profiling (unauthenticated - should fail)
6. ✅ Complete profiling session
7. ✅ Verify profile saved to database
8. ✅ Start brainstorm with profile
9. ✅ Start brainstorm without profile (should fail)
10. ✅ Reset profile and re-do profiling

## Related Files
- `Trawell-BE/app/api/auth.py` - Authentication endpoints
- `Trawell-BE/app/api/profiling.py` - Profiling session management
- `Trawell-BE/app/api/brainstorm.py` - Removed fallback profiles
- `Trawell-BE/app/api/planning.py` - Removed fallback profiles
- `Trawell-BE/app/services/supabase_service.py` - Profile retrieval
- `Trawell-BE/app/services/session_service.py` - Session persistence
- `Trawell-BE/supabase/migrations/add_password_to_users.sql` - Database migration

## Future Improvements
- Add email verification
- Add password reset flow
- Add OAuth providers (Google, Apple)
- Add refresh tokens for long-lived sessions
- Add rate limiting on auth endpoints
- Add session management (view active sessions, logout all devices)
