"""
DataNova - Correlation Engine
Computes correlation matrices, finds strong relationships, and generates scatter plot data.
"""
import pandas as pd
import numpy as np
from app.core.config import STRONG_CORRELATION_THRESHOLD, MODERATE_CORRELATION_THRESHOLD


class CorrelationEngine:
    """Computes and analyzes correlations between numerical variables."""

    def compute(self, df: pd.DataFrame, schema: dict, method: str = "pearson", threshold: float = 0.3) -> dict:
        """Compute correlation analysis for numerical columns."""
        num_cols = [c for c, info in schema.items()
                    if info.get("type") == "numerical" and c in df.columns]

        if len(num_cols) < 2:
            return {
                "matrix": {},
                "strong_positive": [],
                "strong_negative": [],
                "moderate": [],
                "method": method,
                "message": "At least two numerical columns are required for correlation analysis."
            }

        # Build numeric DataFrame
        numeric_df = df[num_cols].apply(pd.to_numeric, errors="coerce")

        # Compute correlation matrix
        try:
            corr_matrix = numeric_df.corr(method=method)
        except Exception:
            corr_matrix = numeric_df.corr(method="pearson")
            method = "pearson"

        # Convert matrix to serializable format
        matrix_dict = {}
        for col in corr_matrix.columns:
            matrix_dict[col] = {}
            for row in corr_matrix.index:
                val = corr_matrix.loc[row, col]
                matrix_dict[col][row] = round(float(val), 4) if not pd.isna(val) else None

        # Find strong relationships
        strong_positive = []
        strong_negative = []
        moderate = []
        processed = set()

        for i, col_a in enumerate(num_cols):
            for j, col_b in enumerate(num_cols):
                if i >= j:
                    continue
                pair_key = tuple(sorted([col_a, col_b]))
                if pair_key in processed:
                    continue
                processed.add(pair_key)

                corr_val = corr_matrix.loc[col_a, col_b]
                if pd.isna(corr_val):
                    continue

                entry = {
                    "column_a": col_a,
                    "column_b": col_b,
                    "correlation": round(float(corr_val), 4),
                    "strength": self._classify_strength(abs(corr_val)),
                }

                if corr_val >= STRONG_CORRELATION_THRESHOLD:
                    strong_positive.append(entry)
                elif corr_val <= -STRONG_CORRELATION_THRESHOLD:
                    strong_negative.append(entry)
                elif abs(corr_val) >= threshold:
                    moderate.append(entry)

        # Sort by absolute correlation
        strong_positive.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        strong_negative.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        moderate.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "matrix": matrix_dict,
            "strong_positive": strong_positive,
            "strong_negative": strong_negative,
            "moderate": moderate,
            "method": method,
            "num_columns": len(num_cols),
        }

    def _classify_strength(self, abs_corr: float) -> str:
        """Classify correlation strength."""
        if abs_corr >= 0.9:
            return "very_strong"
        elif abs_corr >= STRONG_CORRELATION_THRESHOLD:
            return "strong"
        elif abs_corr >= MODERATE_CORRELATION_THRESHOLD:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        return "negligible"

    def get_scatter_data(self, df: pd.DataFrame, col_a: str, col_b: str, max_points: int = 2000) -> dict:
        """Get scatter plot data for two columns."""
        try:
            data = df[[col_a, col_b]].dropna()
            if len(data) > max_points:
                data = data.sample(max_points, random_state=42)

            return {
                "x": data[col_a].tolist(),
                "y": data[col_b].tolist(),
                "x_label": col_a,
                "y_label": col_b,
                "count": len(data),
            }
        except Exception:
            return {"x": [], "y": [], "x_label": col_a, "y_label": col_b, "count": 0}
