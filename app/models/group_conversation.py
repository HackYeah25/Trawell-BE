"""
Models for group conversation / collaborative brainstorming
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ConversationStatus(str, Enum):
    """Status of group conversation"""
    PROFILING = "profiling"  # Still gathering participant profiles
    ACTIVE = "active"  # Active conversation
    CONVERGED = "converged"  # Group has reached consensus
    CONFLICTED = "conflicted"  # Detected conflicts needing resolution


class MessageType(str, Enum):
    """Type of message in group conversation"""
    USER = "user"
    AI_ANALYSIS = "ai_analysis"
    AI_SUGGESTION = "ai_suggestion"
    AI_THINKING = "ai_thinking"
    AI_TOKEN = "ai_token"  # Streaming token
    SYSTEM = "system"


class CompatibilityLevel(str, Enum):
    """Compatibility level between participants"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CONFLICTED = "conflicted"


# Request/Response Models
class CreateGroupConversationRequest(BaseModel):
    """Request to create a new group conversation"""
    user_name: str = Field(..., min_length=1, max_length=100)
    user_profile: Dict[str, Any] = Field(..., description="User's travel preferences")


class JoinGroupConversationRequest(BaseModel):
    """Request to join an existing group conversation"""
    room_code: str = Field(..., min_length=6, max_length=10)
    user_name: str = Field(..., min_length=1, max_length=100)
    user_profile: Dict[str, Any] = Field(..., description="User's travel preferences")


class SendGroupMessageRequest(BaseModel):
    """Request to send a message in group conversation"""
    message: str = Field(..., min_length=1)
    ai_invoked: bool = Field(default=False, description="Whether AI was explicitly invoked")


# Database Models
class GroupConversation(BaseModel):
    """Group conversation model"""
    id: str
    room_code: str
    status: ConversationStatus
    compatibility_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class GroupParticipant(BaseModel):
    """Group participant model"""
    id: str
    conversation_id: str
    user_id: Optional[str] = None
    user_name: str
    user_profile: Dict[str, Any]
    compatibility_score: Optional[float] = None
    is_active: bool = True
    joined_at: datetime
    last_active_at: datetime


class GroupMessage(BaseModel):
    """Group message model"""
    id: str
    conversation_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    message: str
    message_type: MessageType
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        use_enum_values = True


# Response Models
class GroupConversationResponse(BaseModel):
    """Response with conversation details"""
    conversation: GroupConversation
    participants: List[GroupParticipant]
    recent_messages: List[GroupMessage] = []


class CompatibilityConflict(BaseModel):
    """Represents a conflict between participants"""
    aspect: str
    users: List[str]
    issue: str
    severity: float = Field(ge=0.0, le=1.0)


class CompatibilityAnalysis(BaseModel):
    """Analysis of group compatibility"""
    compatibility_level: CompatibilityLevel
    compatibility_score: float = Field(ge=0.0, le=1.0)
    common_ground: List[str] = []
    conflicts: List[CompatibilityConflict] = []
    compromise_needed: bool = False
    suggested_approach: str = ""
    participant_scores: Dict[str, float] = {}  # user_id -> compatibility score

    class Config:
        use_enum_values = True


class AIResponseTrigger(BaseModel):
    """Reason why AI should respond"""
    triggered: bool
    reason: Optional[str] = None
    trigger_type: Optional[str] = None  # 'all_spoke', 'direct_question', 'impasse', 'manual'


# WebSocket message formats
class WSMessageBase(BaseModel):
    """Base WebSocket message"""
    type: str
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WSUserMessage(WSMessageBase):
    """User message via WebSocket"""
    type: str = "user_message"
    user_id: Optional[str] = None
    user_name: str
    message: str
    ai_invoked: bool = False


class WSAIMessage(WSMessageBase):
    """AI message via WebSocket"""
    type: str = "ai_message"
    message: str
    message_type: MessageType = MessageType.AI_SUGGESTION
    metadata: Optional[Dict[str, Any]] = None


class WSSystemMessage(WSMessageBase):
    """System message via WebSocket"""
    type: str = "system_message"
    message: str


class WSThinkingMessage(WSMessageBase):
    """AI thinking indicator"""
    type: str = "ai_thinking"
    message: str = "💭 Analyzing everyone's preferences..."


class WSTokenMessage(WSMessageBase):
    """Streaming AI token"""
    type: str = "ai_token"
    token: str


class WSParticipantUpdate(WSMessageBase):
    """Participant joined/left"""
    type: str = "participant_update"
    action: str  # 'joined', 'left'
    participant: GroupParticipant


class WSCompatibilityUpdate(WSMessageBase):
    """Compatibility analysis update"""
    type: str = "compatibility_update"
    analysis: CompatibilityAnalysis
