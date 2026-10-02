"""
DataNova - Machine Learning Engine
Handles regression, classification, and clustering with automatic preprocessing.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
    silhouette_score, davies_bouldin_score,
)
from app.core.config import ML_TEST_SIZE, ML_RANDOM_STATE, ML_MAX_CATEGORIES_FOR_ENCODING, TARGET_HINTS


class MLEngine:
    """Handles machine learning: regression, classification, and clustering."""

    def suggest_targets(self, df: pd.DataFrame, schema: dict) -> list[dict]:
        """Suggest potential target columns for ML."""
        suggestions = []
        for col in df.columns:
            col_lower = col.lower().strip()
            info = schema.get(col, {})
            col_type = info.get("type", "text")

            score = 0
            reason = []

            # Name-based hints
            for hint in TARGET_HINTS:
                if hint in col_lower:
                    score += 3
                    reason.append(f"Column name suggests a target ('{hint}')")
                    break

            # Type-based scoring
            if col_type == "numerical":
                score += 1
                reason.append("Numerical column (potential regression target)")
            elif col_type == "categorical":
                unique = df[col].nunique()
                if 2 <= unique <= 20:
                    score += 2
                    reason.append(f"Categorical with {unique} classes (potential classification target)")

            if score > 0:
                suggestions.append({
                    "column": col,
                    "type": col_type,
                    "score": score,
                    "reasons": reason,
                    "unique_values": int(df[col].nunique()),
                })

        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:10]

    def run_regression(self, df: pd.DataFrame, schema: dict,
                       target_column: str, feature_columns: list[str] | None = None,
                       model_name: str = "random_forest", test_size: float = ML_TEST_SIZE) -> dict:
        """Train and evaluate a regression model."""
        X, y, feature_names = self._prepare_data(df, schema, target_column, feature_columns, task="regression")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=ML_RANDOM_STATE
        )

        model = self._get_regression_model(model_name)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = round(float(mean_absolute_error(y_test, y_pred)), 4)
        mse = round(float(mean_squared_error(y_test, y_pred)), 4)
        rmse = round(float(np.sqrt(mse)), 4)
        r2 = round(float(r2_score(y_test, y_pred)), 4)

        # Feature importance
        importance = self._get_feature_importance(model, feature_names)

        return {
            "task_type": "regression",
            "model_name": model_name,
            "target": target_column,
            "features": feature_names,
            "train_size": len(X_train),
            "test_size_count": len(X_test),
            "metrics": {"MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2},
            "feature_importance": importance,
            "predictions_sample": [
                {"actual": round(float(a), 2), "predicted": round(float(p), 2)}
                for a, p in zip(y_test[:20], y_pred[:20])
            ],
        }

    def run_classification(self, df: pd.DataFrame, schema: dict,
                            target_column: str, feature_columns: list[str] | None = None,
                            model_name: str = "random_forest", test_size: float = ML_TEST_SIZE) -> dict:
        """Train and evaluate a classification model."""
        X, y, feature_names = self._prepare_data(df, schema, target_column, feature_columns, task="classification")

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=ML_RANDOM_STATE, stratify=y_encoded
        )

        model = self._get_classification_model(model_name)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        n_classes = len(le.classes_)
        avg = "binary" if n_classes == 2 else "weighted"

        metrics = {
            "Accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "Precision": round(float(precision_score(y_test, y_pred, average=avg, zero_division=0)), 4),
            "Recall": round(float(recall_score(y_test, y_pred, average=avg, zero_division=0)), 4),
            "F1": round(float(f1_score(y_test, y_pred, average=avg, zero_division=0)), 4),
        }

        # ROC-AUC
        try:
            if n_classes == 2:
                y_proba = model.predict_proba(X_test)[:, 1]
                metrics["ROC_AUC"] = round(float(roc_auc_score(y_test, y_proba)), 4)
            else:
                y_proba = model.predict_proba(X_test)
                metrics["ROC_AUC"] = round(float(roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted")), 4)
        except Exception:
            pass

        cm = confusion_matrix(y_test, y_pred).tolist()
        importance = self._get_feature_importance(model, feature_names)

        return {
            "task_type": "classification",
            "model_name": model_name,
            "target": target_column,
            "features": feature_names,
            "classes": le.classes_.tolist(),
            "train_size": len(X_train),
            "test_size_count": len(X_test),
            "metrics": metrics,
            "confusion_matrix": cm,
            "feature_importance": importance,
        }

    def run_clustering(self, df: pd.DataFrame, schema: dict,
                        feature_columns: list[str] | None = None,
                        n_clusters: int = 3) -> dict:
        """Run K-Means clustering."""
        from sklearn.cluster import KMeans

        num_cols = feature_columns or [
            c for c, info in schema.items()
            if info.get("type") == "numerical" and c in df.columns
        ]

        if len(num_cols) < 2:
            return {"error": "Need at least 2 numerical columns for clustering."}

        X = df[num_cols].apply(pd.to_numeric, errors="coerce").dropna()
        if len(X) < n_clusters:
            return {"error": "Not enough data points for the requested number of clusters."}

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=n_clusters, random_state=ML_RANDOM_STATE, n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        sil_score = round(float(silhouette_score(X_scaled, labels)), 4) if n_clusters > 1 else 0
        db_score = round(float(davies_bouldin_score(X_scaled, labels)), 4) if n_clusters > 1 else 0

        # Cluster summaries
        X_with_labels = X.copy()
        X_with_labels["cluster"] = labels
        cluster_summary = []
        for i in range(n_clusters):
            cluster_data = X_with_labels[X_with_labels["cluster"] == i]
            summary = {"cluster": i, "size": len(cluster_data), "percentage": round(len(cluster_data) / len(X) * 100, 1)}
            for col in num_cols:
                summary[f"{col}_mean"] = round(float(cluster_data[col].mean()), 2)
            cluster_summary.append(summary)

        return {
            "task_type": "clustering",
            "model_name": "KMeans",
            "n_clusters": n_clusters,
            "features": num_cols,
            "total_points": len(X),
            "metrics": {"Silhouette_Score": sil_score, "Davies_Bouldin": db_score},
            "cluster_labels": labels.tolist(),
            "cluster_centers": kmeans.cluster_centers_.tolist(),
            "cluster_summary": cluster_summary,
        }

    def _prepare_data(self, df: pd.DataFrame, schema: dict,
                       target_column: str, feature_columns: list[str] | None,
                       task: str) -> tuple:
        """Prepare features and target for ML."""
        if feature_columns:
            features = [c for c in feature_columns if c != target_column and c in df.columns]
        else:
            features = [
                c for c, info in schema.items()
                if c != target_column and c in df.columns
                and info.get("type") in ("numerical", "categorical", "boolean")
            ]

        data = df[features + [target_column]].dropna()
        if len(data) < 20:
            raise ValueError("Not enough data after removing missing values (minimum 20 rows).")

        y = data[target_column]
        X = data[features].copy()

        # Encode categoricals
        encoded_features = []
        for col in features:
            col_info = schema.get(col, {})
            if col_info.get("type") in ("categorical", "boolean"):
                if X[col].nunique() <= ML_MAX_CATEGORIES_FOR_ENCODING:
                    dummies = pd.get_dummies(X[col], prefix=col, drop_first=True)
                    X = pd.concat([X.drop(col, axis=1), dummies], axis=1)
                    encoded_features.extend(dummies.columns.tolist())
                else:
                    X = X.drop(col, axis=1)
            else:
                X[col] = pd.to_numeric(X[col], errors="coerce")
                encoded_features.append(col)

        feature_names = [c for c in X.columns]
        X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

        if task == "regression":
            y = pd.to_numeric(y, errors="coerce")
            mask = y.notna()
            X = X[mask]
            y = y[mask]

        return X.values, y.values, feature_names

    def _get_regression_model(self, name: str):
        """Get a regression model by name."""
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.tree import DecisionTreeRegressor
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

        models = {
            "linear_regression": LinearRegression(),
            "ridge": Ridge(random_state=ML_RANDOM_STATE),
            "lasso": Lasso(random_state=ML_RANDOM_STATE),
            "decision_tree": DecisionTreeRegressor(random_state=ML_RANDOM_STATE, max_depth=10),
            "random_forest": RandomForestRegressor(n_estimators=100, random_state=ML_RANDOM_STATE, max_depth=10, n_jobs=-1),
            "gradient_boosting": GradientBoostingRegressor(n_estimators=100, random_state=ML_RANDOM_STATE, max_depth=5),
        }
        return models.get(name, models["random_forest"])

    def _get_classification_model(self, name: str):
        """Get a classification model by name."""
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

        models = {
            "logistic_regression": LogisticRegression(random_state=ML_RANDOM_STATE, max_iter=1000),
            "decision_tree": DecisionTreeClassifier(random_state=ML_RANDOM_STATE, max_depth=10),
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=ML_RANDOM_STATE, max_depth=10, n_jobs=-1),
            "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=ML_RANDOM_STATE, max_depth=5),
        }
        return models.get(name, models["random_forest"])

    def _get_feature_importance(self, model, feature_names: list[str]) -> list[dict]:
        """Extract feature importance from a trained model."""
        try:
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
            elif hasattr(model, "coef_"):
                importances = np.abs(model.coef_).flatten()
            else:
                return []

            importance_list = [
                {"feature": name, "importance": round(float(imp), 4)}
                for name, imp in zip(feature_names, importances)
            ]
            importance_list.sort(key=lambda x: x["importance"], reverse=True)
            return importance_list
        except Exception:
            return []
