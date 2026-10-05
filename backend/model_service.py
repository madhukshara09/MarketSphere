"""Application-facing model and dataset service for MarketSphere."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .analyzer import analyze_dataset
from .data_validator import CAMPAIGN_FEATURES, CLV_FEATURES
from src.opportunity_score import add_opportunity_score


ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA = ROOT / "data" / "processed" / "marketing_campaign_cleaned.csv"


def load_scored_customers() -> pd.DataFrame:
    """Load the project dataset and score it with the saved ML models."""
    scored = add_opportunity_score(analyze_dataset(pd.read_csv(PROCESSED_DATA)))
    scored["Expected_Revenue"] = scored["Response_Probability"] * (
        scored["Total_Spending"] / scored["Total_Purchases"].clip(lower=1)
    )
    scored["Priority"] = pd.cut(
        scored["Opportunity_Score"], bins=[-1, 35, 65, 100], labels=["Low", "Medium", "High"]
    ).astype(str)
    scored["Recommendation"] = scored["Priority"].map({
        "High": "Prioritise personalised campaign",
        "Medium": "Nurture with targeted offer",
        "Low": "Maintain low-cost engagement",
    })
    return scored


def _base_profile(payload: dict) -> dict:
    """Translate the UI's friendly form fields to trained-model features."""
    purchases = max(int(payload["frequency"]), 1)
    spending = float(payload["spending"])
    income = float(payload["income"])
    recency = float(payload["recency"])
    web = max(round(purchases * 0.40), 1)
    catalog = max(round(purchases * 0.20), 0)
    store = max(purchases - web - catalog, 0)
    return {
        "Income": income,
        "Age": int(payload["age"]),
        "Recency": recency,
        "Kidhome": int(payload.get("kidhome", 0)),
        "Teenhome": int(payload.get("teenhome", 0)),
        "NumWebPurchases": web,
        "NumCatalogPurchases": catalog,
        "NumStorePurchases": store,
        "NumWebVisitsMonth": max(round(12 - spending / 15), 1),
        "NumDealsPurchases": max(round(purchases * 0.15), 0),
        "Total_Spending": spending * 25,
        "Total_Purchases": purchases,
    }


def predict_response(payload: dict) -> dict:
    """Run campaign-response inference using the trained classifier."""
    from .analyzer import load_models

    _, _, _, model = load_models()
    profile = _base_profile(payload)
    probability = float(model.predict_proba(pd.DataFrame([profile])[CAMPAIGN_FEATURES])[:, 1][0])
    return {"probability": probability, "responds": probability >= 0.50, "profile": profile}


def predict_clv(payload: dict) -> dict:
    """Run CLV-proxy inference using the trained regressor."""
    from .analyzer import load_models

    _, _, model, _ = load_models()
    profile = _base_profile(payload)
    prediction = float(model.predict(pd.DataFrame([profile])[CLV_FEATURES])[0])
    return {"clv": max(prediction, 0.0), "profile": profile}
