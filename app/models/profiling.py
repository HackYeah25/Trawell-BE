"""
Profiling data models for user profiling conversation
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProfilingStatus(str, Enum):
    """Status of profiling session"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuestionValidationStatus(str, Enum):
    """Validation status for each question answer"""
    NOT_ANSWERED = "not_answered"
    INSUFFICIENT = "insufficient"  # Answer too vague
    SUFFICIENT = "sufficient"
    COMPLETE = "complete"


class ProfilingQuestion(BaseModel):
    """Individual profiling question from YAML"""
    id: str
    order: int
    category: str
    question: str
    context: str
    validation: Dict[str, Any]
    extracts_to: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "traveler_type",
                "order": 1,
                "category": "core_preferences",
                "question": "What kind of traveler are you?",
                "context": "Understanding traveler type...",
                "validation": {
                    "min_tokens": 5,
                    "required_info": ["Activity preference"]
                },
                "extracts_to": {
                    "field": "preferences.traveler_type",
                    "type": "enum",
                    "values": ["explorer", "relaxer", "mixed"]
                }
            }
        }


class ProfilingQuestionResponse(BaseModel):
    """Response to a profiling question"""
    question_id: str
    user_answer: str
    validation_status: QuestionValidationStatus
    extracted_value: Optional[Any] = None
    follow_up_count: int = 0
    answered_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProfilingSession(BaseModel):
    """Complete profiling session"""
    session_id: str
    user_id: Optional[str] = None
    status: ProfilingStatus = ProfilingStatus.NOT_STARTED
    current_question_index: int = 0
    responses: List[ProfilingQuestionResponse] = Field(default_factory=list)
    profile_completeness: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "session_id": "prof_123456",
                "user_id": "user_123",
                "status": "in_progress",
                "current_question_index": 3,
                "responses": [],
                "profile_completeness": 0.25
            }
        }


class ProfilingMessage(BaseModel):
    """Message in profiling conversation"""
    role: str  # "assistant" or "user"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProfilingConversation(BaseModel):
    """Complete profiling conversation history"""
    conversation_id: str
    session: ProfilingSession
    messages: List[ProfilingMessage] = Field(default_factory=list)


# WebSocket message types
class WSProfilingMessage(BaseModel):
    """WebSocket message for profiling conversation"""
    type: str = "profiling_message"
    conversation_id: str
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "type": "profiling_message",
                "conversation_id": "conv_123",
                "role": "assistant",
                "content": "What kind of traveler are you?",
                "timestamp": "2025-01-15T10:30:00"
            }
        }


class WSProfilingProgress(BaseModel):
    """WebSocket progress update"""
    type: str = "profiling_progress"
    conversation_id: str
    current_question: int
    total_questions: int
    completeness: float
    current_question_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "type": "profiling_progress",
                "conversation_id": "conv_123",
                "current_question": 3,
                "total_questions": 13,
                "completeness": 0.23,
                "current_question_id": "accommodation"
            }
        }


class WSProfilingValidation(BaseModel):
    """WebSocket validation feedback"""
    type: str = "profiling_validation"
    conversation_id: str
    question_id: str
    status: QuestionValidationStatus
    feedback: Optional[str] = None  # If insufficient, explain what's needed

    class Config:
        json_schema_extra = {
            "example": {
                "type": "profiling_validation",
                "conversation_id": "conv_123",
                "question_id": "traveler_type",
                "status": "sufficient",
                "feedback": None
            }
        }


class WSProfilingComplete(BaseModel):
    """WebSocket completion notification"""
    type: str = "profiling_complete"
    conversation_id: str
    profile_id: str
    completeness: float
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "type": "profiling_complete",
                "conversation_id": "conv_123",
                "profile_id": "profile_123",
                "completeness": 1.0,
                "message": "Your profile is complete!"
            }
        }


class WSProfilingThinking(BaseModel):
    """WebSocket thinking indicator"""
    type: str = "profiling_thinking"
    conversation_id: str


class WSProfilingToken(BaseModel):
    """WebSocket streaming token"""
    type: str = "profiling_token"
    conversation_id: str
    token: str


# API Request/Response models
class StartProfilingRequest(BaseModel):
    """Request to start profiling session"""
    user_id: Optional[str] = None


class StartProfilingResponse(BaseModel):
    """Response with profiling session details"""
    session: ProfilingSession
    first_message: str
    websocket_url: str


class GetQuestionsResponse(BaseModel):
    """Response with all profiling questions"""
    questions: List[ProfilingQuestion]
    total_count: int
    critical_questions: List[str]


class SendProfilingAnswerRequest(BaseModel):
    """Request to send answer to profiling question"""
    session_id: str
    question_id: str
    answer: str


class ProfilingSessionResponse(BaseModel):
    """Response with session details"""
    session: ProfilingSession
    next_question: Optional[ProfilingQuestion] = None
    is_complete: bool
