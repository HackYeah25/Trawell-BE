# Authentication & Profile Persistence Setup

## Overview
This document describes the authentication and profile persistence system implemented for Trawell.

## What Changed

### 1. Database Schema
Added to `users` table:
- `password_hash` - Bcrypt hashed passwords
- `name` - User display name
- Index on `email` for faster lookups

Migration: `supabase/migrations/add_password_to_users.sql`

### 2. Authentication Endpoints

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "onboardingCompleted": false
  }
}
```

#### Login User
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "onboardingCompleted": true
  }
}
```

### 3. Protected Endpoints
These endpoints now **require** authentication:

- `POST /api/profiling/start` - Start profiling session
- `DELETE /api/profiling/profile/reset` - Reset user profile

Use JWT token in Authorization header:
```bash
Authorization: Bearer <access_token>
```

### 4. Profile Persistence Flow

```
┌─────────────┐
│  Register   │
│   /login    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Get JWT     │
│   Token     │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────────┐
│   Start     │─────▶│ profiling_       │
│  Profiling  │      │ sessions table   │
│             │      │ (user_id linked) │
└──────┬──────┘      └──────────────────┘
       │
       ▼
┌─────────────┐
│  Complete   │
│  Questions  │
│  via WS     │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────────┐
│   Profile   │─────▶│ user_profiles    │
│    Saved    │      │ table            │
└──────┬──────┘      └──────────────────┘
       │
       ▼
┌─────────────┐
│ Brainstorm/ │
│  Planning   │
│ (uses real  │
│  profile)   │
└─────────────┘
```

## No More Fallback Profiles

**IMPORTANT**: The system no longer provides fallback/test profiles. 

If a user tries to use brainstorm or planning without completing profiling:
- WebSocket connection will close with error
- Error message: "User profile not found. Please complete profiling first."

This ensures data integrity and proper user experience.

## Testing

### Run Automated Test
```bash
cd Trawell-BE
python test_auth_flow.py
```

This tests:
1. ✅ User registration
2. ✅ User login
3. ✅ Profile status check
4. ✅ Starting profiling (authenticated)
5. ✅ Rejecting unauthenticated requests
6. ✅ Public endpoints
7. ✅ Wrong password rejection

### Manual Testing

#### 1. Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!",
    "full_name": "Test User"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

Save the `access_token` from response.

#### 3. Check profile status
```bash
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/profiling/status
```

#### 4. Start profiling
```bash
curl -X POST http://localhost:8000/api/profiling/start \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 5. Complete profiling via WebSocket
Connect to: `ws://localhost:8000/api/profiling/ws/<session_id>`

Send answers to questions, complete the flow.

#### 6. Verify profile saved
```bash
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/profiling/status
```

Should show `has_completed_profiling: true`

#### 7. Start brainstorm (should work now)
```bash
curl -X POST http://localhost:8000/api/brainstorm/start \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Frontend Integration

### 1. Add Login/Register Pages
Frontend needs to implement:
- Registration form
- Login form
- Store JWT token in localStorage/sessionStorage
- Add token to all API requests

### 2. Update API Client
```typescript
// Add token to requests
const token = localStorage.getItem('auth_token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

### 3. Handle Authentication Errors
```typescript
// If 401 Unauthorized, redirect to login
if (response.status === 401) {
  localStorage.removeItem('auth_token');
  router.push('/login');
}
```

### 4. Check Onboarding Status
After login, check `user.onboardingCompleted`:
```typescript
if (user.onboardingCompleted) {
  // Skip profiling, go to dashboard
  router.push('/dashboard');
} else {
  // Start profiling
  router.push('/profiling');
}
```

## Security Notes

### Password Hashing
- Uses bcrypt with automatic salt generation
- Passwords are never stored in plain text
- Hash verification happens server-side only

### JWT Tokens
- Tokens expire after configured time (default: 30 days)
- Token contains: `user_id` and `email`
- Tokens are signed with `SECRET_KEY` from environment

### Environment Variables
Required in `.env`:
```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

## Database Tables

### users
```sql
id              UUID PRIMARY KEY
email           TEXT UNIQUE NOT NULL
password_hash   TEXT
name            TEXT
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

### profiling_sessions
```sql
id                      UUID PRIMARY KEY
session_id              VARCHAR UNIQUE
user_id                 UUID REFERENCES users(id)
status                  VARCHAR
current_question_index  INTEGER
profile_completeness    FLOAT
created_at              TIMESTAMPTZ
updated_at              TIMESTAMPTZ
completed_at            TIMESTAMPTZ
```

### user_profiles
```sql
id                      UUID PRIMARY KEY
user_id                 UUID UNIQUE REFERENCES users(id)
travel_style            TEXT
budget_level            TEXT
preferred_climate       TEXT[]
activity_preferences    TEXT[]
... (other profile fields)
```

## Troubleshooting

### "Authentication required" error
- Make sure you're sending JWT token in Authorization header
- Check token hasn't expired
- Verify token format: `Bearer <token>`

### "User profile not found" error
- User needs to complete profiling first
- Check `/api/profiling/status` endpoint
- Complete profiling via `/api/profiling/start` and WebSocket

### "Email already registered" error
- User already exists with that email
- Use login instead of register
- Or use a different email

### Profile not persisting
- Check profiling session completed successfully
- Verify `profiling_sessions` table has record with `status='completed'`
- Check `user_profiles` table has record for user
- Look at server logs for errors during profile save

## Migration from Anonymous System

### For Development
1. Run migration: Database already migrated via MCP
2. Clear any existing test data if needed
3. Register new test users

### For Production
1. Back up database
2. Run migration
3. Notify users they need to re-register
4. Existing anonymous sessions will be orphaned (acceptable for MVP)

## Related Files
- `app/api/auth.py` - Authentication endpoints
- `app/api/profiling.py` - Profiling with auth
- `app/api/deps.py` - JWT validation
- `app/services/supabase_service.py` - Database operations
- `docs/adr/add-user-authentication-and-profile-persistence.md` - Architecture decision record
- `test_auth_flow.py` - Automated test script
