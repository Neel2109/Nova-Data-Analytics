"""
DataNova - Categorical Engine
Analyzes categorical columns: frequency, distribution, dominance, imbalance.
"""
import pandas as pd
import numpy as np


class CategoricalEngine:
    """Analyzes categorical columns in the dataset."""

    def analyze(self, df: pd.DataFrame, schema: dict) -> dict:
        """Analyze all categorical columns."""
        cat_cols = [c for c, info in schema.items()
                    if info.get("type") in ("categorical", "boolean") and c in df.columns]

        if not cat_cols:
            return {"columns": [], "message": "No categorical columns detected."}

        results = []
        for col in cat_cols:
            analysis = self._analyze_column(df[col])
            if analysis:
                results.append(analysis)

        return {"columns": results}

    def _analyze_column(self, series: pd.Series) -> dict | None:
        """Analyze a single categorical column."""
        try:
            non_null = series.dropna()
            if len(non_null) == 0:
                return None

            value_counts = non_null.value_counts()
            total = len(non_null)

            # Distribution
            distribution = []
            for val, count in value_counts.items():
                pct = round(count / total * 100, 2)
                distribution.append({
                    "value": str(val),
                    "count": int(count),
                    "percentage": pct,
                })

            # Top and bottom
            most_common = str(value_counts.index[0]) if len(value_counts) > 0 else None
            least_common = str(value_counts.index[-1]) if len(value_counts) > 0 else None

            # Dominance (top category share)
            dominance = round(float(value_counts.iloc[0] / total * 100), 2) if len(value_counts) > 0 else 0

            # Rare categories (< 1%)
            rare = [str(val) for val, count in value_counts.items() if count / total < 0.01]

            # Imbalance ratio (max / min)
            imbalance_ratio = round(float(value_counts.iloc[0] / value_counts.iloc[-1]), 2) if len(value_counts) > 1 and value_counts.iloc[-1] > 0 else 1.0

            return {
                "column": series.name,
                "unique_count": int(series.nunique()),
                "missing": int(series.isnull().sum()),
                "missing_percentage": round(series.isnull().sum() / len(series) * 100, 2) if len(series) > 0 else 0,
                "most_common": most_common,
                "most_common_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "least_common": least_common,
                "least_common_count": int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
                "dominance": dominance,
                "rare_categories": rare,
                "rare_count": len(rare),
                "imbalance_ratio": imbalance_ratio,
                "distribution": distribution[:20],  # Top 20
            }
        except Exception:
            return None

    def get_group_analysis(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Automatically perform group-by analysis for interesting combinations."""
        cat_cols = [c for c, info in schema.items()
                    if info.get("type") in ("categorical", "boolean") and c in df.columns]
        num_cols = [c for c, info in schema.items()
                    if info.get("type") == "numerical" and c in df.columns]

        results = []
        for cat_col in cat_cols[:5]:  # Limit to 5 categorical columns
            for num_col in num_cols[:5]:  # Limit to 5 numerical columns
                try:
                    numeric_data = pd.to_numeric(df[num_col], errors="coerce")
                    grouped = numeric_data.groupby(df[cat_col])
                    agg = grouped.agg(["mean", "median", "sum", "count", "min", "max"])

                    groups = []
                    for group_name, row in agg.iterrows():
                        groups.append({
                            "group": str(group_name),
                            "mean": round(float(row["mean"]), 2),
                            "median": round(float(row["median"]), 2),
                            "sum": round(float(row["sum"]), 2),
                            "count": int(row["count"]),
                            "min": round(float(row["min"]), 2),
                            "max": round(float(row["max"]), 2),
                        })

                    if groups:
                        results.append({
                            "categorical_column": cat_col,
                            "numerical_column": num_col,
                            "groups": groups[:20],
                        })
                except Exception:
                    continue

        return results
