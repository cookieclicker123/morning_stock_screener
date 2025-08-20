"""Base abstract class for LLM wrappers."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models.llm import LLMRequest, LLMResponse


class BaseLLMWrapper(ABC):
    """Abstract base class for LLM wrapper implementations."""

    def __init__(self, api_key: str, model: str = "gpt-5"):
        """Initialize the LLM wrapper.

        Args:
            api_key: API key for the LLM service
            model: Default model to use
        """
        self.api_key = api_key
        self.default_model = model

    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            request: LLM request containing prompt and parameters

        Returns:
            LLM response with generated content
        """
        pass

    @abstractmethod
    async def generate_chat_response(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        model: Optional[str] = None,
    ) -> LLMResponse:
        """Generate a response from a chat conversation.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            model: Model to use (defaults to self.default_model)

        Returns:
            LLM response with generated content
        """
        pass

    def validate_request(self, request: LLMRequest) -> bool:
        """Validate the LLM request.

        Args:
            request: LLM request to validate

        Returns:
            True if valid, False otherwise
        """
        if not request.system_prompt or not request.user_prompt:
            return False
        if request.temperature < 0 or request.temperature > 2:
            return False
        if request.max_tokens <= 0:
            return False
        return True
