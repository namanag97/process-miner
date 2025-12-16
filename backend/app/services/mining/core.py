import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog

from ...core import get_logger

log = get_logger(__name__)

def create_event_log(
    df: pd.DataFrame,
    case_id_col: str,
    activity_col: str,
    timestamp_col: str,
    resource_col: str | None = None,
    timestamp_format: str | None = None,
) -> EventLog:
    """
    Convert a pandas DataFrame to a PM4Py EventLog.
    """
    log.info(f"Creating event log from {len(df)} rows")
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Parse timestamps
    if timestamp_format and timestamp_format != "ISO8601":
        df[timestamp_col] = pd.to_datetime(
            df[timestamp_col], 
            format=timestamp_format,
            errors="coerce"
        )
    else:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")
    
    # Drop rows with null timestamps
    null_ts = df[timestamp_col].isna().sum()
    if null_ts > 0:
        log.warning(f"Dropping {null_ts} rows with null timestamps")
        df = df.dropna(subset=[timestamp_col])
    
    # Format for PM4Py
    df = pm4py.format_dataframe(
        df,
        case_id=case_id_col,
        activity_key=activity_col,
        timestamp_key=timestamp_col,
    )
    
    # Add resource if provided
    if resource_col and resource_col in df.columns:
        df["org:resource"] = df[resource_col]
    
    # Convert to event log
    event_log = pm4py.convert_to_event_log(df)
    
    log.info(f"Created event log with {len(event_log)} cases")
    return event_log
