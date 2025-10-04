"""
Brainstorm API - Destination discovery with LangChain context management
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import uuid
import asyncio
import json

from app.models.user import UserProfile, UserPreferences, UserConstraints, TokenData
from app.models.destination import Rating

from app.services.supabase_service import get_supabase
from app.agents.brainstorm_agent import BrainstormAgent
from app.api.deps import get_current_user_optional

router = APIRouter(prefix="/api/brainstorm", tags=["brainstorm"])

# In-memory storage for active agents (in production: use Redis)
active_agents: Dict[str, BrainstormAgent] = {}


@router.post("/start")
async def start_brainstorm_session(
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Start new brainstorm session with user profile context

    Returns:
        session_id, first_message, websocket_url
    """
    try:
        # Generate session ID
        session_id = f"brainstorm_{uuid.uuid4().hex[:12]}"

        # Get user profile
        supabase = get_supabase()
        user_id = current_user.user_id if current_user else None

        if not user_id:
            # Testing without auth - use test profile
            print("WARNING: No user_id, using test profile for development")
            user_profile = UserProfile(
                user_id="test_user",
                preferences=UserPreferences(
                    traveler_type="explorer",
                    activity_level="high",
                    environment="mixed",
                    accommodation_style="boutique",
                    budget_sensitivity="medium",
                    culture_interest="high",
                    food_importance="high"
                ),
                constraints=UserConstraints(
                    dietary_restrictions=[],
                    climate_preferences=["mild_temperate", "hot_tropical"],
                    language_preferences=[]
                ),
                wishlist_regions=["Southeast Asia", "Iceland"],
                past_destinations=["Paris", "Barcelona"]
            )
        else:
            # Get real profile from database
            user_profile = await supabase.get_user_profile(user_id)
            if not user_profile:
                raise HTTPException(
                    status_code=404,
                    detail="User profile not found. Complete onboarding first."
                )

        print(f"DEBUG: Starting brainstorm session {session_id}")

        # Create agent with full user context
        agent = BrainstormAgent(user_profile)
        active_agents[session_id] = agent

        # Generate personalized first message
        first_message = agent.generate_first_message()

        return {
            "session_id": session_id,
            "first_message": first_message,
            "websocket_url": f"/api/brainstorm/ws/{session_id}"
        }
    except Exception as e:
        print(f"ERROR in start_brainstorm_session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def brainstorm_websocket(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for real-time brainstorm conversation
    Streams responses token by token
    """
    # Check if session exists
    if session_id not in active_agents:
        await websocket.accept()
        await websocket.close(code=1008, reason="Session not found")
        return

    agent = active_agents[session_id]

    await websocket.accept()
    print(f"DEBUG: WebSocket connected for session {session_id}")

    try:
        while True:
            # Receive message from user
            data = await websocket.receive_json()

            if data.get("type") == "message":
                user_message = data.get("content")
                print(f"DEBUG: Received message: {user_message[:50]}...")

                # Send thinking indicator
                await websocket.send_json({
                    "type": "thinking",
                    "session_id": session_id
                })

                # Stream response from agent
                full_response = ""
                async for token in agent.chat(user_message):
                    full_response += token
                    await websocket.send_json({
                        "type": "token",
                        "session_id": session_id,
                        "token": token
                    })
                    await asyncio.sleep(0.01)  # Small delay for smooth UX

                # Send complete message
                await websocket.send_json({
                    "type": "message",
                    "session_id": session_id,
                    "role": "assistant",
                    "content": full_response
                })

                print(f"DEBUG: Sent response, length: {len(full_response)}")

    except WebSocketDisconnect:
        print(f"DEBUG: WebSocket disconnected for session {session_id}")
        # Keep agent in memory for reconnection
    except Exception as e:
        print(f"ERROR: WebSocket error: {e}")
        import traceback
        traceback.print_exc()


@router.get("/session/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = active_agents[session_id]
    history = agent.get_conversation_history()

    return {
        "session_id": session_id,
        "messages": history,
        "message_count": len(history)
    }


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End brainstorm session and clear memory"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    # Clean up
    del active_agents[session_id]
    print(f"DEBUG: Session {session_id} ended and cleaned up")

    return {"message": "Session ended successfully"}

@router.post("/session/{session_id}/create_recommendation")
async def create_recommendation(session_id: str):
    """Create recommendation for a session"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = active_agents[session_id]
    recommendation = agent.create_recommendation()
    return recommendation

@router.get("/session/{session_id}/recommendation")
async def get_recommendation(session_id: str):
    """Get recommendation for a session"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = active_agents[session_id]
    recommendation = agent.get_recommendation()
    return recommendation

@router.post("/session/{session_id}/recommendation/{recommendation_id}")
async def update_recommendation(
    session_id: str,
    recommendation_id: str, 
    rating: Rating):
    """Update recommendation for a session"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = active_agents[session_id]
    recommendation = agent.update_recommendation(recommendation_id, rating)
    return recommendation