"""
Dataset Loader for Process Mining Demo
Provides multiple event log datasets including BPI Challenge and synthetic ones
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import random
from io import StringIO
import urllib.request
import gzip
import os


@dataclass
class DatasetInfo:
    """Metadata about a dataset."""
    name: str
    description: str
    source: str
    num_cases: int
    num_events: int
    num_activities: int
    domain: str
    case_col: str = "case_id"
    activity_col: str = "activity"
    timestamp_col: str = "timestamp"


class DatasetLoader:
    """
    Load various event log datasets for process mining.
    
    Includes:
    - Synthetic datasets (O2C, P2P, ITSM)
    - BPI Challenge-style realistic data
    - Healthcare process logs
    """
    
    AVAILABLE_DATASETS = {
        "order_to_cash": "Order-to-Cash (Synthetic) - Sales order fulfillment process",
        "procure_to_pay": "Procure-to-Pay (Synthetic) - Procurement and payment process",
        "incident_management": "IT Incident Management (Synthetic) - ITSM ticketing process",
        "patient_treatment": "Hospital Patient Treatment (Synthetic) - Healthcare journey",
        "loan_application": "Loan Application (Synthetic) - Financial services",
        "bpi_2012_sample": "BPI Challenge 2012 Sample - Dutch financial institute loan process",
    }
    
    @classmethod
    def list_datasets(cls) -> Dict[str, str]:
        """List all available datasets."""
        return cls.AVAILABLE_DATASETS
    
    @classmethod
    def get_dataset_info(cls, dataset_name: str) -> Optional[DatasetInfo]:
        """Get metadata about a dataset."""
        if dataset_name not in cls.AVAILABLE_DATASETS:
            return None
        
        # Load sample to get stats
        df = cls.load_dataset(dataset_name, n_cases=100)
        
        return DatasetInfo(
            name=dataset_name,
            description=cls.AVAILABLE_DATASETS[dataset_name],
            source="Synthetic" if "sample" not in dataset_name else "BPI Challenge",
            num_cases=df['case_id'].nunique(),
            num_events=len(df),
            num_activities=df['activity'].nunique(),
            domain=dataset_name.split("_")[0].title()
        )
    
    @classmethod
    def load_dataset(cls, dataset_name: str, n_cases: int = 500, seed: int = 42) -> pd.DataFrame:
        """Load a specific dataset."""
        random.seed(seed)
        np.random.seed(seed)
        
        loaders = {
            "order_to_cash": cls._generate_o2c,
            "procure_to_pay": cls._generate_p2p,
            "incident_management": cls._generate_itsm,
            "patient_treatment": cls._generate_healthcare,
            "loan_application": cls._generate_loan,
            "bpi_2012_sample": cls._generate_bpi_2012_sample,
        }
        
        if dataset_name not in loaders:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(loaders.keys())}")
        
        return loaders[dataset_name](n_cases)
    
    @classmethod
    def _generate_o2c(cls, n_cases: int) -> pd.DataFrame:
        """Generate Order-to-Cash event log."""
        activities = [
            ("Create Sales Order", 0.5),
            ("Credit Check", 2.0),
            ("Approve Credit", 1.0),
            ("Release Order", 0.5),
            ("Pick Materials", 4.0),
            ("Pack Goods", 2.0),
            ("Ship Goods", 24.0),
            ("Create Invoice", 1.0),
            ("Send Invoice", 0.5),
            ("Receive Payment", 168.0),
            ("Close Order", 0.5)
        ]
        
        deviations = {
            "Credit Rejected": ("Credit Check", 0.08),
            "Manual Credit Review": ("Approve Credit", 0.15),
            "Backorder": ("Pick Materials", 0.10),
            "Partial Shipment": ("Ship Goods", 0.05),
            "Payment Reminder": ("Receive Payment", 0.20),
        }
        
        return cls._generate_process_log(n_cases, activities, deviations, "ORDER")
    
    @classmethod
    def _generate_p2p(cls, n_cases: int) -> pd.DataFrame:
        """Generate Procure-to-Pay event log."""
        activities = [
            ("Create Purchase Requisition", 1.0),
            ("Approve Requisition", 4.0),
            ("Create Purchase Order", 2.0),
            ("Send PO to Vendor", 0.5),
            ("Receive Goods", 72.0),
            ("Quality Inspection", 8.0),
            ("Three-Way Match", 2.0),
            ("Invoice Verification", 4.0),
            ("Schedule Payment", 24.0),
            ("Execute Payment", 48.0),
            ("Close PO", 0.5)
        ]
        
        deviations = {
            "Requisition Rejected": ("Approve Requisition", 0.10),
            "Price Discrepancy": ("Three-Way Match", 0.12),
            "Quality Issue": ("Quality Inspection", 0.08),
            "Invoice Error": ("Invoice Verification", 0.15),
            "Payment Hold": ("Schedule Payment", 0.07),
        }
        
        return cls._generate_process_log(n_cases, activities, deviations, "PO")
    
    @classmethod
    def _generate_itsm(cls, n_cases: int) -> pd.DataFrame:
        """Generate IT Incident Management event log."""
        activities = [
            ("Incident Reported", 0.1),
            ("Initial Categorization", 0.5),
            ("Priority Assignment", 0.3),
            ("Assign to Team", 0.5),
            ("Initial Diagnosis", 2.0),
            ("Investigation", 4.0),
            ("Resolution Identified", 2.0),
            ("Apply Fix", 1.0),
            ("User Verification", 4.0),
            ("Close Incident", 0.5)
        ]
        
        deviations = {
            "Escalation L2": ("Initial Diagnosis", 0.25),
            "Escalation L3": ("Investigation", 0.10),
            "Reassignment": ("Assign to Team", 0.20),
            "Reopen": ("User Verification", 0.15),
            "Knowledge Article Created": ("Resolution Identified", 0.08),
        }
        
        return cls._generate_process_log(n_cases, activities, deviations, "INC")
    
    @classmethod
    def _generate_healthcare(cls, n_cases: int) -> pd.DataFrame:
        """Generate Hospital Patient Treatment event log."""
        activities = [
            ("Patient Registration", 0.5),
            ("Triage Assessment", 0.5),
            ("Vital Signs Check", 0.3),
            ("Doctor Consultation", 1.0),
            ("Diagnostic Tests Ordered", 0.5),
            ("Lab Tests", 2.0),
            ("Imaging", 1.5),
            ("Results Review", 1.0),
            ("Treatment Plan", 0.5),
            ("Treatment Administered", 2.0),
            ("Follow-up Scheduled", 0.3),
            ("Discharge", 0.5)
        ]
        
        deviations = {
            "Emergency Transfer": ("Triage Assessment", 0.05),
            "Specialist Referral": ("Doctor Consultation", 0.20),
            "Additional Tests": ("Results Review", 0.25),
            "Admission Required": ("Treatment Plan", 0.15),
            "Readmission": ("Discharge", 0.08),
        }
        
        return cls._generate_process_log(n_cases, activities, deviations, "PAT")
    
    @classmethod
    def _generate_loan(cls, n_cases: int) -> pd.DataFrame:
        """Generate Loan Application event log (BPI 2012 style)."""
        activities = [
            ("A_SUBMITTED", 0.1),
            ("A_PARTLYSUBMITTED", 0.5),
            ("A_PREACCEPTED", 1.0),
            ("W_Completeren aanvraag", 24.0),
            ("A_ACCEPTED", 2.0),
            ("O_SELECTED", 4.0),
            ("O_CREATED", 1.0),
            ("O_SENT", 0.5),
            ("W_Nabellen offertes", 48.0),
            ("O_SENT_BACK", 24.0),
            ("O_ACCEPTED", 12.0),
            ("A_FINALIZED", 2.0),
            ("A_APPROVED", 1.0),
            ("A_ACTIVATED", 0.5)
        ]
        
        deviations = {
            "A_DECLINED": ("A_PREACCEPTED", 0.15),
            "A_CANCELLED": ("A_ACCEPTED", 0.10),
            "O_DECLINED": ("O_SENT_BACK", 0.12),
            "W_Afhandelen leads": ("A_PARTLYSUBMITTED", 0.20),
            "W_Beoordelen fraude": ("A_ACCEPTED", 0.05),
        }
        
        return cls._generate_process_log(n_cases, activities, deviations, "APP")
    
    @classmethod
    def _generate_bpi_2012_sample(cls, n_cases: int) -> pd.DataFrame:
        """Generate BPI 2012-style sample data."""
        return cls._generate_loan(n_cases)
    
    @classmethod
    def _generate_process_log(cls, n_cases: int, 
                              activities: List[Tuple[str, float]], 
                              deviations: Dict[str, Tuple[str, float]],
                              case_prefix: str) -> pd.DataFrame:
        """
        Generic process log generator.
        
        Args:
            n_cases: Number of cases to generate
            activities: List of (activity_name, mean_duration_hours)
            deviations: Dict of deviation_name -> (after_activity, probability)
            case_prefix: Prefix for case IDs
        """
        events = []
        
        customers = [f"Customer_{i}" for i in range(1, 51)]
        resources = [f"Resource_{i}" for i in range(1, 21)]
        regions = ["North", "South", "East", "West", "Central"]
        priorities = ["Low", "Medium", "High", "Critical"]
        
        for case_idx in range(1, n_cases + 1):
            case_id = f"{case_prefix}-{case_idx:06d}"
            timestamp = datetime.now() - timedelta(days=random.randint(1, 180))
            
            # Case attributes
            customer = random.choice(customers)
            priority = random.choices(priorities, weights=[0.3, 0.4, 0.2, 0.1])[0]
            region = random.choice(regions)
            value = round(random.uniform(100, 50000), 2)
            
            # Which deviations apply to this case
            case_deviations = {
                name: random.random() < prob
                for name, (_, prob) in deviations.items()
            }
            
            completed = True
            
            for i, (activity, mean_duration) in enumerate(activities):
                # Add main activity
                resource = random.choice(resources)
                duration = random.expovariate(1.0 / mean_duration) if mean_duration > 0 else 0.1
                
                events.append({
                    "case_id": case_id,
                    "activity": activity,
                    "timestamp": timestamp,
                    "resource": resource,
                    "customer": customer,
                    "priority": priority,
                    "region": region,
                    "value": value,
                    "lifecycle": "complete"
                })
                
                timestamp += timedelta(hours=duration)
                
                # Check for deviations after this activity
                for dev_name, (after_act, _) in deviations.items():
                    if after_act == activity and case_deviations.get(dev_name, False):
                        # Add deviation activity
                        events.append({
                            "case_id": case_id,
                            "activity": dev_name,
                            "timestamp": timestamp,
                            "resource": random.choice(resources),
                            "customer": customer,
                            "priority": priority,
                            "region": region,
                            "value": value,
                            "lifecycle": "complete"
                        })
                        timestamp += timedelta(hours=random.uniform(1, 24))
                        
                        # Some deviations end the case early
                        if "Rejected" in dev_name or "Cancelled" in dev_name or "Declined" in dev_name:
                            completed = False
                            break
                
                if not completed:
                    break
        
        df = pd.DataFrame(events)
        df = df.sort_values(["case_id", "timestamp"]).reset_index(drop=True)
        
        return df


def generate_comparison_datasets() -> Dict[str, pd.DataFrame]:
    """Generate multiple datasets for comparison."""
    loader = DatasetLoader()
    
    return {
        name: loader.load_dataset(name, n_cases=200)
        for name in ["order_to_cash", "procure_to_pay", "incident_management"]
    }


def get_dataset_statistics(df: pd.DataFrame) -> Dict:
    """Calculate statistics for an event log."""
    # Case-level stats
    case_lengths = df.groupby('case_id').size()
    case_durations = df.groupby('case_id')['timestamp'].agg(lambda x: (x.max() - x.min()).total_seconds() / 3600)
    
    # Activity stats
    activity_counts = df['activity'].value_counts()
    
    # Resource stats
    resource_counts = df['resource'].value_counts() if 'resource' in df.columns else pd.Series()
    
    return {
        "total_cases": df['case_id'].nunique(),
        "total_events": len(df),
        "total_activities": df['activity'].nunique(),
        "total_resources": df['resource'].nunique() if 'resource' in df.columns else 0,
        "avg_case_length": case_lengths.mean(),
        "min_case_length": case_lengths.min(),
        "max_case_length": case_lengths.max(),
        "avg_duration_hours": case_durations.mean(),
        "median_duration_hours": case_durations.median(),
        "date_range": {
            "start": df['timestamp'].min().isoformat(),
            "end": df['timestamp'].max().isoformat()
        },
        "top_activities": activity_counts.head(10).to_dict(),
        "top_resources": resource_counts.head(10).to_dict() if len(resource_counts) > 0 else {}
    }
