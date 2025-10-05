"""
Brainstorm Agent - Destination discovery with user profile context
Uses LangChain with ConversationBufferMemory for context preservation
"""
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime
from uuid import uuid4

import supabase


from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from app.models.user import UserProfile
from app.models.destination import DestinationRecommendation , DestinationInfo , Rating

from app.services.supabase_service import get_supabase
from app.prompts.loader import get_prompt_loader

from app.config import settings


class BrainstormAgent:
    """Agent for brainstorm conversations with full user context"""

    def __init__(self, user_profile: UserProfile):
        """
        Initialize agent with user profile

        Args:
            user_profile: Complete user profile from profiling
        """
        self.user_profile = user_profile
        self.supabase = get_supabase()
        
        # Load prompts from brainstorm.yaml
        prompt_loader = get_prompt_loader()
        self.prompts = prompt_loader.get_all_prompts('brainstorm')
        print(f"✅ Loaded {len(self.prompts)} prompts from brainstorm.yaml")
        print(f"   Available prompts: {list(self.prompts.keys())}")

        # Initialize LLM
        # Note: gpt-4o-search-preview does not support temperature/top_p/n parameters
        # Fallback to gpt-4o for now until LangChain supports gpt-4o-search properly
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Use regular gpt-4o instead of gpt-4o-search-preview
            api_key=settings.openai_api_key,
            max_tokens=1000,
            streaming=True,
            temperature=0.8,  # More creative for brainstorming
        )

        # Initialize conversation memory (LangChain built-in context storage)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            ai_prefix="AI Travel Expert",
            human_prefix="Traveler"
        )

        # Build system prompt with user profile injected
        self.system_prompt = self._build_system_prompt()

        print(f"DEBUG: BrainstormAgent initialized for user with profile:")
        print(f"  - Traveler type: {user_profile.preferences.traveler_type}")
        print(f"  - Environment: {user_profile.preferences.environment}")
        print(f"  - Activity level: {user_profile.preferences.activity_level}")

    def _build_system_prompt(self) -> str:
        """Build system prompt from brainstorm.yaml with injected user profile"""

        # Extract key profile info
        prefs = self.user_profile.preferences
        constraints = self.user_profile.constraints

        # Build profile summary
        profile_summary = f"""
        USER PROFILE (use this context for ALL responses):
        - Traveler Type: {prefs.traveler_type or 'mixed'}
        - Activity Level: {prefs.activity_level or 'medium'}
        - Preferred Environment: {prefs.environment or 'varied'}
        - Accommodation Style: {prefs.accommodation_style or 'flexible'}
        - Budget Sensitivity: {prefs.budget_sensitivity or 'medium'}
        - Culture Interest: {prefs.culture_interest or 'medium'}
        - Food Importance: {prefs.food_importance or 'medium'}
        """

        if constraints.dietary_restrictions:
            profile_summary += f"- Dietary: {', '.join(constraints.dietary_restrictions)}\n"

        if constraints.climate_preferences:
            profile_summary += f"- Climate: {', '.join(constraints.climate_preferences)}\n"

        if self.user_profile.wishlist_regions:
            profile_summary += f"- Wishlist: {', '.join(self.user_profile.wishlist_regions)}\n"

        if self.user_profile.past_destinations:
            profile_summary += f"- Been to: {', '.join(self.user_profile.past_destinations[:3])}\n"

        # Get base prompt from brainstorm.yaml
        base_prompt = self.prompts.get('destination_discovery_system', '')
        
        # Inject user profile and current date
        system_prompt = f"""{base_prompt}

{profile_summary}

Current date: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        # Log system prompt for debugging
        print(f"\n{'='*80}")
        print(f"🎯 SYSTEM PROMPT LOADED:")
        print(f"{'='*80}")
        print(f"Base prompt length: {len(base_prompt)} chars")
        print(f"Contains '<locations>' keyword: {'<locations>' in base_prompt}")
        if '<locations>' in base_prompt:
            # Show context around <locations>
            idx = base_prompt.find('<locations>')
            start = max(0, idx - 100)
            end = min(len(base_prompt), idx + 200)
            print(f"Context around <locations>:\n...{base_prompt[start:end]}...")
        print(f"{'='*80}\n")
        
        return system_prompt

    def generate_first_message(self) -> str:
        """
        Generate personalized first message

        Returns:
            Customized greeting based on user profile
        """
        # Get wishlist for customization
        wishlist = self.user_profile.wishlist_regions or []

        # Base greeting
        greeting = "Witaj podróżniku! 🌍"

        # Add customization if wishlist exists
        if wishlist:
            if len(wishlist) == 1:
                greeting += f"\n\nWidzę, że interesujesz się {wishlist[0]}. To fascynujący region!"
            else:
                regions_text = ", ".join(wishlist[:2])
                greeting += f"\n\nWidzę na twojej liście {regions_text}... świetny wybór!"

        greeting += "\n\nOpowiedz mi - o jakiej podróży marzysz teraz? Dokąd chciałbyś się wybrać?"

        return greeting

    async def chat(self, user_message: str) -> AsyncIterator[str]:
        """
        Process user message and stream response

        Args:
            user_message: User's message

        Yields:
            Response tokens
        """
        print(f"\n{'='*80}")
        print(f"🧠 BRAINSTORM AGENT - Processing user message")
        print(f"{'='*80}")
        print(f"📨 User message (length: {len(user_message)} chars):")
        print(f"   {user_message[:150]}...")
        print(f"💾 Memory history: {len(self.memory.chat_memory.messages)} messages")

        # Build messages with system prompt and memory
        messages = [
            SystemMessage(content=self.system_prompt)
        ]

        # Add conversation history from memory
        if self.memory.chat_memory.messages:
            messages.extend(self.memory.chat_memory.messages)
            print(f"   Including {len(self.memory.chat_memory.messages)} historical messages")

        # Add current user message
        messages.append(HumanMessage(content=user_message))

        print(f"🤖 Calling LLM with {len(messages)} total messages (1 system + {len(self.memory.chat_memory.messages)} history + 1 user)")
        print(f"{'='*80}\n")

        # Stream response
        full_response = ""
        chunk_count = 0
        try:
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, "content") and chunk.content:
                    full_response += chunk.content
                    chunk_count += 1
                    yield chunk.content

            print(f"\n{'='*80}")
            print(f"✅ LLM RESPONSE COMPLETED")
            print(f"{'='*80}")
            print(f"📊 Stats:")
            print(f"   Chunks received: {chunk_count}")
            print(f"   Total length: {len(full_response)} chars")
            print(f"   Lines: {full_response.count(chr(10))}")
            
            # Check for location tags in response
            if '<locations>' in full_response:
                print(f"   ✅ Contains <locations> tags")
            else:
                print(f"   ⚠️  Does NOT contain <locations> tags")
            
            print(f"\n📝 Response preview (first 300 chars):")
            print(f"{full_response[:300].replace(chr(10), ' ')}...")
            print(f"{'='*80}\n")

            # Save to memory after streaming completes
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(full_response)

        except Exception as e:
            print(f"\n{'='*80}")
            print(f"❌ ERROR in chat streaming: {e}")
            print(f"{'='*80}")
            import traceback
            traceback.print_exc()
            yield "Przepraszam, wystąpił błąd. Spróbuj ponownie."

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history from memory

        Returns:
            List of messages with role and content
        """
        history = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": message.content})
        return history

    def create_recommendation(self) -> DestinationRecommendation:
        """Get recommendation for a session"""
        recommendation = DestinationRecommendation(
            recommendation_id=uuid4(),
            user_id=self.user_profile.user_id,
            destination=DestinationInfo(
                name="",
                country="",
                region="",
                coordinates=None,
                description=None
            ),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        ret_recommendation = self.supabase.create_recommendation(recommendation)
        return ret_recommendation

    def get_recommendation(self, recommendation_id: str) -> DestinationRecommendation:
        """Get recommendation for a session"""
        recommendation_list = self.supabase.get_user_recommendations(self.user_profile.user_id)
        recommendation = list(filter(lambda x: x.recommendation_id == recommendation_id, recommendation_list))[0]
        return recommendation
    
    def update_recommendation(self, recommendation_id: str, rating: Rating):
        """Update recommendation for a session"""
        recommendation = self.supabase.update_recommendation(recommendation_id, rating)
        return recommendation

    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        print("DEBUG: Conversation memory cleared")