"""
DataNova - Hypothesis Testing Engine
Performs statistical tests: t-test, ANOVA, Chi-square, Mann-Whitney, normality, correlation tests.
"""
import pandas as pd
import numpy as np
from scipy import stats


class HypothesisEngine:
    """Performs statistical hypothesis tests."""

    def run_test(self, df: pd.DataFrame, schema: dict, test_type: str,
                 numerical_column: str | None = None,
                 grouping_column: str | None = None,
                 column_a: str | None = None,
                 column_b: str | None = None) -> dict:
        """Run a statistical test."""
        try:
            if test_type == "normality":
                return self._normality_test(df, numerical_column)
            elif test_type == "ttest":
                return self._ttest(df, numerical_column, grouping_column)
            elif test_type == "anova":
                return self._anova(df, numerical_column, grouping_column)
            elif test_type == "mann_whitney":
                return self._mann_whitney(df, numerical_column, grouping_column)
            elif test_type == "kruskal_wallis":
                return self._kruskal_wallis(df, numerical_column, grouping_column)
            elif test_type == "chi_square":
                return self._chi_square(df, column_a, column_b)
            elif test_type == "correlation_test":
                return self._correlation_test(df, column_a, column_b)
            else:
                return {"error": f"Unknown test type: {test_type}"}
        except Exception as e:
            return {"error": str(e)}

    def _normality_test(self, df: pd.DataFrame, column: str) -> dict:
        """Shapiro-Wilk normality test."""
        data = pd.to_numeric(df[column], errors="coerce").dropna()
        sample = data.sample(min(5000, len(data)), random_state=42) if len(data) > 5000 else data

        stat, p_value = stats.shapiro(sample)

        is_normal = p_value > 0.05
        interpretation = (
            f"The data in '{column}' appears to follow a normal distribution (p = {p_value:.4f})."
            if is_normal else
            f"The data in '{column}' does not appear to follow a normal distribution (p = {p_value:.4f})."
        )

        return {
            "test_name": "Shapiro-Wilk Normality Test",
            "statistic": round(float(stat), 6),
            "p_value": round(float(p_value), 6),
            "interpretation": interpretation,
            "details": {"column": column, "sample_size": len(sample), "is_normal": is_normal},
        }

    def _ttest(self, df: pd.DataFrame, numerical_column: str, grouping_column: str) -> dict:
        """Independent samples t-test."""
        data = df[[numerical_column, grouping_column]].dropna()
        data[numerical_column] = pd.to_numeric(data[numerical_column], errors="coerce")
        data = data.dropna()

        groups = data[grouping_column].unique()
        if len(groups) < 2:
            return {"error": "Need at least 2 groups for t-test."}

        group_a = data[data[grouping_column] == groups[0]][numerical_column]
        group_b = data[data[grouping_column] == groups[1]][numerical_column]

        stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)

        significant = p_value < 0.05
        interpretation = (
            f"There is a statistically significant difference between {groups[0]} and {groups[1]} "
            f"in {numerical_column} (p = {p_value:.4f})."
            if significant else
            f"No statistically significant difference detected between {groups[0]} and {groups[1]} "
            f"in {numerical_column} (p = {p_value:.4f})."
        )

        return {
            "test_name": "Welch's t-test",
            "statistic": round(float(stat), 6),
            "p_value": round(float(p_value), 6),
            "interpretation": interpretation,
            "details": {
                "group_a": str(groups[0]), "group_b": str(groups[1]),
                "n_a": len(group_a), "n_b": len(group_b),
                "mean_a": round(float(group_a.mean()), 4),
                "mean_b": round(float(group_b.mean()), 4),
                "significant": significant,
            },
        }

    def _anova(self, df: pd.DataFrame, numerical_column: str, grouping_column: str) -> dict:
        """One-way ANOVA test."""
        data = df[[numerical_column, grouping_column]].dropna()
        data[numerical_column] = pd.to_numeric(data[numerical_column], errors="coerce")
        data = data.dropna()

        groups = [group[numerical_column].values for name, group in data.groupby(grouping_column)]
        groups = [g for g in groups if len(g) > 1]

        if len(groups) < 2:
            return {"error": "Need at least 2 groups with multiple observations for ANOVA."}

        stat, p_value = stats.f_oneway(*groups)

        significant = p_value < 0.05
        interpretation = (
            f"There is a statistically significant difference among group means "
            f"in {numerical_column} by {grouping_column} (p = {p_value:.4f})."
            if significant else
            f"No statistically significant difference detected among group means "
            f"in {numerical_column} by {grouping_column} (p = {p_value:.4f})."
        )

        return {
            "test_name": "One-way ANOVA",
            "statistic": round(float(stat), 6),
            "p_value": round(float(p_value), 6),
            "interpretation": interpretation,
            "details": {"num_groups": len(groups), "significant": significant},
        }

    def _mann_whitney(self, df: pd.DataFrame, numerical_column: str, grouping_column: str) -> dict:
        """Mann-Whitney U test (non-parametric)."""
        data = df[[numerical_column, grouping_column]].dropna()
        data[numerical_column] = pd.to_numeric(data[numerical_column], errors="coerce")
        data = data.dropna()

        groups = data[grouping_column].unique()
        if len(groups) < 2:
            return {"error": "Need at least 2 groups for Mann-Whitney U test."}

        group_a = data[data[grouping_column] == groups[0]][numerical_column]
        group_b = data[data[grouping_column] == groups[1]][numerical_column]

        stat, p_value = stats.mannwhitneyu(group_a, group_b, alternative="two-sided")

        significant = p_value < 0.05
        interpretation = (
            f"There is a statistically significant difference between {groups[0]} and {groups[1]} "
            f"in {numerical_column} (Mann-Whitney U, p = {p_value:.4f})."
            if significant else
            f"No statistically significant difference detected (Mann-Whitney U, p = {p_value:.4f})."
        )

        return {
            "test_name": "Mann-Whitney U Test",
            "statistic": round(float(stat), 6),
            "p_value": round(float(p_value), 6),
            "interpretation": interpretation,
            "details": {"group_a": str(groups[0]), "group_b": str(groups[1]), "significant": significant},
        }

    def _kruskal_wallis(self, df: pd.DataFrame, numerical_column: str, grouping_column: str) -> dict:
        """Kruskal-Wallis H test."""
        data = df[[numerical_column, grouping_column]].dropna()
        data[numerical_column] = pd.to_numeric(data[numerical_column], errors="coerce")
        data = data.dropna()

        groups = [group[numerical_column].values for name, group in data.groupby(grouping_column)]
        groups = [g for g in groups if len(g) > 0]

        if len(groups) < 2:
            return {"error": "Need at least 2 groups for Kruskal-Wallis test."}

        stat, p_value = stats.kruskal(*groups)

        significant = p_value < 0.05
        interpretation = (
            f"There is a statistically significant difference among groups "
            f"(Kruskal-Wallis, p = {p_value:.4f})."
            if significant else
            f"No statistically significant difference among groups (Kruskal-Wallis, p = {p_value:.4f})."
        )

        return {
            "test_name": "Kruskal-Wallis H Test",
            "statistic": round(float(stat), 6),
            "p_value": round(float(p_value), 6),
            "interpretation": interpretation,
            "details": {"num_groups": len(groups), "significant": significant},
        }

    def _chi_square(self, df: pd.DataFrame, column_a: str, column_b: str) -> dict:
        """Chi-square test of independence."""
        data = df[[column_a, column_b]].dropna()
        contingency = pd.crosstab(data[column_a], data[column_b])

        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        # Cramér's V
        n = contingency.sum().sum()
        min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
        cramers_v = round(float(np.sqrt(chi2 / (n * min_dim))), 4) if min_dim > 0 and n > 0 else 0

        significant = p_value < 0.05
        interpretation = (
            f"There is a statistically significant association between {column_a} and {column_b} "
            f"(χ² = {chi2:.2f}, p = {p_value:.4f}, Cramér's V = {cramers_v})."
            if significant else
            f"No statistically significant association between {column_a} and {column_b} "
            f"(χ² = {chi2:.2f}, p = {p_value:.4f})."
        )

        return {
            "test_name": "Chi-Square Test of Independence",
            "statistic": round(float(chi2), 6),
            "p_value": round(float(p_value), 6),
            "interpretation": interpretation,
            "details": {
                "degrees_of_freedom": int(dof),
                "cramers_v": cramers_v,
                "significant": significant,
            },
        }

    def _correlation_test(self, df: pd.DataFrame, column_a: str, column_b: str) -> dict:
        """Pearson correlation significance test."""
        data = df[[column_a, column_b]].dropna()
        data[column_a] = pd.to_numeric(data[column_a], errors="coerce")
        data[column_b] = pd.to_numeric(data[column_b], errors="coerce")
        data = data.dropna()

        corr, p_value = stats.pearsonr(data[column_a], data[column_b])

        significant = p_value < 0.05
        strength = "strong" if abs(corr) > 0.7 else ("moderate" if abs(corr) > 0.4 else "weak")
        direction = "positive" if corr > 0 else "negative"

        interpretation = (
            f"There is a statistically significant {strength} {direction} correlation "
            f"between {column_a} and {column_b} (r = {corr:.4f}, p = {p_value:.4f})."
            if significant else
            f"The correlation between {column_a} and {column_b} is not statistically significant "
            f"(r = {corr:.4f}, p = {p_value:.4f})."
        )

        return {
            "test_name": "Pearson Correlation Test",
            "statistic": round(float(corr), 6),
            "p_value": round(float(p_value), 6),
            "interpretation": interpretation,
            "details": {"strength": strength, "direction": direction, "significant": significant},
        }
