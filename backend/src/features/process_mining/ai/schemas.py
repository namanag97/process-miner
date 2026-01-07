"""AI Chat Schemas - Request/Response models for AI endpoints."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Chat message role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Single chat message."""

    role: MessageRole
    content: str
    timestamp: datetime | None = None


class AIChatRequest(BaseModel):
    """Request for AI chat completion."""

    dataset_id: str = Field(..., description="Dataset ID for process context")
    message: str = Field(
        ..., min_length=1, max_length=4000, description="User message"
    )
    conversation_history: list[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation for context",
        max_length=20,
    )
    analysis_type: str | None = Field(
        default=None,
        description="Focus area: bottleneck, rework, pattern, cycle_time, summary",
    )


class AIInsight(BaseModel):
    """Structured insight from AI analysis."""

    type: str = Field(
        description="bottleneck, pattern, anomaly, recommendation, metric"
    )
    title: str
    description: str
    severity: str | None = Field(default=None, description="high, medium, low, info")
    data: dict[str, Any] | None = None


class AIChatResponse(BaseModel):
    """Response from AI chat endpoint."""

    message: str = Field(..., description="AI response content")
    insights: list[AIInsight] = Field(default_factory=list)
    context_used: str | None = Field(default=None)
    model: str = Field(default="stub", description="LLM model used")
    tokens_used: int | None = Field(default=None)


class AICapabilitiesResponse(BaseModel):
    """Response describing AI capabilities."""

    capabilities: list[str]
    supported_analysis_types: list[str]
    max_message_length: int
    max_history_length: int
    model_info: dict[str, Any]
