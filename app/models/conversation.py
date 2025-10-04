"""
Conversation and message data models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationModule(str, Enum):
    BRAINSTORM = "brainstorm"
    PLANNING = "planning"
    SUPPORT = "support"


class ConversationMode(str, Enum):
    SOLO = "solo"
    GROUP = "group"


class Message(BaseModel):
    """Individual message in a conversation"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "I'd like to find a destination for a relaxing beach vacation",
                "timestamp": "2024-01-15T10:30:00Z",
                "metadata": {}
            }
        }


class Conversation(BaseModel):
    """Conversation model"""
    conversation_id: str
    user_id: str
    module: ConversationModule
    mode: ConversationMode = ConversationMode.SOLO
    messages: List[Message] = Field(default_factory=list)
    group_participants: List[str] = Field(default_factory=list)
    context_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "user_id": "user_456",
                "module": "brainstorm",
                "mode": "solo",
                "messages": [
                    {
                        "role": "user",
                        "content": "I want to plan a trip",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                ],
                "group_participants": [],
                "context_summary": None
            }
        }


class ConversationCreate(BaseModel):
    """Create new conversation"""
    user_id: str
    module: ConversationModule
    mode: ConversationMode = ConversationMode.SOLO
    group_participants: List[str] = Field(default_factory=list)


class MessageCreate(BaseModel):
    """Create new message in conversation"""
    conversation_id: str
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    """Response from conversation endpoint"""
    conversation_id: str
    message: Message
    ai_response: Optional[Message] = None
