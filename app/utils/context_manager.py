"""
Context manager for conversation handling and token management
"""
import json
from typing import List, Optional
import logging
from datetime import datetime

from app.models.user import UserProfile
from app.models.conversation import Message, MessageRole, Conversation
from app.services.langchain_service import get_langchain_service
from app.prompts.loader import get_prompt_loader

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages conversation context with automatic truncation
    when approaching token limits
    """

    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.langchain_service = get_langchain_service()
        self.prompt_loader = get_prompt_loader()

    def build_user_profile_prompt(self, profile: UserProfile) -> str:
        """
        Build system prompt with user profile

        Args:
            profile: User profile

        Returns:
            System prompt with user profile
        """
        profile_json = json.dumps(profile.model_dump(), indent=2, default=str)

        return self.prompt_loader.load_template(
            module="system",
            prompt_name="user_profile_prefix",
            profile_json=profile_json
        )

    def build_conversation_context(
        self,
        user_profile: UserProfile,
        conversation_history: List[Message],
        system_prompt: Optional[str] = None
    ) -> List[Message]:
        """
        Build complete conversation context with user profile

        Args:
            user_profile: User profile
            conversation_history: Previous messages
            system_prompt: Optional additional system prompt

        Returns:
            Complete message list with profile and context
        """
        messages = []

        # 1. Always start with user profile
        profile_prompt = self.build_user_profile_prompt(user_profile)

        # 2. Add system prompt if provided
        if system_prompt:
            combined_system = f"{profile_prompt}\n\n{system_prompt}"
        else:
            combined_system = profile_prompt

        messages.append(Message(
            role=MessageRole.SYSTEM,
            content=combined_system
        ))

        # 3. Add conversation history (with truncation if needed)
        truncated_history = self._truncate_if_needed(
            conversation_history,
            reserved_tokens=self.langchain_service.count_tokens(combined_system)
        )

        messages.extend(truncated_history)

        return messages

    def _truncate_if_needed(
        self,
        messages: List[Message],
        reserved_tokens: int = 0
    ) -> List[Message]:
        """
        Truncate message history if it exceeds token limit

        Args:
            messages: List of messages
            reserved_tokens: Tokens already used (e.g., system prompt)

        Returns:
            Truncated message list
        """
        # Estimate current tokens
        current_tokens = sum(
            self.langchain_service.count_tokens(msg.content)
            for msg in messages
        )
        current_tokens += reserved_tokens

        # If within limit, return as is
        if current_tokens <= self.max_tokens:
            return messages

        logger.info(f"Context truncation needed: {current_tokens} tokens > {self.max_tokens} limit")

        # Strategy: Keep first message and most recent messages
        # Summarize the middle portion

        if len(messages) <= 2:
            # Can't truncate further
            return messages

        # Keep first and last few messages
        keep_recent = 5
        first_msg = messages[0]
        recent_msgs = messages[-keep_recent:]
        middle_msgs = messages[1:-keep_recent] if len(messages) > keep_recent + 1 else []

        # Create summary of middle messages
        if middle_msgs:
            summary = self._summarize_messages(middle_msgs)
            summary_msg = Message(
                role=MessageRole.SYSTEM,
                content=f"[Previous conversation summary: {summary}]"
            )

            return [first_msg, summary_msg] + recent_msgs
        else:
            return [first_msg] + recent_msgs

    def _summarize_messages(self, messages: List[Message]) -> str:
        """
        Create a summary of messages (simple version)

        Args:
            messages: Messages to summarize

        Returns:
            Summary text
        """
        # Simple summarization - just note the topics
        # In production, you'd use LLM to create better summaries

        topics = []
        for msg in messages:
            if msg.role == MessageRole.USER:
                # Take first 50 chars as topic
                topic = msg.content[:50].strip()
                if len(msg.content) > 50:
                    topic += "..."
                topics.append(f"User asked: {topic}")

        return "; ".join(topics[-5:])  # Last 5 topics

    def add_message_to_context(
        self,
        context: List[Message],
        new_message: Message
    ) -> List[Message]:
        """
        Add a new message to context

        Args:
            context: Current context
            new_message: New message to add

        Returns:
            Updated context
        """
        updated_context = context + [new_message]

        # Check if truncation needed
        total_tokens = sum(
            self.langchain_service.count_tokens(msg.content)
            for msg in updated_context
        )

        if total_tokens > self.max_tokens:
            return self._truncate_if_needed(updated_context)

        return updated_context

    def estimate_remaining_tokens(self, context: List[Message]) -> int:
        """
        Estimate how many tokens are left in the context window

        Args:
            context: Current context

        Returns:
            Remaining token count
        """
        used_tokens = sum(
            self.langchain_service.count_tokens(msg.content)
            for msg in context
        )

        return max(0, self.max_tokens - used_tokens)

    def should_summarize(self, conversation: Conversation) -> bool:
        """
        Check if conversation should be summarized

        Args:
            conversation: Conversation to check

        Returns:
            True if summarization is recommended
        """
        total_tokens = sum(
            self.langchain_service.count_tokens(msg.content)
            for msg in conversation.messages
        )

        # Summarize if we're at 80% capacity
        return total_tokens > (self.max_tokens * 0.8)


# Global instance
context_manager = ContextManager()


def get_context_manager() -> ContextManager:
    """Get context manager instance"""
    return context_manager
