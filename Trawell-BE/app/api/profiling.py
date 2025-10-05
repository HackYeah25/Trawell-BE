"""
Profiling API - User profiling with interactive questions and WebSocket support
"""
import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.profiling import (
    ProfilingSession,
    ProfilingStatus,
    ProfilingQuestion,
    ProfilingQuestionResponse,
    QuestionValidationStatus,
    ProfilingMessage,
    StartProfilingRequest,
    StartProfilingResponse,
    GetQuestionsResponse,
    ProfilingSessionResponse,
    WSProfilingMessage,
    WSProfilingProgress,
    WSProfilingValidation,
    WSProfilingComplete,
    WSProfilingThinking,
    WSProfilingToken,
)
from app.agents.profiling_agent import profiling_agent
from app.services.supabase_service import get_supabase
from app.services.session_service import session_service
from app.api.deps import get_current_user_optional

router = APIRouter(prefix="/api/profiling", tags=["profiling"])


class ProfilingConnectionManager:
    """Manages WebSocket connections for profiling sessions"""

    def __init__(self):
        # session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket to a profiling session"""
        # Close existing connection if any
        if session_id in self.active_connections:
            try:
                old_ws = self.active_connections[session_id]
                await old_ws.close(code=1000, reason="New connection established")
                print(f"DEBUG: Closed old WebSocket for session {session_id}")
            except Exception as e:
                print(f"DEBUG: Error closing old WebSocket: {e}")

        await websocket.accept()
        self.active_connections[session_id] = websocket
        print(f"DEBUG: WebSocket connected for session {session_id}")

    def disconnect(self, session_id: str):
        """Disconnect a WebSocket from a profiling session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_to_session(self, session_id: str, message: dict):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                # Ensure data is JSON serializable
                import json
                # Convert datetime objects to strings
                serializable_message = json.loads(json.dumps(message, default=str))
                await self.active_connections[session_id].send_json(serializable_message)

                # Debug log (only for non-token messages to avoid spam)
                if message.get('type') != 'profiling_token':
                    print(f"DEBUG: Sent {message.get('type')} to session {session_id}")
            except Exception as e:
                print(f"ERROR: Error sending {message.get('type')} to websocket for session {session_id}: {e}")
                # Clean up disconnected websocket
                self.disconnect(session_id)
        else:
            print(f"WARNING: No active connection for session {session_id} to send {message.get('type')}")


manager = ProfilingConnectionManager()


# Redis-based session storage (replaces in-memory storage)
async def get_session(session_id: str) -> Optional[ProfilingSession]:
    """Get session from Redis"""
    session_data = await session_service.get_session(session_id)
    if session_data:
        return ProfilingSession(**session_data)
    return None


async def save_session(session: ProfilingSession) -> bool:
    """Save session to Redis"""
    return await session_service.update_session(session.session_id, session.model_dump())


async def create_session(session: ProfilingSession) -> str:
    """Create new session in Redis"""
    return await session_service.create_session(session.model_dump())


async def add_message_to_conversation(session_id: str, message: ProfilingMessage) -> bool:
    """Add message to conversation history"""
    return await session_service.add_message_to_conversation(
        session_id, 
        message.model_dump()
    )


async def get_conversation(session_id: str) -> List[ProfilingMessage]:
    """Get conversation history"""
    conversation_data = await session_service.get_conversation(session_id)
    return [ProfilingMessage(**msg) for msg in conversation_data]


# API Endpoints
@router.get("/status")
async def check_profile_status(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Check if user has completed profiling by looking at profiling_sessions table

    A user is considered "profiled" if they have ANY completed profiling session,
    regardless of whether user_profiles table has data.

    Returns:
        has_completed_profiling: bool - Whether user has completed profiling
        should_skip_onboarding: bool - Whether to skip onboarding flow
        profile_completeness: float - Completeness percentage (0-100)
        last_session_id: str - ID of most recent completed session (if any)
    """
    # Anonymous users - no completed profiling
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

    try:
        # Check profiling_sessions table for completed sessions
        if supabase.client:
            result = supabase.client.table("profiling_sessions").select("*").eq(
                "user_id", user_id
            ).eq(
                "status", "completed"
            ).order(
                "completed_at", desc=True
            ).limit(1).execute()

            if result.data and len(result.data) > 0:
                # User has at least one completed profiling session
                session = result.data[0]
                return {
                    "has_completed_profiling": True,
                    "should_skip_onboarding": True,
                    "profile_completeness": session.get("profile_completeness", 1.0) * 100,
                    "last_session_id": session["session_id"],
                    "completed_at": session.get("completed_at"),
                    "user_id": user_id
                }
            else:
                # Check if user has any in-progress session
                in_progress = supabase.client.table("profiling_sessions").select("*").eq(
                    "user_id", user_id
                ).eq(
                    "status", "in_progress"
                ).order(
                    "updated_at", desc=True
                ).limit(1).execute()

                if in_progress.data and len(in_progress.data) > 0:
                    session = in_progress.data[0]
                    return {
                        "has_completed_profiling": False,
                        "should_skip_onboarding": False,
                        "profile_completeness": session.get("profile_completeness", 0) * 100,
                        "last_session_id": session["session_id"],
                        "status": "in_progress",
                        "user_id": user_id
                    }
                else:
                    # No profiling sessions at all
                    return {
                        "has_completed_profiling": False,
                        "should_skip_onboarding": False,
                        "profile_completeness": 0,
                        "last_session_id": None,
                        "user_id": user_id
                    }
        else:
            raise Exception("Supabase client not initialized")

    except Exception as e:
        print(f"ERROR checking profile status: {e}")
        return {
            "has_completed_profiling": False,
            "should_skip_onboarding": False,
            "profile_completeness": 0,
            "error": str(e),
            "user_id": user_id
        }


