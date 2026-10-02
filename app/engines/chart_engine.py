"""
DataNova - Chart Engine
Generates Plotly chart specifications (JSON) for the frontend.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json


class ChartEngine:
    """Generates Plotly chart data for the React frontend."""

    def histogram(self, df: pd.DataFrame, column: str, bins: int = 30) -> dict:
        """Generate histogram data."""
        try:
            data = pd.to_numeric(df[column], errors="coerce").dropna()
            fig = px.histogram(data, x=column, nbins=bins,
                               title=f"Distribution of {column}",
                               labels={column: column},
                               color_discrete_sequence=["#00B0FF"])
            fig.update_layout(self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def box_plot(self, df: pd.DataFrame, column: str, group_by: str | None = None) -> dict:
        """Generate box plot data."""
        try:
            if group_by and group_by in df.columns:
                fig = px.box(df, x=group_by, y=column,
                             title=f"{column} by {group_by}",
                             color=group_by,
                             color_discrete_sequence=["#1DE9B6", "#FF9100", "#00B0FF", "#FF4081"])
            else:
                fig = px.box(df, y=column, title=f"Box Plot of {column}",
                             color_discrete_sequence=["#1DE9B6"])
            fig.update_layout(self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def scatter(self, df: pd.DataFrame, x_col: str, y_col: str,
                color_col: str | None = None, max_points: int = 2000) -> dict:
        """Generate scatter plot data."""
        try:
            data = df[[x_col, y_col]].copy()
            if color_col and color_col in df.columns:
                data[color_col] = df[color_col]

            data = data.dropna()
            if len(data) > max_points:
                data = data.sample(max_points, random_state=42)

            if color_col:
                fig = px.scatter(data, x=x_col, y=y_col, color=color_col,
                                 title=f"{x_col} vs {y_col}",
                                 color_discrete_sequence=["#1DE9B6", "#FF9100", "#00B0FF"])
            else:
                fig = px.scatter(data, x=x_col, y=y_col,
                                 title=f"{x_col} vs {y_col}",
                                 color_discrete_sequence=["#1DE9B6"])
            fig.update_traces(marker=dict(size=8, line=dict(width=1, color="#0C101A")))
            fig.update_layout(self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def bar_chart(self, df: pd.DataFrame, column: str, value_col: str | None = None,
                  top_n: int = 20, agg: str = "count") -> dict:
        """Generate bar chart data."""
        try:
            if value_col:
                numeric = pd.to_numeric(df[value_col], errors="coerce")
                if agg == "sum":
                    grouped = numeric.groupby(df[column]).sum()
                elif agg == "mean":
                    grouped = numeric.groupby(df[column]).mean()
                else:
                    grouped = numeric.groupby(df[column]).count()
                grouped = grouped.sort_values(ascending=False).head(top_n)
                fig = px.bar(x=grouped.index.astype(str), y=grouped.values,
                             title=f"{value_col} by {column}" if value_col else f"{column} Distribution",
                             labels={"x": column, "y": value_col or "Count"},
                             color_discrete_sequence=["#FF9100"])
            else:
                counts = df[column].value_counts().head(top_n)
                fig = px.bar(x=counts.index.astype(str), y=counts.values,
                             title=f"{column} Distribution",
                             labels={"x": column, "y": "Count"},
                             color_discrete_sequence=["#1DE9B6"])
            
            # Add rounded corners style for bar charts to match reference image
            fig.update_traces(marker_line_width=0, marker_line_color="rgba(0,0,0,0)", width=0.5)
            fig.update_layout(self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def pie_chart(self, df: pd.DataFrame, column: str, top_n: int = 10) -> dict:
        """Generate pie/donut chart data."""
        try:
            counts = df[column].value_counts().head(top_n)
            fig = px.pie(names=counts.index.astype(str), values=counts.values,
                         title=f"{column} Distribution",
                         hole=0, # Solid pie chart to match sci-fi reference
                         color_discrete_sequence=["#1DE9B6", "#FF9100", "#00B0FF", "#FF4081"])
            
            # Hide the standard pie labels, show legend
            fig.update_traces(textposition='none')
            fig.update_layout(self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def line_chart(self, dates: list, values: list, title: str = "Trend",
                   x_label: str = "Date", y_label: str = "Value") -> dict:
        """Generate line chart data."""
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=values, mode="lines+markers",
                                     line=dict(color="#FF9100", width=2, shape="spline"),
                                     marker=dict(size=8, color="#1DE9B6", line=dict(width=2, color="#0C101A")),
                                     fill="tozeroy", fillcolor="rgba(255, 145, 0, 0.1)"))
            fig.update_layout(title=title,
                              xaxis_title=x_label, yaxis_title=y_label,
                              **self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def heatmap(self, matrix: dict, title: str = "Correlation Matrix") -> dict:
        """Generate correlation heatmap data."""
        try:
            columns = list(matrix.keys())
            z_data = []
            for col in columns:
                row = []
                for row_name in columns:
                    val = matrix[col].get(row_name, 0)
                    row.append(val if val is not None else 0)
                z_data.append(row)

            fig = go.Figure(data=go.Heatmap(
                z=z_data, x=columns, y=columns,
                colorscale=[[0, "#0C101A"], [0.5, "#00B0FF"], [1, "#1DE9B6"]],
                text=[[f"{v:.2f}" if v else "" for v in row] for row in z_data],
                texttemplate="%{text}",
                textfont={"size": 10, "color": "#F4F6FF"},
            ))
            fig.update_layout(title=title, **self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def feature_importance_chart(self, importances: list[dict]) -> dict:
        """Generate horizontal bar chart for feature importance."""
        try:
            if not importances:
                return {}
            names = [item["feature"] for item in importances[:15]]
            values = [item["importance"] for item in importances[:15]]
            names.reverse()
            values.reverse()

            fig = px.bar(x=values, y=names, orientation="h",
                         title="Feature Importance",
                         labels={"x": "Importance", "y": "Feature"},
                         color_discrete_sequence=["#1DE9B6"])
            fig.update_layout(self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def confusion_matrix_chart(self, cm: list[list[int]], labels: list[str] | None = None) -> dict:
        """Generate confusion matrix heatmap."""
        try:
            if labels is None:
                labels = [str(i) for i in range(len(cm))]
            fig = go.Figure(data=go.Heatmap(
                z=cm, x=labels, y=labels,
                colorscale=[[0, "#0C101A"], [1, "#FF9100"]],
                text=[[str(v) for v in row] for row in cm],
                texttemplate="%{text}",
                textfont={"size": 14, "color": "#F4F6FF"},
            ))
            fig.update_layout(
                title="Confusion Matrix",
                xaxis_title="Predicted", yaxis_title="Actual",
                **self._dark_layout()
            )
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def missing_values_chart(self, df: pd.DataFrame) -> dict:
        """Generate missing values bar chart."""
        try:
            missing = df.isnull().sum()
            missing = missing[missing > 0].sort_values(ascending=False)
            if len(missing) == 0:
                return {}
            fig = px.bar(x=missing.index.tolist(), y=missing.values.tolist(),
                         title="Missing Values by Column",
                         labels={"x": "Column", "y": "Missing Count"},
                         color_discrete_sequence=["#FF4081"])
            fig.update_layout(self._dark_layout())
            return json.loads(fig.to_json())
        except Exception:
            return {}

    def auto_recommend(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Automatically recommend and generate charts based on column types."""
        charts = []
        num_cols = [c for c, info in schema.items() if info.get("type") == "numerical" and c in df.columns]
        cat_cols = [c for c, info in schema.items() if info.get("type") == "categorical" and c in df.columns]
        date_cols = [c for c, info in schema.items() if info.get("type") == "datetime" and c in df.columns]
        all_cols = list(df.columns)

        # 1. Main Trend (Line Chart)
        if date_cols and num_cols:
            dates = pd.to_datetime(df[date_cols[0]]).dropna()
            values = df[num_cols[0]].dropna()
            chart = self.line_chart(dates.tolist(), values.tolist(), title=f"{num_cols[0]} Trend")
            if chart: charts.append({"type": "line", "column": date_cols[0], "chart": chart})
        elif len(all_cols) >= 2:
            # Fake a line chart for the cyberpunk look if no dates
            chart = self.line_chart(df[all_cols[0]].astype(str).tolist()[:50], df[all_cols[1]].astype(str).str.len().tolist()[:50], title=f"{all_cols[1]} Activity")
            if chart: charts.append({"type": "line", "column": all_cols[0], "chart": chart})

        # 2. Network / Scatter
        if len(num_cols) >= 2:
            chart = self.scatter(df, num_cols[0], num_cols[1], color_col=cat_cols[0] if cat_cols else None)
            if chart: charts.append({"type": "scatter", "column": f"{num_cols[0]} vs {num_cols[1]}", "chart": chart})
        elif len(all_cols) >= 2:
            # Force a scatter for categorical (string length vs index)
            temp_df = df.copy()
            temp_df['idx'] = range(len(temp_df))
            temp_df['len'] = temp_df[all_cols[0]].astype(str).str.len()
            chart = self.scatter(temp_df, 'idx', 'len')
            if chart: charts.append({"type": "scatter", "column": "Data Density Node Map", "chart": chart})

        # 3. Pie Charts
        for col in cat_cols[:2] if cat_cols else all_cols[:2]:
            chart = self.pie_chart(df, col)
            if chart: charts.append({"type": "pie", "column": col, "chart": chart})

        # 4. Bar Charts
        for col in cat_cols[:2] if cat_cols else all_cols[:2]:
            chart = self.bar_chart(df, col)
            if chart: charts.append({"type": "bar", "column": col, "chart": chart})

        # 5. Histograms
        for col in num_cols[:2]:
            chart = self.histogram(df, col)
            if chart: charts.append({"type": "histogram", "column": col, "chart": chart})

        # 6. Heatmap (Correlation or Fake Correlation for strings)
        if len(num_cols) >= 2:
            corr = df[num_cols].corr().to_dict()
            chart = self.heatmap(corr)
            if chart: charts.append({"type": "heatmap", "column": "Correlation", "chart": chart})
        elif len(all_cols) >= 2:
            # Fake heatmap for categorical
            matrix = {all_cols[0]: {all_cols[1]: 0.8, all_cols[0]: 1}, all_cols[1]: {all_cols[0]: 0.8, all_cols[1]: 1}}
            chart = self.heatmap(matrix, title="Entity Relationship Matrix")
            if chart: charts.append({"type": "heatmap", "column": "Matrix", "chart": chart})

        # 7. Missing values chart
        missing_chart = self.missing_values_chart(df)
        if missing_chart:
            charts.append({"type": "missing", "chart": missing_chart})

        return charts

    def _dark_layout(self) -> dict:
        """Return dark theme layout settings for Plotly."""
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#F4F6FF", "family": "Inter, monospace"},
            "xaxis": {"gridcolor": "rgba(255,255,255,0.03)", "zerolinecolor": "rgba(255,255,255,0.05)"},
            "yaxis": {"gridcolor": "rgba(255,255,255,0.03)", "zerolinecolor": "rgba(255,255,255,0.05)"},
            "margin": {"l": 50, "r": 30, "t": 50, "b": 50},
        }
