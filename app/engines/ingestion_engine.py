"""
DataNova - Ingestion Engine
Handles CSV file loading with automatic encoding/delimiter detection.
"""
import pandas as pd
from pathlib import Path
from app.utils.file_utils import detect_encoding, detect_delimiter, get_file_size_bytes
from app.core.exceptions import InvalidFileError


class IngestionEngine:
    """Handles CSV file ingestion with automatic detection."""

    def ingest(self, file_path: str | Path) -> dict:
        """
        Ingest a CSV file and return the DataFrame with metadata.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise InvalidFileError(f"File not found: {file_path}")

        # Detect encoding
        encoding = detect_encoding(file_path)

        # Detect delimiter
        try:
            delimiter = detect_delimiter(file_path, encoding)
        except Exception:
            delimiter = ","

        # Read CSV
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter,
                low_memory=False,
                on_bad_lines="skip",
            )
        except Exception as e:
            # Fallback attempts
            for enc in ["utf-8", "latin-1", "cp1252"]:
                for delim in [",", ";", "\t", "|"]:
                    try:
                        df = pd.read_csv(
                            file_path,
                            encoding=enc,
                            delimiter=delim,
                            low_memory=False,
                            on_bad_lines="skip",
                        )
                        encoding = enc
                        delimiter = delim
                        break
                    except Exception:
                        continue
                else:
                    continue
                break
            else:
                raise InvalidFileError(f"Unable to parse CSV: {str(e)}")

        # Clean column names
        df.columns = df.columns.str.strip()

        file_size = get_file_size_bytes(file_path)

        return {
            "dataframe": df,
            "filename": file_path.name,
            "encoding": encoding,
            "delimiter": delimiter,
            "rows": len(df),
            "columns": len(df.columns),
            "file_size_bytes": file_size,
        }
