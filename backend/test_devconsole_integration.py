"""Quick test script to verify DevConsole integration with structlog."""

import asyncio
import sys
import time

# Add src to path
sys.path.insert(0, '/Users/namanagarwal/system/backend')

from src.core.logging_config import configure_logging, get_logger, log_business_metric
from src.core.config import get_settings

# Configure logging first
configure_logging()

logger = get_logger("test")

async def test_logging():
    """Test that logs appear in DevConsole."""

    print("=" * 60)
    print("Testing DevConsole Integration")
    print("=" * 60)

    # Wait a moment for everything to initialize
    await asyncio.sleep(1)

    # Test 1: Basic log
    logger.info("test_message", test_key="test_value", count=123)
    print("✓ Sent basic log")

    # Test 2: Log with duration
    logger.info("operation_completed", duration=2.5, operation="test_operation")
    print("✓ Sent log with duration")

    # Test 3: Business metric
    log_business_metric("test_metric", 42.5, "units", tags={"env": "test"})
    print("✓ Sent business metric")

    # Test 4: Error log
    logger.error("test_error", error_code="TEST_ERROR", details={"reason": "testing"})
    print("✓ Sent error log")

    # Wait for logs to propagate
    await asyncio.sleep(2)

    print("\n" + "=" * 60)
    print("Test complete! Check DevConsole SSE stream:")
    print("  curl -N http://localhost:8001/api/v1/dev/logs/stream")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_logging())
