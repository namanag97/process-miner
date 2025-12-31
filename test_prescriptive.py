
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock pm4py to avoid dependency issues
sys.modules["pm4py"] = MagicMock()
sys.modules["pm4py.objects"] = MagicMock()
sys.modules["pm4py.objects.log"] = MagicMock()
sys.modules["pm4py.objects.log.obj"] = MagicMock()

from src.services.recommendation import recommendation_service, SignalType
from src.models.orm import EventLog, ProcessCase
from unittest.mock import MagicMock

async def test_prescriptive_engine():
    print("\n--- Testing Prescriptive Engine (Pillar 1) ---\n")

    # MOCK DATA
    log_id = "mock-log-123"
    case_id = "CASE-999"

    # SCENARIO 1: High Delay -> Recommends Priority
    print(f"Scenario 1: Prediction says Case {case_id} will be late by 50 hours.")
    signal_data_delay = {
        "remaining_time_seconds": 180000, # 50 hours (Rule > 48h)
        "current_activity": "Approve Invoice"
    }

    # Generate Recommendations
    recs = await recommendation_service.generate_recommendations(
        session=MagicMock(), # Mock DB session
        log_id=log_id,
        case_id=case_id,
        signal_type=SignalType.PREDICTED_DELAY,
        signal_data=signal_data_delay,
        persist=False # Don't try to save to mock DB
    )

    if recs:
        print(f"✅ Success! Generated {len(recs)} recommendation(s):")
        for r in recs:
            print(f"   -> Action: {r.action_type}")
            print(f"   -> Priority: {r.priority}")
            print(f"   -> Params: {r.action_params_json}")
    else:
        print("❌ Failed: No recommendations generated.")

    print("\n" + "="*30 + "\n")

    # SCENARIO 2: Resource Overload -> Recommends Reassign
    print("Scenario 2: Resource 'Bob' is at 95% utilization.")
    signal_data_resource = {
        "resource": "Bob",
        "utilization": 0.95 # Rule > 0.9
    }

    recs_2 = await recommendation_service.generate_recommendations(
        session=MagicMock(),
        log_id=log_id,
        case_id=case_id,
        signal_type=SignalType.RESOURCE_OVERLOAD,
        signal_data=signal_data_resource,
        persist=False
    )

    if recs_2:
        print(f"✅ Success! Generated {len(recs_2)} recommendation(s):")
        for r in recs_2:
            print(f"   -> Action: {r.action_type}")
            print(f"   -> Priority: {r.priority}")
            print(f"   -> Params: {r.action_params_json}")
    else:
        print("❌ Failed: No recommendations generated.")

if __name__ == "__main__":
    asyncio.run(test_prescriptive_engine())
