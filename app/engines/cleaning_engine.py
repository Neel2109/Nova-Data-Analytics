"""
DataNova - Cleaning Engine
Provides configurable data cleaning operations with a detailed log.
"""
import pandas as pd
import numpy as np
from app.core.config import IQR_MULTIPLIER, ZSCORE_THRESHOLD


class CleaningEngine:
    """Handles all data cleaning operations with tracking."""

    def clean(self, df: pd.DataFrame, schema: dict, options: dict) -> dict:
        """
        Clean the dataset according to the provided options.
        Returns cleaned DataFrame and an operations log.
        """
        original_rows = len(df)
        original_missing = int(df.isnull().sum().sum())
        original_duplicates = int(df.duplicated().sum())
        log = []
        cleaned = df.copy()

        # 1. Handle duplicates
        dup_strategy = options.get("duplicate_strategy", "remove")
        if dup_strategy == "remove":
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates()
            removed = before - len(cleaned)
            if removed > 0:
                log.append(f"{removed} duplicate rows removed")

        # 2. Handle missing values
        missing_strategy = options.get("missing_strategy", "median")
        constant_val = options.get("missing_constant_value", "Unknown")
        numerical_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in cleaned.columns]
        categorical_cols = [c for c, info in schema.items() if info.get("type") in ("categorical", "boolean") and c in cleaned.columns]

        if missing_strategy == "drop":
            before = len(cleaned)
            cleaned = cleaned.dropna()
            dropped = before - len(cleaned)
            if dropped > 0:
                log.append(f"{dropped} rows with missing values removed")
        elif missing_strategy == "mean":
            for col in numerical_cols:
                count = int(cleaned[col].isnull().sum())
                if count > 0:
                    cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
                    cleaned[col] = cleaned[col].fillna(cleaned[col].mean())
                    log.append(f"{count} missing values in '{col}' filled with mean")
            for col in categorical_cols:
                count = int(cleaned[col].isnull().sum())
                if count > 0:
                    mode_val = cleaned[col].mode()
                    fill_val = mode_val.iloc[0] if len(mode_val) > 0 else constant_val
                    cleaned[col] = cleaned[col].fillna(fill_val)
                    log.append(f"{count} missing values in '{col}' filled with mode")
        elif missing_strategy == "median":
            for col in numerical_cols:
                count = int(cleaned[col].isnull().sum())
                if count > 0:
                    cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
                    cleaned[col] = cleaned[col].fillna(cleaned[col].median())
                    log.append(f"{count} missing values in '{col}' filled with median")
            for col in categorical_cols:
                count = int(cleaned[col].isnull().sum())
                if count > 0:
                    mode_val = cleaned[col].mode()
                    fill_val = mode_val.iloc[0] if len(mode_val) > 0 else constant_val
                    cleaned[col] = cleaned[col].fillna(fill_val)
                    log.append(f"{count} missing values in '{col}' filled with mode")
        elif missing_strategy == "mode":
            for col in cleaned.columns:
                count = int(cleaned[col].isnull().sum())
                if count > 0:
                    mode_val = cleaned[col].mode()
                    if len(mode_val) > 0:
                        cleaned[col] = cleaned[col].fillna(mode_val.iloc[0])
                        log.append(f"{count} missing values in '{col}' filled with mode")
        elif missing_strategy == "forward_fill":
            filled = int(cleaned.isnull().sum().sum())
            cleaned = cleaned.ffill()
            filled -= int(cleaned.isnull().sum().sum())
            if filled > 0:
                log.append(f"{filled} missing values forward-filled")
        elif missing_strategy == "backward_fill":
            filled = int(cleaned.isnull().sum().sum())
            cleaned = cleaned.bfill()
            filled -= int(cleaned.isnull().sum().sum())
            if filled > 0:
                log.append(f"{filled} missing values backward-filled")
        elif missing_strategy == "constant":
            for col in numerical_cols:
                count = int(cleaned[col].isnull().sum())
                if count > 0:
                    cleaned[col] = cleaned[col].fillna(0)
                    log.append(f"{count} missing values in '{col}' filled with 0")
            for col in categorical_cols:
                count = int(cleaned[col].isnull().sum())
                if count > 0:
                    cleaned[col] = cleaned[col].fillna(constant_val)
                    log.append(f"{count} missing values in '{col}' filled with '{constant_val}'")

        # 3. Handle outliers
        outlier_strategy = options.get("outlier_strategy", "keep")
        if outlier_strategy != "keep":
            for col in numerical_cols:
                try:
                    numeric_col = pd.to_numeric(cleaned[col], errors="coerce")
                    q1 = numeric_col.quantile(0.25)
                    q3 = numeric_col.quantile(0.75)
                    iqr = q3 - q1
                    lower = q1 - IQR_MULTIPLIER * iqr
                    upper = q3 + IQR_MULTIPLIER * iqr
                    outlier_mask = (numeric_col < lower) | (numeric_col > upper)
                    outlier_count = int(outlier_mask.sum())

                    if outlier_count > 0:
                        if outlier_strategy == "remove":
                            cleaned = cleaned[~outlier_mask]
                            log.append(f"{outlier_count} outliers removed from '{col}'")
                        elif outlier_strategy == "cap":
                            cleaned.loc[numeric_col < lower, col] = lower
                            cleaned.loc[numeric_col > upper, col] = upper
                            log.append(f"{outlier_count} outliers capped in '{col}'")
                        elif outlier_strategy == "winsorize":
                            p5 = numeric_col.quantile(0.05)
                            p95 = numeric_col.quantile(0.95)
                            cleaned.loc[numeric_col < p5, col] = p5
                            cleaned.loc[numeric_col > p95, col] = p95
                            log.append(f"Winsorized extremes in '{col}'")
                except Exception:
                    continue

        # 4. Standardize text (if enabled)
        standardize = options.get("standardize_text", True)
        if standardize:
            for col in categorical_cols:
                try:
                    if cleaned[col].dtype == object:
                        before_unique = cleaned[col].nunique()
                        cleaned[col] = cleaned[col].astype(str).str.strip().str.title()
                        after_unique = cleaned[col].nunique()
                        if before_unique != after_unique:
                            log.append(f"Standardized text in '{col}' ({before_unique} → {after_unique} unique values)")
                except Exception:
                    continue

        # 5. Convert types (if enabled)
        convert = options.get("convert_types", True)
        if convert:
            datetime_cols = [c for c, info in schema.items() if info.get("type") == "datetime" and c in cleaned.columns]
            for col in datetime_cols:
                try:
                    cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce", infer_datetime_format=True)
                    log.append(f"Converted '{col}' to datetime")
                except Exception:
                    pass
            for col in numerical_cols:
                try:
                    cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
                except Exception:
                    pass

        cleaned = cleaned.reset_index(drop=True)

        return {
            "dataframe": cleaned,
            "original_rows": original_rows,
            "cleaned_rows": len(cleaned),
            "original_missing": original_missing,
            "cleaned_missing": int(cleaned.isnull().sum().sum()),
            "original_duplicates": original_duplicates,
            "cleaned_duplicates": int(cleaned.duplicated().sum()),
            "operations_log": log,
        }