@router.delete("/profile/reset")
async def reset_user_profile(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Reset user profile - deletes profile from database
    Allows user to go through onboarding again

    Returns:
        success: bool
        message: str
    """
    TEST_USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

    # Allow test user even without auth for development
    if not current_user:
        user_id = TEST_USER_ID
        print(f"DEBUG: No auth, using test user_id for reset: {user_id}")
    else:
        user_id = current_user.get("id") or TEST_USER_ID

    supabase = get_supabase()

    try:
        # Delete user profile from database
        if supabase.client:
            # Delete from user_profiles table
            supabase.client.table("user_profiles").delete().eq("user_id", user_id).execute()

            # Also delete any profiling sessions
            supabase.client.table("profiling_sessions").delete().eq("user_id", user_id).execute()

            print(f"✅ Deleted profile for user {user_id}")
            return {
                "success": True,
                "message": "Profile reset successfully. You can now complete onboarding again.",
                "user_id": user_id
            }
        else:
            raise HTTPException(status_code=500, detail="Database not available")

    except Exception as e:
        print(f"ERROR resetting profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset profile: {str(e)}")


@router.get("/questions")
async def get_profiling_questions():
    """Get all profiling questions (for frontend to display)"""
    questions = profiling_agent.get_all_questions()

    # Transform to frontend format
    frontend_questions = [
        {
            "id": q.id,
            "markdownQuestion": q.question
        }
        for q in questions
    ]

    return frontend_questions


@router.post("/start")
async def start_profiling(
    request: StartProfilingRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
) -> StartProfilingResponse:
    """Start a new profiling session"""
    try:
        session_id = f"prof_{uuid.uuid4().hex[:12]}"
        user_id = request.user_id or (current_user.get("id") if current_user else None)

        session = ProfilingSession(
            session_id=session_id,
            user_id=user_id,
            status=ProfilingStatus.IN_PROGRESS,
            current_question_index=0,
            responses=[],
            profile_completeness=0.0,
        )

        # Create session in Redis
        await create_session(session)

        print(f"DEBUG: Created session {session_id}, total sessions: Redis")

        intro_message = profiling_agent.get_intro_message()

        # Add intro message to conversation
        intro_msg = ProfilingMessage(role="assistant", content=intro_message)
        await add_message_to_conversation(session_id, intro_msg)

        websocket_url = f"/api/profiling/ws/{session_id}"

        return StartProfilingResponse(
            session=session, first_message=intro_message, websocket_url=websocket_url
        )
    except Exception as e:
        print(f"ERROR: Failed to start profiling session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start profiling session: {str(e)}")


@router.get("/session/{session_id}")
async def get_profiling_session(session_id: str) -> ProfilingSessionResponse:
    """Get profiling session details"""
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    next_question = profiling_agent.get_next_question(session)
    is_complete = profiling_agent.is_profile_complete(session)

    return ProfilingSessionResponse(
        session=session, next_question=next_question, is_complete=is_complete
    )


@router.post("/session/{session_id}/abandon")
async def abandon_profiling_session(session_id: str):
    """Abandon a profiling session"""
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = ProfilingStatus.ABANDONED
    await save_session(session)

    return {"message": "Session abandoned", "session": session}


# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def profiling_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket endpoint for profiling conversation"""

    # Verify session exists in Redis BEFORE accepting
    session = await get_session(session_id)
    if not session:
        # Accept first, then close with reason
        await websocket.accept()
        await websocket.close(code=1008, reason="Session not found")
        return

    # Connect WebSocket (this accepts the connection)
    await manager.connect(websocket, session_id)

    # Send current question
    current_question = profiling_agent.get_next_question(session)
    print(f"DEBUG: Sending first question to {session_id}: {current_question.id if current_question else 'None'}")

    if current_question:
        await manager.send_to_session(
            session_id,
            WSProfilingMessage(
                conversation_id=session_id,
                role="assistant",
                content=current_question.question,
            ).model_dump(),
        )

        # Send progress
        await manager.send_to_session(
            session_id,
            WSProfilingProgress(
                conversation_id=session_id,
                current_question=session.current_question_index + 1,
                total_questions=len(profiling_agent.questions),
                completeness=session.profile_completeness,
                current_question_id=current_question.id,
            ).model_dump(),
        )

    try:
        while True:
            # Receive message from user
            data = await websocket.receive_json()

            if data.get("type") == "user_answer":
                await handle_user_answer(session_id, data["answer"])

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)


