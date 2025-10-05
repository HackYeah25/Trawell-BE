# Onboarding Skip Logic - Implementation Guide

## Overview

System automatycznie pomija onboarding (profiling questionnaire) dla użytkowników, którzy już ukończyli profiling, bazując **wyłącznie** na tabeli `profiling_sessions`.

**Nie wymaga** tabeli `user_profiles` - wystarczy zakończona sesja profilowania.

---

## How It Works

### 1. User Login Flow

```
User Logs In
     ↓
Frontend calls GET /api/profiling/status
     ↓
Backend checks profiling_sessions table:
  - WHERE user_id = {logged_in_user_id}
  - AND status = 'completed'
     ↓
Response: should_skip_onboarding = true/false
     ↓
Frontend decides routing
```

### 2. Database Check

```sql
SELECT * FROM profiling_sessions
WHERE user_id = '{user_id}'
AND status = 'completed'
ORDER BY completed_at DESC
LIMIT 1;
```

- **If found** → User has completed profiling → SKIP
- **If not found** → User needs profiling → START

---

## API Endpoint

### `GET /api/profiling/status`

**Purpose:** Check if user should skip onboarding

**Authentication:** Optional (returns different data for auth vs anonymous)

**Response Schema:**

```typescript
{
  has_completed_profiling: boolean,      // User has completed session
  should_skip_onboarding: boolean,       // Frontend should skip
  profile_completeness: number,          // 0-100%
  last_session_id: string | null,        // Most recent session
  completed_at?: string,                 // When completed (ISO datetime)
  status?: "in_progress" | "completed",  // Current status
  user_id: string | null                 // User UUID
}
```

### Response Examples

#### Scenario 1: User with Completed Profiling ✅
```json
{
  "has_completed_profiling": true,
  "should_skip_onboarding": true,
  "profile_completeness": 100,
  "last_session_id": "prof_abc123xyz",
  "completed_at": "2025-10-04T20:00:00Z",
  "user_id": "user-uuid-here"
}
```
→ **Action:** Skip onboarding, go to `/brainstorm`

#### Scenario 2: User with In-Progress Session 🔄
```json
{
  "has_completed_profiling": false,
  "should_skip_onboarding": false,
  "profile_completeness": 45.5,
  "last_session_id": "prof_xyz789abc",
  "status": "in_progress",
  "user_id": "user-uuid-here"
}
```
→ **Action:** Resume profiling at `/profiling/resume/{session_id}`

#### Scenario 3: New User (No Sessions) 🆕
```json
{
  "has_completed_profiling": false,
  "should_skip_onboarding": false,
  "profile_completeness": 0,
  "last_session_id": null,
  "user_id": "user-uuid-here"
}
```
→ **Action:** Start new profiling at `/profiling/start`

#### Scenario 4: Anonymous User (Not Logged In) 👤
```json
{
  "has_completed_profiling": false,
  "should_skip_onboarding": false,
  "profile_completeness": 0,
  "last_session_id": null,
  "user_id": null
}
```
→ **Action:** Require login or start anonymous profiling

---

## Frontend Integration

### React/Next.js Example

```typescript
import { useRouter } from 'next/router';
import { useEffect } from 'react';

async function checkOnboardingStatus(userToken: string) {
  const response = await fetch('/api/profiling/status', {
    headers: {
      'Authorization': `Bearer ${userToken}`
    }
  });

  return await response.json();
}

function useOnboardingCheck() {
  const router = useRouter();

  useEffect(() => {
    async function checkAndRoute() {
      const user = getCurrentUser(); // Your auth function

      if (!user) {
        router.push('/login');
        return;
      }

      const status = await checkOnboardingStatus(user.token);

      // User completed profiling - skip to main app
      if (status.should_skip_onboarding) {
        router.push('/brainstorm');
      }

      // User has in-progress session - resume
      else if (status.status === 'in_progress') {
        router.push(`/profiling/resume/${status.last_session_id}`);
      }

      // New user - start profiling
      else {
        router.push('/profiling/start');
      }
    }

    checkAndRoute();
  }, []);
}

// Usage in login callback or app initialization
function App() {
  useOnboardingCheck();

  return <YourAppContent />;
}
```

### Vue/Nuxt Example

```javascript
// composables/useOnboarding.js
export function useOnboarding() {
  const router = useRouter();
  const user = useUser(); // Your auth composable

  async function checkOnboardingStatus() {
    const response = await $fetch('/api/profiling/status', {
      headers: {
        Authorization: `Bearer ${user.value.token}`
      }
    });

    if (response.should_skip_onboarding) {
      router.push('/brainstorm');
    } else if (response.status === 'in_progress') {
      router.push(`/profiling/resume/${response.last_session_id}`);
    } else {
      router.push('/profiling/start');
    }
  }

  return { checkOnboardingStatus };
}

// In your login page or app.vue
const { checkOnboardingStatus } = useOnboarding();

onMounted(() => {
  if (user.value) {
    checkOnboardingStatus();
  }
});
```

---

## Database Schema

### profiling_sessions Table

```sql
CREATE TABLE profiling_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),  -- Can be NULL for anonymous
    status VARCHAR(20) NOT NULL,         -- 'in_progress', 'completed', 'abandoned'
    current_question_index INTEGER,
    profile_completeness FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_profiling_sessions_user_status
    ON profiling_sessions(user_id, status);
```

