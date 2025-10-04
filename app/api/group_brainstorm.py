"""
Group Brainstorm API - Collaborative travel planning with AI moderation
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.group_conversation import (
    CreateGroupConversationRequest,
    JoinGroupConversationRequest,
    SendGroupMessageRequest,
    GroupConversationResponse,
    GroupConversation,
    GroupParticipant,
    GroupMessage,
    MessageType,
    WSUserMessage,
    WSAIMessage,
    WSSystemMessage,
    WSThinkingMessage,
    WSTokenMessage,
    WSParticipantUpdate,
    WSCompatibilityUpdate,
    ConversationStatus,
)
from app.services.supabase import supabase_client
from app.agents.group_moderator import group_moderator
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/brainstorm/group", tags=["group-brainstorm"])


class GroupConnectionManager:
    """Manages WebSocket connections for group conversations"""

    def __init__(self):
        # conversation_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Connect a WebSocket to a conversation room"""
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Disconnect a WebSocket from a conversation room"""
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)

    async def broadcast(self, conversation_id: str, message: dict):
        """Broadcast message to all connections in a conversation"""
        if conversation_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            # Clean up disconnected websockets
            for conn in disconnected:
                self.disconnect(conn, conversation_id)

    async def send_to_websocket(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending to websocket: {e}")


manager = GroupConnectionManager()


# Helper functions for Supabase operations
async def create_conversation(room_code: str) -> GroupConversation:
    """Create a new group conversation"""
    result = supabase_client.table("group_conversations").insert(
        {
            "room_code": room_code,
            "status": ConversationStatus.PROFILING.value,
            "compatibility_data": None,
            "metadata": {},
        }
    ).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create conversation")

    return GroupConversation(**result.data[0])


async def get_conversation_by_room_code(room_code: str) -> Optional[GroupConversation]:
    """Get conversation by room code"""
    result = supabase_client.table("group_conversations").select("*").eq(
        "room_code", room_code
    ).execute()

    if not result.data:
        return None

    return GroupConversation(**result.data[0])


async def get_conversation(conversation_id: str) -> Optional[GroupConversation]:
    """Get conversation by ID"""
    result = supabase_client.table("group_conversations").select("*").eq(
        "id", conversation_id
    ).execute()

    if not result.data:
        return None

    return GroupConversation(**result.data[0])


async def add_participant(
    conversation_id: str,
    user_id: Optional[str],
    user_name: str,
    user_profile: dict,
) -> GroupParticipant:
    """Add participant to conversation"""
    result = supabase_client.table("group_participants").insert(
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_name": user_name,
            "user_profile": user_profile,
            "is_active": True,
        }
    ).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to add participant")

    return GroupParticipant(**result.data[0])


async def get_participants(conversation_id: str) -> List[GroupParticipant]:
    """Get all active participants in conversation"""
    result = supabase_client.table("group_participants").select("*").eq(
        "conversation_id", conversation_id
    ).eq("is_active", True).execute()

    return [GroupParticipant(**p) for p in result.data]


async def get_messages(conversation_id: str, limit: int = 50) -> List[GroupMessage]:
    """Get recent messages from conversation"""
    result = supabase_client.table("group_messages").select("*").eq(
        "conversation_id", conversation_id
    ).order("created_at", desc=True).limit(limit).execute()

    messages = [GroupMessage(**m) for m in result.data]
    return list(reversed(messages))  # Oldest first


async def add_message(
    conversation_id: str,
    user_id: Optional[str],
    user_name: Optional[str],
    message: str,
    message_type: MessageType = MessageType.USER,
    metadata: Optional[dict] = None,
) -> GroupMessage:
    """Add message to conversation"""
    result = supabase_client.table("group_messages").insert(
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_name": user_name,
            "message": message,
            "message_type": message_type.value,
            "metadata": metadata or {},
        }
    ).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to add message")

    return GroupMessage(**result.data[0])


async def update_conversation_compatibility(
    conversation_id: str, compatibility_data: dict, status: ConversationStatus
):
    """Update conversation with compatibility analysis"""
    supabase_client.table("group_conversations").update(
        {
            "compatibility_data": compatibility_data,
            "status": status.value,
        }
    ).eq("id", conversation_id).execute()


# API Endpoints
@router.post("/create")
async def create_group_conversation(
    request: CreateGroupConversationRequest,
    current_user: Optional[dict] = Depends(get_current_user),
) -> GroupConversationResponse:
    """Create a new group conversation"""

    # Generate unique room code
    import random
    import string

    room_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Ensure uniqueness
    while await get_conversation_by_room_code(room_code):
        room_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Create conversation
    conversation = await create_conversation(room_code)

    # Add creator as first participant
    user_id = current_user.get("id") if current_user else None
    participant = await add_participant(
        conversation.id,
        user_id,
        request.user_name,
        request.user_profile,
    )

    return GroupConversationResponse(
        conversation=conversation,
        participants=[participant],
        recent_messages=[],
    )


@router.post("/join")
async def join_group_conversation(
    request: JoinGroupConversationRequest,
    current_user: Optional[dict] = Depends(get_current_user),
) -> GroupConversationResponse:
    """Join an existing group conversation"""

    # Find conversation
    conversation = await get_conversation_by_room_code(request.room_code)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Add participant
    user_id = current_user.get("id") if current_user else None
    participant = await add_participant(
        conversation.id,
        user_id,
        request.user_name,
        request.user_profile,
    )

    # Get all participants and messages
    participants = await get_participants(conversation.id)
    messages = await get_messages(conversation.id)

    # Trigger compatibility analysis (async, don't wait)
    asyncio.create_task(
        analyze_and_broadcast_compatibility(conversation.id, participants)
    )

    return GroupConversationResponse(
        conversation=conversation,
        participants=participants,
        recent_messages=messages,
    )


@router.get("/{conversation_id}")
async def get_group_conversation(
    conversation_id: str,
) -> GroupConversationResponse:
    """Get conversation details"""

    conversation = await get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    participants = await get_participants(conversation_id)
    messages = await get_messages(conversation_id)

    return GroupConversationResponse(
        conversation=conversation,
        participants=participants,
        recent_messages=messages,
    )


# WebSocket endpoint
@router.websocket("/ws/{conversation_id}")
async def group_websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    user_id: Optional[str] = None,
    user_name: str = "Anonymous",
):
    """WebSocket endpoint for group conversation"""

    # Verify conversation exists
    conversation = await get_conversation(conversation_id)
    if not conversation:
        await websocket.close(code=1008, reason="Conversation not found")
        return

    # Connect WebSocket
    await manager.connect(websocket, conversation_id)

    try:
        while True:
            # Receive message from user
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "user_message":
                # Store message in database
                message = await add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    user_name=user_name,
                    message=data["message"],
                    message_type=MessageType.USER,
                    metadata={"ai_invoked": data.get("ai_invoked", False)},
                )

                # Broadcast to all participants
                await manager.broadcast(
                    conversation_id,
                    {
                        "type": "user_message",
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "user_name": user_name,
                        "message": data["message"],
                        "timestamp": message.created_at.isoformat(),
                    },
                )

                # Check if AI should respond
                participants = await get_participants(conversation_id)
                messages = await get_messages(conversation_id)

                trigger = group_moderator.should_ai_respond(messages, participants)

                if trigger.triggered:
                    # Process AI response asynchronously
                    asyncio.create_task(
                        process_ai_response(conversation_id, participants, messages)
                    )

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, conversation_id)


# Helper functions for async tasks
async def analyze_and_broadcast_compatibility(
    conversation_id: str, participants: List[GroupParticipant]
):
    """Analyze compatibility and broadcast results"""

    # Run compatibility analysis
    compatibility = await group_moderator.analyze_compatibility(participants)

    # Update conversation with compatibility data
    status = (
        ConversationStatus.CONFLICTED
        if compatibility.compatibility_level.value == "conflicted"
        else ConversationStatus.ACTIVE
    )

    await update_conversation_compatibility(
        conversation_id, compatibility.dict(), status
    )

    # Broadcast compatibility update
    await manager.broadcast(
        conversation_id,
        WSCompatibilityUpdate(
            conversation_id=conversation_id,
            analysis=compatibility,
        ).dict(),
    )

    # Send system message if compromise needed
    if compatibility.compromise_needed:
        conflict_aspects = ", ".join([c.aspect for c in compatibility.conflicts])
        system_msg = f"⚠️ Heads up! Your group has different preferences in: {conflict_aspects}. I'll focus on finding destinations with flexibility for everyone."

        await add_message(
            conversation_id=conversation_id,
            user_id=None,
            user_name=None,
            message=system_msg,
            message_type=MessageType.SYSTEM,
        )

        await manager.broadcast(
            conversation_id,
            WSSystemMessage(
                conversation_id=conversation_id,
                message=system_msg,
            ).dict(),
        )


async def process_ai_response(
    conversation_id: str,
    participants: List[GroupParticipant],
    messages: List[GroupMessage],
):
    """Process and stream AI response"""

    # Get compatibility data
    conversation = await get_conversation(conversation_id)
    if not conversation or not conversation.compatibility_data:
        # Run compatibility analysis first
        compatibility = await group_moderator.analyze_compatibility(participants)
    else:
        from app.models.group_conversation import CompatibilityAnalysis

        compatibility = CompatibilityAnalysis(**conversation.compatibility_data)

    # Send thinking indicator
    await manager.broadcast(
        conversation_id,
        WSThinkingMessage(
            conversation_id=conversation_id,
        ).dict(),
    )

    # Stream AI response
    full_response = ""

    async for token in group_moderator.stream_response(
        participants, messages, compatibility
    ):
        full_response += token

        # Broadcast token
        await manager.broadcast(
            conversation_id,
            WSTokenMessage(
                conversation_id=conversation_id,
                token=token,
            ).dict(),
        )

        # Small delay for better UX
        await asyncio.sleep(0.01)

    # Store complete AI message
    await add_message(
        conversation_id=conversation_id,
        user_id=None,
        user_name=None,
        message=full_response,
        message_type=MessageType.AI_SUGGESTION,
    )

    # Send completion message
    await manager.broadcast(
        conversation_id,
        WSAIMessage(
            conversation_id=conversation_id,
            message=full_response,
            message_type=MessageType.AI_SUGGESTION,
        ).dict(),
    )
