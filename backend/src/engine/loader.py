"""Loader - Read event logs from various formats.

Wraps pm4py.read_* functions.
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import pm4py

from src.domain.models import Dataset, DatasetType


def load_event_log(dataset: Dataset) -> pm4py.EventLog:
    """Load a PM4Py EventLog from a Dataset entity.
    
    Args:
        dataset: The Dataset entity containing file path info.
        
    Returns:
        PM4Py EventLog object ready for analysis.
        
    Raises:
        FileNotFoundError: If the source file doesn't exist.
        ValueError: If the file format is unsupported.
    """
    # Prefer processed parquet file if available
    file_path = dataset.processed_file_path or dataset.source_file_path
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Event log file not found: {file_path}")
    
    ext = Path(file_path).suffix.lower()
    
    if ext == ".parquet":
        df = pd.read_parquet(file_path)
        return pm4py.convert_to_event_log(df)
    elif ext == ".csv":
        return pm4py.read_csv(file_path)
    elif ext == ".xes":
        return pm4py.read_xes(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def load_dataframe(dataset: Dataset) -> pd.DataFrame:
    """Load event log as a pandas DataFrame.
    
    Useful for statistics and variant analysis where
    DataFrame operations are more efficient.
    """
    file_path = dataset.processed_file_path or dataset.source_file_path
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Event log file not found: {file_path}")
    
    ext = Path(file_path).suffix.lower()
    
    if ext == ".parquet":
        return pd.read_parquet(file_path)
    elif ext == ".csv":
        return pd.read_csv(file_path)
    elif ext == ".xes":
        log = pm4py.read_xes(file_path)
        return pm4py.convert_to_dataframe(log)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def get_log_metadata(log: pm4py.EventLog) -> dict:
    """Extract metadata from a PM4Py EventLog.
    
    Returns:
        Dict with case_count, event_count, activity_count, activities.
    """
    cases = len(log)
    events = sum(len(trace) for trace in log)
    activities = list(pm4py.get_event_attribute_values(log, "concept:name").keys())
    
    return {
        "case_count": cases,
        "event_count": events,
        "activity_count": len(activities),
        "activities": activities,
    }
