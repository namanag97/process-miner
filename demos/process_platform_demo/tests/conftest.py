"""
Pytest Configuration and Fixtures for Process Platform Demo Tests
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_event_log():
    """Generate a small sample event log for testing."""
    np.random.seed(42)
    events = []
    
    activities = [
        "Create Sales Order",
        "Credit Check",
        "Approve Credit",
        "Release Order",
        "Pick Materials",
        "Pack Goods",
        "Ship Goods",
        "Create Invoice",
        "Receive Payment",
        "Close Order"
    ]
    
    for case_id in range(1, 21):  # 20 cases
        timestamp = datetime.now() - timedelta(days=np.random.randint(1, 30))
        
        # Each case goes through some activities
        num_activities = np.random.randint(5, len(activities) + 1)
        case_activities = activities[:num_activities]
        
        for activity in case_activities:
            events.append({
                "case_id": f"CASE-{case_id:04d}",
                "activity": activity,
                "timestamp": timestamp,
                "resource": f"Resource_{np.random.randint(1, 5)}",
                "customer": f"Customer_{np.random.randint(1, 10)}",
                "priority": np.random.choice(["Low", "Medium", "High"]),
                "region": np.random.choice(["North", "South", "East", "West"]),
                "value": round(np.random.uniform(100, 5000), 2)
            })
            timestamp += timedelta(hours=np.random.uniform(0.5, 24))
    
    return pd.DataFrame(events).sort_values(["case_id", "timestamp"]).reset_index(drop=True)


@pytest.fixture
def minimal_event_log():
    """Minimal event log for quick tests."""
    return pd.DataFrame([
        {"case_id": "C1", "activity": "Start", "timestamp": datetime(2024, 1, 1, 10, 0)},
        {"case_id": "C1", "activity": "Process", "timestamp": datetime(2024, 1, 1, 11, 0)},
        {"case_id": "C1", "activity": "End", "timestamp": datetime(2024, 1, 1, 12, 0)},
        {"case_id": "C2", "activity": "Start", "timestamp": datetime(2024, 1, 1, 10, 0)},
        {"case_id": "C2", "activity": "End", "timestamp": datetime(2024, 1, 1, 11, 0)},
    ])


@pytest.fixture
def sample_invoice_text():
    """Sample invoice text for document processing tests."""
    return """INVOICE
Invoice Number: INV-2024-00123
Date: January 15, 2024
Due Date: February 14, 2024

Bill To:
Acme Corporation
123 Business Street
New York, NY 10001

Description                     Qty    Unit Price    Amount
Professional Services           5      $200.00       $1,000.00
Software License               2      $500.00       $1,000.00

Subtotal: $2,000.00
Tax (10%): $200.00
TOTAL: $2,200.00

Payment Terms: Net 30
"""
