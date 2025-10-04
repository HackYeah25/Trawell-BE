"""
Profiling API - User profiling with interactive questions and WebSocket support
"""
import asyncio
import uuid
from typing import Dict, List, Optional
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
from app.services.supabase import get_supabase
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/profiling", tags=["profiling"])


class ProfilingConnectionManager:
    """Manages WebSocket connections for profiling sessions"""

    def __init__(self):
        # session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket to a profiling session"""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Disconnect a WebSocket from a profiling session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_to_session(self, session_id: str, message: dict):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                print(f"Error sending to websocket: {e}")
                self.disconnect(session_id)


manager = ProfilingConnectionManager()


# In-memory storage for profiling sessions (in production, use database)
# session_id -> ProfilingSession
profiling_sessions: Dict[str, ProfilingSession] = {}

# session_id -> List[ProfilingMessage]
profiling_conversations: Dict[str, List[ProfilingMessage]] = {}


# API Endpoints
@router.get("/questions")
async def get_profiling_questions() -> GetQuestionsResponse:
    """Get all profiling questions (for frontend to display)"""
    questions = profiling_agent.get_all_questions()
    critical = profiling_agent.get_critical_questions()

    return GetQuestionsResponse(
        questions=questions, total_count=len(questions), critical_questions=critical
    )


@router.post("/start")
async def start_profiling(
    request: StartProfilingRequest,
    current_user: Optional[dict] = Depends(get_current_user),
) -> StartProfilingResponse:
    """Start a new profiling session"""
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

    profiling_sessions[session_id] = session
    profiling_conversations[session_id] = []

    intro_message = profiling_agent.get_intro_message()

    # Add intro message to conversation
    profiling_conversations[session_id].append(
        ProfilingMessage(role="assistant", content=intro_message)
    )

    websocket_url = f"/api/profiling/ws/{session_id}"

    return StartProfilingResponse(
        session=session, first_message=intro_message, websocket_url=websocket_url
    )


@router.get("/session/{session_id}")
async def get_profiling_session(session_id: str) -> ProfilingSessionResponse:
    """Get profiling session details"""
    if session_id not in profiling_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = profiling_sessions[session_id]
    next_question = profiling_agent.get_next_question(session)
    is_complete = profiling_agent.is_profile_complete(session)

    return ProfilingSessionResponse(
        session=session, next_question=next_question, is_complete=is_complete
    )


@router.post("/session/{session_id}/abandon")
async def abandon_profiling_session(session_id: str):
    """Abandon a profiling session"""
    if session_id not in profiling_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = profiling_sessions[session_id]
    session.status = ProfilingStatus.ABANDONED

    return {"message": "Session abandoned", "session": session}


# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def profiling_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket endpoint for profiling conversation"""

    # Verify session exists
    if session_id not in profiling_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return

    session = profiling_sessions[session_id]

    # Connect WebSocket
    await manager.connect(websocket, session_id)

    # Send current question
    current_question = profiling_agent.get_next_question(session)
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
    session = profiling_sessions[session_id]
    current_question = profiling_agent.get_next_question(session)

    if not current_question:
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

    # Add user message to conversation
    profiling_conversations[session_id].append(
        ProfilingMessage(role="user", content=answer)
    )

    # Send thinking indicator
    await manager.send_to_session(
        session_id, WSProfilingThinking(conversation_id=session_id).model_dump()
    )

    # Validate answer
    validation_status, feedback, extracted_value = await profiling_agent.validate_answer(
        current_question, answer, session
    )

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

    # Check if profiling is complete
    if profiling_agent.is_profile_complete(session):
        session.status = ProfilingStatus.COMPLETED
        session.completed_at = datetime.utcnow()

        # Extract and save user profile
        user_profile = profiling_agent.extract_user_profile(session)

        # Save to database
        supabase = get_supabase()
        if supabase.client and session.user_id:
            try:
                await supabase.create_user_profile(user_profile)
            except Exception as e:
                print(f"Error saving profile: {e}")

        # Send completion message
        completion_msg = profiling_agent.get_completion_message()
        await stream_ai_message(session_id, completion_msg)

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
            await stream_ai_message(session_id, next_question.question)

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


async def stream_ai_message(session_id: str, message: str):
    """Stream AI message token by token"""
    # Add to conversation
    profiling_conversations[session_id].append(
        ProfilingMessage(role="assistant", content=message)
    )

    # Stream tokens
    for token in message.split():
        await manager.send_to_session(
            session_id,
            WSProfilingToken(conversation_id=session_id, token=token + " ").model_dump(),
        )
        await asyncio.sleep(0.02)  # Small delay for better UX

    # Send complete message
    await manager.send_to_session(
        session_id,
        WSProfilingMessage(
            conversation_id=session_id, role="assistant", content=message
        ).model_dump(),
    )
