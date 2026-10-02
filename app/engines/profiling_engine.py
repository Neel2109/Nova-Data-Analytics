"""
DataNova - Profiling Engine
Generates complete data profiles for every column.
"""
import pandas as pd
import numpy as np
from app.utils.type_detection import detect_all_column_types, get_columns_by_type
from app.core.config import IQR_MULTIPLIER


class ProfilingEngine:
    """Generates comprehensive column-level data profiles."""

    def profile_dataset(self, df: pd.DataFrame, schema: dict | None = None) -> dict:
        """Generate a full profile for the dataset."""
        if schema is None:
            schema = detect_all_column_types(df)

        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols
        missing_cells = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)

        num_cols = get_columns_by_type(schema, "numerical")
        cat_cols = get_columns_by_type(schema, "categorical")
        date_cols = get_columns_by_type(schema, "datetime")
        bool_cols = get_columns_by_type(schema, "boolean")

        # Quality score
        completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 100
        uniqueness = (1 - duplicate_rows / total_rows) * 100 if total_rows > 0 else 100
        quality_score = round((completeness * 0.6 + uniqueness * 0.4), 1)

        # Column profiles
        column_profiles = []
        for col in df.columns:
            profile = self._profile_column(df[col], schema.get(col, {}), total_rows)
            column_profiles.append(profile)

        return {
            "rows": total_rows,
            "columns": total_cols,
            "numerical_columns": len(num_cols),
            "categorical_columns": len(cat_cols),
            "datetime_columns": len(date_cols),
            "boolean_columns": len(bool_cols),
            "missing_cells": missing_cells,
            "missing_percentage": round(missing_cells / total_cells * 100, 2) if total_cells > 0 else 0,
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": round(duplicate_rows / total_rows * 100, 2) if total_rows > 0 else 0,
            "memory_usage_mb": memory_mb,
            "quality_score": quality_score,
            "schema": schema,
            "column_profiles": column_profiles,
        }

    def _profile_column(self, series: pd.Series, col_info: dict, total_rows: int) -> dict:
        """Generate a profile for a single column."""
        col_type = col_info.get("type", "text")
        col_subtype = col_info.get("subtype")
        non_null = series.dropna()

        profile = {
            "name": series.name,
            "dtype": str(series.dtype),
            "column_type": col_type,
            "subtype": col_subtype,
            "count": int(non_null.count()),
            "missing": int(series.isnull().sum()),
            "missing_percentage": round(series.isnull().sum() / total_rows * 100, 2) if total_rows > 0 else 0,
            "unique": int(series.nunique()),
        }

        if col_type == "numerical":
            profile.update(self._numerical_stats(non_null))
        elif col_type == "categorical" or col_type == "boolean":
            profile.update(self._categorical_stats(non_null))
        elif col_type == "datetime":
            profile.update(self._datetime_stats(series))

        return profile

    def _numerical_stats(self, series: pd.Series) -> dict:
        """Calculate statistics for numerical columns."""
        try:
            numeric = pd.to_numeric(series, errors="coerce").dropna()
            if len(numeric) == 0:
                return {}

            q1 = float(numeric.quantile(0.25))
            q2 = float(numeric.quantile(0.50))
            q3 = float(numeric.quantile(0.75))
            iqr = q3 - q1
            lower = q1 - IQR_MULTIPLIER * iqr
            upper = q3 + IQR_MULTIPLIER * iqr
            outliers = int(((numeric < lower) | (numeric > upper)).sum())

            mode_val = numeric.mode()
            mode_result = float(mode_val.iloc[0]) if len(mode_val) > 0 else None

            return {
                "mean": round(float(numeric.mean()), 4),
                "median": round(float(numeric.median()), 4),
                "mode": mode_result,
                "std": round(float(numeric.std()), 4),
                "variance": round(float(numeric.var()), 4),
                "min_val": round(float(numeric.min()), 4),
                "max_val": round(float(numeric.max()), 4),
                "range_val": round(float(numeric.max() - numeric.min()), 4),
                "q1": round(q1, 4),
                "q2": round(q2, 4),
                "q3": round(q3, 4),
                "iqr": round(iqr, 4),
                "skewness": round(float(numeric.skew()), 4),
                "kurtosis": round(float(numeric.kurtosis()), 4),
                "zero_count": int((numeric == 0).sum()),
                "negative_count": int((numeric < 0).sum()),
                "outlier_count": outliers,
                "percentile_5": round(float(numeric.quantile(0.05)), 4),
                "percentile_95": round(float(numeric.quantile(0.95)), 4),
            }
        except Exception:
            return {}

    def _categorical_stats(self, series: pd.Series) -> dict:
        """Calculate statistics for categorical columns."""
        try:
            value_counts = series.value_counts()
            total = len(series)
            top_n = min(10, len(value_counts))
            top_categories = {}
            for val, count in value_counts.head(top_n).items():
                top_categories[str(val)] = {
                    "count": int(count),
                    "percentage": round(count / total * 100, 2) if total > 0 else 0,
                }

            mode_val = series.mode()
            return {
                "mode": str(mode_val.iloc[0]) if len(mode_val) > 0 else None,
                "top_categories": top_categories,
            }
        except Exception:
            return {}

    def _datetime_stats(self, series: pd.Series) -> dict:
        """Calculate statistics for datetime columns."""
        try:
            dates = pd.to_datetime(series, errors="coerce", infer_datetime_format=True).dropna()
            if len(dates) == 0:
                return {}

            min_date = dates.min()
            max_date = dates.max()
            date_range = (max_date - min_date).days

            return {
                "min_date": str(min_date.date()),
                "max_date": str(max_date.date()),
                "date_range_days": int(date_range),
            }
        except Exception:
            return {}
