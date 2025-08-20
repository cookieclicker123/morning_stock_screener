"""OpenAI API wrapper implementation."""

import time
from typing import List, Optional

from openai import AsyncOpenAI

from ..models.llm import LLMRequest, LLMResponse
from .base import BaseLLMWrapper


class OpenAIWrapper(BaseLLMWrapper):
    """OpenAI API wrapper implementation."""

    def __init__(self, api_key: str, model: str = "gpt-5"):
        """Initialize OpenAI wrapper.

        Args:
            api_key: OpenAI API key
            model: Default model to use
        """
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate a response using OpenAI API.

        Args:
            request: LLM request containing prompt and parameters

        Returns:
            LLM response with generated content
        """
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                model_used=request.model,
                tokens_used=0,
                finish_reason="validation_failed",
                response_time_ms=0.0,
                success=False,
                error_message="Invalid request parameters",
            )

        start_time = time.time()

        try:
            # Combine system and user prompts
            messages = [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ]

            # GPT-5 has different API parameters
            if request.model.startswith("gpt-5"):
                api_params = {
                    "model": request.model,
                    "messages": messages,
                    # GPT-5 expects max_completion_tokens
                    "max_completion_tokens": request.max_tokens,
                    # Force plain text to avoid non-text content parts
                    "response_format": {"type": "text"},
                    **request.additional_params,
                }
                # GPT-5 only supports default temperature (1)
                if request.temperature != 1.0:
                    print("⚠️  Warning: GPT-5 only supports default temperature (1). Ignoring custom temperature.")
            else:
                api_params = {
                    "model": request.model,
                    "messages": messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    **request.additional_params,
                }
            
            response = await self.client.chat.completions.create(**api_params)

            response_time = (time.time() - start_time) * 1000

            # Some models may return empty content if the response was structured; ensure we coerce to text
            content_text = getattr(response.choices[0].message, "content", "") or ""
            return LLMResponse(
                content=content_text,
                model_used=response.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                response_time_ms=response_time,
                success=True,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return LLMResponse(
                content="",
                model_used=request.model,
                tokens_used=0,
                finish_reason="error",
                response_time_ms=response_time,
                success=False,
                error_message=str(e),
            )

    async def generate_chat_response(
        self,
        messages: List[dict],
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
        model_to_use = model or self.default_model
        start_time = time.time()

        try:
            # GPT-5 has different API parameters
            if model_to_use.startswith("gpt-5"):
                api_params = {
                    "model": model_to_use,
                    "messages": messages,
                    # GPT-5 expects max_completion_tokens
                    "max_completion_tokens": max_tokens,
                    # Force plain text to avoid non-text content parts
                    "response_format": {"type": "text"},
                }
                # GPT-5 only supports default temperature (1)
                if temperature != 1.0:
                    print("⚠️  Warning: GPT-5 only supports default temperature (1). Ignoring custom temperature.")
            else:
                api_params = {
                    "model": model_to_use,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            
            response = await self.client.chat.completions.create(**api_params)

            response_time = (time.time() - start_time) * 1000

            content_text = getattr(response.choices[0].message, "content", "") or ""
            return LLMResponse(
                content=content_text,
                model_used=response.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                response_time_ms=response_time,
                success=True,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return LLMResponse(
                content="",
                model_used=model_to_use,
                tokens_used=0,
                finish_reason="error",
                response_time_ms=response_time,
                success=False,
                error_message=str(e),
            )
