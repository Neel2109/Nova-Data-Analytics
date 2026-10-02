"""
DataNova - Insight Engine
Generates automatic evidence-based insights from the dataset analysis.
"""
import pandas as pd
import numpy as np
from app.core.config import STRONG_CORRELATION_THRESHOLD, IQR_MULTIPLIER


class InsightEngine:
    """Generates structured, evidence-based insights from dataset analysis."""

    def generate(self, df: pd.DataFrame, schema: dict, profile: dict) -> list[dict]:
        """Generate all automatic insights."""
        insights = []
        insights.extend(self._data_quality_insights(df, profile))
        insights.extend(self._distribution_insights(df, schema))
        insights.extend(self._correlation_insights(df, schema))
        insights.extend(self._outlier_insights(df, schema))
        insights.extend(self._categorical_insights(df, schema))
        insights.extend(self._timeseries_insights(df, schema))

        # Sort by severity priority
        severity_order = {"critical": 0, "warning": 1, "info": 2, "success": 3}
        insights.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 2))
        return insights

    def _data_quality_insights(self, df: pd.DataFrame, profile: dict) -> list[dict]:
        """Generate data quality insights."""
        insights = []
        missing_pct = profile.get("missing_percentage", 0)
        dup_count = profile.get("duplicate_rows", 0)
        quality = profile.get("quality_score", 100)

        if quality >= 95:
            insights.append({
                "type": "data_quality", "severity": "success",
                "title": "Excellent Data Quality",
                "message": f"Your dataset has a quality score of {quality}%, indicating very clean data.",
                "evidence": {"quality_score": quality},
            })
        elif quality < 80:
            insights.append({
                "type": "data_quality", "severity": "critical",
                "title": "Low Data Quality",
                "message": f"Data quality score is {quality}%. Significant cleaning may be required.",
                "evidence": {"quality_score": quality},
            })

        if missing_pct > 5:
            insights.append({
                "type": "data_quality", "severity": "warning",
                "title": "Significant Missing Data",
                "message": f"{missing_pct}% of cells contain missing values.",
                "evidence": {"missing_percentage": missing_pct, "missing_cells": profile.get("missing_cells", 0)},
            })
        elif missing_pct > 0:
            insights.append({
                "type": "data_quality", "severity": "info",
                "title": "Missing Values Detected",
                "message": f"{missing_pct}% of cells contain missing values.",
                "evidence": {"missing_percentage": missing_pct},
            })

        if dup_count > 0:
            dup_pct = profile.get("duplicate_percentage", 0)
            sev = "warning" if dup_pct > 1 else "info"
            insights.append({
                "type": "data_quality", "severity": sev,
                "title": "Duplicate Records Found",
                "message": f"{dup_count} duplicate rows detected ({dup_pct}%).",
                "evidence": {"duplicate_rows": dup_count, "duplicate_percentage": dup_pct},
            })

        # Per-column missing
        for col_profile in profile.get("column_profiles", []):
            col_missing = col_profile.get("missing_percentage", 0)
            if col_missing > 10:
                insights.append({
                    "type": "data_quality", "severity": "warning",
                    "title": f"High Missing Rate in '{col_profile['name']}'",
                    "message": f"Column '{col_profile['name']}' has {col_missing}% missing values.",
                    "column": col_profile["name"],
                    "evidence": {"missing_percentage": col_missing},
                })

        return insights

    def _distribution_insights(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Generate distribution insights for numerical columns."""
        insights = []
        num_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in df.columns]

        for col in num_cols[:10]:
            try:
                numeric = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(numeric) < 10:
                    continue

                skew = float(numeric.skew())
                kurt = float(numeric.kurtosis())

                if abs(skew) > 2:
                    direction = "right" if skew > 0 else "left"
                    insights.append({
                        "type": "distribution", "severity": "info",
                        "title": f"Highly Skewed Distribution in '{col}'",
                        "message": f"'{col}' shows strong {direction} skewness ({skew:.2f}). Consider log transformation for analysis.",
                        "column": col,
                        "evidence": {"skewness": round(skew, 4), "direction": direction},
                    })

                if kurt > 7:
                    insights.append({
                        "type": "distribution", "severity": "info",
                        "title": f"Heavy-Tailed Distribution in '{col}'",
                        "message": f"'{col}' has high kurtosis ({kurt:.2f}), indicating heavy tails or outliers.",
                        "column": col,
                        "evidence": {"kurtosis": round(kurt, 4)},
                    })
            except Exception:
                continue

        return insights

    def _correlation_insights(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Generate correlation insights."""
        insights = []
        num_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in df.columns]

        if len(num_cols) < 2:
            return insights

        try:
            numeric_df = df[num_cols].apply(pd.to_numeric, errors="coerce")
            corr_matrix = numeric_df.corr()

            processed = set()
            for i, col_a in enumerate(num_cols):
                for j, col_b in enumerate(num_cols):
                    if i >= j:
                        continue
                    pair = tuple(sorted([col_a, col_b]))
                    if pair in processed:
                        continue
                    processed.add(pair)

                    corr_val = corr_matrix.loc[col_a, col_b]
                    if pd.isna(corr_val):
                        continue

                    if abs(corr_val) >= STRONG_CORRELATION_THRESHOLD:
                        direction = "positive" if corr_val > 0 else "negative"
                        insights.append({
                            "type": "correlation", "severity": "info",
                            "title": f"Strong {'Positive' if corr_val > 0 else 'Negative'} Correlation",
                            "message": f"'{col_a}' and '{col_b}' show a strong {direction} correlation (r = {corr_val:.3f}). Association does not imply causation.",
                            "columns": [col_a, col_b],
                            "evidence": {"correlation": round(float(corr_val), 4), "direction": direction},
                        })
        except Exception:
            pass

        return insights

    def _outlier_insights(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Generate outlier insights."""
        insights = []
        num_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in df.columns]

        for col in num_cols[:10]:
            try:
                numeric = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(numeric) < 10:
                    continue

                q1 = numeric.quantile(0.25)
                q3 = numeric.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - IQR_MULTIPLIER * iqr
                upper = q3 + IQR_MULTIPLIER * iqr
                outlier_count = int(((numeric < lower) | (numeric > upper)).sum())
                outlier_pct = round(outlier_count / len(numeric) * 100, 2)

                if outlier_pct > 5:
                    insights.append({
                        "type": "outlier", "severity": "warning",
                        "title": f"High Outlier Concentration in '{col}'",
                        "message": f"'{col}' contains {outlier_count} potential outliers ({outlier_pct}% of values) using the IQR method.",
                        "column": col,
                        "evidence": {"outlier_count": outlier_count, "outlier_percentage": outlier_pct},
                    })
                elif outlier_count > 0:
                    insights.append({
                        "type": "outlier", "severity": "info",
                        "title": f"Outliers Detected in '{col}'",
                        "message": f"'{col}' contains {outlier_count} potential outliers ({outlier_pct}%).",
                        "column": col,
                        "evidence": {"outlier_count": outlier_count, "outlier_percentage": outlier_pct},
                    })
            except Exception:
                continue

        return insights

    def _categorical_insights(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Generate categorical insights."""
        insights = []
        cat_cols = [c for c, info in schema.items() if info.get("type") == "categorical" and c in df.columns]

        for col in cat_cols[:10]:
            try:
                value_counts = df[col].value_counts()
                total = df[col].count()
                if total == 0:
                    continue

                top_val = str(value_counts.index[0])
                top_pct = round(value_counts.iloc[0] / total * 100, 1)

                if top_pct > 80:
                    insights.append({
                        "type": "category", "severity": "warning",
                        "title": f"Dominant Category in '{col}'",
                        "message": f"'{top_val}' represents {top_pct}% of '{col}'. This column has very low diversity.",
                        "column": col,
                        "evidence": {"dominant_value": top_val, "percentage": top_pct},
                    })
                elif len(value_counts) >= 2:
                    insights.append({
                        "type": "category", "severity": "info",
                        "title": f"Top Category in '{col}'",
                        "message": f"'{top_val}' is the most common value in '{col}' ({top_pct}%).",
                        "column": col,
                        "evidence": {"top_value": top_val, "percentage": top_pct, "unique_count": len(value_counts)},
                    })
            except Exception:
                continue

        return insights[:5]

    def _timeseries_insights(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Generate time-series insights."""
        insights = []
        date_cols = [c for c, info in schema.items() if info.get("type") == "datetime" and c in df.columns]
        num_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in df.columns]

        if not date_cols or not num_cols:
            return insights

        date_col = date_cols[0]
        try:
            dates = pd.to_datetime(df[date_col], errors="coerce", infer_datetime_format=True).dropna()
            if len(dates) > 10:
                date_range = (dates.max() - dates.min()).days
                insights.append({
                    "type": "time_series", "severity": "info",
                    "title": "Time-Series Data Available",
                    "message": f"Dataset spans {date_range} days ({dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}). Time-series analysis is available.",
                    "column": date_col,
                    "evidence": {"start": str(dates.min().date()), "end": str(dates.max().date()), "days": date_range},
                })
        except Exception:
            pass

        return insights
