"""
Brainstorm API v2 - Database-persisted brainstorm sessions
Creates conversations in DB with LangChain memory
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Optional, List
import uuid
import asyncio
import json
from datetime import datetime

from app.models.user import UserProfile, UserPreferences, UserConstraints, TokenData
from app.models.destination import Rating

from app.services.supabase_service import get_supabase
from app.agents.brainstorm_agent import BrainstormAgent
from app.api.deps import get_current_user_optional

router = APIRouter(prefix="/api/brainstorm", tags=["brainstorm"])

# In-memory storage for active agents (rehydrated from DB on reconnect)
active_agents: Dict[str, BrainstormAgent] = {}

# Test user ID for development
TEST_USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"


@router.get("/sessions")
async def list_brainstorm_sessions(
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    List all brainstorm sessions for current user

    Returns:
        sessions: List of conversation sessions with metadata
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Query conversations table for brainstorm module
        result = supabase.client.table("conversations").select(
            "conversation_id, context_summary, created_at, updated_at, messages, mode"
        ).eq("user_id", user_id).eq("module", "brainstorm").order(
            "updated_at", desc=True
        ).execute()

        sessions = []
        for conv in result.data:
            # Get last message preview
            messages = conv.get("messages", [])
            last_message = messages[-1] if messages else None

            sessions.append({
                "id": conv["conversation_id"],
                "title": conv.get("context_summary") or "New Brainstorm",
                "lastMessage": last_message.get("content", "")[:100] if last_message else "",
                "createdAt": conv["created_at"],
                "updatedAt": conv["updated_at"],
                "messageCount": len(messages),
                "isShared": conv.get("mode") == "group"
            })

        return {"sessions": sessions}

    except Exception as e:
        print(f"ERROR listing brainstorm sessions: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_brainstorm_session(
    title: Optional[str] = None,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Create new brainstorm session
    Persists to database and returns session details

    Args:
        title: Optional title for the session

    Returns:
        session_id, first_message, websocket_url
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        # Get user profile
        user_profile = await supabase.get_user_profile(user_id)

        if not user_profile:
            # Use test profile for development
            print(f"WARNING: No profile for user {user_id}, using test profile")
            user_profile = UserProfile(
                user_id=user_id,
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

        # Generate session ID
        session_id = f"brainstorm_{uuid.uuid4().hex[:12]}"

        # Create agent with user profile
        agent = BrainstormAgent(user_profile)
        active_agents[session_id] = agent

        # Generate personalized first message
        first_message = agent.generate_first_message()

        # Create conversation in database
        if supabase.client:
            conversation_data = {
                "conversation_id": session_id,
                "user_id": user_id,
                "module": "brainstorm",
                "mode": "solo",
                "messages": [{
                    "role": "assistant",
                    "content": first_message,
                    "timestamp": datetime.utcnow().isoformat()
                }],
                "context_summary": title or "New Travel Brainstorm",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            supabase.client.table("conversations").insert(conversation_data).execute()
            print(f"✅ Created conversation {session_id} in database")

        return {
            "session_id": session_id,
            "title": title or "New Travel Brainstorm",
            "first_message": first_message,
            "websocket_url": f"/api/brainstorm/ws/{session_id}"
        }

    except Exception as e:
        print(f"ERROR creating brainstorm session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_brainstorm_session(
    session_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Get brainstorm session details and full conversation history
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get conversation from database
        result = supabase.client.table("conversations").select("*").eq(
            "conversation_id", session_id
        ).eq("user_id", user_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        conversation = result.data[0]

        return {
            "session_id": conversation["conversation_id"],
            "title": conversation.get("context_summary", "Brainstorm Session"),
            "messages": conversation.get("messages", []),
            "createdAt": conversation["created_at"],
            "updatedAt": conversation["updated_at"],
            "mode": conversation.get("mode", "solo")
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR getting brainstorm session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def brainstorm_websocket(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for real-time brainstorm conversation
    Streams responses and persists to database
    """
    await websocket.accept()
    supabase = get_supabase()

    try:
        # Load or rehydrate agent
        if session_id not in active_agents:
            # Try to load from database
            if not supabase.client:
                await websocket.close(code=1011, reason="Database not available")
                return

            result = supabase.client.table("conversations").select("*").eq(
                "conversation_id", session_id
            ).execute()

            if not result.data:
                await websocket.close(code=1008, reason="Session not found")
                return

            conversation = result.data[0]

            # Get user profile
            user_profile = await supabase.get_user_profile(conversation["user_id"])
            if not user_profile:
                await websocket.close(code=1011, reason="User profile not found")
                return

            # Rehydrate agent with conversation history
            agent = BrainstormAgent(user_profile)

            # Restore conversation memory from messages
            messages = conversation.get("messages", [])
            for msg in messages:
                if msg["role"] == "user":
                    agent.memory.chat_memory.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    agent.memory.chat_memory.add_ai_message(msg["content"])

            active_agents[session_id] = agent
            print(f"✅ Rehydrated agent for session {session_id} with {len(messages)} messages")

        agent = active_agents[session_id]

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
                    await asyncio.sleep(0.01)

                # Send complete message
                await websocket.send_json({
                    "type": "message",
                    "session_id": session_id,
                    "role": "assistant",
                    "content": full_response
                })

                # Persist to database
                if supabase.client:
                    # Get current conversation
                    result = supabase.client.table("conversations").select("messages").eq(
                        "conversation_id", session_id
                    ).execute()

                    if result.data:
                        current_messages = result.data[0].get("messages", [])

                        # Append new messages
                        current_messages.append({
                            "role": "user",
                            "content": user_message,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        current_messages.append({
                            "role": "assistant",
                            "content": full_response,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                        # Update conversation
                        supabase.client.table("conversations").update({
                            "messages": current_messages,
                            "updated_at": datetime.utcnow().isoformat()
                        }).eq("conversation_id", session_id).execute()

                        print(f"✅ Persisted conversation to database")

                print(f"DEBUG: Sent response, length: {len(full_response)}")

    except WebSocketDisconnect:
        print(f"DEBUG: WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"ERROR: WebSocket error: {e}")
        import traceback
        traceback.print_exc()


@router.delete("/sessions/{session_id}")
async def delete_brainstorm_session(
    session_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Delete brainstorm session from database"""
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Delete from database
        supabase.client.table("conversations").delete().eq(
            "conversation_id", session_id
        ).eq("user_id", user_id).execute()

        # Clean up in-memory agent
        if session_id in active_agents:
            del active_agents[session_id]

        print(f"✅ Deleted session {session_id}")

        return {"message": "Session deleted successfully"}

    except Exception as e:
        print(f"ERROR deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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