"""
Supabase client and database operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.config import settings
from app.models.user import UserProfile, User
from app.models.conversation import Conversation, Message
from app.models.destination import DestinationRecommendation, Rating
from app.models.trip import TripPlan


class SupabaseService:
    """Supabase database service"""

    def __init__(self):
        self.client: Optional[Client] = None

    def init(self):
        """Initialize Supabase client"""
        try:
            if not settings.supabase_url or settings.supabase_url == "your_supabase_url_here":
                print("WARNING: Supabase not configured, skipping initialization")
                return

            self.client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            print("Supabase client initialized successfully")
        except Exception as e:
            print(f"WARNING: Failed to initialize Supabase client: {e}")
            self.client = None

    # User Profile Operations
    async def get_user(self, user_id: str) -> Optional[User]:
        """Fetch user and map to API User: {id, name, email?, onboardingCompleted}."""
        if not self.client:
            raise Exception("Supabase client not initialized")
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            if response.data:
                return User(**response.data[0])
            return None
        except Exception as e:
            raise Exception(f"Error fetching user: {str(e)}")

    async def update_user(self, user_id: str, fields: Dict[str, Any]) -> User:
        """Update user with whatever fields are provided; returns updated User."""
        if not self.client:
            raise Exception("Supabase client not initialized")
        try:
            update_payload: Dict[str, Any] = {k: v for k, v in fields.items() if v is not None}

            if not update_payload:
                user = await self.get_user(user_id)
                if not user:
                    raise Exception("User not found")
                return user

            update_payload["updated_at"] = datetime.utcnow().isoformat()
            self.client.table("users").update(update_payload).eq("id", user_id).execute()

            user = await self.get_user(user_id)
            if not user:
                raise Exception("User not found after update")
            return user
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Fetch user profile by user_id
        
        Returns None if profile doesn't exist - caller must handle this case.
        No fallback profiles are provided.
        """
        if not self.client:
            raise Exception("Supabase client not initialized")
        try:
            response = self.client.table("user_profiles").select("*").eq("user_id", user_id).execute()
            if response.data:
                return UserProfile(**response.data[0])
            return None
        except Exception as e:
            print(f"Error fetching user profile for {user_id}: {e}")
            raise Exception(f"Error fetching user profile: {str(e)}")

    async def has_completed_profiling(self, user_id: str) -> bool:
        """Check if user has completed profiling"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        try:
            response = self.client.table("profiling_sessions").select("id").eq(
                "user_id", user_id
            ).eq(
                "status", "completed"
            ).limit(1).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error checking profiling status for {user_id}: {e}")
            return False

    async def create_user_profile(self, profile: UserProfile) -> UserProfile:
        """Create new user profile"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        try:
            data = profile.model_dump(mode="json")
            response = self.client.table("user_profiles").insert(data).execute()
            return UserProfile(**response.data[0])
        except Exception as e:
            raise Exception(f"Error creating user profile: {str(e)}")

    async def update_user_profile(self, user_id: str, profile: UserProfile) -> UserProfile:
        """Update existing user profile"""
        try:
            profile.updated_at = datetime.utcnow()
            data = profile.model_dump(mode="json")
            response = self.client.table("user_profiles").update(data).eq("user_id", user_id).execute()
            return UserProfile(**response.data[0])
        except Exception as e:
            raise Exception(f"Error updating user profile: {str(e)}")

    # Conversation Operations
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Fetch conversation by ID"""
        try:
            response = self.client.table("conversations").select("*").eq("conversation_id", conversation_id).execute()
            if response.data:
                return Conversation(**response.data[0])
            return None
        except Exception as e:
            raise Exception(f"Error fetching conversation: {str(e)}")

    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """Create new conversation"""
        try:
            data = conversation.model_dump(mode="json")
            response = self.client.table("conversations").insert(data).execute()
            return Conversation(**response.data[0])
        except Exception as e:
            raise Exception(f"Error creating conversation: {str(e)}")

    async def add_message(self, conversation_id: str, message: Message) -> Conversation:
        """Add message to conversation"""
        try:
            # Fetch current conversation
            conv = await self.get_conversation(conversation_id)
            if not conv:
                raise Exception("Conversation not found")

            # Add new message
            conv.messages.append(message)
            conv.updated_at = datetime.utcnow()

            # Update in database
            data = conv.model_dump(mode="json")
            response = self.client.table("conversations").update(data).eq("conversation_id", conversation_id).execute()
            return Conversation(**response.data[0])
        except Exception as e:
            raise Exception(f"Error adding message: {str(e)}")

    async def get_user_conversations(self, user_id: str, module: Optional[str] = None) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            query = self.client.table("conversations").select("*").eq("user_id", user_id)
            if module:
                query = query.eq("module", module)
            response = query.execute()
            return [Conversation(**conv) for conv in response.data]
        except Exception as e:
            raise Exception(f"Error fetching user conversations: {str(e)}")
            
    # Trip Plan Operations
    async def create_trip_plan(self, trip: TripPlan) -> TripPlan:
        """Create new trip plan"""
        try:
            data = trip.model_dump(mode="json")
            response = self.client.table("trip_plans").insert(data).execute()
            return TripPlan(**response.data[0])
        except Exception as e:
            raise Exception(f"Error creating trip plan: {str(e)}")

    async def get_trip_plan(self, trip_id: str) -> Optional[TripPlan]:
        """Fetch trip plan by ID"""
        try:
            response = self.client.table("trip_plans").select("*").eq("trip_id", trip_id).execute()
            if response.data:
                return TripPlan(**response.data[0])
            return None
        except Exception as e:
            raise Exception(f"Error fetching trip plan: {str(e)}")

    async def update_trip_plan(self, trip_id: str, trip: TripPlan) -> TripPlan:
        """Update trip plan"""
        try:
            trip.updated_at = datetime.utcnow()
            data = trip.model_dump(mode="json")
            response = self.client.table("trip_plans").update(data).eq("trip_id", trip_id).execute()
            return TripPlan(**response.data[0])
        except Exception as e:
            raise Exception(f"Error updating trip plan: {str(e)}")

    async def get_user_trips(self, user_id: str) -> List[TripPlan]:
        """Get all trips for a user"""
        try:
            response = self.client.table("trip_plans").select("*").eq("user_id", user_id).execute()
            return [TripPlan(**trip) for trip in response.data]
        except Exception as e:
            raise Exception(f"Error fetching user trips: {str(e)}")


# Global instance
supabase_service = SupabaseService()


def init_supabase():
    """Initialize Supabase service"""
    supabase_service.init()


def get_supabase() -> SupabaseService:
    """Get Supabase service instance"""
    return supabase_service
