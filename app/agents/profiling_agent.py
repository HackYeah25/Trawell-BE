"""
Profiling Agent - Manages user profiling conversation with validation
"""
import os
import yaml
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from app.models.profiling import (
    ProfilingQuestion,
    ProfilingQuestionResponse,
    ProfilingSession,
    QuestionValidationStatus,
)
from app.models.user import UserProfile, UserPreferences, UserConstraints
from app.config import settings


class ProfilingAgent:
    """Agent for conducting profiling conversations with validation"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.profiling_llm_model,
            api_key=settings.openai_api_key,
            temperature=0.7,
            max_tokens=2000,
            streaming=True,
        )

        # Load profiling configuration from YAML
        self.config = self._load_config()
        self.questions = self._load_questions()

    def _load_config(self) -> Dict[str, Any]:
        """Load profiling configuration from YAML"""
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "profiling.yaml"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_questions(self) -> List[ProfilingQuestion]:
        """Parse questions from config into ProfilingQuestion objects"""
        questions = []
        for q in self.config["questions"]:
            questions.append(ProfilingQuestion(**q))
        return sorted(questions, key=lambda x: x.order)

    def get_all_questions(self) -> List[ProfilingQuestion]:
        """Get all profiling questions"""
        return self.questions

    def get_critical_questions(self) -> List[str]:
        """Get list of critical question IDs"""
        return self.config["validation_rules"]["critical_questions"]

    def get_intro_message(self) -> str:
        """Get introduction message"""
        return self.config["intro_message"]

    def get_completion_message(self) -> str:
        """Get completion message"""
        return self.config["completion_message"]

    def get_question_by_id(self, question_id: str) -> Optional[ProfilingQuestion]:
        """Get specific question by ID"""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None

    def get_next_question(
        self, session: ProfilingSession
    ) -> Optional[ProfilingQuestion]:
        """Get next question based on session progress"""
        if session.current_question_index >= len(self.questions):
            return None
        return self.questions[session.current_question_index]

    async def validate_answer(
        self,
        question: ProfilingQuestion,
        answer: str,
        session: ProfilingSession,
    ) -> tuple[QuestionValidationStatus, Optional[str], Optional[Any]]:
        """
        Validate user's answer against question requirements

        Returns:
            - validation_status: Status of the answer
            - feedback: Feedback message if insufficient
            - extracted_value: Extracted structured value if sufficient
        """
        # Check minimum token count
        min_tokens = question.validation.get("min_tokens", 3)
        token_count = len(answer.split())

        if token_count < min_tokens:
            return (
                QuestionValidationStatus.INSUFFICIENT,
                "Could you provide a bit more detail?",
                None,
            )

        # Use LLM to validate against required information
        validation_prompt = self._build_validation_prompt(question, answer)

        response = await self.llm.ainvoke([SystemMessage(content=validation_prompt)])
        validation_result = response.content.strip()

        # Parse validation result (expects JSON-like response)
        try:
            import json

            result = json.loads(validation_result)

            status_map = {
                "insufficient": QuestionValidationStatus.INSUFFICIENT,
                "sufficient": QuestionValidationStatus.SUFFICIENT,
                "complete": QuestionValidationStatus.COMPLETE,
            }

            status = status_map.get(
                result.get("status", "insufficient"),
                QuestionValidationStatus.INSUFFICIENT,
            )
            feedback = result.get("feedback")
            extracted = result.get("extracted_value")

            return status, feedback, extracted

        except Exception as e:
            print(f"Validation parsing error: {e}")
            # Default to sufficient if parsing fails but answer has content
            return QuestionValidationStatus.SUFFICIENT, None, None

    def _build_validation_prompt(
        self, question: ProfilingQuestion, answer: str
    ) -> str:
        """Build prompt for validating user answer"""
        required_info = question.validation.get("required_info", [])

        prompt = f"""You are validating a user's answer to a profiling question.

Question: {question.question}

Required Information: {', '.join(required_info)}

User's Answer: {answer}

Evaluate if the answer contains sufficient information to satisfy the requirements.

Respond ONLY with valid JSON in this exact format:
{{
    "status": "insufficient" | "sufficient" | "complete",
    "feedback": "specific feedback if insufficient, otherwise null",
    "extracted_value": "the key information extracted from the answer"
}}

Rules:
- "insufficient": Answer is too vague or missing key information
- "sufficient": Answer provides minimum required information
- "complete": Answer is detailed and comprehensive

