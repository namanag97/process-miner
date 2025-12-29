"""
Synthetic Data Generators for Process Mining Demo
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()


def generate_event_log(n_cases: int = 500) -> pd.DataFrame:
    """
    Generate a synthetic event log for Order-to-Cash process.
    
    Activities: Order Received -> Credit Check -> Stock Check -> 
                Pick & Pack -> Ship -> Invoice -> Payment
    """
    activities = [
        "Order Received",
        "Credit Check", 
        "Stock Check",
        "Pick & Pack",
        "Ship",
        "Invoice Created",
        "Payment Received"
    ]
    
    # Possible deviations
    deviation_activities = ["Manual Review", "Credit Rejected", "Backorder"]
    
    events = []
    
    for case_id in range(1, n_cases + 1):
        case_key = f"ORDER-{case_id:05d}"
        timestamp = fake.date_time_between(start_date="-90d", end_date="-1d")
        
        # Case attributes
        customer = fake.company()
        order_value = round(random.uniform(100, 10000), 2)
        region = random.choice(["North", "South", "East", "West"])
        priority = random.choice(["Low", "Medium", "High"])
        
        # Determine if case has deviations
        has_deviation = random.random() < 0.2
        deviation_type = random.choice(deviation_activities) if has_deviation else None
        
        # Process flow
        for i, activity in enumerate(activities):
            # Activity duration (random but realistic)
            if activity == "Credit Check":
                duration = timedelta(hours=random.uniform(0.5, 24))
            elif activity == "Pick & Pack":
                duration = timedelta(hours=random.uniform(1, 48))
            elif activity == "Ship":
                duration = timedelta(days=random.uniform(1, 5))
            elif activity == "Payment Received":
                duration = timedelta(days=random.uniform(1, 30))
            else:
                duration = timedelta(hours=random.uniform(0.1, 4))
            
            resource = fake.first_name()
            
            events.append({
                "case_id": case_key,
                "activity": activity,
                "timestamp": timestamp,
                "resource": resource,
                "customer": customer,
                "order_value": order_value,
                "region": region,
                "priority": priority,
                "lifecycle": "complete"
            })
            
            timestamp += duration
            
            # Insert deviation after Credit Check
            if activity == "Credit Check" and deviation_type == "Manual Review":
                events.append({
                    "case_id": case_key,
                    "activity": "Manual Review",
                    "timestamp": timestamp,
                    "resource": "Supervisor",
                    "customer": customer,
                    "order_value": order_value,
                    "region": region,
                    "priority": priority,
                    "lifecycle": "complete"
                })
                timestamp += timedelta(hours=random.uniform(2, 8))
            
            # Credit rejection - case ends early
            if activity == "Credit Check" and deviation_type == "Credit Rejected":
                events.append({
                    "case_id": case_key,
                    "activity": "Credit Rejected",
                    "timestamp": timestamp,
                    "resource": "System",
                    "customer": customer,
                    "order_value": order_value,
                    "region": region,
                    "priority": priority,
                    "lifecycle": "complete"
                })
                break
            
            # Backorder after stock check
            if activity == "Stock Check" and deviation_type == "Backorder":
                events.append({
                    "case_id": case_key,
                    "activity": "Backorder",
                    "timestamp": timestamp,
                    "resource": "System",
                    "customer": customer,
                    "order_value": order_value,
                    "region": region,
                    "priority": priority,
                    "lifecycle": "complete"
                })
                timestamp += timedelta(days=random.uniform(5, 14))
    
    df = pd.DataFrame(events)
    df = df.sort_values(["case_id", "timestamp"]).reset_index(drop=True)
    
    return df


def generate_invoice_text() -> str:
    """Generate sample invoice text for NLP demo."""
    return f"""
    INVOICE
    
    Invoice Number: INV-{random.randint(10000, 99999)}
    Date: {fake.date_this_year().strftime('%B %d, %Y')}
    Due Date: {fake.date_between(start_date='today', end_date='+30d').strftime('%B %d, %Y')}
    
    Bill To:
    {fake.company()}
    {fake.address()}
    
    Ship To:
    {fake.name()}
    {fake.address()}
    
    Description                     Qty    Unit Price    Amount
    ----------------------------------------------------------------
    Professional Services           10     $150.00       $1,500.00
    Software License               1      $2,500.00     $2,500.00
    Support & Maintenance          1      $500.00       $500.00
    
    ----------------------------------------------------------------
    Subtotal:                                           $4,500.00
    Tax (8%):                                           $360.00
    ----------------------------------------------------------------
    TOTAL:                                              $4,860.00
    
    Payment Terms: Net 30
    Please remit payment to: {fake.company()} Bank Account: {fake.bban()}
    
    Thank you for your business!
    """


def generate_staffing_demand() -> dict:
    """Generate sample demand data for optimization demo."""
    return {
        "shifts": ["Morning", "Afternoon", "Evening", "Night"],
        "demand": {
            "Morning": random.randint(5, 15),
            "Afternoon": random.randint(8, 20),
            "Evening": random.randint(4, 12),
            "Night": random.randint(2, 6)
        },
        "cost_per_hour": {
            "Morning": 25,
            "Afternoon": 25,
            "Evening": 30,
            "Night": 35
        },
        "hours_per_shift": 8
    }
