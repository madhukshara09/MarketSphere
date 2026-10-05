"""Presentation helpers backed by the root MarketSphere ML pipeline."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
APP_VERSION = "2.0.0"
COMPANY_NAME = "MarketSphere"

SEGMENTS = ["Premium VIP Customers", "Loyal Customers", "Low-Value Customers", "Dormant Customers"]
SEGMENT_COLORS = {
    "Premium VIP Customers": "#2563EB",
    "Loyal Customers": "#10B981",
    "Low-Value Customers": "#F59E0B",
    "Dormant Customers": "#EF4444",
}
CHANNELS = ["Email", "Paid Search", "Social Media", "Display", "Affiliate", "Direct Mail"]

PALETTE = {
    "bg": "#0F172A",
    "card": "#1E293B",
    "primary": "#2563EB",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#FFFFFF",
    "text2": "#CBD5E1",
    "border": "#334155",
}


# ----------------------------------------------------------------------------
# Formatting
# ----------------------------------------------------------------------------
def format_currency(value: float, decimals: int = 0) -> str:
    """Format a number as compact USD currency."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "-"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 10_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.{decimals}f}"


def format_number(value: float) -> str:
    """Format a plain number with thousands separators."""
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return "-"


def format_percent(value: float, decimals: int = 1) -> str:
    """Format a 0-100 scaled value as a percentage string."""
    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return "-"