async def handle_user_answer(session_id: str, answer: str):
    """Process user's answer to current question"""
    print(f"DEBUG: Handling answer for session {session_id}: {answer[:50]}...")

    session = await get_session(session_id)
    if not session:
        print(f"ERROR: Session {session_id} not found in Redis")
        return

    current_question = profiling_agent.get_next_question(session)

    if not current_question:
        print(f"DEBUG: Profiling already complete for {session_id}")
        # Already complete
        await manager.send_to_session(
            session_id,
            WSProfilingComplete(
                conversation_id=session_id,
                profile_id=session.user_id or session.session_id,
                completeness=session.profile_completeness,
                message=profiling_agent.get_completion_message(),
            ).model_dump(),
        )
        return

    print(f"DEBUG: Current question: {current_question.id}, index: {session.current_question_index}")

    # Add user message to conversation
    user_msg = ProfilingMessage(role="user", content=answer)
    await add_message_to_conversation(session_id, user_msg)

    # Send thinking indicator
    await manager.send_to_session(
        session_id, WSProfilingThinking(conversation_id=session_id).model_dump()
    )

    print(f"DEBUG: Validating answer with LLM...")
    # Validate answer
    validation_status, feedback, extracted_value = await profiling_agent.validate_answer(
        current_question, answer, session
    )
    print(f"DEBUG: Validation result: {validation_status}, feedback: {feedback}")

    # Check if this question already has responses
    existing_response = None
    for resp in session.responses:
        if resp.question_id == current_question.id:
            existing_response = resp
            break

    if validation_status == QuestionValidationStatus.INSUFFICIENT:
        # Answer is insufficient - ask for more details
        follow_up_count = existing_response.follow_up_count if existing_response else 0

        follow_up = await profiling_agent.generate_follow_up(
            current_question, answer, follow_up_count
        )

        if follow_up:
            # Send follow-up question
            response_text = f"{feedback}\n\n{follow_up}" if feedback else follow_up

            # Update or create response
            if existing_response:
                existing_response.follow_up_count += 1
            else:
                session.responses.append(
                    ProfilingQuestionResponse(
                        question_id=current_question.id,
                        user_answer=answer,
                        validation_status=validation_status,
                        follow_up_count=1,
                    )
                )

            # Save session to Redis
            await save_session(session)

            # Stream follow-up
            await stream_ai_message(session_id, response_text)

            # Send validation status
            await manager.send_to_session(
                session_id,
                WSProfilingValidation(
                    conversation_id=session_id,
                    question_id=current_question.id,
                    status=validation_status,
                    feedback=feedback,
                ).model_dump(),
            )
        else:
            # Max follow-ups reached - accept answer and move on
            validation_status = QuestionValidationStatus.SUFFICIENT
            await process_sufficient_answer(
                session_id, session, current_question, answer, extracted_value
            )
    else:
        # Answer is sufficient or complete
        await process_sufficient_answer(
            session_id, session, current_question, answer, extracted_value
        )


