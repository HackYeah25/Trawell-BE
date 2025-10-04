"""
Session management service using Redis backend
"""
import json
from typing import Dict, Optional, Any
from uuid import UUID, uuid4
import redis.asyncio as redis
from app.config import settings


class SessionService:
    """Redis-based session management service"""

    def __init__(self):
        self.redis_client = None
        self.session_prefix = "profiling_session:"
        self.conversation_prefix = "profiling_conversation:"
        self.session_ttl = 3600  # 1 hour

    async def _get_redis(self):
        """Get or create async Redis client"""
        if self.redis_client is None:
            self.redis_client = await redis.Redis(
                host='redis',  # Docker service name
                port=6379,
                db=0,
                decode_responses=True
            )
        return self.redis_client
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"{self.session_prefix}{session_id}"
    
    def _get_conversation_key(self, session_id: str) -> str:
        """Get Redis key for conversation"""
        return f"{self.conversation_prefix}{session_id}"
    
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new profiling session"""
        redis = await self._get_redis()
        session_id = session_data.get("session_id")
        if not session_id:
            session_id = f"prof_{uuid4().hex[:12]}"

        session_key = self._get_session_key(session_id)

        # Store session data
        await redis.setex(
            session_key,
            self.session_ttl,
            json.dumps(session_data, default=str)
        )

        # Initialize empty conversation
        conversation_key = self._get_conversation_key(session_id)
        await redis.setex(conversation_key, self.session_ttl, json.dumps([]))

        print(f"DEBUG: Created session {session_id} in Redis")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        redis = await self._get_redis()
        session_key = self._get_session_key(session_id)
        session_data = await redis.get(session_key)

        if session_data:
            try:
                return json.loads(session_data)
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse session data for {session_id}: {e}")
                return None
        return None
    
    async def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data in Redis"""
        redis = await self._get_redis()
        session_key = self._get_session_key(session_id)

        # Check if session exists
        if not await redis.exists(session_key):
            return False

        # Update session data
        await redis.setex(
            session_key,
            self.session_ttl,
            json.dumps(session_data, default=str)
        )

        print(f"DEBUG: Updated session {session_id} in Redis")
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        redis = await self._get_redis()
        session_key = self._get_session_key(session_id)
        conversation_key = self._get_conversation_key(session_id)

        # Delete both session and conversation
        deleted = await redis.delete(session_key, conversation_key)

        if deleted:
            print(f"DEBUG: Deleted session {session_id} from Redis")

        return deleted > 0
    
    async def add_message_to_conversation(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add message to conversation history"""
        redis = await self._get_redis()
        conversation_key = self._get_conversation_key(session_id)

        # Check if session exists
        if not await redis.exists(self._get_session_key(session_id)):
            return False

        # Get current conversation
        conversation_data = await redis.get(conversation_key)
        if conversation_data:
            conversation = json.loads(conversation_data)
        else:
            conversation = []

        # Add new message
        conversation.append(message)

        # Update conversation
        await redis.setex(conversation_key, self.session_ttl, json.dumps(conversation, default=str))

        return True
    
    async def get_conversation(self, session_id: str) -> list:
        """Get conversation history"""
        redis = await self._get_redis()
        conversation_key = self._get_conversation_key(session_id)
        conversation_data = await redis.get(conversation_key)

        if conversation_data:
            return json.loads(conversation_data)
        return []
    
    async def extend_session_ttl(self, session_id: str) -> bool:
        """Extend session TTL"""
        redis = await self._get_redis()
        session_key = self._get_session_key(session_id)
        conversation_key = self._get_conversation_key(session_id)

        if await redis.exists(session_key):
            await redis.expire(session_key, self.session_ttl)
            await redis.expire(conversation_key, self.session_ttl)
            return True

        return False


# Global session service instance
session_service = SessionService()
