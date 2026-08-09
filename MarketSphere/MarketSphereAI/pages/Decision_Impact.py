"""Decision Impact Engine: enterprise campaign simulation and decision support."""

from __future__ import annotations

import numpy as np
import streamlit as st

from utils import charts
from utils.components import (
    callout, list_card, metric_card, page_header, progress_card, section_header, stat_card,
)
from utils.helpers import (
    CHANNELS, SEGMENTS, format_currency, format_number, format_percent,
    projection_series, simulate_decision,
)

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


def render() -> None:
    """Render the decision impact simulation page."""
    page_header(
        "Decision Impact Engine",
        "Model the financial consequences of a campaign decision before committing budget.",
        chip="Simulation environment",
    )

    section_header("Scenario Configuration", "Adjust inputs and run the simulation")
    with st.form("simulation_form"):
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            budget = st.number_input("Campaign budget (USD)", 5_000, 2_000_000, 180_000, step=5_000)
        with r1c2:
            discount = st.slider("Discount percentage", 0, 50, 12)
        with r1c3:
            channel = st.selectbox("Marketing channel", CHANNELS, index=0)

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            segment = st.selectbox("Target customer segment", ["All Segments"] + SEGMENTS, index=1)
        with r2c2:
            duration = st.slider("Campaign duration (days)", 7, 120, 45)
        with r2c3:
            reach = st.number_input("Expected customer reach", 1_000, 500_000, 48_000, step=1_000)

        submitted = st.form_submit_button("Run Simulation", use_container_width=True)

    payload = {"budget": budget, "discount": discount, "channel": channel,
               "segment": segment, "duration": duration, "reach": reach}

    # Future FastAPI Integration
    # response = requests.post("/simulate", json=input_data)
    # simulation = response.json()

    if submitted:
        st.session_state["simulation_result"] = simulate_decision(payload)
        st.session_state["simulation_payload"] = payload

    if not st.session_state.get("simulation_result"):
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        callout(
            "Configure the scenario above and run the simulation to produce a full financial "
            "impact assessment, risk profile and executive summary.",
            title="No scenario executed",
        )
        return

    result = st.session_state["simulation_result"]
    payload = st.session_state["simulation_payload"]
    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    # ---------------- Headline outcomes ----------------
    section_header("Projected Outcomes", f"{payload['channel']} - {payload['segment']} - {payload['duration']} days")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("Expected Revenue", format_currency(result["revenue"]),
                    "Gross attributed revenue", 12.6, "revenue")
    with k2:
        metric_card("Expected ROI", format_percent(result["roi"], 0),
                    "Return on marketing investment",
                    round(result["roi"] - 120, 1), "target")
    with k3:
        metric_card("Conversion Rate", format_percent(result["conversion_rate"], 2),
                    "Share of reached audience converting", 2.4, "check")
    with k4:
        metric_card("Net Profit", format_currency(result["profit"]),
                    "After marketing spend and cost of goods",
                    8.1 if result["profit"] > 0 else -8.1, "value")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        stat_card("Marketing Cost", format_currency(result["marketing_cost"]), "Committed campaign budget", "warning")
    with s2:
        stat_card("Customer Growth", format_number(result["growth"]), "Net new active customers", "success")
    with s3:
        stat_card("Conversions", format_number(result["conversions"]), "Expected converting customers", "primary")
    with s4:
        stat_card("Average Order Value", format_currency(result["avg_order"], 2), "After discount effect", "neutral")

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    # ---------------- Gauges ----------------
    section_header("Performance Gauges", "Against internal benchmarks")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(charts.gauge_chart(min(result["roi"], 400), "ROI versus 200% target", 400, "%",
                                           height=270, thresholds=(25, 50)),
                        use_container_width=True, config=PLOT_CONFIG)
    with g2:
        st.plotly_chart(charts.gauge_chart(result["conversion_rate"], "Conversion rate", 30, "%",
                                           height=270, thresholds=(25, 50)),
                        use_container_width=True, config=PLOT_CONFIG)
    with g3:
        margin = max(min(result["profit"] / result["revenue"] * 100, 100), 0) if result["revenue"] else 0
        st.plotly_chart(charts.gauge_chart(margin, "Net profit margin", 60, "%",
                                           height=270, thresholds=(25, 50)),
                        use_container_width=True, config=PLOT_CONFIG)

    # ---------------- Projection charts ----------------
    projection = projection_series(result)
    c1, c2 = st.columns([1.35, 1])
    with c1:
        section_header("Revenue and Cost Projection", "Weekly campaign trajectory")
        st.plotly_chart(
            charts.line_chart(projection["Week"],
                              {"Revenue": projection["Revenue"], "Profit": projection["Profit"],
                               "Cost": projection["Cost"]}, height=330),
            use_container_width=True, config=PLOT_CONFIG,
        )
    with c2:
        section_header("Budget Allocation", "Where the spend lands")
        allocation = {
            "Media": result["marketing_cost"] * 0.58,
            "Creative": result["marketing_cost"] * 0.16,
            "Incentives": result["marketing_cost"] * 0.18,
            "Operations": result["marketing_cost"] * 0.08,
        }
        st.plotly_chart(
            charts.donut_chart(list(allocation.keys()), list(allocation.values()), height=330,
                               center_text=format_currency(result["marketing_cost"])),
            use_container_width=True, config=PLOT_CONFIG,
        )

    # ---------------- Sensitivity ----------------
    c3, c4 = st.columns([1.35, 1])
    with c3:
        section_header("Discount Sensitivity", "ROI across alternative discount depths")
        depths = list(range(0, 45, 5))
        roi_curve = []
        for depth in depths:
            scenario = dict(payload, discount=depth)
            roi_curve.append(round(simulate_decision(scenario)["roi"], 1))
        st.plotly_chart(
            charts.bar_chart([f"{d}%" for d in depths], roi_curve, height=310, text_format="%{y:.0f}%"),
            use_container_width=True, config=PLOT_CONFIG,
        )
    with c4:
        section_header("Risk Analysis", "Exposure by category")
        progress_card("Risk Profile", [
            (risk["name"], risk["level"], f"{risk['level']:.0f}/100") for risk in result["risks"]
        ], tone="danger")

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # ---------------- Executive summary ----------------
    section_header("Executive Summary", "Decision support output")
    e1, e2 = st.columns([1.2, 1])
    with e1:
        callout(result["recommendation"], tone=result["tone"], title=result["verdict"])
        st.markdown(
            f"""
            <div class="ms-card ms-anim" style="margin-top:14px">
              <div class="ms-kpi-label">Scenario at a glance</div>
              <div style="font-size:0.86rem;color:#CBD5E1;line-height:2.1;margin-top:10px">
                Channel<span style="float:right;color:#fff;font-weight:600">{payload['channel']}</span><br>
                Target segment<span style="float:right;color:#fff;font-weight:600">{payload['segment']}</span><br>
                Duration<span style="float:right;color:#fff;font-weight:600">{payload['duration']} days</span><br>
                Audience reach<span style="float:right;color:#fff;font-weight:600">{format_number(payload['reach'])}</span><br>
                Discount depth<span style="float:right;color:#fff;font-weight:600">{payload['discount']}%</span><br>
                Break-even conversions<span style="float:right;color:#fff;font-weight:600">
                  {format_number(result['marketing_cost'] / max(result['avg_order'], 1))}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e2:
        payback = result["marketing_cost"] / max(result["revenue"] / max(payload["duration"], 1), 1)
        list_card("Key Findings", [
            {"title": f"Return on investment of {result['roi']:.0f}%",
             "text": f"Every dollar committed returns {1 + result['roi'] / 100:.2f} dollars in gross revenue.",
             "tone": "success" if result["roi"] >= 120 else "warning"},
            {"title": f"Payback in approximately {payback:.0f} days",
             "text": "Time required for cumulative revenue to cover the committed budget.", "tone": "primary"},
            {"title": f"{format_number(result['growth'])} incremental customers",
             "text": "Expected net additions to the active customer base.", "tone": "primary"},
            {"title": "Highest exposure: " + max(result["risks"], key=lambda r: r["level"])["name"],
             "text": "Monitor this factor weekly and set an automated spend guardrail.", "tone": "danger"},
        ])
