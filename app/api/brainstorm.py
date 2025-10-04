"""
Brainstorm module endpoints - Destination discovery
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid

from app.models.conversation import Conversation, ConversationCreate, MessageCreate, ConversationResponse, Message, MessageRole
from app.models.destination import BrainstormRequest, BrainstormResponse
from app.models.user import TokenData
from app.services.supabase_service import SupabaseService
from app.services.langchain_service import LangChainService
from app.utils.context_manager import ContextManager
from app.prompts.loader import PromptLoader
from app.api.deps import (
    get_current_user,
    get_supabase_dep,
    get_langchain_dep,
    get_context_manager_dep,
    get_prompt_loader_dep
)

router = APIRouter()


@router.post("/start")
async def start_brainstorm_session(
    request: BrainstormRequest,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Start a new brainstorming session

    Args:
        request: Brainstorm request data
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        New conversation session
    """
    # Create new conversation
    conversation = Conversation(
        conversation_id=f"conv_{uuid.uuid4().hex[:12]}",
        user_id=current_user.user_id,
        module="brainstorm",
        mode="group" if request.group_mode else "solo",
        group_participants=request.group_participants if request.group_mode else []
    )

    # Save to database
    created_conversation = await supabase.create_conversation(conversation)

    return {
        "conversation_id": created_conversation.conversation_id,
        "mode": created_conversation.mode,
        "message": "Brainstorm session started! Tell me what kind of trip you're dreaming about."
    }


@router.post("/{conversation_id}/message", response_model=ConversationResponse)
async def send_message(
    conversation_id: str,
    message: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep),
    langchain: LangChainService = Depends(get_langchain_dep),
    context_mgr: ContextManager = Depends(get_context_manager_dep),
    prompts: PromptLoader = Depends(get_prompt_loader_dep)
):
    """
    Send a message in a brainstorm session

    Args:
        conversation_id: Conversation ID
        message: User message
        current_user: Authenticated user
        supabase: Supabase service
        langchain: LangChain service
        context_mgr: Context manager
        prompts: Prompt loader

    Returns:
        Conversation response with AI reply
    """
    # Get conversation
    conversation = await supabase.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get user profile
    user_profile = await supabase.get_user_profile(current_user.user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Create user message
    user_message = Message(
        role=MessageRole.USER,
        content=message
    )

    # Add to conversation
    conversation = await supabase.add_message(conversation_id, user_message)

    # Build context with user profile
    system_prompt = prompts.load("brainstorm", "destination_discovery_system")
    context = context_mgr.build_conversation_context(
        user_profile=user_profile,
        conversation_history=conversation.messages,
        system_prompt=system_prompt
    )

    # Get AI response
    ai_response_text = await langchain.chat(context)

    # Create AI message
    ai_message = Message(
        role=MessageRole.ASSISTANT,
        content=ai_response_text
    )

    # Add AI response to conversation
    await supabase.add_message(conversation_id, ai_message)

    return ConversationResponse(
        conversation_id=conversation_id,
        message=user_message,
        ai_response=ai_message
    )


@router.get("/{conversation_id}/suggestions")
async def get_suggestions(
    conversation_id: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Get AI destination suggestions for a brainstorm session

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        List of destination suggestions
    """
    # TODO: Implement suggestion generation logic
    raise HTTPException(
        status_code=501,
        detail="Suggestions endpoint not yet implemented"
    )


@router.post("/{conversation_id}/group/invite")
async def invite_to_group(
    conversation_id: str,
    user_ids: List[str],
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Invite users to a group brainstorm session

    Args:
        conversation_id: Conversation ID
        user_ids: List of user IDs to invite
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        Updated conversation
    """
    # TODO: Implement group invitation logic
    raise HTTPException(
        status_code=501,
        detail="Group invitation endpoint not yet implemented"
    )
