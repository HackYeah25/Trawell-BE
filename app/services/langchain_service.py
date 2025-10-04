"""
LangChain service wrapper for LLM operations
"""
from typing import List, Dict, Any, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from app.config import settings
from app.models.conversation import Message, MessageRole

logger = logging.getLogger(__name__)


class LangChainService:
    """Service for LangChain LLM operations"""

    def __init__(self):
        self.llm: Optional[Any] = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        try:
            # Default to OpenAI if API key is available
            if settings.openai_api_key:
                self.llm = ChatOpenAI(
                    model=settings.default_llm_model,
                    temperature=settings.default_llm_temperature,
                    max_tokens=settings.max_tokens_response,
                    openai_api_key=settings.openai_api_key
                )
                logger.info(f"Initialized OpenAI LLM: {settings.default_llm_model}")

            # Fallback to Anthropic if OpenAI not available
            elif settings.anthropic_api_key:
                self.llm = ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    temperature=settings.default_llm_temperature,
                    max_tokens=settings.max_tokens_response,
                    anthropic_api_key=settings.anthropic_api_key
                )
                logger.info("Initialized Anthropic Claude LLM")

            else:
                logger.warning("No LLM API keys configured!")

        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise

    def _convert_messages(self, messages: List[Message]) -> List[Any]:
        """Convert our Message models to LangChain message format"""
        langchain_messages = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == MessageRole.USER:
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                langchain_messages.append(AIMessage(content=msg.content))

        return langchain_messages

    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Send chat messages to LLM and get response

        Args:
            messages: List of conversation messages
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            stream: Whether to stream the response

        Returns:
            LLM response as string
        """
        if not self.llm:
            raise ValueError("LLM not initialized")

        try:
            # Convert messages to LangChain format
            langchain_messages = self._convert_messages(messages)

            # Override parameters if provided
            llm = self.llm
            if temperature is not None:
                llm = llm.bind(temperature=temperature)
            if max_tokens is not None:
                llm = llm.bind(max_tokens=max_tokens)

            # Get response
            if stream:
                # TODO: Implement streaming
                response = await llm.ainvoke(langchain_messages)
            else:
                response = await llm.ainvoke(langchain_messages)

            return response.content

        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise

    async def chat_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Chat with a system prompt

        Args:
            system_prompt: System prompt to set context
            user_message: User's message
            conversation_history: Optional previous messages
            temperature: Optional temperature override

        Returns:
            LLM response
        """
        messages = []

        # Add system prompt
        messages.append(Message(
            role=MessageRole.SYSTEM,
            content=system_prompt
        ))

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append(Message(
            role=MessageRole.USER,
            content=user_message
        ))

        return await self.chat(messages, temperature=temperature)

    async def extract_structured_data(
        self,
        prompt: str,
        user_input: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured data from user input based on a schema

        Args:
            prompt: Instruction prompt
            user_input: User's input text
            schema: JSON schema for expected output

        Returns:
            Extracted data as dictionary
        """
        import json

        system_prompt = f"""
        {prompt}

        Extract information according to this schema:
        {json.dumps(schema, indent=2)}

        Return ONLY valid JSON matching the schema, no other text.
        """

        response = await self.chat_with_system_prompt(
            system_prompt=system_prompt,
            user_message=user_input,
            temperature=0.1  # Low temperature for structured extraction
        )

        try:
            # Parse JSON response
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse structured response: {response}")
            raise ValueError("LLM did not return valid JSON")

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4

    def estimate_conversation_tokens(self, messages: List[Message]) -> int:
        """
        Estimate total tokens in conversation

        Args:
            messages: List of messages

        Returns:
            Estimated total token count
        """
        total = 0
        for msg in messages:
            total += self.count_tokens(msg.content)
            total += 4  # Message metadata overhead
        return total


# Global instance
langchain_service = LangChainService()


def get_langchain_service() -> LangChainService:
    """Get LangChain service instance"""
    return langchain_service
