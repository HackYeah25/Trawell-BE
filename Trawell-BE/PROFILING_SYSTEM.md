# User Profiling System

## Overview

System profilowania użytkowników z dynamicznymi pytaniami, walidacją odpowiedzi przez AI i komunikacją przez WebSocket.

## Architecture

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ WebSocket
       ▼
┌─────────────────────────────────────┐
│     Profiling API & WebSocket       │
│  /api/profiling/*                   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Profiling Agent (LangChain)      │
│  - Question management              │
│  - Answer validation                │
│  - Follow-up generation             │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Questions Config (YAML)           │
│  app/prompts/profiling.yaml         │
│  - 13 questions                     │
│  - Validation rules                 │
│  - Follow-up prompts                │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│       Supabase Database             │
│  - profiling_sessions               │
│  - profiling_responses              │
│  - profiling_messages               │
│  - user_profiles                    │
└─────────────────────────────────────┘
```

## Flow Diagram

```
1. User Login/Start
   │
   ▼
2. POST /api/profiling/start
   ├─ Creates ProfilingSession
   ├─ Returns WebSocket URL
   └─ Returns intro message
   │
   ▼
3. WebSocket Connection
   ws://localhost:8000/api/profiling/ws/{session_id}
   │
   ▼
4. First Question Sent
   ├─ Question from profiling.yaml
   ├─ Progress indicator (1/13)
   └─ Completeness: 0%
   │
   ▼
5. User Answers ──────────────┐
   │                          │
   ▼                          │
6. AI Validation              │
   ├─ Sufficient? ────YES────>│
   │                          │
   └─ Insufficient?           │
       │                      │
       ▼                      │
   7. Follow-up Question      │
       │                      │
       └──────────────────────┘
                              │
                              ▼
                         8. Next Question
                              │
                              ▼
                         9. Repeat 5-8
                              │
                              ▼
                    10. Profile Complete (80%+)
                              │
                              ▼
                    11. Extract UserProfile
                              │
                              ▼
                    12. Save to user_profiles table
                              │
                              ▼
                    13. Ready for Brainstorm
```

## Components

### 1. YAML Configuration (`app/prompts/profiling.yaml`)

**13 Questions** organized by category:

#### Core Preferences (7 questions)
- `traveler_type` - Explorer/Relaxer/Mixed
- `activity_level` - High/Medium/Low
- `accommodation` - All-inclusive/Boutique/Hostel/Mixed
- `environment` - City/Nature/Beach/Mountains/Mixed
- `budget_sensitivity` - High/Medium/Low
- `culture_interest` - High/Medium/Low
- `food_importance` - High/Medium/Low

#### Constraints (4 questions)
- `dietary_restrictions` - List of restrictions
- `mobility_accessibility` - Accessibility needs
- `climate_preference` - Hot/Mild/Cool/No preference
- `language_comfort` - Language preferences

#### Experience (2 questions)
- `past_destinations` - Previous trips and insights
- `wishlist_regions` - Dream destinations

**Validation Rules** for each question:
```yaml
validation:
  min_tokens: 5
  required_info:
    - "Activity preference indicator"
  examples_if_unclear:
    - "For example: hiking vs beach lounging"
  follow_up_questions:
    - condition: "vague"
      question: "Can you tell me more?"
```

**Critical Questions** (must be answered):
- traveler_type
- activity_level
- environment
- budget_sensitivity

**Minimum Completeness**: 80% (10/13 questions)

### 2. Data Models (`app/models/profiling.py`)

#### ProfilingSession
```python
{
    "session_id": "prof_abc123",
    "user_id": "uuid",
    "status": "in_progress",
    "current_question_index": 3,
    "responses": [...],
    "profile_completeness": 0.25,
    "created_at": "...",
    "updated_at": "...",
    "completed_at": null
}
```

#### ProfilingQuestionResponse
```python
{
    "question_id": "traveler_type",
    "user_answer": "I love exploring...",
    "validation_status": "sufficient",
    "extracted_value": "explorer",
    "follow_up_count": 0,
    "answered_at": "..."
}
```

#### QuestionValidationStatus
- `NOT_ANSWERED` - Not yet answered
- `INSUFFICIENT` - Too vague, needs follow-up
- `SUFFICIENT` - Minimum info provided
- `COMPLETE` - Detailed answer

### 3. Profiling Agent (`app/agents/profiling_agent.py`)

**Key Methods:**

```python
class ProfilingAgent:
    async def validate_answer(
        question: ProfilingQuestion,
        answer: str,
        session: ProfilingSession
    ) -> tuple[Status, Feedback, ExtractedValue]

    async def generate_follow_up(
        question: ProfilingQuestion,
        answer: str,
        follow_up_count: int
    ) -> str

    def calculate_completeness(
        session: ProfilingSession
    ) -> float

    def is_profile_complete(
        session: ProfilingSession
    ) -> bool

    def extract_user_profile(
        session: ProfilingSession
    ) -> UserProfile
```

**Validation Process:**
1. Check minimum token count
2. Use LLM to validate against required_info
3. Extract structured value from answer
4. Return validation status + feedback

**Follow-up Logic:**
- Max 3 follow-ups per question
- Uses predefined follow-ups from YAML
- Falls back to LLM-generated follow-ups
- After max attempts, accepts answer and moves on

### 4. API Endpoints (`app/api/profiling.py`)

#### REST Endpoints

```
GET  /api/profiling/questions
     → Get all questions (for frontend)

POST /api/profiling/start
     → Start profiling session
     ← { session, first_message, websocket_url }

GET  /api/profiling/session/{session_id}
     → Get session details
     ← { session, next_question, is_complete }

POST /api/profiling/session/{session_id}/abandon
     → Mark session as abandoned
```

#### WebSocket Endpoint

```
WS /api/profiling/ws/{session_id}
```

**Message Types (Server → Client):**

1. **profiling_message** - AI/User message
```json
{
    "type": "profiling_message",
    "conversation_id": "prof_123",
    "role": "assistant",
    "content": "What kind of traveler are you?",
    "timestamp": "..."
}
```

2. **profiling_progress** - Progress update
```json
{
    "type": "profiling_progress",
    "conversation_id": "prof_123",
    "current_question": 3,
    "total_questions": 13,
    "completeness": 0.23,
    "current_question_id": "accommodation"
}
```

3. **profiling_validation** - Validation feedback
```json
{
    "type": "profiling_validation",
    "conversation_id": "prof_123",
    "question_id": "traveler_type",
    "status": "insufficient",
    "feedback": "Could you provide more detail?"
}
```

4. **profiling_thinking** - AI is thinking
```json
{
    "type": "profiling_thinking",
    "conversation_id": "prof_123"
}
```

5. **profiling_token** - Streaming token
```json
{
    "type": "profiling_token",
    "conversation_id": "prof_123",
    "token": "I'd "
}
```

6. **profiling_complete** - Profiling finished
```json
{
    "type": "profiling_complete",
    "conversation_id": "prof_123",
    "profile_id": "user_123",
    "completeness": 1.0,
    "message": "Your profile is complete!"
}
```

**Message Types (Client → Server):**

```json
{
    "type": "user_answer",
    "answer": "I prefer active exploring..."
}
```

### 5. Database Schema

#### profiling_sessions
```sql
- id (UUID, PK)
- session_id (VARCHAR, UNIQUE)
- user_id (UUID, FK → users)
- status (VARCHAR) -- not_started, in_progress, completed, abandoned
- current_question_index (INTEGER)
- profile_completeness (FLOAT)
- created_at, updated_at, completed_at (TIMESTAMP)
```

#### profiling_responses
```sql
- id (UUID, PK)
- session_id (VARCHAR, FK)
- question_id (VARCHAR)
- user_answer (TEXT)
- validation_status (VARCHAR)
- extracted_value (JSONB)
- follow_up_count (INTEGER)
- answered_at (TIMESTAMP)
- UNIQUE(session_id, question_id)
```

#### profiling_messages
```sql
- id (UUID, PK)
- session_id (VARCHAR, FK)
- role (VARCHAR) -- 'assistant' or 'user'
- content (TEXT)
- metadata (JSONB)
- created_at (TIMESTAMP)
```

**Database Functions:**

1. `calculate_profile_completeness(session_id)` - Auto-calculates completeness
2. `complete_profiling_session(session_id)` - Marks complete + creates UserProfile

**Triggers:**
- Auto-update `profile_completeness` on response insert/update
- Auto-update `updated_at` on session changes

## Frontend Integration

### 1. Start Profiling Session

```javascript
const response = await fetch('/api/profiling/start', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer TOKEN' },
    body: JSON.stringify({
        user_id: 'user_123' // optional
    })
});

const { session, first_message, websocket_url } = await response.json();
```

### 2. Connect WebSocket

```javascript
const ws = new WebSocket(`ws://localhost:8000${websocket_url}`);

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    switch(message.type) {
        case 'profiling_message':
            displayMessage(message.role, message.content);
            break;

        case 'profiling_progress':
            updateProgressBar(message.completeness);
            updateQuestionCounter(
                message.current_question,
                message.total_questions
            );
            break;

        case 'profiling_validation':
            if (message.status === 'insufficient') {
                showValidationError(message.feedback);
            } else {
                showValidationSuccess();
            }
            break;

        case 'profiling_thinking':
            showThinkingIndicator();
            break;

        case 'profiling_token':
            appendToken(message.token);
            break;

        case 'profiling_complete':
            onProfilingComplete(message.profile_id);
            break;
    }
};
```

### 3. Send User Answer

```javascript
function sendAnswer(answer) {
    ws.send(JSON.stringify({
        type: 'user_answer',
        answer: answer
    }));
}
```

### 4. UI/UX Recommendations

**Progress Indicator:**
```
Question 3 of 13
[████████░░░░░░░░░░] 23%
```

**Question Display:**
```
┌─────────────────────────────────────┐
│ What kind of traveler are you?      │
│                                     │
│ 🏃 Active explorer                  │
│ 🧘 Relaxed vacationer               │
│ 🔀 Mix of both                      │
│                                     │
│ [User input field]                  │
└─────────────────────────────────────┘
```

**Validation Feedback:**
```
✗ Could you provide more detail?

Suggestion: Think about your last vacation -
were you exploring most days or relaxing?
```

**Completion:**
```
🎉 Your profile is complete!

We've learned all about your travel style.
Ready to discover your perfect destination?

[Start Brainstorming] →
```

## Example Flow

### Complete Conversation Example

```
[SYSTEM] → Welcome! I'm excited to help you discover amazing destinations...

[SYSTEM] → What kind of traveler are you?
          🏃 Active explorer | 🧘 Relaxed | 🔀 Mix

[USER]   → I like to explore

[SYSTEM] → [THINKING...]

[SYSTEM] → [VALIDATION: INSUFFICIENT]
          Can you tell me more? Do you prefer hiking and activities,
          or more relaxed exploration like city walks?

[USER]   → I love hiking, trying local food, and visiting museums

[SYSTEM] → [VALIDATION: SUFFICIENT] ✓
          [PROGRESS: 1/13 - 8%]

[SYSTEM] → Great! How active do you like your trips to be?
          🥾 High | 🚶 Medium | 🛋️ Low

[USER]   → High activity - I can hike all day!

[SYSTEM] → [VALIDATION: SUFFICIENT] ✓
          [PROGRESS: 2/13 - 15%]

[continues for all 13 questions...]

[SYSTEM] → Fantastic! 🎉 Your profile is complete!
          Ready to start brainstorming your next adventure?
```

## Configuration & Deployment

### Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-sonnet-20240229
```

### Run Migration

```bash
# Using Supabase CLI
supabase db push

# Or manually in Supabase SQL Editor
# Run: supabase/migrations/002_profiling_sessions.sql
```

### Enable Realtime (Optional)

In Supabase Dashboard → Database → Replication:
```sql
ALTER PUBLICATION supabase_realtime ADD TABLE profiling_sessions;
ALTER PUBLICATION supabase_realtime ADD TABLE profiling_responses;
ALTER PUBLICATION supabase_realtime ADD TABLE profiling_messages;
```

## Testing

### Manual Testing

1. **Start session:**
```bash
curl -X POST http://localhost:8000/api/profiling/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": null}'
```

2. **Get questions:**
```bash
curl http://localhost:8000/api/profiling/questions
```

3. **WebSocket (using wscat):**
```bash
npm install -g wscat
wscat -c ws://localhost:8000/api/profiling/ws/prof_abc123

# Send answer
> {"type": "user_answer", "answer": "I love exploring"}
```

### Key Features to Test

- [ ] All 13 questions load from YAML
- [ ] Critical questions enforced
- [ ] Validation catches vague answers
- [ ] Follow-up questions generated
- [ ] Max 3 follow-ups respected
- [ ] Progress calculation accurate
- [ ] 80% completeness threshold works
- [ ] UserProfile extracted correctly
- [ ] Database saves session/responses
- [ ] WebSocket streams properly
- [ ] Anonymous users supported

## Monitoring & Logs

```python
# Check session status
SELECT session_id, status, profile_completeness, current_question_index
FROM profiling_sessions
WHERE user_id = 'user_123'
ORDER BY created_at DESC;

# Check responses
SELECT question_id, validation_status, follow_up_count
FROM profiling_responses
WHERE session_id = 'prof_abc123'
ORDER BY answered_at;

# Average completeness
SELECT AVG(profile_completeness) as avg_completeness
FROM profiling_sessions
WHERE status = 'completed';

# Completion rate
SELECT
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM profiling_sessions
GROUP BY status;
```

## Future Enhancements

1. **Adaptive Questioning**
   - Skip irrelevant questions based on previous answers
   - Dynamic question ordering

2. **Multi-language Support**
   - Translate questions via YAML
   - Detect user language

3. **Voice Input**
   - Speech-to-text integration
   - Natural conversation flow

4. **Profile Evolution**
   - Update profile after trips
   - Learn from user behavior

5. **Social Profiling**
   - Import from social media
   - Travel style compatibility matching

6. **A/B Testing**
   - Test different question phrasings
   - Optimize completion rates

## Troubleshooting

**Issue: WebSocket not connecting**
- Check session_id exists
- Verify CORS settings
- Check firewall/proxy

**Issue: Validation always insufficient**
- Check ANTHROPIC_API_KEY
- Verify Claude model access
- Check prompt formatting

**Issue: Profile not saving**
- Verify user_id in session
- Check database permissions
- Review RLS policies

**Issue: Questions not loading**
- Check YAML file path
- Verify YAML syntax
- Check file permissions

## API Documentation

Full API documentation available at:
```
http://localhost:8000/docs#tag/Profiling
```

Interactive WebSocket testing:
```
http://localhost:8000/redoc
```
