"""
DataNova - File Utilities
Handles file operations, encoding detection, and path management.
"""
import os
import uuid
import chardet
from pathlib import Path
from app.core.config import UPLOAD_DIR, OUTPUT_DIR, SUPPORTED_ENCODINGS


def generate_dataset_id() -> str:
    """Generate a unique dataset identifier."""
    return str(uuid.uuid4())[:8]


def get_upload_path(dataset_id: str, filename: str) -> Path:
    """Get the full upload path for a dataset file."""
    dataset_dir = UPLOAD_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)
    return dataset_dir / filename


def get_output_path(dataset_id: str, filename: str) -> Path:
    """Get the full output path for a generated file."""
    dataset_dir = OUTPUT_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)
    return dataset_dir / filename


def detect_encoding(file_path: str | Path) -> str:
    """Detect the encoding of a file using chardet."""
    with open(file_path, "rb") as f:
        raw_data = f.read(100000)  # Read first 100KB
    result = chardet.detect(raw_data)
    detected = result.get("encoding", "utf-8")
    confidence = result.get("confidence", 0)

    if detected and confidence > 0.5:
        # Normalize encoding name
        detected = detected.lower().replace("-", "").replace("_", "")
        for enc in SUPPORTED_ENCODINGS:
            if enc.replace("-", "").replace("_", "") == detected:
                return enc
        return detected
    return "utf-8"


def detect_delimiter(file_path: str | Path, encoding: str = "utf-8") -> str:
    """Detect the delimiter of a CSV file."""
    import csv
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        sample = f.read(8192)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ","


def get_file_size_bytes(file_path: str | Path) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """Format file size for display."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def cleanup_dataset(dataset_id: str):
    """Remove all files for a dataset."""
    import shutil
    upload_dir = UPLOAD_DIR / dataset_id
    output_dir = OUTPUT_DIR / dataset_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
