"""
File Service - Handles file parsing and column detection.

Uses pandas for CSV/Excel parsing and provides column metadata
for the frontend column mapping interface.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from dateutil import parser as date_parser

from ..models import (
    ColumnMetadata,
    ValidationResult,
    ValidationError,
    ValidationWarning,
    ValidationStats,
    MappingCreate,
)
from ..core import get_logger

log = get_logger(__name__)

# Common datetime formats to try
DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%d/%m/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
]


def parse_file(file_path: Path, max_rows: int | None = None) -> pd.DataFrame:
    """
    Parse a CSV or Excel file into a pandas DataFrame.
    
    Args:
        file_path: Path to the file
        max_rows: Optional limit on rows to read
        
    Returns:
        DataFrame with parsed data
    """
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == ".csv":
            # Try UTF-8 first, then latin-1
            try:
                df = pd.read_csv(file_path, nrows=max_rows)
            except UnicodeDecodeError:
                log.warning("UTF-8 decode failed, trying latin-1")
                df = pd.read_csv(file_path, nrows=max_rows, encoding="latin-1")
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(file_path, nrows=max_rows, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        log.info("file_parsed", row_count=len(df), column_count=len(df.columns))
        return df
        
    except Exception as e:
        log.error("file_parse_failed", error=str(e))
        raise


def detect_datetime_format(series: pd.Series) -> str | None:
    """
    Detect the datetime format of a series by trying common formats.
    
    Args:
        series: Pandas series to analyze
        
    Returns:
        Detected format string or None
    """
    # Get non-null sample values
    sample = series.dropna().head(20).astype(str).tolist()
    if not sample:
        return None
    
    # Try each format
    for fmt in DATETIME_FORMATS:
        try:
            # Try parsing first few values
            successes = 0
            for val in sample[:5]:
                try:
                    datetime.strptime(str(val).strip(), fmt)
                    successes += 1
                except ValueError:
                    pass
            
            if successes >= 3:  # At least 3/5 must parse
                return fmt
        except Exception:
            continue
    
    # Try dateutil as fallback
    try:
        for val in sample[:3]:
            date_parser.parse(str(val))
        return "ISO8601"  # Generic indicator
    except Exception:
        pass
    
    return None


def detect_column_type(series: pd.Series) -> tuple[str, str | None]:
    """
    Detect the type of a column.
    
    Args:
        series: Pandas series to analyze
        
    Returns:
        Tuple of (type_name, format_string_if_datetime)
    """
    # Check for datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime", None
    
    # Check if it looks like datetime strings
    sample = series.dropna().head(10).astype(str).tolist()
    if sample:
        fmt = detect_datetime_format(series)
        if fmt:
            return "datetime", fmt
    
    # Check for boolean
    if pd.api.types.is_bool_dtype(series):
        return "boolean", None
    
    # Check for numeric
    if pd.api.types.is_numeric_dtype(series):
        return "number", None
    
    # Check if string values look like numbers
    try:
        non_null = series.dropna().head(20)
        if len(non_null) > 0:
            pd.to_numeric(non_null)
            return "number", None
    except (ValueError, TypeError):
        pass
    
    return "string", None


def detect_columns(df: pd.DataFrame) -> list[ColumnMetadata]:
    """
    Analyze DataFrame columns and return metadata.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        List of ColumnMetadata objects
    """
    columns = []
    
    for col_name in df.columns:
        series = df[col_name]
        
        # Detect type
        col_type, detected_format = detect_column_type(series)
        
        # Get sample values (first 5 non-null, as strings)
        samples = (
            series.dropna()
            .head(5)
            .astype(str)
            .tolist()
        )
        
        # Calculate statistics
        null_count = series.isna().sum()
        null_pct = (null_count / len(series) * 100) if len(series) > 0 else 0
        unique_count = series.nunique()
        
        columns.append(ColumnMetadata(
            name=str(col_name),
            detected_type=col_type,
            sample_values=samples,
            null_percentage=round(null_pct, 2),
            unique_count=unique_count,
            detected_format=detected_format,
        ))
    
    log.info("columns_detected", column_count=len(columns))
    return columns


def validate_mapping(
    df: pd.DataFrame,
    mapping: MappingCreate,
    max_rows: int = 10000,
) -> ValidationResult:
    """
    Validate a column mapping against the data.
    
    Args:
        df: DataFrame to validate against
        mapping: The column mapping to validate
        max_rows: Max rows to validate
        
    Returns:
        ValidationResult with errors, warnings, and stats
    """
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []
    
    # Use sample for validation
    sample_df = df.head(max_rows)
    
    # Check required columns exist
    required = {
        "case_id": mapping.case_id_column,
        "activity": mapping.activity_column,
        "timestamp": mapping.timestamp_column,
    }
    
    for field, col_name in required.items():
        if col_name not in df.columns:
            errors.append(ValidationError(
                field=field,
                message=f"Column '{col_name}' not found in file",
            ))
    
    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
    
    # Validate case_id column
    case_col = sample_df[mapping.case_id_column]
    case_nulls = case_col.isna().sum()
    if case_nulls > 0:
        errors.append(ValidationError(
            field="case_id",
            message=f"{case_nulls} null values in case ID column",
            sample_bad_values=["(null)"] * min(3, case_nulls),
        ))
    
    case_unique = case_col.nunique()
    if case_unique > len(sample_df) * 0.8:
        warnings.append(ValidationWarning(
            field="case_id",
            message=f"High uniqueness ({case_unique}/{len(sample_df)} unique) - might be wrong column",
            suggestion="Case ID should group related events together",
        ))
    
    # Validate activity column
    activity_col = sample_df[mapping.activity_column]
    activity_nulls = activity_col.isna().sum()
    if activity_nulls > 0:
        errors.append(ValidationError(
            field="activity",
            message=f"{activity_nulls} null values in activity column",
        ))
    
    activity_unique = activity_col.nunique()
    if activity_unique > 500:
        warnings.append(ValidationWarning(
            field="activity",
            message=f"Very high activity count ({activity_unique}) - might be a description field",
            suggestion="Activity should be categorical, not free text",
        ))
    
    # Validate timestamp column
    ts_col = sample_df[mapping.timestamp_column]
    ts_nulls = ts_col.isna().sum()
    if ts_nulls > len(sample_df) * 0.05:
        errors.append(ValidationError(
            field="timestamp",
            message=f"{ts_nulls} null values ({ts_nulls/len(sample_df)*100:.1f}%) in timestamp column",
        ))
    
    # Try parsing timestamps
    parsed_ts = None
    try:
        if mapping.timestamp_format:
            parsed_ts = pd.to_datetime(ts_col, format=mapping.timestamp_format, errors="coerce")
        else:
            parsed_ts = pd.to_datetime(ts_col, errors="coerce")
        
        unparsed = parsed_ts.isna().sum() - ts_nulls  # Exclude original nulls
        if unparsed > len(sample_df) * 0.05:
            bad_samples = ts_col[parsed_ts.isna() & ts_col.notna()].head(3).astype(str).tolist()
            errors.append(ValidationError(
                field="timestamp",
                message=f"{unparsed} values could not be parsed as timestamps",
                sample_bad_values=bad_samples,
            ))
    except Exception as e:
        errors.append(ValidationError(
            field="timestamp",
            message=f"Failed to parse timestamps: {str(e)}",
        ))
    
    # Build stats
    stats = None
    if not errors and parsed_ts is not None:
        valid_ts = parsed_ts.dropna()
        stats = ValidationStats(
            total_rows=len(sample_df),
            valid_rows=len(sample_df) - sum(1 for e in errors if e.field in required),
            case_count=case_unique,
            activity_count=activity_unique,
            date_range_start=valid_ts.min() if len(valid_ts) > 0 else None,
            date_range_end=valid_ts.max() if len(valid_ts) > 0 else None,
        )
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        stats=stats,
    )


def get_row_count(file_path: Path) -> int:
    """
    Get the total row count of a file without loading it all.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Number of data rows (excluding header)
    """
    suffix = file_path.suffix.lower()
    
    if suffix == ".csv":
        # Count lines efficiently
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f) - 1  # Subtract header
    elif suffix in (".xlsx", ".xls"):
        # For Excel, we need to load it
        df = pd.read_excel(file_path, engine="openpyxl")
        return len(df)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
