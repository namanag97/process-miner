"""AI Chat Router - API endpoints for AI-powered process analysis.

Provides conversational AI capabilities for process mining insights.
Uses CQRS QueryBus to fetch analytics context for intelligent responses.
"""

from fastapi import APIRouter

from src.api.dependencies import CurrentUser, QueryBusDep
from src.application.queries.analytics_queries import (
    GetBottlenecksQuery,
    GetCycleTimeQuery,
    GetReworkQuery,
    GetThroughputQuery,
)
from src.infra.core.logging_config import get_logger

from .schemas import AICapabilitiesResponse, AIChatRequest, AIChatResponse
from .service import ai_chat_service

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    request: AIChatRequest,
    user: CurrentUser,
    query_bus: QueryBusDep,
) -> AIChatResponse:
    """Send a message to the AI assistant for process analysis.

    The AI assistant uses process analytics data (bottlenecks, cycle times,
    rework patterns) to provide contextual, data-driven responses.

    Args:
        request: Chat request with message and dataset_id
        user: Current authenticated user
        query_bus: CQRS query bus for fetching analytics

    Returns:
        AIChatResponse with AI-generated message and optional insights
    """
    logger.info(
        "ai_chat_request",
        user_id=user.id,
        dataset_id=request.dataset_id,
        message_preview=request.message[:50] if request.message else "",
    )

    # Build context from analytics data
    context = await _build_process_context(request.dataset_id, query_bus)

    # Generate response using AI service
    response = await ai_chat_service.chat(request, context=context)

    logger.info(
        "ai_chat_response",
        user_id=user.id,
        model=response.model,
        insights_count=len(response.insights),
    )

    return response


@router.get("/capabilities", response_model=AICapabilitiesResponse)
async def get_capabilities(
    user: CurrentUser,
) -> AICapabilitiesResponse:
    """Get AI assistant capabilities and configuration.

    Returns information about what the AI can do and its current limits.
    """
    logger.info("ai_capabilities_request", user_id=user.id)

    return AICapabilitiesResponse(
        capabilities=[
            "Process bottleneck analysis",
            "Rework pattern detection",
            "Cycle time analysis",
            "Pattern discovery",
            "Process health summaries",
            "Contextual recommendations",
        ],
        supported_analysis_types=[
            "bottleneck",
            "rework",
            "cycle_time",
            "pattern",
            "summary",
        ],
        max_message_length=4000,
        max_history_length=20,
        model_info={
            "default_model": "stub-v1",
            "live_mode": ai_chat_service.use_real_llm,
            "provider": "openrouter" if ai_chat_service.use_real_llm else "stub",
        },
    )


async def _build_process_context(
    dataset_id: str,
    query_bus: QueryBusDep,
) -> dict:
    """Fetch analytics data to provide context for AI responses.

    Dispatches multiple CQRS queries to gather bottlenecks, cycle times,
    throughput, and rework data that the AI can reference in responses.
    """
    context: dict = {"dataset_id": dataset_id}

    try:
        # Fetch bottlenecks
        bottleneck_result = await query_bus.dispatch(
            GetBottlenecksQuery(dataset_id=dataset_id, limit=5)
        )
        context["bottlenecks"] = [
            {
                "activity": b.activity,
                "avg_wait_seconds": b.avg_wait_time_seconds,
                "is_bottleneck": b.avg_wait_time_seconds > 3600,
            }
            for b in bottleneck_result.bottlenecks
        ]

        # Fetch cycle time
        cycle_result = await query_bus.dispatch(
            GetCycleTimeQuery(dataset_id=dataset_id)
        )
        context["cycle_time"] = {
            "avg_seconds": cycle_result.mean_seconds,
            "median_seconds": cycle_result.median_seconds,
            "min_seconds": cycle_result.min_seconds,
            "max_seconds": cycle_result.max_seconds,
        }

        # Fetch throughput
        throughput_result = await query_bus.dispatch(
            GetThroughputQuery(dataset_id=dataset_id)
        )
        context["throughput"] = {
            "total_cases": throughput_result.total_cases,
            "cases_per_day": throughput_result.cases_per_day,
        }

        # Fetch rework
        rework_result = await query_bus.dispatch(
            GetReworkQuery(dataset_id=dataset_id)
        )
        context["rework"] = {
            "rate": rework_result.rework_rate * 100,
            "total_cases": rework_result.total_cases_with_rework,
            "activities": [
                {
                    "activity": r.activity,
                    "rework_count": r.repeat_count,
                    "rework_percentage": r.percentage,
                }
                for r in rework_result.rework_patterns[:5]
            ],
        }

        logger.debug(
            "ai_context_built",
            dataset_id=dataset_id,
            bottleneck_count=len(context.get("bottlenecks", [])),
            total_cases=context.get("throughput", {}).get("total_cases", 0),
        )

    except Exception as e:
        # Log error but continue with partial context
        logger.warning(
            "ai_context_build_error",
            dataset_id=dataset_id,
            error=str(e),
        )

    return context