def load_css(file_path: str) -> None:
    """Inject the external stylesheet into the Streamlit app."""
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as handle:
        st.markdown(f"<style>{handle.read()}</style>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Data and model access
# ----------------------------------------------------------------------------
def load_customers() -> pd.DataFrame:
    """Load and score the real project dataset with saved ML models."""
    active_dataset = st.session_state.get("active_dataset")
    if active_dataset is not None:
        return active_dataset.copy()
    from backend.model_service import load_scored_customers
    return load_scored_customers()


@st.cache_data(show_spinner=False)
def monthly_revenue(months: int = 12) -> pd.DataFrame:
    """Aggregate observed spending by customer-enrolment month."""
    customers = load_customers().copy()
    customers["Dt_Customer"] = pd.to_datetime(customers["Dt_Customer"])
    grouped = customers.groupby(customers["Dt_Customer"].dt.to_period("M"))["Total_Spending"].sum().tail(months)
    return pd.DataFrame({"Month": grouped.index.astype(str), "Revenue": grouped.values, "Target": grouped.values * 0.95})


@st.cache_data(show_spinner=False)
def retention_trend(months: int = 12) -> pd.DataFrame:
    """Retention and churn percentages by month."""
    rng = np.random.default_rng(7)
    frame = monthly_revenue(months)[["Month"]].copy()
    retention = np.clip(np.cumsum(rng.normal(0.45, 1.1, months)) + 78, 63, 94)
    frame["Retention"] = np.round(retention, 2)
    frame["Churn"] = np.round(100 - retention, 2)
    return frame


@st.cache_data(show_spinner=False)
def campaign_performance() -> pd.DataFrame:
    """Model-based campaign potential split across illustrative channels."""
    customers = load_customers()
    response_rate = customers["Response_Probability"].mean() * 100
    total = len(customers)
    weights = np.array([0.26, 0.19, 0.17, 0.14, 0.13, 0.11])
    reached = (total * weights).round().astype(int)
    frame = pd.DataFrame({"Channel": CHANNELS, "Reached": reached})
    frame["Conversion Rate"] = np.round(response_rate * np.array([1.12, 1.04, 0.98, 0.88, 0.93, 0.82]), 2)
    frame["Converted"] = (frame["Reached"] * frame["Conversion Rate"] / 100).round().astype(int)
    frame["Spend"] = frame["Reached"] * 8
    frame["Revenue"] = frame["Converted"] * customers["Total_Spending"].mean() / max(customers["Total_Purchases"].mean(), 1)
    frame["ROI"] = ((frame["Revenue"] - frame["Spend"]) / frame["Spend"] * 100).round(1)
    return frame


@st.cache_data(show_spinner=False)
def recent_activity() -> list[dict]:
    """Mock activity feed entries."""
    return [
        {"title": "Q3 Retention Campaign launched", "text": "Targeting 12,480 at-risk customers across email and social.", "meta": "12 min ago", "tone": "primary"},
        {"title": "Segmentation model refreshed", "text": "Five clusters recomputed on the latest 300-customer snapshot.", "meta": "1 hr ago", "tone": "success"},
        {"title": "Budget threshold reached", "text": "Display channel consumed 92% of its monthly allocation.", "meta": "3 hrs ago", "tone": "warning"},
        {"title": "Executive report exported", "text": "September performance summary shared with the leadership group.", "meta": "Yesterday", "tone": "neutral"},
        {"title": "Churn spike detected", "text": "Hibernating segment grew 4.1% week over week.", "meta": "2 days ago", "tone": "danger"},
    ]


# ----------------------------------------------------------------------------
# Heuristic "prediction" logic (placeholder for future model service)
# ----------------------------------------------------------------------------
def predict_response(payload: dict) -> dict:
    """Run the trained campaign-response model and create UI explanation data."""
    from backend.model_service import predict_response as model_predict_response
    result = model_predict_response(payload)
    probability = result["probability"]
    result["confidence"] = max(0.5, abs(probability - 0.5) * 2)
    result["drivers"] = {"Purchase frequency": min(payload["frequency"] / 40, 1), "Income level": min(payload["income"] / 150000, 1), "Engagement recency": max(0, 1 - payload["recency"] / 100), "Spending score": payload["spending"] / 100}
    result["recommendation"] = "Include in the next campaign wave." if result["responds"] else "Use a low-cost nurture campaign before paid targeting."
    return result


def predict_clv(payload: dict) -> dict:
    """Run the trained CLV-proxy model and derive business presentation fields."""
    from backend.model_service import predict_clv as model_predict_clv
    result = model_predict_clv(payload)
    clv = result["clv"]
    avg_order = payload["spending"] * 25 / max(payload["frequency"], 1)
    yearly_orders = max(payload["frequency"], 1)
    expected_years = float(np.clip(5.5 - payload["recency"] / 120 - payload["complaints"] * 0.45, 0.6, 7.5))

    if clv >= 12_000:
        tier, tier_tone = "Platinum", "primary"
    elif clv >= 7_000:
        tier, tier_tone = "Gold", "success"
    elif clv >= 3_200:
        tier, tier_tone = "Silver", "warning"
    else:
        tier, tier_tone = "Bronze", "danger"

    risk = float(np.clip(
        payload["recency"] / 4.2 + payload["complaints"] * 8.5 - payload["frequency"] * 1.1 + 12,
        3, 96,
    ))

    if risk >= 65:
        retention = "High churn exposure. Trigger a win-back offer within 7 days and assign to a retention specialist."
    elif risk >= 40:
        retention = "Moderate risk. Add to a loyalty nurture track and offer a tier upgrade incentive."
    else:
        retention = "Healthy account. Focus on cross-sell and advocacy programmes to expand wallet share."

    result.update({
        "tier": tier,
        "tier_tone": tier_tone,
        "risk": risk,
        "retention": retention,
        "avg_order": avg_order,
        "expected_years": expected_years,
        "yearly_orders": yearly_orders,
    })
    return result


def simulate_decision(payload: dict) -> dict:
    """Simulate the business impact of a campaign configuration."""
    # Future FastAPI Integration
    # response = requests.post("/simulate/decision", json=payload)
    # simulation = response.json()

    channel_factor = {
        "Email": 1.24, "Paid Search": 1.12, "Social Media": 1.05,
        "Display": 0.88, "Affiliate": 0.96, "Direct Mail": 0.79,
    }
    segment_factor = {
        "Champions": 1.38, "Loyal": 1.18, "Potential": 1.0,
        "At Risk": 0.78, "Hibernating": 0.58, "All Segments": 1.0,
    }

    base_rate = 0.072
    discount_lift = 1 + payload["discount"] / 100 * 1.35
    duration_lift = 1 + min(payload["duration"], 90) / 90 * 0.28
    conversion_rate = float(np.clip(
        base_rate * channel_factor[payload["channel"]] * segment_factor[payload["segment"]]
        * discount_lift * duration_lift, 0.008, 0.42,
    ))

    conversions = payload["reach"] * conversion_rate
    avg_order = 214.0 * (1 - payload["discount"] / 100 * 0.55)
    revenue = conversions * avg_order
    marketing_cost = float(payload["budget"])
    cogs = revenue * 0.42
    profit = revenue - marketing_cost - cogs
    roi = (revenue - marketing_cost) / marketing_cost * 100 if marketing_cost else 0.0
    growth = conversions * 0.36

    if roi >= 180 and profit > 0:
        verdict, tone = "Proceed at full scale", "success"
        recommendation = ("The configuration clears the internal ROI hurdle with a comfortable margin. "
                          "Approve the full budget and hold 10% in reserve for mid-flight optimisation.")
    elif roi >= 70:
        verdict, tone = "Proceed with adjustments", "warning"
        recommendation = ("Returns are acceptable but sensitive to discount depth. Reduce the discount by "
                          "3-5 points or shift spend toward the highest converting channel before launch.")
    else:
        verdict, tone = "Revise before launch", "danger"
        recommendation = ("Projected returns fall below the portfolio benchmark. Narrow the audience to "
                          "higher-value segments and re-run the simulation before committing budget.")

    risks = [
        {"name": "Discount margin erosion", "level": min(payload["discount"] * 3.1, 100)},
        {"name": "Channel saturation", "level": float(np.clip((payload["reach"] / 60_000) * 100, 5, 100))},
        {"name": "Budget concentration", "level": float(np.clip(payload["budget"] / 2_500, 5, 100))},
        {"name": "Segment fatigue", "level": float(np.clip(100 - segment_factor[payload["segment"]] * 62, 5, 100))},
    ]

    return {
        "revenue": revenue,
        "roi": roi,
        "conversion_rate": conversion_rate * 100,
        "profit": profit,
        "marketing_cost": marketing_cost,
        "growth": growth,
        "conversions": conversions,
        "avg_order": avg_order,
        "verdict": verdict,
        "tone": tone,
        "recommendation": recommendation,
        "risks": risks,
    }


def projection_series(result: dict, weeks: int = 8) -> pd.DataFrame:
    """Build a weekly revenue / cost projection curve from a simulation result."""
    weights = np.array([0.06, 0.11, 0.15, 0.16, 0.15, 0.14, 0.12, 0.11])[:weeks]
    weights = weights / weights.sum()
    return pd.DataFrame({
        "Week": [f"Week {i + 1}" for i in range(len(weights))],
        "Revenue": np.round(result["revenue"] * weights, 2),
        "Cost": np.round(result["marketing_cost"] * np.full(len(weights), 1 / len(weights)), 2),
        "Profit": np.round(result["profit"] * weights, 2),
    })