If insufficient, provide specific feedback about what's missing.
Extract the core value from the answer (e.g., "explorer", "high activity", etc.)
"""
        return prompt

    async def generate_follow_up(
        self, question: ProfilingQuestion, answer: str, follow_up_count: int
    ) -> str:
        """Generate contextual follow-up question"""
        max_attempts = self.config["validation_rules"]["max_follow_up_attempts"]

        if follow_up_count >= max_attempts:
            # After max attempts, move on with what we have
            return None

        # Check if question has predefined follow-ups
        follow_ups = question.validation.get("follow_up_questions", [])

        if follow_ups:
            # Use predefined follow-ups
            if follow_up_count < len(follow_ups):
                return follow_ups[follow_up_count]["question"]

        # Generate dynamic follow-up
        examples = question.validation.get("examples_if_unclear", [])
        examples_text = "\n".join(examples) if examples else ""

        prompt = f"""The user gave a vague answer to this question:

Question: {question.question}

Their answer: {answer}

Context: {question.context}

{f"Here are some examples you can use: {examples_text}" if examples_text else ""}

Generate a friendly follow-up question to get more specific information.
Be conversational and encouraging. Keep it brief (1-2 sentences).
"""

        response = await self.llm.ainvoke([SystemMessage(content=prompt)])
        return response.content.strip()

    async def stream_response(
        self,
        session: ProfilingSession,
        conversation_history: List[Dict[str, str]],
    ) -> AsyncIterator[str]:
        """Stream AI response for profiling conversation"""
        current_question = self.get_next_question(session)

        if not current_question:
            # Profiling complete
            async for token in self._stream_completion_message(session):
                yield token
            return

        # Build system prompt
        system_prompt = self._build_system_prompt(session, current_question)

        # Build conversation messages
        messages = [SystemMessage(content=system_prompt)]

        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Stream response
        async for chunk in self.llm.astream(messages):
            if hasattr(chunk, "content"):
                yield chunk.content

    def _build_system_prompt(
        self, session: ProfilingSession, current_question: ProfilingQuestion
    ) -> str:
        """Build system prompt for current profiling state"""
        base_prompt = self.config["system_prompt"]

        progress = f"""
Current Progress:
- Question {session.current_question_index + 1} of {len(self.questions)}
- Profile completeness: {session.profile_completeness * 100:.0f}%

Current Question Context:
{current_question.context}

Current Question:
{current_question.question}

Validation Requirements:
{current_question.validation}
"""

        return f"{base_prompt}\n\n{progress}"

    async def _stream_completion_message(
        self, session: ProfilingSession
    ) -> AsyncIterator[str]:
        """Stream completion message"""
        message = self.get_completion_message()
        for char in message:
            yield char

    def calculate_completeness(self, session: ProfilingSession) -> float:
        """Calculate profile completeness percentage"""
        if not self.questions:
            return 0.0

        total_questions = len(self.questions)
        answered_questions = len(
            [
                r
                for r in session.responses
                if r.validation_status
                in [QuestionValidationStatus.SUFFICIENT, QuestionValidationStatus.COMPLETE]
            ]
        )

        return answered_questions / total_questions

    def is_profile_complete(self, session: ProfilingSession) -> bool:
        """Check if profile meets minimum completeness requirements"""
        min_completeness = self.config["validation_rules"]["min_profile_completeness"]
        current_completeness = self.calculate_completeness(session)

        if current_completeness < min_completeness:
            return False

        # Check if all critical questions are answered
        critical_questions = self.get_critical_questions()
        answered_critical = set()

        for response in session.responses:
            if response.validation_status in [
                QuestionValidationStatus.SUFFICIENT,
                QuestionValidationStatus.COMPLETE,
            ]:
                answered_critical.add(response.question_id)

        return all(q in answered_critical for q in critical_questions)

    def extract_user_profile(self, session: ProfilingSession) -> UserProfile:
        """Extract UserProfile from completed profiling session"""
        preferences = UserPreferences()
        constraints = UserConstraints()
        past_destinations = []
        wishlist_regions = []

        for response in session.responses:
            if response.validation_status not in [
                QuestionValidationStatus.SUFFICIENT,
                QuestionValidationStatus.COMPLETE,
            ]:
                continue

            question = self.get_question_by_id(response.question_id)
            if not question:
                continue

            extract_config = question.extracts_to
            field = extract_config.get("field")
            value = response.extracted_value

            # Map to UserProfile fields
            if field and value:
                if field.startswith("preferences."):
                    pref_field = field.split(".", 1)[1]
                    setattr(preferences, pref_field, value)
                elif field.startswith("constraints."):
                    const_field = field.split(".", 1)[1]
                    setattr(constraints, const_field, value)
                elif field == "past_destinations":
                    past_destinations = value if isinstance(value, list) else [value]
                elif field == "wishlist_regions":
                    wishlist_regions = value if isinstance(value, list) else [value]

        return UserProfile(
            user_id=session.user_id or f"temp_{session.session_id}",
            preferences=preferences,
            constraints=constraints,
            past_destinations=past_destinations,
            wishlist_regions=wishlist_regions,
        )


# Global instance
profiling_agent = ProfilingAgent()
