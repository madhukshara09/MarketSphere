"""Opportunity scoring used by the decision-impact workflow."""

from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


REQUIRED_COLUMNS = {"Income", "Total_Spending", "Total_Purchases", "Recency"}


def add_opportunity_score(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a transparent 0-100 marketing-opportunity score."""
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing score columns: {', '.join(sorted(missing))}")

    result = df.copy()
    normalized = MinMaxScaler().fit_transform(
        result[["Income", "Total_Spending", "Total_Purchases", "Recency"]]
    )
    result["Opportunity_Score"] = (
        normalized[:, 0] * 0.20 + normalized[:, 1] * 0.35
        + normalized[:, 2] * 0.25 + (1 - normalized[:, 3]) * 0.20
    ) * 100
    return result
