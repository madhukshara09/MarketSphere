"""General purpose helpers: formatting, mock data access, deterministic business logic.

No backend, no database, no ML. All numbers are derived from local mock data and
transparent heuristic formulas so the UI behaves realistically.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CUSTOMERS_CSV = os.path.join(DATA_DIR, "customers.csv")

APP_VERSION = "1.4.2"
COMPANY_NAME = "MarketSphere Analytics, Inc."

SEGMENTS = ["Champions", "Loyal", "Potential", "At Risk", "Hibernating"]
SEGMENT_COLORS = {
    "Champions": "#2563EB",
    "Loyal": "#10B981",
    "Potential": "#38BDF8",
    "At Risk": "#F59E0B",
    "Hibernating": "#EF4444",
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
# Mock data access
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_customers() -> pd.DataFrame:
    """Load the mock customer dataset, generating it on first run."""
    if not os.path.exists(CUSTOMERS_CSV):
        from data.generate_mock_data import generate_customers, save_customers

        save_customers(generate_customers())
    return pd.read_csv(CUSTOMERS_CSV)


@st.cache_data(show_spinner=False)
def monthly_revenue(months: int = 12) -> pd.DataFrame:
    """Deterministic monthly revenue / target series."""
    rng = np.random.default_rng(21)
    today = datetime.today().replace(day=1)
    labels, revenue, target = [], [], []
    base = 780_000.0
    for offset in range(months - 1, -1, -1):
        point = today - timedelta(days=30 * offset)
        labels.append(point.strftime("%b %Y"))
        base *= 1 + rng.normal(0.028, 0.032)
        revenue.append(round(base, 2))
        target.append(round(base * rng.uniform(0.9, 1.1), 2))
    return pd.DataFrame({"Month": labels, "Revenue": revenue, "Target": target})


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
    """Per-channel campaign performance summary."""
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({
        "Channel": CHANNELS,
        "Reached": rng.integers(9_000, 48_000, len(CHANNELS)),
        "Conversion Rate": np.round(rng.uniform(4.2, 19.5, len(CHANNELS)), 2),
        "Spend": np.round(rng.uniform(18_000, 96_000, len(CHANNELS)), 2),
    })
    frame["Converted"] = (frame["Reached"] * frame["Conversion Rate"] / 100).round().astype(int)
    frame["Revenue"] = (frame["Converted"] * rng.uniform(120, 320, len(CHANNELS))).round(2)
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
    """Estimate campaign response probability from form inputs.

    Transparent weighted scoring - not a machine learning model.
    """
    # Future FastAPI Integration
    # response = requests.post("/predict/response", json=payload)
    # prediction = response.json()

    education_weight = {"High School": 0.0, "Bachelor": 0.06, "Master": 0.10, "PhD": 0.13}
    occupation_weight = {"Student": -0.04, "Employed": 0.05, "Self-Employed": 0.07, "Manager": 0.10, "Retired": -0.02}
    marital_weight = {"Single": 0.01, "Married": 0.05, "Divorced": -0.02, "Widowed": -0.03}

    score = 0.18
    score += min(payload["income"] / 200_000, 1.0) * 0.22
    score += min(payload["frequency"] / 30, 1.0) * 0.20
    score += (1 - min(payload["recency"] / 365, 1.0)) * 0.18
    score += payload["spending"] / 100 * 0.16
    score += education_weight.get(payload["education"], 0.0)
    score += occupation_weight.get(payload["occupation"], 0.0)
    score += marital_weight.get(payload["marital_status"], 0.0)
    score -= abs(payload["age"] - 42) / 100 * 0.08

    probability = float(np.clip(score, 0.02, 0.97))
    confidence = float(np.clip(0.62 + abs(probability - 0.5) * 0.72, 0.6, 0.98))
    responds = probability >= 0.5

    if probability >= 0.72:
        recommendation = "Prioritise this customer in the next campaign wave with a premium offer and a personalised landing page."
    elif probability >= 0.5:
        recommendation = "Include in the main campaign with a mid-tier incentive and a two-step reminder sequence."
    elif probability >= 0.3:
        recommendation = "Nurture first. Run a low-cost re-engagement sequence before adding to a paid campaign."
    else:
        recommendation = "Suppress from paid targeting. Keep in lifecycle email only to protect campaign efficiency."

    return {
        "probability": probability,
        "responds": responds,
        "confidence": confidence,
        "recommendation": recommendation,
        "drivers": {
            "Purchase frequency": min(payload["frequency"] / 30, 1.0),
            "Income level": min(payload["income"] / 200_000, 1.0),
            "Engagement recency": 1 - min(payload["recency"] / 365, 1.0),
            "Spending score": payload["spending"] / 100,
        },
    }


def predict_clv(payload: dict) -> dict:
    """Estimate customer lifetime value from form inputs."""
    # Future FastAPI Integration
    # response = requests.post("/predict/clv", json=payload)
    # prediction = response.json()

    avg_order = 45 + payload["income"] / 1_400 + payload["spending"] * 1.6
    yearly_orders = max(payload["frequency"], 1)
    expected_years = float(np.clip(5.5 - payload["recency"] / 120 - payload["complaints"] * 0.45, 0.6, 7.5))
    clv = float(avg_order * yearly_orders * expected_years * 0.72)

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

    return {
        "clv": clv,
        "tier": tier,
        "tier_tone": tier_tone,
        "risk": risk,
        "retention": retention,
        "avg_order": avg_order,
        "expected_years": expected_years,
        "yearly_orders": yearly_orders,
    }


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
