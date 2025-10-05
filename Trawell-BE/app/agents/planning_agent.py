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
        existing_messages: list = None,
        logistics_data: dict = None
    ):
        self.recommendation = recommendation
        self.user_profile = user_profile
        self.logistics_data = logistics_data or {}
        
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

    def generate_opening_message(self) -> str:
        """
        Generate opening message with logistics data summary
        """
        prompt_loader = get_prompt_loader()
        opening_template = self.prompts.get('planning_opening_with_logistics', '')
        
        if not opening_template:
            return "Hello! I'm ready to help you plan your trip. What would you like to know?"
        
        # Build flight summary
        flight_summary = "No flight data available yet."
        if self.logistics_data and self.logistics_data.get('flights'):
            flights = self.logistics_data['flights']
            outbound = flights.get('outbound', {})
            return_flight = flights.get('return', {})
            
            if outbound:
                outbound_price = f"{outbound.get('price', 'N/A')} {outbound.get('currency', 'EUR')}"
                outbound_duration = outbound.get('itinerary', {}).get('totalDuration', 'N/A')
                flight_summary = f"Outbound flight: {outbound_duration} for {outbound_price}"
                
                if return_flight:
                    return_price = f"{return_flight.get('price', 'N/A')} {return_flight.get('currency', 'EUR')}"
                    return_duration = return_flight.get('itinerary', {}).get('totalDuration', 'N/A')
                    flight_summary += f"\nReturn flight: {return_duration} for {return_price}"
                    total_price = float(outbound.get('price', 0)) + float(return_flight.get('price', 0))
                    flight_summary += f"\nTotal: {total_price:.2f} {outbound.get('currency', 'EUR')}"
        
        # Build hotel summary
        hotel_summary = "No hotel data available yet."
        if self.logistics_data and self.logistics_data.get('hotels'):
            hotels = self.logistics_data['hotels']
            if hotels:
                top_3 = hotels[:3]
                hotel_lines = []
                for hotel in top_3:
                    name = hotel.get('name', 'Unknown')
                    price = hotel.get('price', 'N/A')
                    currency = hotel.get('currency', 'USD')
                    hotel_lines.append(f"• {name}: {price} {currency}")
                hotel_summary = "\n".join(hotel_lines)
                if len(hotels) > 3:
                    hotel_summary += f"\n(+{len(hotels) - 3} more options available)"
        
        # Build weather summary
        weather_summary = "Weather data will be available soon."
        if self.logistics_data and self.logistics_data.get('weather'):
            weather = self.logistics_data['weather']
            weather_summary = weather.get('summary', 'Weather forecast available for your travel dates.')
        
        # Format the opening message
        destination = self.recommendation.destination
        destination_name = f"{destination.city}, {destination.country}"
        
        opening_message = opening_template.format(
            destination=destination_name,
            flight_summary=flight_summary,
            hotel_summary=hotel_summary,
            weather_summary=weather_summary
        )
        
        return opening_message

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

Current trip details (may be incomplete - will be gathered during conversation):
- This is a newly created trip, we'll build the plan together
"""

        # Add logistics data context
        logistics_context = ""
        if self.logistics_data:
            flights = self.logistics_data.get('flights', {})
            hotels = self.logistics_data.get('hotels', [])
            weather = self.logistics_data.get('weather', {})
            
            logistics_context = "\nLOGISTICS DATA AVAILABLE:\n"
            
            if flights and flights.get('outbound'):
                outbound = flights['outbound']
                return_flight = flights.get('return', {})
                logistics_context += f"""
FLIGHTS:
- Outbound: {outbound.get('itinerary', {}).get('totalDuration', 'N/A')} for {outbound.get('price', 'N/A')} {outbound.get('currency', 'EUR')}
  Route: {' → '.join([seg.get('from', '') for seg in outbound.get('itinerary', {}).get('segments', [])] + [outbound.get('itinerary', {}).get('segments', [{}])[-1].get('to', '') if outbound.get('itinerary', {}).get('segments') else ''])}
"""
                if return_flight:
                    logistics_context += f"- Return: {return_flight.get('itinerary', {}).get('totalDuration', 'N/A')} for {return_flight.get('price', 'N/A')} {return_flight.get('currency', 'EUR')}\n"
            
            if hotels:
                logistics_context += f"\nHOTELS ({len(hotels)} options found):\n"
                for i, hotel in enumerate(hotels[:3], 1):
                    logistics_context += f"- {hotel.get('name', 'N/A')}: {hotel.get('price', 'N/A')} {hotel.get('currency', 'USD')}\n"
            
            if weather:
                logistics_context += f"\nWEATHER FORECAST:\n- {weather.get('summary', 'Weather data available')}\n"

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
{logistics_context}

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

**IMPORTANT - Visual Enhancement:**

When mentioning specific attractions, landmarks, or places, include a photo tag so the user can see it:

<photo>{{
  "query": "Uluwatu Temple Bali",
  "caption": "Uluwatu Temple - Perched on a cliff with breathtaking sunset views"
}}</photo>

Use photo tags for:
- Temples, monuments, landmarks
- Beaches, waterfalls, natural attractions
- Famous viewpoints and scenic spots
- Cultural sites and museums

Keep captions short and descriptive. The system will automatically fetch and display the photos inline.

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