**Key Fields for Skip Logic:**
- `user_id` - Must match logged-in user
- `status` - Must be `'completed'`
- `profile_completeness` - Should be ≥ 0.8 (80%)
- `completed_at` - Timestamp of completion

---

## Backend Logic

### Endpoint Implementation

Located in: `app/api/profiling.py`

```python
@router.get("/status")
async def check_profile_status(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Check if user has completed profiling"""

    if not current_user:
        return {
            "has_completed_profiling": False,
            "should_skip_onboarding": False,
            "profile_completeness": 0,
            "last_session_id": None,
            "user_id": None
        }

    user_id = current_user.get("id")
    supabase = get_supabase()

    # Check for completed sessions
    result = supabase.client.table("profiling_sessions").select("*").eq(
        "user_id", user_id
    ).eq(
        "status", "completed"
    ).order(
        "completed_at", desc=True
    ).limit(1).execute()

    if result.data and len(result.data) > 0:
        session = result.data[0]
        return {
            "has_completed_profiling": True,
            "should_skip_onboarding": True,
            "profile_completeness": session["profile_completeness"] * 100,
            "last_session_id": session["session_id"],
            "completed_at": session["completed_at"],
            "user_id": user_id
        }

    # Check for in-progress sessions
    # ... (similar logic for in_progress)

    # No sessions found
    return {
        "has_completed_profiling": False,
        "should_skip_onboarding": False,
        "profile_completeness": 0,
        "last_session_id": None,
        "user_id": user_id
    }
```

---

## Session Completion Flow

### When User Completes Profiling

1. **WebSocket Handler** detects profile completeness ≥ 80%
   ```python
   if profiling_agent.is_profile_complete(session):
       session.status = ProfilingStatus.COMPLETED
       session.completed_at = datetime.utcnow()
   ```

2. **Save to Database**
   ```python
   await session_service.save_session_to_database(session_id)
   ```

3. **Session Saved** to `profiling_sessions` table with:
   - `status = 'completed'`
   - `profile_completeness = 1.0`
   - `completed_at = {timestamp}`
   - `user_id = {logged_in_user_uuid}`

4. **Next Login** → `/status` returns `should_skip_onboarding: true`

---

## Testing

### Test Scenarios

#### 1. Create Completed Session (Manual)

```python
import asyncio
from app.services.session_service import session_service

async def create_test_session():
    session_data = {
        "session_id": "prof_test_123",
        "user_id": "your-user-uuid-here",
        "status": "completed",
        "current_question_index": 13,
        "profile_completeness": 1.0,
        "completed_at": "2025-10-04T20:00:00Z"
    }

    await session_service.create_session(session_data)
    await session_service.save_session_to_database("prof_test_123")

asyncio.run(create_test_session())
```

#### 2. Test Status Endpoint

```bash
# Without auth (anonymous)
curl http://localhost:8000/api/profiling/status

# With auth (requires valid JWT)
curl http://localhost:8000/api/profiling/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Verify Database

```sql
-- Check all completed sessions
SELECT
    session_id,
    user_id,
    status,
    profile_completeness,
    completed_at
FROM profiling_sessions
WHERE status = 'completed'
ORDER BY completed_at DESC;
```

---

## Important Notes

### ✅ What We DO Use
- `profiling_sessions` table → Source of truth for skip logic
- `status = 'completed'` → Indicates user finished profiling
- `user_id` → Links session to logged-in user

### ❌ What We DON'T Use
- `user_profiles` table → **NOT required** for skip logic
- Seed files → Not needed (sessions created dynamically)
- External state → Everything in database

### 🔄 Session Lifecycle

```
1. User starts profiling
   → POST /api/profiling/start
   → Creates session with status='in_progress'

2. User answers questions
   → WebSocket /ws/{session_id}
   → Updates session in Redis

3. User completes profiling (≥80%)
   → status='completed'
   → Saved to Supabase database

4. User logs in later
   → GET /api/profiling/status
   → Returns should_skip_onboarding=true
```

---

## Troubleshooting

### Issue: Skip not working

**Check:**
1. Session has `user_id` set (not NULL/anonymous)
2. Session `status = 'completed'`
3. Session saved to Supabase (not just Redis)
4. JWT token contains correct `user_id`

**Debug:**
```bash
# Check user's sessions
python -c "
from app.services.supabase_service import get_supabase, init_supabase
init_supabase()
supabase = get_supabase()
result = supabase.client.table('profiling_sessions').select('*').eq('user_id', 'YOUR_USER_ID').execute()
print(result.data)
"
```

### Issue: Session not saved

**Check:**
```python
# Verify save_session_to_database was called
# Look for log: "✅ Saved session {session_id} to Supabase"

# Check Redis vs Supabase
await session_service.get_session(session_id)  # Redis
supabase.client.table("profiling_sessions").select("*").eq("session_id", session_id)  # Supabase
```

---

## Summary

✅ **Simple Logic:** Check `profiling_sessions.status = 'completed'`
✅ **No Extra Tables:** Don't need `user_profiles` for skip
✅ **Automatic:** Sessions saved on completion
✅ **Frontend-Friendly:** Single endpoint, clear responses
✅ **Flexible:** Supports anonymous, in-progress, and completed states

**Next Steps:**
1. Implement frontend routing based on `/status` response
2. Test with real user authentication
3. Add error handling for edge cases
4. Monitor session completion rates
