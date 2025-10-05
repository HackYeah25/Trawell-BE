"""
Group Moderator Agent - AI moderator for collaborative travel planning
Handles compatibility analysis, conflict resolution, and group suggestions
"""
import json
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from app.config import settings
from app.models.group_conversation import (
    GroupParticipant,
    GroupMessage,
    CompatibilityAnalysis,
    CompatibilityConflict,
    CompatibilityLevel,
    AIResponseTrigger,
)


class GroupModeratorAgent:
    """AI agent for moderating group travel planning conversations"""

    def __init__(self):
        if not settings.openai_api_key:
            print("Warning: OPENAI_API_KEY not set. GroupModeratorAgent will not function.")
            self.llm = None
            self.streaming_llm = None
            return
            
        self.llm = ChatOpenAI(
            model=settings.default_llm_model,
            temperature=0.7,
            api_key=settings.openai_api_key,
        )

        self.streaming_llm = ChatOpenAI(
            model=settings.default_llm_model,
            temperature=0.7,
            api_key=settings.openai_api_key,
            streaming=True,
        )

        self._build_chains()

    def _build_chains(self):
        """Build LangChain chains for different tasks"""

        # Compatibility Analysis Chain
        self.compatibility_prompt = ChatPromptTemplate.from_template("""
You are analyzing travel compatibility for a group planning a trip together.

Participant Profiles:
{profiles_json}

Analyze the compatibility and output ONLY valid JSON with this exact structure:
{{
  "compatibility_level": "high|medium|low|conflicted",
  "compatibility_score": 0.0-1.0,
  "common_ground": ["list", "of", "shared", "interests"],
  "conflicts": [
    {{
      "aspect": "specific aspect",
      "users": ["User1", "User2"],
      "issue": "description of conflict",
      "severity": 0.0-1.0
    }}
  ],
  "compromise_needed": true|false,
  "suggested_approach": "overall strategy for this group",
  "participant_scores": {{
    "participant_name": 0.0-1.0
  }}
}}

Rules:
- compatibility_score: 0.8-1.0 = high, 0.5-0.79 = medium, 0.3-0.49 = low, <0.3 = conflicted
- Focus on: traveler_type, activity_level, accommodation_style, environment, budget
- Be specific in conflicts: identify WHO wants WHAT and WHY it conflicts
- suggested_approach should be actionable and concrete
- participant_scores: individual compatibility vs group average (1.0 = perfect match)
""")

        self.compatibility_chain = (
            {"profiles_json": RunnablePassthrough()}
            | self.compatibility_prompt
            | self.llm
            | StrOutputParser()
        )

        # Group Suggestion Prompt (High Compatibility)
        self.suggestion_high_prompt = ChatPromptTemplate.from_template("""
You are a friendly AI travel assistant helping a highly compatible group plan their trip.

Group Context:
- Participants: {participant_count}
- Compatibility: HIGH
- Common Interests: {common_ground}

Recent Conversation:
{recent_messages}

Suggest 3 destinations that will delight everyone. For each destination:
1. Name and brief description
2. Why it perfectly matches the group's shared interests
3. Specific activities/experiences they'll love

Keep response natural, enthusiastic, and conversational (2-3 paragraphs max).
Start with a friendly acknowledgment of what you heard in their conversation.
""")

        self.suggestion_high_chain = (
            self.suggestion_high_prompt
            | self.llm
            | StrOutputParser()
        )

        # Group Suggestion Prompt (Low Compatibility / Conflicts)
        self.suggestion_low_prompt = ChatPromptTemplate.from_template("""
You are a diplomatic AI travel assistant helping a group with different preferences.

Group Context:
- Participants: {participant_count}
- Compatibility: {compatibility_level}
- Common Ground: {common_ground}
- Conflicts: {conflicts_json}

Recent Conversation:
{recent_messages}

The group has different preferences. Provide:

1. **Honest acknowledgment**: Briefly note the different preferences you see
2. **Compromise destinations** (2-3 options):
   - Places with built-in variety (e.g., Barcelona: beach + city + culture)
   - Explain how EACH person's needs are met
3. **Flexible approach**:
   - Shared base location idea
   - Split activity suggestions
   - What can bring everyone together (meals, evenings)

Be warm, practical, and solution-oriented. Show you understand each person.
Keep it conversational (3-4 paragraphs max).
""")

        self.suggestion_low_chain = (
            self.suggestion_low_prompt
            | self.llm
            | StrOutputParser()
        )

        # AI Moderator Intervention Prompt
        self.moderator_prompt = ChatPromptTemplate.from_template("""
You are an AI moderator in a group travel planning discussion.

Group Compatibility:
{compatibility_summary}

Recent Discussion (last 10 messages):
{recent_messages}

Your role:
- Synthesize what you're hearing from the group
- Identify emerging consensus or patterns
- Gently point out important considerations they might be missing
- Suggest concrete next steps

Respond naturally as if you're a helpful friend in the conversation.
Be concise (2-3 sentences) unless they ask for detailed suggestions.
If they seem aligned, encourage them. If there's tension, help bridge it.
""")

        self.moderator_chain = (
            self.moderator_prompt
            | self.llm
            | StrOutputParser()
        )

    async def analyze_compatibility(
        self, participants: List[GroupParticipant]
    ) -> CompatibilityAnalysis:
        """
        Analyze compatibility between group participants

        Args:
            participants: List of group participants with profiles

        Returns:
            CompatibilityAnalysis with scores, conflicts, and suggestions
        """
        if len(participants) < 2:
            return CompatibilityAnalysis(
                compatibility_level=CompatibilityLevel.HIGH,
                compatibility_score=1.0,
                common_ground=["Starting group - waiting for more participants"],
                conflicts=[],
                compromise_needed=False,
                suggested_approach="Invite more friends to join!",
                participant_scores={},
            )

        # Prepare profiles for analysis
        profiles = [
            {
                "name": p.user_name,
                "profile": p.user_profile,
            }
            for p in participants
        ]

        profiles_json = json.dumps(profiles, indent=2)

        # Run compatibility analysis
        try:
            result_str = await self.compatibility_chain.ainvoke(profiles_json)

            # Parse JSON response
            result = json.loads(result_str)

            # Convert to CompatibilityAnalysis model
            conflicts = [
                CompatibilityConflict(**c) for c in result.get("conflicts", [])
            ]

            analysis = CompatibilityAnalysis(
                compatibility_level=CompatibilityLevel(result["compatibility_level"]),
                compatibility_score=result["compatibility_score"],
                common_ground=result.get("common_ground", []),
                conflicts=conflicts,
                compromise_needed=result.get("compromise_needed", False),
                suggested_approach=result.get("suggested_approach", ""),
                participant_scores=result.get("participant_scores", {}),
            )

            return analysis

        except Exception as e:
            # Fallback to basic analysis on error
            print(f"Compatibility analysis error: {e}")
            return CompatibilityAnalysis(
                compatibility_level=CompatibilityLevel.MEDIUM,
                compatibility_score=0.6,
                common_ground=["Travel planning"],
                conflicts=[],
                compromise_needed=False,
                suggested_approach="Let's explore options together!",
                participant_scores={},
            )

    def should_ai_respond(
        self,
        messages: List[GroupMessage],
        participants: List[GroupParticipant],
    ) -> AIResponseTrigger:
        """
        Determine if AI should respond to the conversation

        Args:
            messages: Recent messages in conversation
            participants: Current participants

        Returns:
            AIResponseTrigger with decision and reason
        """
        if not messages:
            return AIResponseTrigger(triggered=False)

        recent_messages = messages[-10:]  # Last 10 messages

        # Trigger 1: Manual invocation
        last_message = messages[-1]
        if last_message.metadata and last_message.metadata.get("ai_invoked"):
            return AIResponseTrigger(
                triggered=True,
                reason="User explicitly asked for AI input",
                trigger_type="manual",
            )

        # Trigger 2: Direct question to AI
        last_text = last_message.message.lower()
        ai_triggers = [
            "ai",
            "suggest",
            "what do you think",
            "any ideas",
            "recommend",
            "help us",
            "what about",
        ]
        if any(trigger in last_text for trigger in ai_triggers):
            return AIResponseTrigger(
                triggered=True,
                reason="Direct question or request to AI",
                trigger_type="direct_question",
            )

        # Trigger 3: Everyone has spoken at least once
        user_messages = [m for m in recent_messages if m.user_id]
        users_who_spoke = set(m.user_id for m in user_messages if m.user_id)
        all_participant_ids = set(
            p.user_id for p in participants if p.user_id and p.is_active
        )

        if (
            users_who_spoke == all_participant_ids
            and len(recent_messages) >= len(participants)
        ):
            return AIResponseTrigger(
                triggered=True,
                reason="All participants have shared their thoughts",
                trigger_type="all_spoke",
            )

        # Trigger 4: Impasse - 6+ messages without AI input
        ai_messages = [m for m in recent_messages if not m.user_id]
        user_only_streak = len(recent_messages) - len(ai_messages)

        if user_only_streak >= 6:
            return AIResponseTrigger(
                triggered=True,
                reason="Extended discussion without AI input",
                trigger_type="impasse",
            )

        return AIResponseTrigger(triggered=False)

    async def generate_group_suggestion(
        self,
        participants: List[GroupParticipant],
        messages: List[GroupMessage],
        compatibility: CompatibilityAnalysis,
    ) -> str:
        """
        Generate AI suggestion for the group

        Args:
            participants: Group participants
            messages: Conversation messages
            compatibility: Compatibility analysis

        Returns:
            AI suggestion text
        """
        # Format recent messages
        recent_msgs = messages[-15:] if len(messages) > 15 else messages
        formatted_messages = "\n".join(
            [
                f"{m.user_name or 'AI'}: {m.message}"
                for m in recent_msgs
                if m.message_type.value in ["user", "ai_suggestion"]
            ]
        )

        # Choose chain based on compatibility
        if compatibility.compatibility_level in [
            CompatibilityLevel.HIGH,
            CompatibilityLevel.MEDIUM,
        ]:
            response = await self.suggestion_high_chain.ainvoke(
                {
                    "participant_count": len(participants),
                    "common_ground": ", ".join(compatibility.common_ground),
                    "recent_messages": formatted_messages,
                }
            )
        else:
            # Low compatibility or conflicted
            conflicts_json = json.dumps(
                [c.dict() for c in compatibility.conflicts], indent=2
            )

            response = await self.suggestion_low_chain.ainvoke(
                {
                    "participant_count": len(participants),
                    "compatibility_level": compatibility.compatibility_level.value,
                    "common_ground": ", ".join(compatibility.common_ground)
                    if compatibility.common_ground
                    else "None identified yet",
                    "conflicts_json": conflicts_json,
                    "recent_messages": formatted_messages,
                }
            )

        return response

    async def generate_moderator_response(
        self,
        participants: List[GroupParticipant],
        messages: List[GroupMessage],
        compatibility: CompatibilityAnalysis,
    ) -> str:
        """
        Generate AI moderator intervention

        Args:
            participants: Group participants
            messages: Conversation messages
            compatibility: Compatibility analysis

        Returns:
            Moderator response text
        """
        # Format recent messages
        recent_msgs = messages[-10:] if len(messages) > 10 else messages
        formatted_messages = "\n".join(
            [f"{m.user_name or 'AI'}: {m.message}" for m in recent_msgs]
        )

        # Compatibility summary
        compatibility_summary = f"""
Compatibility Level: {compatibility.compatibility_level.value}
Common Ground: {', '.join(compatibility.common_ground)}
Conflicts: {len(compatibility.conflicts)} identified
Compromise Needed: {compatibility.compromise_needed}
"""

        response = await self.moderator_chain.ainvoke(
            {
                "compatibility_summary": compatibility_summary,
                "recent_messages": formatted_messages,
            }
        )

        return response

    async def stream_response(
        self,
        participants: List[GroupParticipant],
        messages: List[GroupMessage],
        compatibility: CompatibilityAnalysis,
    ) -> AsyncIterator[str]:
        """
        Stream AI response token by token

        Args:
            participants: Group participants
            messages: Conversation messages
            compatibility: Compatibility analysis

        Yields:
            Response tokens as they're generated
        """
        # Use same logic as generate_group_suggestion but with streaming
        recent_msgs = messages[-15:] if len(messages) > 15 else messages
        formatted_messages = "\n".join(
            [
                f"{m.user_name or 'AI'}: {m.message}"
                for m in recent_msgs
                if m.message_type.value in ["user", "ai_suggestion"]
            ]
        )

        if compatibility.compatibility_level in [
            CompatibilityLevel.HIGH,
            CompatibilityLevel.MEDIUM,
        ]:
            prompt = self.suggestion_high_prompt.format(
                participant_count=len(participants),
                common_ground=", ".join(compatibility.common_ground),
                recent_messages=formatted_messages,
            )
        else:
            conflicts_json = json.dumps(
                [c.dict() for c in compatibility.conflicts], indent=2
            )

            prompt = self.suggestion_low_prompt.format(
                participant_count=len(participants),
                compatibility_level=compatibility.compatibility_level.value,
                common_ground=", ".join(compatibility.common_ground)
                if compatibility.common_ground
                else "None identified yet",
                conflicts_json=conflicts_json,
                recent_messages=formatted_messages,
            )

        # Stream response
        async for chunk in self.streaming_llm.astream(prompt):
            if chunk.content:
                yield chunk.content


# Global instance (lazy initialization)
_group_moderator_instance = None

def get_group_moderator() -> GroupModeratorAgent:
    """Get or create the global GroupModeratorAgent instance"""
    global _group_moderator_instance
    if _group_moderator_instance is None:
        _group_moderator_instance = GroupModeratorAgent()
    return _group_moderator_instance

# For backward compatibility
group_moderator = None
