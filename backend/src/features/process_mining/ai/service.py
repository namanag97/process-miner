"""AI Chat Service - Business logic for AI-powered process analysis.

Provides conversational AI capabilities for process mining insights.
Supports stub mode (default) and OpenRouter integration for real LLM responses.
"""

import os
from typing import Any

from src.infra.core.logging_config import get_logger

from .schemas import AIChatRequest, AIChatResponse, AIInsight

logger = get_logger(__name__)


def _format_duration(seconds: float) -> str:
    """Format seconds into human readable duration."""
    if seconds < 60:
        return f"{round(seconds)}s"
    if seconds < 3600:
        return f"{round(seconds / 60)}m"
    if seconds < 86400:
        return f"{seconds / 3600:.1f}h"
    return f"{seconds / 86400:.1f}d"


class AIChatService:
    """AI Chat Service supporting stub mode (default) and OpenRouter mode.

    Environment Variables:
        OPENROUTER_API_KEY: API key for OpenRouter (empty = stub mode)
        AI_CHAT_LIVE_MODE: Set to "true" to enable real LLM calls
    """

    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "anthropic/claude-3-haiku"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.use_real_llm = bool(self.api_key) and os.getenv(
            "AI_CHAT_LIVE_MODE", "false"
        ).lower() == "true"
        logger.info(
            "ai_chat_service_initialized",
            live_mode=self.use_real_llm,
            has_api_key=bool(self.api_key),
        )

    async def chat(
        self,
        request: AIChatRequest,
        context: dict[str, Any] | None = None,
    ) -> AIChatResponse:
        """Process chat request and generate response.

        Args:
            request: The chat request with message and dataset context
            context: Optional pre-fetched analytics context (bottlenecks, cycle time, etc.)

        Returns:
            AIChatResponse with message and optional insights
        """
        logger.info(
            "ai_chat_processing",
            dataset_id=request.dataset_id,
            message_length=len(request.message),
            has_context=context is not None,
        )

        # For now, always use stub responses
        # When OPENROUTER_API_KEY is set and AI_CHAT_LIVE_MODE=true,
        # this can be extended to call the real LLM
        if self.use_real_llm and self.api_key:
            return await self._call_openrouter(request, context or {})

        return self._generate_stub_response(request, context or {})

    async def _call_openrouter(
        self,
        request: AIChatRequest,
        context: dict[str, Any],
    ) -> AIChatResponse:
        """Call OpenRouter API for real LLM response.

        This is a placeholder for future implementation.
        When ready, implement using httpx or aiohttp to call OpenRouter.
        """
        # For now, fall back to stub response
        logger.info("openrouter_call_placeholder", msg="Real LLM not yet implemented")
        return self._generate_stub_response(request, context)

    def _generate_stub_response(
        self,
        request: AIChatRequest,
        context: dict[str, Any],
    ) -> AIChatResponse:
        """Generate intelligent stub response based on keywords and context.

        The stub response logic matches the frontend's generateMockResponse pattern,
        providing contextual responses based on the question topic.
        """
        message = request.message.lower()
        insights: list[AIInsight] = []

        # Extract context data with safe defaults
        bottlenecks = context.get("bottlenecks", [])
        cycle_time = context.get("cycle_time", {})
        throughput = context.get("throughput", {})
        rework = context.get("rework", {})

        total_cases = throughput.get("total_cases", 0)
        avg_cycle = cycle_time.get("avg_seconds", 0)
        median_cycle = cycle_time.get("median_seconds", 0)
        # Note: rework_rate = rework.get("rate", 0) available if needed

        # Keyword-based response generation
        if any(word in message for word in ["bottleneck", "slow", "delay", "wait"]):
            response_text = self._bottleneck_response(bottlenecks)
            if bottlenecks:
                for b in bottlenecks[:3]:
                    insights.append(
                        AIInsight(
                            type="bottleneck",
                            title=b.get("activity", "Unknown"),
                            description=f"Avg wait: {_format_duration(b.get('avg_wait_seconds', 0))}",
                            severity="high" if b.get("avg_wait_seconds", 0) > 86400 else "medium",
                        )
                    )

        elif any(word in message for word in ["rework", "repeat", "loop", "redo"]):
            response_text = self._rework_response(rework, total_cases)
            if rework.get("activities"):
                for r in rework["activities"][:3]:
                    insights.append(
                        AIInsight(
                            type="pattern",
                            title=r.get("activity", "Unknown"),
                            description=f"{r.get('rework_count', 0)} occurrences",
                            severity="high" if r.get("rework_percentage", 0) > 30 else "medium",
                        )
                    )

        elif any(word in message for word in ["cycle", "time", "duration", "long"]):
            response_text = self._cycle_time_response(cycle_time, total_cases)
            insights.append(
                AIInsight(
                    type="metric",
                    title="Cycle Time",
                    description=f"Average: {_format_duration(avg_cycle)}, Median: {_format_duration(median_cycle)}",
                    severity="info",
                )
            )

        elif any(word in message for word in ["pattern", "variant", "common", "frequent"]):
            response_text = self._pattern_response(context)

        elif any(word in message for word in ["summary", "overview", "status", "health"]):
            response_text = self._summary_response(
                bottlenecks, cycle_time, throughput, rework
            )
            insights.append(
                AIInsight(
                    type="metric",
                    title="Process Health",
                    description=f"{total_cases} cases, {_format_duration(avg_cycle)} avg cycle",
                    severity="info",
                )
            )

        elif any(word in message for word in ["help", "what can", "capabilities"]):
            response_text = self._help_response()

        else:
            response_text = self._default_response(
                bottlenecks, cycle_time, throughput, rework
            )

        logger.info(
            "ai_chat_stub_response",
            response_length=len(response_text),
            insights_count=len(insights),
        )

        return AIChatResponse(
            message=response_text,
            insights=insights,
            model="stub-v1",
            context_used="analytics" if context else None,
        )

    def _bottleneck_response(self, bottlenecks: list[dict]) -> str:
        """Generate bottleneck-focused response."""
        if not bottlenecks:
            return (
                "Good news! I don't see any significant bottlenecks in this process. "
                "The activities are flowing smoothly with acceptable waiting times.\n\n"
                "Would you like me to analyze another aspect of the process?"
            )

        top = bottlenecks[0]
        activity = top.get("activity", "Unknown activity")
        wait_time = _format_duration(top.get("avg_wait_seconds", 0))

        return (
            f"The main bottleneck in this process is **{activity}** "
            f"with an average waiting time of {wait_time}.\n\n"
            f"**Recommendations:**\n"
            f"1. Consider adding parallel processing capacity for {activity}\n"
            f"2. Review resource allocation during peak times\n"
            f"3. Implement automation for routine {activity} tasks\n\n"
            f"Would you like me to analyze what's causing this bottleneck?"
        )

    def _rework_response(self, rework: dict, total_cases: int) -> str:
        """Generate rework-focused response."""
        rate = rework.get("rate", 0)
        total_rework_cases = rework.get("total_cases", 0)
        activities = rework.get("activities", [])

        if rate < 5:
            return (
                f"The rework rate in this process is very low at {rate:.1f}%. "
                "This indicates good process quality and first-time-right performance.\n\n"
                "Keep monitoring to maintain this excellent performance!"
            )

        top_activity = activities[0].get("activity", "N/A") if activities else "N/A"
        top_count = activities[0].get("rework_count", 0) if activities else 0

        return (
            f"The rework rate in this process is **{rate:.1f}%**, "
            f"affecting {total_rework_cases:,} cases.\n\n"
            f"The most repeated activity is **{top_activity}** with {top_count} occurrences.\n\n"
            f"**Suggestions:**\n"
            f"1. Investigate root causes for {top_activity} rework\n"
            f"2. Implement validation checks earlier in the process\n"
            f"3. Consider process redesign to reduce loops"
        )

    def _cycle_time_response(self, cycle_time: dict, total_cases: int) -> str:
        """Generate cycle time analysis response."""
        avg = cycle_time.get("avg_seconds", 0)
        median = cycle_time.get("median_seconds", 0)
        min_val = cycle_time.get("min_seconds", 0)
        max_val = cycle_time.get("max_seconds", 0)

        analysis = (
            "some cases are taking significantly longer than typical, skewing the average upward"
            if avg > median * 1.5
            else "relatively consistent processing times across cases"
        )

        return (
            f"**Cycle Time Analysis:**\n\n"
            f"- **Average:** {_format_duration(avg)}\n"
            f"- **Median:** {_format_duration(median)}\n"
            f"- **Range:** {_format_duration(min_val)} to {_format_duration(max_val)}\n\n"
            f"The difference between average and median suggests {analysis}.\n\n"
            f"Would you like me to identify which cases are outliers?"
        )

    def _pattern_response(self, context: dict) -> str:
        """Generate pattern analysis response."""
        patterns = context.get("patterns", [])

        if not patterns:
            return (
                "I couldn't identify distinct patterns with sufficient frequency in this process. "
                "The process may have high variability which could indicate either flexibility "
                "or lack of standardization.\n\n"
                "Would you like me to analyze the process variants instead?"
            )

        pattern_text = "\n".join(
            f"{i+1}. {p.get('pattern', 'N/A')} ({p.get('support', 0)*100:.1f}% of cases)"
            for i, p in enumerate(patterns[:3])
        )

        return (
            f"Here are the most common patterns in this process:\n\n"
            f"{pattern_text}\n\n"
            f"The dominant pattern represents the 'happy path' - optimizing this flow "
            f"will have the highest impact on overall process performance."
        )

    def _summary_response(
        self,
        bottlenecks: list[dict],
        cycle_time: dict,
        throughput: dict,
        rework: dict,
    ) -> str:
        """Generate comprehensive process summary."""
        total_cases = throughput.get("total_cases", 0)
        avg_cycle = _format_duration(cycle_time.get("avg_seconds", 0))
        cases_per_day = throughput.get("cases_per_day", 0)
        bottleneck_count = len([b for b in bottlenecks if b.get("is_bottleneck")])
        rework_rate = rework.get("rate", 0)

        health = (
            "showing signs of inefficiency that could benefit from optimization"
            if bottleneck_count > 2 or rework_rate > 25
            else "performing reasonably well with room for incremental improvements"
        )

        return (
            f"**Process Summary**\n\n"
            f"- **Volume:** {total_cases:,} cases processed\n"
            f"- **Cycle Time:** Average {avg_cycle}\n"
            f"- **Throughput:** {cases_per_day:.1f} cases/day\n"
            f"- **Bottlenecks:** {bottleneck_count} identified\n"
            f"- **Rework Rate:** {rework_rate:.1f}%\n\n"
            f"Overall, the process is {health}.\n\n"
            f"What would you like to explore in more detail?"
        )

    def _help_response(self) -> str:
        """Generate help/capabilities response."""
        return (
            "I can help you analyze your process mining data. Here's what I can do:\n\n"
            "**Analysis Types:**\n"
            "- **Bottleneck Analysis** - Identify slow activities and delays\n"
            "- **Rework Detection** - Find repeated activities and loops\n"
            "- **Cycle Time Analysis** - Understand case duration patterns\n"
            "- **Pattern Discovery** - Find common process paths\n"
            "- **Process Summary** - Get an overall health check\n\n"
            "**Try asking:**\n"
            "- 'What are the main bottlenecks?'\n"
            "- 'Show me rework patterns'\n"
            "- 'How long do cases take?'\n"
            "- 'Give me a process summary'"
        )

    def _default_response(
        self,
        bottlenecks: list[dict],
        cycle_time: dict,
        throughput: dict,
        rework: dict,
    ) -> str:
        """Generate default helpful response."""
        total_cases = throughput.get("total_cases", 0)
        avg_cycle = _format_duration(cycle_time.get("avg_seconds", 0))
        bottleneck_count = len([b for b in bottlenecks if b.get("is_bottleneck")])
        rework_rate = rework.get("rate", 0)

        return (
            f"Based on the data, here's what I can tell you:\n\n"
            f"- The process handles **{total_cases:,} cases** with an average cycle time of **{avg_cycle}**\n"
            f"- There are **{bottleneck_count} bottlenecks** and a **{rework_rate:.1f}% rework rate**\n\n"
            f"Would you like me to dive deeper into any specific area like "
            f"bottlenecks, patterns, or performance trends?"
        )


# Singleton instance
ai_chat_service = AIChatService()
