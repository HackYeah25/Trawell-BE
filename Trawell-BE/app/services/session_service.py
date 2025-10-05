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
            # Determine Redis host based on environment
            # In Docker, use service name 'redis', otherwise use 'localhost'
            import os
            redis_host = os.environ.get('REDIS_HOST', 'redis' if os.path.exists('/.dockerenv') else 'localhost')

            self.redis_client = await redis.Redis(
                host=redis_host,
                port=6379,
                db=0,
                decode_responses=True
            )
            print(f"DEBUG: Connected to Redis at {redis_host}:6379")
        return self.redis_client
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"{self.session_prefix}{session_id}"
    
    def _get_conversation_key(self, session_id: str) -> str:
        """Get Redis key for conversation"""
        return f"{self.conversation_prefix}{session_id}"
    
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new profiling session"""
        try:
            redis_client = await self._get_redis()
            session_id = session_data.get("session_id")
            if not session_id:
                session_id = f"prof_{uuid4().hex[:12]}"

            session_key = self._get_session_key(session_id)

            # Store session data
            await redis_client.setex(
                session_key,
                self.session_ttl,
                json.dumps(session_data, default=str)
            )

            # Initialize empty conversation
            conversation_key = self._get_conversation_key(session_id)
            await redis_client.setex(conversation_key, self.session_ttl, json.dumps([]))

            print(f"DEBUG: Created session {session_id} in Redis")
            return session_id
        except Exception as e:
            print(f"ERROR: Failed to create session in Redis: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        redis_client = await self._get_redis()
        session_key = self._get_session_key(session_id)
        session_data = await redis_client.get(session_key)

        if session_data:
            try:
                return json.loads(session_data)
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse session data for {session_id}: {e}")
                return None
        return None
    
    async def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data in Redis"""
        redis_client = await self._get_redis()
        session_key = self._get_session_key(session_id)

        # Check if session exists
        if not await redis_client.exists(session_key):
            return False

        # Update session data
        await redis_client.setex(
            session_key,
            self.session_ttl,
            json.dumps(session_data, default=str)
        )

        print(f"DEBUG: Updated session {session_id} in Redis")
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        redis_client = await self._get_redis()
        session_key = self._get_session_key(session_id)
        conversation_key = self._get_conversation_key(session_id)

        # Delete both session and conversation
        deleted = await redis_client.delete(session_key, conversation_key)

        if deleted:
            print(f"DEBUG: Deleted session {session_id} from Redis")

        return deleted > 0
    
    async def add_message_to_conversation(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add message to conversation history"""
        redis_client = await self._get_redis()
        conversation_key = self._get_conversation_key(session_id)

        # Check if session exists
        if not await redis_client.exists(self._get_session_key(session_id)):
            return False

        # Get current conversation
        conversation_data = await redis_client.get(conversation_key)
        if conversation_data:
            conversation = json.loads(conversation_data)
        else:
            conversation = []

        # Add new message
        conversation.append(message)

        # Update conversation
        await redis_client.setex(conversation_key, self.session_ttl, json.dumps(conversation, default=str))

        return True
    
    async def get_conversation(self, session_id: str) -> list:
        """Get conversation history"""
        redis_client = await self._get_redis()
        conversation_key = self._get_conversation_key(session_id)
        conversation_data = await redis_client.get(conversation_key)

        if conversation_data:
            return json.loads(conversation_data)
        return []
    
    async def extend_session_ttl(self, session_id: str) -> bool:
        """Extend session TTL"""
        redis_client = await self._get_redis()
        session_key = self._get_session_key(session_id)
        conversation_key = self._get_conversation_key(session_id)

        if await redis_client.exists(session_key):
            await redis_client.expire(session_key, self.session_ttl)
            await redis_client.expire(conversation_key, self.session_ttl)
            return True

        return False

    async def save_session_to_database(self, session_id: str) -> bool:
        """Save session from Redis to Supabase database"""
        from app.services.supabase_service import get_supabase
        
        # Get session from Redis
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        supabase = get_supabase()
        if not supabase.client:
            print("ERROR: Supabase client not initialized")
            return False
        
        try:
            # Save session to profiling_sessions table
            supabase.client.table("profiling_sessions").insert({
                "session_id": session_data["session_id"],
                "user_id": session_data.get("user_id"),
                "status": session_data["status"],
                "current_question_index": session_data["current_question_index"],
                "profile_completeness": session_data["profile_completeness"],
                "created_at": session_data.get("created_at"),
                "updated_at": session_data.get("updated_at"),
                "completed_at": session_data.get("completed_at")
            }).execute()
            
            # Save responses
            for response in session_data.get("responses", []):
                supabase.client.table("profiling_responses").insert({
                    "session_id": session_id,
                    "question_id": response["question_id"],
                    "user_answer": response["user_answer"],
                    "validation_status": response["validation_status"],
                    "extracted_value": response.get("extracted_value"),
                    "follow_up_count": response.get("follow_up_count", 0),
                    "answered_at": response.get("answered_at")
                }).execute()
            
            # Save conversation messages
            conversation = await self.get_conversation(session_id)
            for message in conversation:
                supabase.client.table("profiling_messages").insert({
                    "session_id": session_id,
                    "role": message["role"],
                    "content": message["content"],
                    "metadata": message.get("metadata"),
                    "created_at": message.get("timestamp") or message.get("created_at")
                }).execute()
            
            print(f"✅ Saved session {session_id} to Supabase")
            return True
            
        except Exception as e:
            print(f"ERROR saving session to Supabase: {e}")
            return False


# Global session service instance
session_service = SessionService()
