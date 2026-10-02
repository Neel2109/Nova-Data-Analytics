"""
DataNova - Outlier Engine
Detects outliers using IQR, Z-score, and Isolation Forest methods.
"""
import pandas as pd
import numpy as np
from scipy import stats
from app.core.config import IQR_MULTIPLIER, ZSCORE_THRESHOLD


class OutlierEngine:
    """Detects and reports outliers in numerical columns."""

    def detect(self, df: pd.DataFrame, schema: dict, method: str = "iqr",
               columns: list[str] | None = None) -> dict:
        """Detect outliers using the specified method."""
        num_cols = columns or [
            c for c, info in schema.items()
            if info.get("type") == "numerical" and c in df.columns
        ]

        if not num_cols:
            return {"method": method, "summary": [], "total_outliers": 0}

        summary = []
        total_outliers = 0

        for col in num_cols:
            try:
                numeric = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(numeric) == 0:
                    continue

                if method == "iqr":
                    result = self._iqr_detection(numeric, col)
                elif method == "zscore":
                    result = self._zscore_detection(numeric, col)
                elif method == "isolation_forest":
                    result = self._isolation_forest_detection(numeric, col)
                else:
                    result = self._iqr_detection(numeric, col)

                if result:
                    summary.append(result)
                    total_outliers += result["outlier_count"]
            except Exception:
                continue

        summary.sort(key=lambda x: x["outlier_count"], reverse=True)

        return {
            "method": method,
            "summary": summary,
            "total_outliers": total_outliers,
        }

    def _iqr_detection(self, series: pd.Series, col_name: str) -> dict:
        """Detect outliers using IQR method."""
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - IQR_MULTIPLIER * iqr
        upper = q3 + IQR_MULTIPLIER * iqr
        outlier_mask = (series < lower) | (series > upper)
        outlier_count = int(outlier_mask.sum())

        return {
            "column": col_name,
            "outlier_count": outlier_count,
            "outlier_percentage": round(outlier_count / len(series) * 100, 2),
            "lower_bound": round(lower, 4),
            "upper_bound": round(upper, 4),
            "q1": round(q1, 4),
            "q3": round(q3, 4),
            "iqr": round(iqr, 4),
            "min_outlier": round(float(series[outlier_mask].min()), 4) if outlier_count > 0 else None,
            "max_outlier": round(float(series[outlier_mask].max()), 4) if outlier_count > 0 else None,
        }

    def _zscore_detection(self, series: pd.Series, col_name: str) -> dict:
        """Detect outliers using Z-score method."""
        z_scores = np.abs(stats.zscore(series, nan_policy="omit"))
        outlier_mask = z_scores > ZSCORE_THRESHOLD
        outlier_count = int(outlier_mask.sum())

        return {
            "column": col_name,
            "outlier_count": outlier_count,
            "outlier_percentage": round(outlier_count / len(series) * 100, 2),
            "threshold": ZSCORE_THRESHOLD,
            "max_zscore": round(float(z_scores.max()), 4),
            "mean_zscore": round(float(z_scores.mean()), 4),
        }

    def _isolation_forest_detection(self, series: pd.Series, col_name: str) -> dict:
        """Detect outliers using Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest

            data = series.values.reshape(-1, 1)
            clf = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
            predictions = clf.fit_predict(data)
            outlier_count = int((predictions == -1).sum())

            return {
                "column": col_name,
                "outlier_count": outlier_count,
                "outlier_percentage": round(outlier_count / len(series) * 100, 2),
                "contamination": 0.05,
            }
        except Exception:
            return self._iqr_detection(series, col_name)
