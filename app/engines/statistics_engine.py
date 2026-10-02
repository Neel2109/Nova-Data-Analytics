"""
DataNova - Statistics Engine
Generates descriptive statistics for numerical and categorical columns.
"""
import pandas as pd
import numpy as np


class StatisticsEngine:
    """Computes descriptive statistics for the dataset."""

    def compute(self, df: pd.DataFrame, schema: dict) -> dict:
        """Compute descriptive statistics for all columns."""
        numerical_stats = []
        categorical_stats = []

        for col, info in schema.items():
            if col not in df.columns:
                continue

            if info.get("type") == "numerical":
                stats = self._numerical_statistics(df[col])
                if stats:
                    numerical_stats.append(stats)
            elif info.get("type") in ("categorical", "boolean"):
                stats = self._categorical_statistics(df[col])
                if stats:
                    categorical_stats.append(stats)

        return {
            "numerical": numerical_stats,
            "categorical": categorical_stats,
        }

    def _numerical_statistics(self, series: pd.Series) -> dict | None:
        """Full descriptive stats for a numerical column."""
        try:
            numeric = pd.to_numeric(series, errors="coerce").dropna()
            if len(numeric) == 0:
                return None

            mode_val = numeric.mode()
            percentiles = {
                "5%": round(float(numeric.quantile(0.05)), 4),
                "10%": round(float(numeric.quantile(0.10)), 4),
                "25%": round(float(numeric.quantile(0.25)), 4),
                "50%": round(float(numeric.quantile(0.50)), 4),
                "75%": round(float(numeric.quantile(0.75)), 4),
                "90%": round(float(numeric.quantile(0.90)), 4),
                "95%": round(float(numeric.quantile(0.95)), 4),
            }

            return {
                "column": series.name,
                "count": int(numeric.count()),
                "mean": round(float(numeric.mean()), 4),
                "median": round(float(numeric.median()), 4),
                "mode": round(float(mode_val.iloc[0]), 4) if len(mode_val) > 0 else None,
                "min": round(float(numeric.min()), 4),
                "max": round(float(numeric.max()), 4),
                "range": round(float(numeric.max() - numeric.min()), 4),
                "std": round(float(numeric.std()), 4),
                "variance": round(float(numeric.var()), 4),
                "q1": round(float(numeric.quantile(0.25)), 4),
                "q2": round(float(numeric.quantile(0.50)), 4),
                "q3": round(float(numeric.quantile(0.75)), 4),
                "iqr": round(float(numeric.quantile(0.75) - numeric.quantile(0.25)), 4),
                "skewness": round(float(numeric.skew()), 4),
                "kurtosis": round(float(numeric.kurtosis()), 4),
                "percentiles": percentiles,
                "zero_count": int((numeric == 0).sum()),
                "negative_count": int((numeric < 0).sum()),
            }
        except Exception:
            return None

    def _categorical_statistics(self, series: pd.Series) -> dict | None:
        """Full descriptive stats for a categorical column."""
        try:
            non_null = series.dropna()
            if len(non_null) == 0:
                return None

            value_counts = non_null.value_counts()
            total = len(non_null)

            frequencies = {}
            for val, count in value_counts.items():
                frequencies[str(val)] = {
                    "count": int(count),
                    "percentage": round(count / total * 100, 2),
                }

            mode_val = non_null.mode()
            cardinality = non_null.nunique()

            return {
                "column": series.name,
                "count": int(non_null.count()),
                "unique": cardinality,
                "mode": str(mode_val.iloc[0]) if len(mode_val) > 0 else None,
                "mode_frequency": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "mode_percentage": round(value_counts.iloc[0] / total * 100, 2) if len(value_counts) > 0 else 0,
                "cardinality": cardinality,
                "frequencies": frequencies,
            }
        except Exception:
            return None