async def process_sufficient_answer(
    session_id: str,
    session: ProfilingSession,
    question: ProfilingQuestion,
    answer: str,
    extracted_value: Any,
):
    """Process a sufficient answer and move to next question"""
    # Update or create response
    existing_response = None
    for resp in session.responses:
        if resp.question_id == question.id:
            existing_response = resp
            break

    if existing_response:
        existing_response.validation_status = QuestionValidationStatus.SUFFICIENT
        existing_response.extracted_value = extracted_value
        existing_response.user_answer = answer
    else:
        session.responses.append(
            ProfilingQuestionResponse(
                question_id=question.id,
                user_answer=answer,
                validation_status=QuestionValidationStatus.SUFFICIENT,
                extracted_value=extracted_value,
            )
        )

    # Save session to Redis
    await save_session(session)

    # Send validation success
    await manager.send_to_session(
        session_id,
        WSProfilingValidation(
            conversation_id=session_id,
            question_id=question.id,
            status=QuestionValidationStatus.SUFFICIENT,
            feedback=None,
        ).model_dump(),
    )

    # Move to next question
    session.current_question_index += 1
    session.profile_completeness = profiling_agent.calculate_completeness(session)
    session.updated_at = datetime.utcnow()

    # Save session to Redis after updating
    await save_session(session)

    # Check if profiling is complete
    if profiling_agent.is_profile_complete(session):
        session.status = ProfilingStatus.COMPLETED
        session.completed_at = datetime.utcnow()

        # Save final session state
        await save_session(session)

        # Save session to Supabase database
        await session_service.save_session_to_database(session_id)

        # Extract and save user profile
        user_profile = profiling_agent.extract_user_profile(session)

        # Save to database
        supabase = get_supabase()
        if supabase.client and session.user_id:
            try:
                existing = await supabase.get_user_profile(session.user_id)
                if existing:
                    await supabase.update_user_profile(session.user_id, user_profile)
                else:
                    await supabase.create_user_profile(user_profile)
            except Exception as e:
                print(f"Error saving profile: {e}")

        # Send completion message
        completion_msg = profiling_agent.get_completion_message()
        await send_question_message(session_id, completion_msg)

        await manager.send_to_session(
            session_id,
            WSProfilingComplete(
                conversation_id=session_id,
                profile_id=session.user_id or session.session_id,
                completeness=session.profile_completeness,
                message=completion_msg,
            ).model_dump(),
        )
    else:
        # Get next question
        next_question = profiling_agent.get_next_question(session)
        if next_question:
            # Send question directly (not streaming for pre-defined questions)
            await send_question_message(session_id, next_question.question)

            # Send progress
            await manager.send_to_session(
                session_id,
                WSProfilingProgress(
                    conversation_id=session_id,
                    current_question=session.current_question_index + 1,
                    total_questions=len(profiling_agent.questions),
                    completeness=session.profile_completeness,
                    current_question_id=next_question.id,
                ).model_dump(),
            )


async def send_question_message(session_id: str, question: str):
    """Send a pre-defined question without LLM streaming"""
    # Add to conversation
    await add_message_to_conversation(
        session_id,
        ProfilingMessage(role="assistant", content=question)
    )

    # Send complete message
    await manager.send_to_session(
        session_id,
        WSProfilingMessage(
            conversation_id=session_id, role="assistant", content=question
        ).model_dump(),
    )


async def stream_ai_message(session_id: str, follow_up_prompt: str):
    """Stream AI-generated follow-up message using LLM"""
    session = await get_session(session_id)
    if not session:
        return

    # Build conversation history for context
    conversation = await get_conversation(session_id)

    # Stream response from LLM for follow-up
    full_response = ""

    try:
        # Get current question context
        current_question = profiling_agent.get_next_question(session)
        if not current_question:
            return

        # Build prompt for LLM to generate natural follow-up
        system_prompt = f"""You are a friendly travel assistant asking follow-up questions.

Current question context: {current_question.context}
Original question: {current_question.question}

The user gave an answer that needs more detail. Generate a friendly, natural follow-up question.
Keep it conversational and encouraging. Be specific about what information you need.

Follow-up guidance: {follow_up_prompt}
"""

        # Create messages for LLM
        from langchain.schema import SystemMessage, HumanMessage

        messages = [SystemMessage(content=system_prompt)]

        # Add recent conversation for context (last 3 messages)
        for msg in conversation[-3:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))

        # Stream response
        print(f"DEBUG: Starting LLM stream for session {session_id}")
        token_count = 0
        async for chunk in profiling_agent.llm.astream(messages):
            if hasattr(chunk, "content") and chunk.content:
                token_count += 1
                full_response += chunk.content
                await manager.send_to_session(
                    session_id,
                    WSProfilingToken(conversation_id=session_id, token=chunk.content).model_dump(),
                )
                await asyncio.sleep(0.01)
        print(f"DEBUG: Streamed {token_count} tokens, full response: {full_response[:100]}...")

    except Exception as e:
        print(f"ERROR: Error streaming from LLM: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to simple message
        full_response = follow_up_prompt
        for token in follow_up_prompt.split():
            await manager.send_to_session(
                session_id,
                WSProfilingToken(conversation_id=session_id, token=token + " ").model_dump(),
            )
            await asyncio.sleep(0.02)

    # Add to conversation
    await add_message_to_conversation(
        session_id,
        ProfilingMessage(role="assistant", content=full_response)
    )

    # Send complete message
    await manager.send_to_session(
        session_id,
        WSProfilingMessage(
            conversation_id=session_id, role="assistant", content=full_response
        ).model_dump(),
    )
