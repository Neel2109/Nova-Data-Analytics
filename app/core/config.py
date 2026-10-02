"""
DataNova - Core Configuration
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Upload/output directories
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File limits
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported encodings
SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "utf-16", "latin-1", "cp1252", "ascii"]

# Supported delimiters
SUPPORTED_DELIMITERS = [",", ";", "\t", "|"]

# Correlation thresholds
STRONG_CORRELATION_THRESHOLD = 0.7
MODERATE_CORRELATION_THRESHOLD = 0.4

# Outlier detection
IQR_MULTIPLIER = 1.5
ZSCORE_THRESHOLD = 3.0

# ML defaults
ML_TEST_SIZE = 0.2
ML_RANDOM_STATE = 42
ML_MAX_CATEGORIES_FOR_ENCODING = 50

# Categorical detection
MAX_UNIQUE_RATIO_FOR_CATEGORICAL = 0.05
MAX_UNIQUE_COUNT_FOR_CATEGORICAL = 50

# Date detection patterns
DATE_PATTERNS = [
    "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",
    "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",
    "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S",
    "%Y/%m/%d %H:%M:%S", "%m/%d/%Y %H:%M:%S",
    "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y",
]

# Target column name hints (for auto-detection)
TARGET_HINTS = [
    "target", "label", "class", "outcome", "result",
    "sales", "revenue", "price", "profit", "amount",
    "score", "rating", "status", "churn", "default",
    "survived", "diagnosis", "category",
]

# API settings
API_PREFIX = "/api"
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
