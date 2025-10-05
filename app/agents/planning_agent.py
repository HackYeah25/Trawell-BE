"""
Planning Agent - LangChain-powered trip planning with context awareness
"""
import os
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from app.models.user import UserProfile
from app.models.destination import DestinationRecommendation
from app.prompts.loader import get_prompt_loader


class PlanningAgent:
    """
    LangChain agent for trip planning conversations.
    Maintains context of:
    - User profile (preferences, constraints)
    - Destination recommendation (selected location)
    - Conversation history with memory
    """

    def __init__(
        self,
        recommendation: DestinationRecommendation,
        user_profile: UserProfile,
        existing_messages: list = None
    ):
        self.recommendation = recommendation
        self.user_profile = user_profile
        
        # Initialize LangChain LLM
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            streaming=True,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

        # Load prompts
        prompt_loader = get_prompt_loader()
        self.prompts = prompt_loader.get_all_prompts('planning')
        print(f"✅ Loaded {len(self.prompts)} planning prompts")

        # Rehydrate memory from existing messages
        if existing_messages:
            self._rehydrate_memory(existing_messages)
            print(f"🔄 Rehydrated memory with {len(existing_messages)} messages")

    def _rehydrate_memory(self, messages: list):
        """Load existing conversation into memory"""
        for msg in messages:
            if msg.get("role") == "user":
                self.memory.chat_memory.add_user_message(msg.get("content", ""))
            elif msg.get("role") == "assistant":
                self.memory.chat_memory.add_ai_message(msg.get("content", ""))

    def _build_system_prompt(self) -> str:
        """Build system prompt with user profile and destination context"""
        base_prompt = self.prompts.get('trip_planning_system', '')
        
        # Add destination context
        destination = self.recommendation.destination
        dest_context = f"""
DESTINATION CONTEXT:
- Location: {destination.city}, {destination.country}
- Description: {destination.description or 'N/A'}
- Selected with rating: {self.recommendation.rating.value if self.recommendation.rating else 'N/A'}/3 stars

Current trip details (may be incomplete - extract and update during conversation):
- Season: {getattr(self.recommendation, 'optimal_season', 'Not specified')}
- Budget: {getattr(self.recommendation, 'estimated_budget', 'Not specified')}
- Highlights: {getattr(self.recommendation, 'highlights', [])}
"""

        # Add user profile context
        prefs = self.user_profile.preferences
        constraints = self.user_profile.constraints
        profile_context = f"""
USER PROFILE:
- Traveler Type: {prefs.traveler_type}
- Activity Level: {prefs.activity_level}
- Preferred Environment: {prefs.environment}
- Accommodation Style: {prefs.accommodation_style}
- Budget Sensitivity: {prefs.budget_sensitivity}
- Culture Interest: {prefs.culture_interest}
- Food Importance: {prefs.food_importance}
- Dietary: {', '.join(constraints.dietary_restrictions) if constraints.dietary_restrictions else 'None'}
"""

        # Add constraints if any
        if self.user_profile.constraints:
            constraints_context = f"""
CONSTRAINTS:
- Mobility limitations: {', '.join(constraints.mobility_limitations) if constraints.mobility_limitations else 'None'}
- Climate preferences: {', '.join(constraints.climate_preferences) if constraints.climate_preferences else 'None'}
- Language preferences: {', '.join(constraints.language_preferences) if constraints.language_preferences else 'None'}
"""
        else:
            constraints_context = ""

        # Combine all context
        system_prompt = f"""{base_prompt}

{dest_context}

{profile_context}

{constraints_context}

CRITICAL - Structured Information Extraction:

As you gather information during the conversation, identify and extract:

1. **Trip Dates & Duration**
   - Start date, end date
   - Number of days
   - Season/time of year

2. **Budget Information**
   - Total budget or daily budget
   - Currency
   - What's included (flights, accommodation, activities, food)

3. **Weather & Packing**
   - Expected weather conditions
   - Temperature range
   - What to pack (clothing, essentials)

4. **Logistics**
   - Flight options and prices
   - Accommodation recommendations (with price ranges)
   - Local transportation options

5. **Activities & Highlights**
   - Must-see attractions
   - Hidden gems
   - Day-by-day rough itinerary

6. **Practical Info**
   - Visa requirements
   - Vaccinations needed
   - Travel insurance
   - Emergency contacts
   - Local customs and etiquette

When you've gathered enough information in a category, use structured tags:

<trip_update>
{{
  "field": "optimal_season",
  "value": "March-April (Spring, Sakura season)"
}}
</trip_update>

<trip_update>
{{
  "field": "estimated_budget",
  "value": 1500,
  "currency": "USD"
}}
</trip_update>

<trip_update>
{{
  "field": "highlights",
  "value": ["Shibuya Crossing", "Senso-ji Temple", "Tsukiji Market"]
}}
</trip_update>

Be conversational and helpful - extract information naturally through dialogue!
"""
        
        print(f"🎯 PLANNING SYSTEM PROMPT built (length: {len(system_prompt)} chars)")
        return system_prompt

    async def chat(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        Stream chat response using LangChain with full context awareness
        """
        print(f"\n{'='*80}")
        print(f"💬 PLANNING AGENT - Processing user message")
        print(f"   User: {user_message[:100]}...")
        print(f"   Memory size: {len(self.memory.chat_memory.messages)} messages")
        print(f"{'='*80}\n")

        # Build messages with context
        system_prompt = self._build_system_prompt()
        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history
        history = self.memory.chat_memory.messages
        messages.extend(history)

        # Add current user message
        messages.append(HumanMessage(content=user_message))

        # Stream response from LLM
        print("🤖 Calling LLM for planning response...")
        full_response = ""
        chunk_count = 0

        async for chunk in self.llm.astream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                token = chunk.content
                full_response += token
                chunk_count += 1
                yield token

        # Save to memory
        self.memory.chat_memory.add_user_message(user_message)
        self.memory.chat_memory.add_ai_message(full_response)

        print(f"\n{'='*80}")
        print(f"✅ LLM Response complete")
        print(f"   Chunks: {chunk_count}")
        print(f"   Total length: {len(full_response)} chars")
        print(f"   Contains <trip_update>: {'<trip_update>' in full_response}")
        print(f"{'='*80}\n")
