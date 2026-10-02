"""
DataNova - FastAPI Main Application
Universal CSV Data Intelligence Platform API.
"""
import os
import json
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd

from app.core.config import CORS_ORIGINS, UPLOAD_DIR, OUTPUT_DIR, API_PREFIX
from app.core.dataset_manager import store
from app.utils.file_utils import generate_dataset_id, get_upload_path, get_output_path

# ── App Setup ──────────────────────────────────────────────────

app = FastAPI(
    title="DataNova API",
    description="Universal CSV Data Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_dataset_or_404(dataset_id: str):
    """Helper to get dataset or raise 404."""
    ds = store.get_dataset(dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found. Upload a dataset first.")
    return ds


# ── Upload ─────────────────────────────────────────────────────

@app.post(f"{API_PREFIX}/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV file and automatically profile it."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    dataset_id = generate_dataset_id()
    file_path = get_upload_path(dataset_id, file.filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        ds = store.load_dataset(dataset_id, file_path)
        profile = ds["profile"]

        return {
            "success": True,
            "dataset_id": dataset_id,
            "filename": ds["filename"],
            "rows": profile["rows"],
            "columns": profile["columns"],
            "encoding": ds["encoding"],
            "delimiter": ds["delimiter"],
            "numerical_columns": profile["numerical_columns"],
            "categorical_columns": profile["categorical_columns"],
            "datetime_columns": profile["datetime_columns"],
            "boolean_columns": profile["boolean_columns"],
            "missing_cells": profile["missing_cells"],
            "missing_percentage": profile["missing_percentage"],
            "duplicate_rows": profile["duplicate_rows"],
            "duplicate_percentage": profile["duplicate_percentage"],
            "memory_usage_mb": profile["memory_usage_mb"],
            "quality_score": profile["quality_score"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


# ── Dataset Info ───────────────────────────────────────────────

@app.get(f"{API_PREFIX}/datasets")
async def list_datasets():
    """List all loaded datasets."""
    return {"datasets": store.list_datasets()}


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}")
async def get_dataset_info(dataset_id: str):
    """Get dataset overview."""
    ds = get_dataset_or_404(dataset_id)
    profile = ds["profile"]
    return {
        "id": dataset_id,
        "filename": ds["filename"],
        "encoding": ds["encoding"],
        "delimiter": ds["delimiter"],
        "file_size_bytes": ds["file_size_bytes"],
        **profile,
    }


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/preview")
async def get_dataset_preview(dataset_id: str, head: int = 50):
    """Get a preview of the dataset (first N rows)."""
    ds = get_dataset_or_404(dataset_id)
    df = ds["dataframe"]
    preview = df.head(min(head, 200))
    return {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "data": json.loads(preview.to_json(orient="records", default_handler=str)),
        "total_rows": len(df),
        "showing": len(preview),
    }


@app.delete(f"{API_PREFIX}/dataset/{{dataset_id}}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset from memory."""
    store.delete_dataset(dataset_id)
    return {"success": True, "message": f"Dataset '{dataset_id}' deleted."}


# ── Profile ────────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/profile")
async def get_profile(dataset_id: str):
    """Get full data profiling results."""
    ds = get_dataset_or_404(dataset_id)
    return ds["profile"]


# ── Data Quality ───────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/quality")
async def get_quality(dataset_id: str):
    """Get data quality report."""
    ds = get_dataset_or_404(dataset_id)
    profile = ds["profile"]
    df = ds["dataframe"]

    # Per-column missing
    missing_by_column = []
    for col in df.columns:
        missing_count = int(df[col].isnull().sum())
        if missing_count > 0:
            missing_by_column.append({
                "column": col,
                "missing_count": missing_count,
                "missing_percentage": round(missing_count / len(df) * 100, 2),
            })
    missing_by_column.sort(key=lambda x: x["missing_count"], reverse=True)

    # Missing values chart
    missing_chart = store.charts.missing_values_chart(df)

    return {
        "quality_score": profile["quality_score"],
        "completeness": round((1 - profile["missing_percentage"] / 100) * 100, 1),
        "uniqueness": round((1 - profile["duplicate_percentage"] / 100) * 100, 1),
        "total_cells": profile["rows"] * profile["columns"],
        "missing_cells": profile["missing_cells"],
        "missing_percentage": profile["missing_percentage"],
        "duplicate_rows": profile["duplicate_rows"],
        "duplicate_percentage": profile["duplicate_percentage"],
        "missing_by_column": missing_by_column,
        "missing_chart": missing_chart,
    }


# ── Cleaning ───────────────────────────────────────────────────

@app.post(f"{API_PREFIX}/dataset/{{dataset_id}}/clean")
async def clean_dataset(dataset_id: str, options: dict = None):
    """Clean the dataset with specified options."""
    ds = get_dataset_or_404(dataset_id)
    if options is None:
        options = {
            "missing_strategy": "median",
            "duplicate_strategy": "remove",
            "outlier_strategy": "keep",
            "standardize_text": True,
            "convert_types": True,
        }

    result = store.cleaner.clean(ds["dataframe"], ds["schema"], options)
    store.update_dataframe(dataset_id, result["dataframe"])

    return {
        "success": True,
        "original_rows": result["original_rows"],
        "cleaned_rows": result["cleaned_rows"],
        "original_missing": result["original_missing"],
        "cleaned_missing": result["cleaned_missing"],
        "original_duplicates": result["original_duplicates"],
        "cleaned_duplicates": result["cleaned_duplicates"],
        "operations_log": result["operations_log"],
    }


@app.post(f"{API_PREFIX}/dataset/{{dataset_id}}/reset")
async def reset_dataset(dataset_id: str):
    """Reset dataset to original (before cleaning)."""
    ds = get_dataset_or_404(dataset_id)
    store.update_dataframe(dataset_id, ds["original_dataframe"].copy())
    return {"success": True, "message": "Dataset reset to original."}


# ── Statistics ─────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/statistics")
async def get_statistics(dataset_id: str):
    """Get descriptive statistics."""
    ds = get_dataset_or_404(dataset_id)
    return store.statistics.compute(ds["dataframe"], ds["schema"])


# ── Distributions ──────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/distributions")
async def get_distributions(dataset_id: str, column: str = None):
    """Get distribution charts."""
    ds = get_dataset_or_404(dataset_id)
    schema = ds["schema"]
    df = ds["dataframe"]

    if column:
        chart = store.charts.histogram(df, column)
        box = store.charts.box_plot(df, column)
        return {"column": column, "histogram": chart, "box_plot": box}

    # Auto-generate for all numerical columns
    num_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in df.columns]
    distributions = []
    for col in num_cols[:10]:
        hist = store.charts.histogram(df, col)
        if hist:
            distributions.append({"column": col, "chart": hist})

    return {"distributions": distributions, "columns": num_cols}


# ── Correlations ───────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/correlations")
async def get_correlations(dataset_id: str, method: str = "pearson"):
    """Get correlation analysis."""
    ds = get_dataset_or_404(dataset_id)
    result = store.correlation.compute(ds["dataframe"], ds["schema"], method=method)

    # Generate heatmap chart
    if result.get("matrix"):
        result["heatmap_chart"] = store.charts.heatmap(result["matrix"], f"Correlation Matrix ({method.title()})")

    # Generate scatter plots for strong relationships
    scatter_plots = []
    for rel in (result.get("strong_positive", []) + result.get("strong_negative", []))[:5]:
        scatter = store.charts.scatter(ds["dataframe"], rel["column_a"], rel["column_b"])
        if scatter:
            scatter_plots.append({
                "columns": [rel["column_a"], rel["column_b"]],
                "correlation": rel["correlation"],
                "chart": scatter,
            })
    result["scatter_plots"] = scatter_plots

    return result


# ── Outliers ───────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/outliers")
async def get_outliers(dataset_id: str, method: str = "iqr"):
    """Get outlier analysis."""
    ds = get_dataset_or_404(dataset_id)
    result = store.outlier.detect(ds["dataframe"], ds["schema"], method=method)

    # Generate box plots for columns with outliers
    box_plots = []
    for item in result.get("summary", [])[:5]:
        if item.get("outlier_count", 0) > 0:
            chart = store.charts.box_plot(ds["dataframe"], item["column"])
            if chart:
                box_plots.append({"column": item["column"], "chart": chart})
    result["box_plots"] = box_plots

    return result


# ── Categorical ────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/categorical")
async def get_categorical(dataset_id: str):
    """Get categorical analysis."""
    ds = get_dataset_or_404(dataset_id)
    result = store.categorical.analyze(ds["dataframe"], ds["schema"])

    # Generate charts for each categorical column
    for col_data in result.get("columns", [])[:10]:
        col_name = col_data["column"]
        bar = store.charts.bar_chart(ds["dataframe"], col_name)
        pie = store.charts.pie_chart(ds["dataframe"], col_name)
        col_data["bar_chart"] = bar
        col_data["pie_chart"] = pie

    # Group-by analysis
    result["group_analysis"] = store.categorical.get_group_analysis(ds["dataframe"], ds["schema"])[:10]

    return result


# ── Time Series ────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/timeseries")
async def get_timeseries(dataset_id: str, date_column: str = None,
                         value_column: str = None, frequency: str = "monthly"):
    """Get time-series analysis."""
    ds = get_dataset_or_404(dataset_id)
    result = store.timeseries.analyze(
        ds["dataframe"], ds["schema"],
        date_column=date_column, value_column=value_column, frequency=frequency
    )

    # Generate trend chart
    if result.get("available") and result.get("trend_data"):
        dates = [d["date"] for d in result["trend_data"]]
        values = [d["sum"] for d in result["trend_data"]]
        result["trend_chart"] = store.charts.line_chart(
            dates, values,
            title=f"{result.get('value_column', '')} Trend ({frequency.title()})",
            x_label="Date", y_label=result.get("value_column", "Value")
        )

    return result


# ── Hypothesis Testing ─────────────────────────────────────────

@app.post(f"{API_PREFIX}/dataset/{{dataset_id}}/hypothesis")
async def run_hypothesis_test(dataset_id: str, request: dict):
    """Run a statistical hypothesis test."""
    ds = get_dataset_or_404(dataset_id)
    result = store.hypothesis.run_test(
        ds["dataframe"], ds["schema"],
        test_type=request.get("test_type", "normality"),
        numerical_column=request.get("numerical_column"),
        grouping_column=request.get("grouping_column"),
        column_a=request.get("column_a"),
        column_b=request.get("column_b"),
    )
    return result


# ── Machine Learning ───────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/ml/targets")
async def suggest_ml_targets(dataset_id: str):
    """Suggest potential ML target columns."""
    ds = get_dataset_or_404(dataset_id)
    return {"targets": store.ml.suggest_targets(ds["dataframe"], ds["schema"])}


@app.post(f"{API_PREFIX}/dataset/{{dataset_id}}/ml/regression")
async def run_regression(dataset_id: str, request: dict):
    """Run a regression model."""
    ds = get_dataset_or_404(dataset_id)
    try:
        result = store.ml.run_regression(
            ds["dataframe"], ds["schema"],
            target_column=request["target_column"],
            feature_columns=request.get("feature_columns"),
            model_name=request.get("model_name", "random_forest"),
            test_size=request.get("test_size", 0.2),
        )
        # Add charts
        if result.get("feature_importance"):
            result["importance_chart"] = store.charts.feature_importance_chart(result["feature_importance"])
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(f"{API_PREFIX}/dataset/{{dataset_id}}/ml/classification")
async def run_classification(dataset_id: str, request: dict):
    """Run a classification model."""
    ds = get_dataset_or_404(dataset_id)
    try:
        result = store.ml.run_classification(
            ds["dataframe"], ds["schema"],
            target_column=request["target_column"],
            feature_columns=request.get("feature_columns"),
            model_name=request.get("model_name", "random_forest"),
            test_size=request.get("test_size", 0.2),
        )
        if result.get("feature_importance"):
            result["importance_chart"] = store.charts.feature_importance_chart(result["feature_importance"])
        if result.get("confusion_matrix"):
            result["cm_chart"] = store.charts.confusion_matrix_chart(
                result["confusion_matrix"], result.get("classes")
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(f"{API_PREFIX}/dataset/{{dataset_id}}/ml/clustering")
async def run_clustering(dataset_id: str, request: dict):
    """Run a clustering model."""
    ds = get_dataset_or_404(dataset_id)
    try:
        result = store.ml.run_clustering(
            ds["dataframe"], ds["schema"],
            feature_columns=request.get("feature_columns"),
            n_clusters=request.get("n_clusters", 3),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Insights ───────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/insights")
async def get_insights(dataset_id: str):
    """Get automatic insights."""
    ds = get_dataset_or_404(dataset_id)
    insights = store.insight.generate(ds["dataframe"], ds["schema"], ds["profile"])
    return {"insights": insights, "count": len(insights)}


# ── Natural Language Query ─────────────────────────────────────

@app.post(f"{API_PREFIX}/dataset/{{dataset_id}}/query")
async def query_dataset(dataset_id: str, request: dict):
    """Process a natural language query about the dataset."""
    ds = get_dataset_or_404(dataset_id)
    question = request.get("question", "").lower().strip()
    df = ds["dataframe"]
    schema = ds["schema"]

    if not question:
        raise HTTPException(status_code=400, detail="Please provide a question.")

    num_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in df.columns]
    cat_cols = [c for c, info in schema.items() if info.get("type") == "categorical" and c in df.columns]

    answer = ""
    chart = None
    data = None

    # Pattern matching for common queries
    if any(w in question for w in ["missing", "null", "empty", "incomplete"]):
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        answer = f"Found {int(missing.sum())} missing values across {len(missing)} columns."
        if len(missing) > 0:
            data = {col: int(count) for col, count in missing.items()}
            chart = store.charts.missing_values_chart(df)

    elif any(w in question for w in ["correlat", "relationship", "associated"]):
        if len(num_cols) >= 2:
            corr_result = store.correlation.compute(df, schema)
            strong = corr_result.get("strong_positive", []) + corr_result.get("strong_negative", [])
            if strong:
                top = strong[0]
                answer = f"The strongest correlation is between '{top['column_a']}' and '{top['column_b']}' (r = {top['correlation']})."
                data = {"relationships": strong[:5]}
                chart = store.charts.heatmap(corr_result["matrix"])
            else:
                answer = "No strong correlations found in the numerical columns."
        else:
            answer = "Need at least 2 numerical columns for correlation analysis."

    elif any(w in question for w in ["outlier", "unusual", "anomal", "extreme"]):
        outlier_result = store.outlier.detect(df, schema)
        total = outlier_result.get("total_outliers", 0)
        answer = f"Detected {total} potential outliers across {len(outlier_result.get('summary', []))} columns."
        data = outlier_result.get("summary", [])[:10]

    elif any(w in question for w in ["highest", "top", "maximum", "most", "best", "largest"]):
        # Try to find the relevant column
        target_col = None
        for col in num_cols:
            if col.lower() in question:
                target_col = col
                break
        if not target_col and num_cols:
            target_col = num_cols[0]

        if target_col:
            if cat_cols:
                group_col = cat_cols[0]
                for col in cat_cols:
                    if col.lower() in question:
                        group_col = col
                        break
                grouped = pd.to_numeric(df[target_col], errors="coerce").groupby(df[group_col]).sum().sort_values(ascending=False)
                top_val = grouped.index[0] if len(grouped) > 0 else "N/A"
                top_amount = round(float(grouped.iloc[0]), 2) if len(grouped) > 0 else 0
                answer = f"'{top_val}' has the highest {target_col} with a total of {top_amount:,.2f}."
                chart = store.charts.bar_chart(df, group_col, target_col, agg="sum")
                data = {str(k): round(float(v), 2) for k, v in grouped.head(10).items()}
            else:
                max_val = round(float(pd.to_numeric(df[target_col], errors="coerce").max()), 2)
                answer = f"The maximum value in '{target_col}' is {max_val:,.2f}."
        else:
            answer = "No numerical columns found to analyze."

    elif any(w in question for w in ["trend", "time", "over time", "monthly", "daily"]):
        date_cols = [c for c, info in schema.items() if info.get("type") == "datetime" and c in df.columns]
        if date_cols and num_cols:
            ts_result = store.timeseries.analyze(df, schema)
            if ts_result.get("available"):
                growth = ts_result.get("growth_rate")
                answer = f"Time-series analysis available. "
                if growth is not None:
                    answer += f"Growth rate: {growth:+.1f}%."
                if ts_result.get("trend_data"):
                    dates = [d["date"] for d in ts_result["trend_data"]]
                    values = [d["sum"] for d in ts_result["trend_data"]]
                    chart = store.charts.line_chart(dates, values, "Trend Analysis")
            else:
                answer = ts_result.get("message", "Time-series analysis not available.")
        else:
            answer = "No datetime columns found for time-series analysis."

    elif any(w in question for w in ["distribut", "histogram", "spread"]):
        if num_cols:
            col = num_cols[0]
            for c in num_cols:
                if c.lower() in question:
                    col = c
                    break
            chart = store.charts.histogram(df, col)
            stats = pd.to_numeric(df[col], errors="coerce").describe()
            answer = f"Distribution of '{col}': Mean = {stats['mean']:.2f}, Median = {stats['50%']:.2f}, Std = {stats['std']:.2f}."
        else:
            answer = "No numerical columns found."

    elif any(w in question for w in ["categor", "frequency", "count", "breakdown"]):
        if cat_cols:
            col = cat_cols[0]
            for c in cat_cols:
                if c.lower() in question:
                    col = c
                    break
            counts = df[col].value_counts().head(10)
            answer = f"Top categories in '{col}': " + ", ".join(
                [f"{k} ({v})" for k, v in counts.items()]
            )
            chart = store.charts.bar_chart(df, col)
            data = {str(k): int(v) for k, v in counts.items()}
        else:
            answer = "No categorical columns found."

    elif any(w in question for w in ["summary", "overview", "describe", "info"]):
        profile = ds["profile"]
        answer = (
            f"Dataset: {ds['filename']} | "
            f"{profile['rows']:,} rows × {profile['columns']} columns | "
            f"Quality: {profile['quality_score']}% | "
            f"Missing: {profile['missing_percentage']}% | "
            f"Duplicates: {profile['duplicate_rows']}"
        )

    else:
        answer = (
            "I understood your question but couldn't match it to a specific analysis. "
            "Try asking about: missing values, correlations, outliers, top categories, "
            "trends, distributions, or a summary of the dataset."
        )

    return {
        "question": request.get("question", ""),
        "answer": answer,
        "chart": chart,
        "data": data,
    }


# ── Charts ─────────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/charts")
async def get_auto_charts(dataset_id: str):
    """Get automatically recommended charts."""
    ds = get_dataset_or_404(dataset_id)
    charts = store.charts.auto_recommend(ds["dataframe"], ds["schema"])
    return {"charts": charts}


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/chart/histogram")
async def get_histogram(dataset_id: str, column: str):
    ds = get_dataset_or_404(dataset_id)
    return store.charts.histogram(ds["dataframe"], column)


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/chart/box")
async def get_box_plot(dataset_id: str, column: str, group_by: str = None):
    ds = get_dataset_or_404(dataset_id)
    return store.charts.box_plot(ds["dataframe"], column, group_by)


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/chart/scatter")
async def get_scatter(dataset_id: str, x: str, y: str, color: str = None):
    ds = get_dataset_or_404(dataset_id)
    return store.charts.scatter(ds["dataframe"], x, y, color)


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/chart/bar")
async def get_bar(dataset_id: str, column: str, value: str = None, agg: str = "count"):
    ds = get_dataset_or_404(dataset_id)
    return store.charts.bar_chart(ds["dataframe"], column, value, agg=agg)


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/chart/pie")
async def get_pie(dataset_id: str, column: str):
    ds = get_dataset_or_404(dataset_id)
    return store.charts.pie_chart(ds["dataframe"], column)


# ── Export ─────────────────────────────────────────────────────

@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/export/csv")
async def export_csv(dataset_id: str):
    """Export the cleaned dataset as CSV."""
    ds = get_dataset_or_404(dataset_id)
    output_path = get_output_path(dataset_id, f"cleaned_{ds['filename']}")
    ds["dataframe"].to_csv(output_path, index=False)
    return FileResponse(
        path=str(output_path),
        filename=f"cleaned_{ds['filename']}",
        media_type="text/csv",
    )


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/export/json")
async def export_json(dataset_id: str):
    """Export analysis results as JSON."""
    ds = get_dataset_or_404(dataset_id)
    profile = ds["profile"]
    insights = store.insight.generate(ds["dataframe"], ds["schema"], profile)
    stats = store.statistics.compute(ds["dataframe"], ds["schema"])
    corr = store.correlation.compute(ds["dataframe"], ds["schema"])

    export_data = {
        "dataset": {"filename": ds["filename"], "rows": profile["rows"], "columns": profile["columns"]},
        "quality_score": profile["quality_score"],
        "profile": {k: v for k, v in profile.items() if k != "column_profiles"},
        "column_profiles": profile.get("column_profiles", []),
        "statistics": stats,
        "correlations": {k: v for k, v in corr.items() if k != "matrix"},
        "insights": insights,
    }

    output_path = get_output_path(dataset_id, "analysis_report.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)

    return FileResponse(
        path=str(output_path),
        filename="analysis_report.json",
        media_type="application/json",
    )


@app.get(f"{API_PREFIX}/dataset/{{dataset_id}}/export/excel")
async def export_excel(dataset_id: str):
    """Export analysis as multi-sheet Excel file."""
    ds = get_dataset_or_404(dataset_id)
    df = ds["dataframe"]
    profile = ds["profile"]
    stats = store.statistics.compute(df, ds["schema"])

    output_path = get_output_path(dataset_id, "analysis_report.xlsx")

    with pd.ExcelWriter(str(output_path), engine="openpyxl") as writer:
        # Sheet 1: Dataset
        df.head(10000).to_excel(writer, sheet_name="Dataset", index=False)

        # Sheet 2: Data Dictionary
        col_profiles = profile.get("column_profiles", [])
        if col_profiles:
            dict_df = pd.DataFrame(col_profiles)
            cols_to_keep = [c for c in ["name", "column_type", "subtype", "count", "missing",
                                        "missing_percentage", "unique", "mean", "median", "std",
                                        "min_val", "max_val", "skewness"] if c in dict_df.columns]
            dict_df[cols_to_keep].to_excel(writer, sheet_name="Data Dictionary", index=False)

        # Sheet 3: Statistics
        if stats.get("numerical"):
            num_df = pd.DataFrame(stats["numerical"])
            num_df.to_excel(writer, sheet_name="Numerical Statistics", index=False)
        if stats.get("categorical"):
            cat_df = pd.DataFrame([{k: v for k, v in item.items() if k != "frequencies"}
                                   for item in stats["categorical"]])
            if len(cat_df) > 0:
                cat_df.to_excel(writer, sheet_name="Categorical Statistics", index=False)

        # Sheet 4: Insights
        insights = store.insight.generate(df, ds["schema"], profile)
        if insights:
            insights_df = pd.DataFrame([{
                "Type": i.get("type", ""), "Severity": i.get("severity", ""),
                "Title": i.get("title", ""), "Message": i.get("message", ""),
            } for i in insights])
            insights_df.to_excel(writer, sheet_name="Insights", index=False)

    return FileResponse(
        path=str(output_path),
        filename="analysis_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """API health check."""
    return {
        "status": "operational",
        "service": "DataNova API",
        "version": "1.0.0",
        "datasets_loaded": len(store.datasets),
    }


@app.get("/")
async def root():
    return {"message": "DataNova API - Universal CSV Data Intelligence Platform", "docs": "/docs"}
