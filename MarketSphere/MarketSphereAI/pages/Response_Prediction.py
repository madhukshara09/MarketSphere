"""Campaign response prediction workspace."""

from __future__ import annotations

import streamlit as st

from utils import charts
from utils.components import callout, page_header, progress_card, section_header, stat_card
from utils.helpers import format_currency, format_percent, predict_response

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


def render() -> None:
    """Render the campaign response prediction page."""
    page_header(
        "Campaign Response Prediction",
        "Score an individual customer profile against the next campaign wave.",
        chip="Scoring engine ready",
    )

    form_col, result_col = st.columns([1, 1.45])

    with form_col:
        section_header("Customer Profile", "All fields required")
        with st.form("response_form"):
            age = st.slider("Age", 18, 85, 38)
            income = st.number_input("Annual income (USD)", 12_000, 400_000, 72_000, step=1_000)
            education = st.selectbox("Education", ["High School", "Bachelor", "Master", "PhD"], index=1)
            occupation = st.selectbox("Occupation", ["Student", "Employed", "Self-Employed", "Manager", "Retired"], index=1)
            marital_status = st.selectbox("Marital status", ["Single", "Married", "Divorced", "Widowed"], index=1)
            recency = st.slider("Recency (days since last purchase)", 1, 365, 45)
            frequency = st.slider("Purchase frequency (orders per year)", 1, 40, 12)
            spending = st.slider("Spending score", 1, 100, 62)
            submitted = st.form_submit_button("Predict Response", use_container_width=True)

    payload = {
        "age": age, "income": income, "education": education, "occupation": occupation,
        "marital_status": marital_status, "recency": recency, "frequency": frequency,
        "spending": spending,
    }

    # Future FastAPI Integration
    # response = requests.post("/predict", json=input_data)
    # prediction = response.json()

    with result_col:
        if not submitted and not st.session_state.get("response_result"):
            section_header("Prediction Output", "Awaiting input")
            callout(
                "Complete the customer profile and run the prediction to generate a response "
                "probability, confidence band and recommended action.",
                title="No prediction yet",
            )
            return

        if submitted:
            st.session_state["response_result"] = predict_response(payload)
        result = st.session_state["response_result"]
        probability = result["probability"] * 100
        tone = "success" if result["responds"] else "danger"
        verdict = "Likely to respond" if result["responds"] else "Unlikely to respond"

        section_header("Prediction Output", "Generated locally from profile inputs")
        st.markdown(
            f"""
            <div class="ms-card ms-anim" style="border-left:3px solid {'#10B981' if result['responds'] else '#EF4444'}">
              <div class="ms-kpi-label">Predicted outcome</div>
              <div style="font-size:2rem;font-weight:780;color:#fff;margin:8px 0 4px 0">{probability:.1f}%</div>
              <div class="ms-kpi-desc">Probability of responding to the next campaign</div>
              <div style="margin-top:14px">
                <span class="ms-badge ms-badge-{tone}">{verdict}</span>
                <span class="ms-badge ms-badge-primary" style="margin-left:6px">
                  Confidence {result['confidence'] * 100:.0f}%
                </span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            charts.gauge_chart(probability, "Response probability", 100, "%", height=290, thresholds=(30, 60)),
            use_container_width=True, config=PLOT_CONFIG,
        )

    if not st.session_state.get("response_result"):
        return

    result = st.session_state["response_result"]
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        stat_card("Response Probability", format_percent(result["probability"] * 100), "Model output")
    with m2:
        stat_card("Model Confidence", format_percent(result["confidence"] * 100), "Interval reliability", "success")
    with m3:
        stat_card("Expected Order Value", format_currency(80 + payload["income"] / 1_200 + payload["spending"] * 1.4),
                  "If the customer converts", "primary")
    with m4:
        stat_card("Suggested Incentive",
                  "None" if result["probability"] > 0.72 else ("10%" if result["probability"] > 0.4 else "18%"),
                  "Discount depth to apply", "warning")

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    d1, d2 = st.columns([1.1, 1])
    with d1:
        progress_card("Contributing Factors", [
            (name, value * 100, f"{value * 100:.0f}%") for name, value in result["drivers"].items()
        ])
    with d2:
        section_header("Business Recommendation", "Next best action")
        callout(result["recommendation"], tone="success" if result["responds"] else "warning",
                title=("Include in campaign" if result["responds"] else "Hold from paid targeting"))
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        st.plotly_chart(
            charts.bar_chart(
                list(result["drivers"].keys()),
                [round(v * 100, 1) for v in result["drivers"].values()],
                height=250, horizontal=True,
            ),
            use_container_width=True, config=PLOT_CONFIG,
        )
