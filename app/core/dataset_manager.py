"""
DataNova - Dataset Manager
Central manager that holds loaded datasets and provides engine access.
"""
import pandas as pd
from pathlib import Path
from app.engines.ingestion_engine import IngestionEngine
from app.engines.profiling_engine import ProfilingEngine
from app.engines.cleaning_engine import CleaningEngine
from app.engines.statistics_engine import StatisticsEngine
from app.engines.correlation_engine import CorrelationEngine
from app.engines.outlier_engine import OutlierEngine
from app.engines.categorical_engine import CategoricalEngine
from app.engines.timeseries_engine import TimeSeriesEngine
from app.engines.hypothesis_engine import HypothesisEngine
from app.engines.ml_engine import MLEngine
from app.engines.insight_engine import InsightEngine
from app.engines.chart_engine import ChartEngine
from app.utils.type_detection import detect_all_column_types


class DatasetStore:
    """In-memory store for loaded datasets."""

    def __init__(self):
        self.datasets: dict[str, dict] = {}
        self.ingestion = IngestionEngine()
        self.profiler = ProfilingEngine()
        self.cleaner = CleaningEngine()
        self.statistics = StatisticsEngine()
        self.correlation = CorrelationEngine()
        self.outlier = OutlierEngine()
        self.categorical = CategoricalEngine()
        self.timeseries = TimeSeriesEngine()
        self.hypothesis = HypothesisEngine()
        self.ml = MLEngine()
        self.insight = InsightEngine()
        self.charts = ChartEngine()

    def load_dataset(self, dataset_id: str, file_path: Path) -> dict:
        """Load a CSV file into the store."""
        result = self.ingestion.ingest(file_path)
        df = result["dataframe"]
        schema = detect_all_column_types(df)
        profile = self.profiler.profile_dataset(df, schema)

        self.datasets[dataset_id] = {
            "id": dataset_id,
            "filename": result["filename"],
            "file_path": str(file_path),
            "encoding": result["encoding"],
            "delimiter": result["delimiter"],
            "file_size_bytes": result["file_size_bytes"],
            "dataframe": df,
            "original_dataframe": df.copy(),
            "schema": schema,
            "profile": profile,
        }
        return self.datasets[dataset_id]

    def get_dataset(self, dataset_id: str) -> dict | None:
        """Get a loaded dataset by ID."""
        return self.datasets.get(dataset_id)

    def get_df(self, dataset_id: str) -> pd.DataFrame | None:
        """Get the DataFrame for a dataset."""
        ds = self.datasets.get(dataset_id)
        return ds["dataframe"] if ds else None

    def get_schema(self, dataset_id: str) -> dict | None:
        """Get the schema for a dataset."""
        ds = self.datasets.get(dataset_id)
        return ds["schema"] if ds else None

    def get_profile(self, dataset_id: str) -> dict | None:
        """Get the profile for a dataset."""
        ds = self.datasets.get(dataset_id)
        return ds["profile"] if ds else None

    def update_dataframe(self, dataset_id: str, df: pd.DataFrame):
        """Update the working DataFrame (e.g., after cleaning)."""
        ds = self.datasets.get(dataset_id)
        if ds:
            ds["dataframe"] = df
            ds["schema"] = detect_all_column_types(df)
            ds["profile"] = self.profiler.profile_dataset(df, ds["schema"])

    def delete_dataset(self, dataset_id: str):
        """Remove a dataset from the store."""
        self.datasets.pop(dataset_id, None)

    def list_datasets(self) -> list[dict]:
        """List all loaded datasets."""
        result = []
        for ds_id, ds in self.datasets.items():
            result.append({
                "id": ds_id,
                "filename": ds["filename"],
                "rows": ds["profile"]["rows"],
                "columns": ds["profile"]["columns"],
                "quality_score": ds["profile"]["quality_score"],
            })
        return result


# Global store instance
store = DatasetStore()
