"""AI Module - AI-powered process analysis.

Provides conversational AI capabilities for process mining insights,
including bottleneck analysis, rework detection, and process health summaries.
"""

from .router import router
from .schemas import AICapabilitiesResponse, AIChatRequest, AIChatResponse, AIInsight
from .service import AIChatService, ai_chat_service

__all__ = [
    "AICapabilitiesResponse",
    "AIChatRequest",
    "AIChatResponse",
    "AIChatService",
    "AIInsight",
    "ai_chat_service",
    "router",
]
