"""Customer segmentation workspace: upload, analyse, explore clusters."""

from __future__ import annotations

import streamlit as st

from utils import charts
from utils.components import (
    callout, data_table, list_card, page_header, section_header, stat_card,
)
from utils.helpers import (
    SEGMENT_COLORS,
    format_currency,
    format_number,
    format_percent,
    load_customers,
)

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}

# Future FastAPI Integration
# response = requests.post("/segment", json=customer_payload)
# segments = response.json()


def _segment_tone(value: str) -> str:
    return {
        "Premium VIP Customers": "primary", "Loyal Customers": "success",
        "Low-Value Customers": "warning", "Dormant Customers": "danger",
    }.get(str(value), "neutral")


def render() -> None:
    """Render the segmentation page."""
    page_header(
        "Customer Segmentation",
        "Cluster the customer base by behaviour, value and engagement recency.",
        chip="4 active clusters",
    )

    customers = load_customers()
    source = st.session_state.get("active_dataset_name", "Built-in marketing campaign dataset")
    st.markdown(f'<div class="ms-note" style="margin:6px 0 14px 0">{source} &middot; '
                f'{len(customers)} records processed</div>', unsafe_allow_html=True)

    # ---------------- Statistics ----------------
    section_header("Customer Statistics", "Portfolio level summary")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        stat_card("Customers Analysed", format_number(len(customers)), "Records in the active snapshot")
    with s2:
        stat_card("Average CLV", format_currency(float(customers["Predicted_CLV"].mean())),
                  "Projected lifetime value", "success")
    with s3:
        stat_card("Average Income", format_currency(float(customers["Income"].mean())),
                  "Annual household income", "primary")
    with s4:
        stat_card(
            "Average Spending",
            format_currency(float(customers["Total_Spending"].mean())),
            "Total customer spending",
            "warning",
            )
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    # ---------------- Distribution + scatter ----------------
    c1, c2 = st.columns([1, 1.4])
    counts = customers["Customer_Segment"].value_counts()
    with c1:
        section_header("Segment Distribution", "Customers per cluster")
        st.plotly_chart(
            charts.donut_chart(counts.index.tolist(), counts.values.tolist(), height=350,
                               center_text=f"{len(customers)}<br><span style='font-size:11px'>customers</span>"),
            use_container_width=True, config=PLOT_CONFIG,
        )
    with c2:
        section_header(
            "Cluster Scatter Plot",
            "Income against total spending"
            )
        st.plotly_chart(
            charts.scatter_chart(
                customers,
                "Income",
                "Total_Spending",
                "Customer_Segment",
                size="Predicted_CLV",
                height=350,
                hover="ID",
                ),
                use_container_width=True,
                config=PLOT_CONFIG,
                )
    # ---------------- Segment cards ----------------
    section_header("Segment Cards", "Cluster level economics")
    summary = customers.groupby("Customer_Segment").agg(
        Customers=("ID", "count"),
        AvgCLV=("Predicted_CLV", "mean"),
        AvgIncome=("Income", "mean"),
        AvgRecency=("Recency", "mean"),
        Probability=("Response_Probability", "mean"),
    ).reset_index().sort_values("AvgCLV", ascending=False)

    cards = st.columns(min(len(summary), 5))
    for column, (_, row) in zip(cards, summary.iterrows()):
        color = SEGMENT_COLORS.get(row["Customer_Segment"], "#2563EB")
        with column:
            st.markdown(
                f"""
                <div class="ms-card ms-anim" style="border-top:3px solid {color}">
                  <div class="ms-kpi-label">{row['Customer_Segment']}</div>
                  <div style="font-size:1.5rem;font-weight:750;color:#fff;margin:8px 0 2px 0">
                    {int(row['Customers'])}
                  </div>
                  <div class="ms-kpi-desc">customers in cluster</div>
                  <div style="margin-top:12px;font-size:0.8rem;color:#CBD5E1;line-height:1.9">
                    Avg CLV<span style="float:right;color:#fff;font-weight:600">{format_currency(row['AvgCLV'])}</span><br>
                    Avg income<span style="float:right;color:#fff;font-weight:600">{format_currency(row['AvgIncome'])}</span><br>
                    Response<span style="float:right;color:#fff;font-weight:600">{format_percent(row['Probability'] * 100)}</span><br>
                    Recency<span style="float:right;color:#fff;font-weight:600">{row['AvgRecency']:.0f} days</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    # ---------------- Table ----------------
    section_header("Customer Table", "First 200 records")
    table = customers.copy()
    table["Predicted_CLV"] = table["Predicted_CLV"].apply(format_currency)
    table["Income"] = table["Income"].apply(format_currency)
    table["Total_Spending"] = table["Total_Spending"].apply(format_currency)
    table["Response_Probability"] = (table["Response_Probability"] * 100).round(1).astype(str) + "%"
    display = table[[
        "ID",
        "Age",
        "Income",
        "Total_Purchases",
        "Recency",
        "Total_Spending",
        "Customer_Segment",
        "Predicted_CLV",
        "Response_Probability",
        ]].rename(columns={
            "ID": "Customer ID",
            "Total_Purchases": "Purchases",
            "Total_Spending": "Total Spending",
            "Customer_Segment": "Segment",
            "Predicted_CLV": "CLV",
            "Response_Probability": "Probability",
            })
    data_table(display, badge_columns={"Segment": _segment_tone})

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    # ---------------- Insights ----------------
    i1, i2 = st.columns(2)
    best = summary.iloc[0]
    worst = summary.iloc[-1]
    with i1:
        list_card("Business Insights", [
            {"title": f"{best['Customer_Segment']} drive portfolio value",
             "text": f"Average CLV of {format_currency(best['AvgCLV'])} across {int(best['Customers'])} customers.",
             "tone": "success"},
            {"title": f"{worst['Customer_Segment']} require intervention",
             "text": f"Average recency of {worst['AvgRecency']:.0f} days signals disengagement.",
             "tone": "danger"},
            {"title": "Income is not the strongest predictor",
             "text": "Purchase frequency correlates more closely with lifetime value than income.",
             "tone": "primary"},
        ])
    with i2:
        section_header("CLV Distribution", "Across all analysed customers")
        st.plotly_chart(
            charts.histogram(customers["Predicted_CLV"], height=300),
            use_container_width=True, config=PLOT_CONFIG,
        )
