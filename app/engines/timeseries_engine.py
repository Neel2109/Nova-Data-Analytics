"""
DataNova - Time Series Engine
Analyzes date/time columns: trends, growth, moving averages, seasonality.
"""
import pandas as pd
import numpy as np


class TimeSeriesEngine:
    """Analyzes time-series data in the dataset."""

    def analyze(self, df: pd.DataFrame, schema: dict,
                date_column: str | None = None, value_column: str | None = None,
                frequency: str = "monthly") -> dict:
        """Perform time-series analysis."""
        # Auto-detect date column
        date_cols = [c for c, info in schema.items()
                     if info.get("type") == "datetime" and c in df.columns]

        if not date_column and date_cols:
            date_column = date_cols[0]

        if not date_column:
            return {"available": False, "message": "No datetime column detected."}

        # Auto-detect value column (first numerical column)
        num_cols = [c for c, info in schema.items()
                    if info.get("type") == "numerical" and c in df.columns]
        if not value_column and num_cols:
            value_column = num_cols[0]

        if not value_column:
            return {"available": False, "message": "No numerical column available for time-series analysis."}

        try:
            ts_df = df[[date_column, value_column]].copy()
            ts_df[date_column] = pd.to_datetime(ts_df[date_column], errors="coerce", infer_datetime_format=True)
            ts_df = ts_df.dropna()

            if len(ts_df) == 0:
                return {"available": False, "message": "No valid date-value pairs found."}

            ts_df = ts_df.sort_values(date_column)
            ts_df = ts_df.set_index(date_column)
            numeric_series = pd.to_numeric(ts_df[value_column], errors="coerce").dropna()

            if len(numeric_series) == 0:
                return {"available": False, "message": "No valid numerical data for time-series."}

            # Resample based on frequency
            freq_map = {
                "daily": "D", "weekly": "W", "monthly": "MS",
                "quarterly": "QS", "yearly": "YS",
            }
            resample_freq = freq_map.get(frequency, "MS")

            try:
                resampled = numeric_series.resample(resample_freq).agg(["sum", "mean", "count"])
                resampled = resampled[resampled["count"] > 0]
            except Exception:
                resampled = pd.DataFrame()

            # Build trend data
            trend_data = []
            if len(resampled) > 0:
                for date_idx, row in resampled.iterrows():
                    trend_data.append({
                        "date": str(date_idx.date()),
                        "sum": round(float(row["sum"]), 2),
                        "mean": round(float(row["mean"]), 2),
                        "count": int(row["count"]),
                    })

            # Growth rate
            growth_rate = None
            if len(resampled) >= 2:
                first_val = resampled["sum"].iloc[0]
                last_val = resampled["sum"].iloc[-1]
                if first_val != 0:
                    growth_rate = round(((last_val - first_val) / abs(first_val)) * 100, 2)

            # Moving averages
            moving_avg = []
            if len(numeric_series) > 7:
                ma7 = numeric_series.rolling(window=7, min_periods=1).mean()
                for date_idx, val in ma7.items():
                    moving_avg.append({
                        "date": str(date_idx.date()) if hasattr(date_idx, "date") else str(date_idx),
                        "value": round(float(val), 2),
                    })

            # Peak and trough
            peak_idx = resampled["sum"].idxmax() if len(resampled) > 0 else None
            trough_idx = resampled["sum"].idxmin() if len(resampled) > 0 else None

            return {
                "available": True,
                "date_column": date_column,
                "value_column": value_column,
                "frequency": frequency,
                "date_columns": date_cols,
                "numerical_columns": num_cols,
                "start_date": str(numeric_series.index.min().date()) if len(numeric_series) > 0 else None,
                "end_date": str(numeric_series.index.max().date()) if len(numeric_series) > 0 else None,
                "total_periods": len(resampled),
                "growth_rate": growth_rate,
                "peak_date": str(peak_idx.date()) if peak_idx is not None else None,
                "peak_value": round(float(resampled["sum"].max()), 2) if len(resampled) > 0 else None,
                "trough_date": str(trough_idx.date()) if trough_idx is not None else None,
                "trough_value": round(float(resampled["sum"].min()), 2) if len(resampled) > 0 else None,
                "trend_data": trend_data[:500],
                "moving_average": moving_avg[:500] if len(moving_avg) <= 500 else moving_avg[::max(1, len(moving_avg) // 500)],
            }
        except Exception as e:
            return {"available": False, "message": f"Time-series analysis error: {str(e)}"}
