import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog

from ...core import get_logger

log = get_logger(__name__)


class EventLogCreationError(Exception):
    """Raised when event log creation fails."""

    def __init__(self, message: str, cause: Exception | None = None):
        self.message = message
        self.cause = cause
        super().__init__(message)


class EmptyEventLogError(EventLogCreationError):
    """Raised when resulting event log is empty."""

    def __init__(self, message: str = "Event log is empty after processing"):
        super().__init__(message)


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

    Raises:
        EventLogCreationError: If event log creation fails
        EmptyEventLogError: If resulting event log is empty
    """
    log.info(f"Creating event log from {len(df)} rows")

    if df.empty:
        raise EmptyEventLogError("Input DataFrame is empty")

    # Validate required columns exist
    missing_cols = []
    for col, name in [(case_id_col, "case_id"), (activity_col, "activity"), (timestamp_col, "timestamp")]:
        if col not in df.columns:
            missing_cols.append(f"{name} column '{col}'")
    if missing_cols:
        raise EventLogCreationError(f"Missing columns: {', '.join(missing_cols)}")

    try:
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
            log.warning(f"Dropping {null_ts} rows with null/unparseable timestamps")
            df = df.dropna(subset=[timestamp_col])

        if df.empty:
            raise EmptyEventLogError("All rows were dropped due to invalid timestamps")

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

        if len(event_log) == 0:
            raise EmptyEventLogError("Event log has no cases after conversion")

        log.info(f"Created event log with {len(event_log)} cases")
        return event_log

    except EmptyEventLogError:
        raise
    except Exception as e:
        log.error(f"Event log creation failed: {e}")
        raise EventLogCreationError(f"Failed to create event log: {str(e)}", cause=e)
