"""
DataNova - Pydantic Schemas for API request/response models
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────

class ColumnType(str, Enum):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    TEXT = "text"
    IDENTIFIER = "identifier"


class ColumnSubtype(str, Enum):
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    DATETIME_FULL = "datetime"
    BINARY = "binary"
    ORDINAL = "ordinal"
    NOMINAL = "nominal"


class MissingStrategy(str, Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    CONSTANT = "constant"
    DROP = "drop"


class DuplicateStrategy(str, Enum):
    REMOVE = "remove"
    KEEP = "keep"


class OutlierStrategy(str, Enum):
    KEEP = "keep"
    REMOVE = "remove"
    CAP = "cap"
    WINSORIZE = "winsorize"


class CorrelationMethod(str, Enum):
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"


class OutlierMethod(str, Enum):
    IQR = "iqr"
    ZSCORE = "zscore"
    ISOLATION_FOREST = "isolation_forest"


class MLTaskType(str, Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"


class HypothesisTestType(str, Enum):
    TTEST = "ttest"
    ANOVA = "anova"
    MANN_WHITNEY = "mann_whitney"
    KRUSKAL_WALLIS = "kruskal_wallis"
    CHI_SQUARE = "chi_square"
    NORMALITY = "normality"
    CORRELATION = "correlation_test"


class InsightType(str, Enum):
    DATA_QUALITY = "data_quality"
    TREND = "trend"
    CORRELATION = "correlation"
    OUTLIER = "outlier"
    DISTRIBUTION = "distribution"
    CATEGORY = "category"
    TIME_SERIES = "time_series"
    STATISTICAL = "statistical"
    ML = "ml"


class InsightSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"


# ── Request Models ─────────────────────────────────────────────

class CleaningRequest(BaseModel):
    missing_strategy: MissingStrategy = MissingStrategy.MEDIAN
    missing_constant_value: Optional[str] = None
    duplicate_strategy: DuplicateStrategy = DuplicateStrategy.REMOVE
    outlier_strategy: OutlierStrategy = OutlierStrategy.KEEP
    standardize_text: bool = True
    convert_types: bool = True


class CorrelationRequest(BaseModel):
    method: CorrelationMethod = CorrelationMethod.PEARSON
    threshold: float = 0.3


class OutlierRequest(BaseModel):
    method: OutlierMethod = OutlierMethod.IQR
    columns: Optional[list[str]] = None


class HypothesisRequest(BaseModel):
    test_type: HypothesisTestType
    numerical_column: Optional[str] = None
    grouping_column: Optional[str] = None
    column_a: Optional[str] = None
    column_b: Optional[str] = None


class MLRequest(BaseModel):
    task_type: MLTaskType
    target_column: Optional[str] = None
    feature_columns: Optional[list[str]] = None
    model_name: Optional[str] = None
    test_size: float = 0.2
    n_clusters: int = 3


class QueryRequest(BaseModel):
    question: str


class ReportRequest(BaseModel):
    report_name: str = "DataNova Analysis Report"
    sections: list[str] = Field(default_factory=lambda: [
        "overview", "quality", "statistics", "correlations",
        "outliers", "categorical", "insights"
    ])


# ── Response Models ────────────────────────────────────────────

class DatasetInfo(BaseModel):
    id: str
    filename: str
    rows: int
    columns: int
    file_size_bytes: int
    encoding: str
    delimiter: str
    numerical_columns: int
    categorical_columns: int
    datetime_columns: int
    boolean_columns: int
    missing_cells: int
    missing_percentage: float
    duplicate_rows: int
    memory_usage_mb: float
    quality_score: float


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    column_type: str
    subtype: Optional[str] = None
    count: int
    missing: int
    missing_percentage: float
    unique: int
    # Numerical stats
    mean: Optional[float] = None
    median: Optional[float] = None
    mode: Optional[Any] = None
    std: Optional[float] = None
    variance: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    range_val: Optional[float] = None
    q1: Optional[float] = None
    q2: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    zero_count: Optional[int] = None
    negative_count: Optional[int] = None
    outlier_count: Optional[int] = None
    # Categorical stats
    top_categories: Optional[dict] = None
    # Date stats
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    date_range_days: Optional[int] = None


class Insight(BaseModel):
    type: str
    severity: str
    title: str
    message: str
    column: Optional[str] = None
    columns: Optional[list[str]] = None
    evidence: Optional[dict] = None


class CleaningResult(BaseModel):
    original_rows: int
    cleaned_rows: int
    original_missing: int
    cleaned_missing: int
    original_duplicates: int
    cleaned_duplicates: int
    operations_log: list[str]


class CorrelationResult(BaseModel):
    matrix: dict
    strong_positive: list[dict]
    strong_negative: list[dict]
    method: str


class OutlierResult(BaseModel):
    method: str
    summary: list[dict]
    total_outliers: int


class HypothesisResult(BaseModel):
    test_name: str
    statistic: float
    p_value: float
    interpretation: str
    details: Optional[dict] = None


class MLResult(BaseModel):
    task_type: str
    model_name: str
    metrics: dict
    feature_importance: Optional[list[dict]] = None
    confusion_matrix: Optional[list[list[int]]] = None
    predictions_sample: Optional[list] = None
    cluster_labels: Optional[list[int]] = None
    cluster_centers: Optional[list[list[float]]] = None


class QueryResult(BaseModel):
    question: str
    answer: str
    chart: Optional[dict] = None
    data: Optional[dict] = None


class APIResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None
