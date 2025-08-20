"""LLM request and response data models."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """Request structure for LLM API calls."""

    system_prompt: str = Field(..., description="System prompt/instructions")
    user_prompt: str = Field(..., description="User query/prompt")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=4000, gt=0, description="Maximum tokens in response"
    )
    model: str = Field(default="gpt-5", description="LLM model to use")
    additional_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional model parameters"
    )


class LLMResponse(BaseModel):
    """Response structure from LLM API calls."""

    content: str = Field(..., description="Generated response content")
    model_used: str = Field(..., description="Model that generated the response")
    tokens_used: int = Field(..., description="Total tokens used in request/response")
    finish_reason: str = Field(
        ..., description="Reason for completion (stop, length, etc.)"
    )
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    success: bool = Field(..., description="Whether the request was successful")
    error_message: Optional[str] = Field(
        default=None, description="Error message if request failed"
    )

    model_config = {"json_encoders": {float: lambda v: round(v, 2) if v else v}}
