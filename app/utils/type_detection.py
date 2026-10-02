"""
DataNova - Type Detection Utilities
Detects column types (numerical, categorical, datetime, boolean, text, ID).
"""
import pandas as pd
import numpy as np
from app.core.config import (
    MAX_UNIQUE_RATIO_FOR_CATEGORICAL,
    MAX_UNIQUE_COUNT_FOR_CATEGORICAL,
    DATE_PATTERNS,
)


def detect_column_type(series: pd.Series, total_rows: int) -> tuple[str, str | None]:
    """
    Detect the semantic type and subtype of a column.
    Returns (type, subtype).
    """
    col_name = str(series.name).lower().strip()
    non_null = series.dropna()

    if len(non_null) == 0:
        return "text", None

    # Check boolean first
    if _is_boolean(non_null):
        return "boolean", "binary"

    # Check datetime
    if _is_datetime(non_null, col_name):
        return "datetime", "date"

    # Check if it's an ID column
    if _is_identifier(non_null, col_name, total_rows):
        return "identifier", None

    # Check numerical
    if pd.api.types.is_numeric_dtype(non_null):
        if pd.api.types.is_integer_dtype(non_null) or all(non_null.dropna().apply(lambda x: float(x).is_integer())):
            return "numerical", "integer"
        return "numerical", "float"

    # Try to convert to numeric
    try:
        numeric_converted = pd.to_numeric(non_null, errors="coerce")
        valid_ratio = numeric_converted.notna().sum() / len(non_null)
        if valid_ratio > 0.8:
            return "numerical", "float"
    except (ValueError, TypeError):
        pass

    # Check categorical
    unique_count = non_null.nunique()
    unique_ratio = unique_count / total_rows if total_rows > 0 else 0

    if unique_ratio <= MAX_UNIQUE_RATIO_FOR_CATEGORICAL or unique_count <= MAX_UNIQUE_COUNT_FOR_CATEGORICAL:
        return "categorical", "nominal"

    # Default to text
    return "text", None


def _is_boolean(series: pd.Series) -> bool:
    """Check if a column contains boolean-like values."""
    unique_vals = set(series.astype(str).str.lower().str.strip().unique())
    bool_sets = [
        {"true", "false"},
        {"yes", "no"},
        {"1", "0"},
        {"t", "f"},
        {"y", "n"},
        {"1.0", "0.0"},
    ]
    return any(unique_vals.issubset(s) and len(unique_vals) <= 3 for s in bool_sets)


def _is_datetime(series: pd.Series, col_name: str) -> bool:
    """Check if a column contains datetime values."""
    # Check column name hints
    date_hints = ["date", "time", "datetime", "timestamp", "created", "updated", "dob", "birth"]
    if any(hint in col_name for hint in date_hints):
        try:
            pd.to_datetime(series.head(100), errors="raise", infer_datetime_format=True)
            return True
        except (ValueError, TypeError):
            pass

    # Check if already datetime type
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    # Try parsing sample
    if series.dtype == object:
        sample = series.dropna().head(50)
        if len(sample) == 0:
            return False
        for pattern in DATE_PATTERNS:
            try:
                pd.to_datetime(sample, format=pattern, errors="raise")
                return True
            except (ValueError, TypeError):
                continue
        # Try generic parsing
        try:
            result = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
            valid_ratio = result.notna().sum() / len(sample)
            if valid_ratio > 0.8:
                return True
        except (ValueError, TypeError):
            pass

    return False


def _is_identifier(series: pd.Series, col_name: str, total_rows: int) -> bool:
    """Check if a column is likely an identifier/ID column."""
    id_hints = ["id", "key", "code", "index", "uuid", "guid", "serial", "number", "no", "num"]
    name_is_id = any(col_name == hint or col_name.endswith(f"_{hint}") or col_name.startswith(f"{hint}_")
                      for hint in id_hints)

    if not name_is_id:
        return False

    # ID columns typically have high uniqueness
    unique_ratio = series.nunique() / total_rows if total_rows > 0 else 0
    return unique_ratio > 0.9


def detect_all_column_types(df: pd.DataFrame) -> dict[str, dict]:
    """
    Detect types for all columns in a DataFrame.
    Returns dict mapping column name -> {type, subtype}.
    """
    total_rows = len(df)
    schema = {}
    for col in df.columns:
        col_type, col_subtype = detect_column_type(df[col], total_rows)
        schema[col] = {
            "type": col_type,
            "subtype": col_subtype,
        }
    return schema


def get_columns_by_type(schema: dict, col_type: str) -> list[str]:
    """Get column names of a specific type."""
    return [col for col, info in schema.items() if info["type"] == col_type]
