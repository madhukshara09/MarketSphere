"""Executive dashboard: KPIs, segmentation, campaign, revenue, retention and insights."""

from __future__ import annotations

import numpy as np
import streamlit as st

from utils import charts
from utils.components import (
    data_table, list_card, metric_card, page_header, progress_card, section_header,
)
from utils.helpers import (
    campaign_performance, format_currency, format_number, format_percent,
    load_customers, monthly_revenue, recent_activity, retention_trend,
)

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


def _segment_tone(value: str) -> str:
    return {
        "Champions": "primary", "Loyal": "success", "Potential": "neutral",
        "At Risk": "warning", "Hibernating": "danger",
    }.get(str(value), "neutral")


def render() -> None:
    """Render the dashboard page."""
    customers = load_customers()
    revenue = monthly_revenue()
    retention = retention_trend()
    campaigns = campaign_performance()

    page_header(
        "Executive Dashboard",
        "Consolidated marketing performance across all active channels and segments.",
        chip="Live data - synced 4 minutes ago",
    )

    # ---------------- Row 1: KPI cards ----------------
    total_revenue = float(revenue["Revenue"].sum())
    success_rate = float(campaigns["Conversion Rate"].mean())
    avg_clv = float(customers["Predicted_CLV"].mean())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("Total Customers", format_number(len(customers)),
                    "Active accounts in the current portfolio", 6.4, "users")
    with k2:
        metric_card("Revenue", format_currency(total_revenue),
                    "Trailing twelve month attributed revenue", 11.2, "revenue")
    with k3:
        metric_card("Campaign Success Rate", format_percent(success_rate),
                    "Blended conversion across all channels", -1.8, "target")
    with k4:
        metric_card("Average Customer LTV", format_currency(avg_clv),
                    "Projected lifetime value per customer", 4.9, "value")

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    # ---------------- Row 2: Segmentation + campaign ----------------
    c1, c2 = st.columns([1, 1.35])
    with c1:
        section_header("Customer Segmentation", "Share of portfolio")
        counts = customers["Customer_Segment"].value_counts()
        st.plotly_chart(
            charts.pie_chart(counts.index.tolist(), counts.values.tolist(), height=330),
            use_container_width=True, config=PLOT_CONFIG,
        )
    with c2:
        section_header("Campaign Performance", "Conversion rate by channel")
        st.plotly_chart(
            charts.grouped_bar_chart(
                campaigns["Channel"],
                {"Conversion Rate %": campaigns["Conversion Rate"], "ROI (x10)": campaigns["ROI"] / 10},
                height=330,
            ),
            use_container_width=True, config=PLOT_CONFIG,
        )

    # ---------------- Row 3: Revenue + retention ----------------
    c3, c4 = st.columns(2)
    with c3:
        section_header("Monthly Revenue", "Actual against plan")
        st.plotly_chart(
            charts.line_chart(revenue["Month"], {"Revenue": revenue["Revenue"], "Target": revenue["Target"]}, height=320),
            use_container_width=True, config=PLOT_CONFIG,
        )
    with c4:
        section_header("Retention Trend", "Retained versus churned")
        st.plotly_chart(
            charts.area_chart(retention["Month"], {"Retention %": retention["Retention"]}, height=320),
            use_container_width=True, config=PLOT_CONFIG,
        )

    # ---------------- Row 4: Recent customers ----------------
    section_header("Recent Customers", f"{len(customers)} records in current snapshot")
    table = customers.head(12).copy()
    table["Predicted_CLV"] = table["Predicted_CLV"].apply(lambda v: format_currency(v))
    table["Response_Probability"] = (table["Response_Probability"] * 100).round(1).astype(str) + "%"
    table = table[[
        "Customer_ID", "Customer_Name", "Customer_Segment",
        "Predicted_CLV", "Response_Probability", "Recommendation",
    ]].rename(columns={
        "Customer_ID": "Customer ID", "Customer_Name": "Customer Name",
        "Customer_Segment": "Segment", "Predicted_CLV": "CLV",
        "Response_Probability": "Probability",
    })
    data_table(table, badge_columns={"Segment": _segment_tone})

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    # ---------------- Bottom: insights, recommendations, activity ----------------
    b1, b2, b3 = st.columns(3)
    top_channel = campaigns.sort_values("ROI", ascending=False).iloc[0]
    weak_channel = campaigns.sort_values("ROI").iloc[0]
    champions = int((customers["Customer_Segment"] == "Champions").sum())
    at_risk = int(customers["Customer_Segment"].isin(["At Risk", "Hibernating"]).sum())

    with b1:
        list_card("Business Insights", [
            {"title": f"{top_channel['Channel']} leads on efficiency",
             "text": f"Delivering {top_channel['ROI']:.0f}% ROI on {format_currency(top_channel['Spend'])} of spend.",
             "tone": "success"},
            {"title": f"{champions} champion accounts",
             "text": f"They contribute {format_currency(float(customers[customers['Customer_Segment'] == 'Champions']['Predicted_CLV'].sum()))} of projected lifetime value.",
             "tone": "primary"},
            {"title": f"{at_risk} customers need attention",
             "text": "At-risk and hibernating cohorts have grown for three consecutive weeks.",
             "tone": "warning"},
            {"title": f"{weak_channel['Channel']} underperforms",
             "text": f"ROI of {weak_channel['ROI']:.0f}% sits below the portfolio benchmark.",
             "tone": "danger"},
        ], subtitle="Generated from the current data snapshot")

    with b2:
        list_card("AI Recommendations", [
            {"title": "Reallocate 15% of display budget",
             "text": f"Shift spend toward {top_channel['Channel']} to lift blended ROI by an estimated 9 points.",
             "tone": "primary"},
            {"title": "Launch a win-back sequence",
             "text": "Target the at-risk cohort with a 12% incentive capped at four weeks.", "tone": "warning"},
            {"title": "Introduce a loyalty tier",
             "text": "Champions respond strongly to status-based rewards over price discounts.", "tone": "success"},
            {"title": "Refine frequency capping",
             "text": "Reduce weekly touches from five to three for the potential segment.", "tone": "neutral"},
        ], subtitle="Heuristic engine - model integration pending")

    with b3:
        list_card("Recent Activity", recent_activity(), subtitle="Workspace event stream")

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        share = customers["Customer_Segment"].value_counts(normalize=True) * 100
        progress_card("Segment Distribution", [
            (name, float(value), f"{value:.1f}%") for name, value in share.items()
        ])
    with p2:
        top = campaigns.sort_values("Conversion Rate", ascending=False).head(5)
        peak = float(top["Conversion Rate"].max())
        progress_card("Channel Conversion Index", [
            (row["Channel"], float(row["Conversion Rate"] / peak * 100), f"{row['Conversion Rate']:.1f}%")
            for _, row in top.iterrows()
        ], tone="success")

    st.markdown(
        f'<div class="ms-note" style="margin-top:18px">Data refreshed automatically from the local mock '
        f'dataset. Median customer age {int(np.median(customers["Age"]))}, median income '
        f'{format_currency(float(np.median(customers["Income"])))}.</div>',
        unsafe_allow_html=True,
    )
