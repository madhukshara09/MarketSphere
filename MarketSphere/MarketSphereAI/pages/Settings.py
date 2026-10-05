"""Workspace settings, preferences and product information."""

from __future__ import annotations

import streamlit as st

from utils.components import callout, page_header, section_header, stat_card
from utils.helpers import APP_VERSION, COMPANY_NAME


def render() -> None:
    """Render the settings page."""
    page_header(
        "Settings",
        "Manage workspace preferences, notifications and account information.",
        chip="Administrator access",
    )

    tabs = st.tabs(["Appearance", "Notifications", "Profile", "Application", "About"])

    with tabs[0]:
        section_header("Theme", "Interface presentation")
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Theme mode", ["Midnight (default)", "Slate", "Carbon"], index=0)
            st.selectbox("Accent colour", ["Blue", "Emerald", "Amber", "Rose"], index=0)
        with c2:
            st.selectbox("Density", ["Comfortable", "Compact"], index=0)
            st.selectbox("Chart palette", ["Enterprise", "High contrast", "Monochrome"], index=0)
        st.toggle("Enable card hover animations", value=True)
        st.toggle("Reduce motion", value=False)
        callout("Theme changes apply to the current browser session only in this demonstration build.")

    with tabs[1]:
        section_header("Notifications", "Alerting preferences")
        c1, c2 = st.columns(2)
        with c1:
            st.toggle("Email digest", value=True)
            st.toggle("Campaign threshold alerts", value=True)
            st.toggle("Weekly executive summary", value=False)
        with c2:
            st.toggle("Churn spike warnings", value=True)
            st.toggle("Budget consumption alerts", value=True)
            st.toggle("Product announcements", value=False)
        st.slider("Alert sensitivity", 1, 10, 6)
        st.text_input("Distribution list", value="analytics-team@marketsphere.ai")

    with tabs[2]:
        section_header("Profile", "Account details")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Full name", value=st.session_state.get("username", "Alex Morgan").title())
            st.text_input("Email address", value="alex.morgan@marketsphere.ai")
            st.selectbox("Role", ["Marketing Director", "Analyst", "Administrator", "Viewer"], index=0)
        with c2:
            st.text_input("Department", value="Growth Marketing")
            st.selectbox("Time zone", ["UTC", "Europe/London", "America/New_York", "Asia/Kolkata"], index=3)
            st.selectbox("Language", ["English", "Spanish", "German", "French", "Hindi"], index=0)
        st.button("Save profile changes")

    with tabs[3]:
        section_header("Application Settings", "Workspace defaults")
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Default landing page", ["Dashboard", "Decision Impact Engine", "Reports"], index=0)
            st.selectbox("Currency", ["USD", "EUR", "GBP", "INR"], index=0)
            st.selectbox("Date format", ["DD MMM YYYY", "MM/DD/YYYY", "YYYY-MM-DD"], index=0)
        with c2:
            st.number_input("Records per table page", 10, 500, 200, step=10)
            st.selectbox("Data refresh interval", ["Manual", "Every 15 minutes", "Hourly", "Daily"], index=1)
            st.toggle("Cache generated reports", value=True)
        st.text_input("Prediction service endpoint", value="https://api.marketsphere.ai/v1",
                      help="Placeholder for future backend integration. Not called in this build.")
        # Future FastAPI Integration
        # response = requests.post(f"{endpoint}/predict", json=input_data)
        # prediction = response.json()

    with tabs[4]:
        section_header("About", "Product and company information")
        c1, c2, c3 = st.columns(3)
        with c1:
            stat_card("Application Version", APP_VERSION, "Enterprise edition")
        with c2:
            stat_card("Build Channel", "Stable", "Integrated ML application", "success")
        with c3:
            stat_card("Data Source", "Marketing Campaign dataset", "Local processed customer records", "warning")

        st.markdown(
            f"""
            <div class="ms-card ms-anim" style="margin-top:16px">
              <div class="ms-section-title">Company Information</div>
              <div style="font-size:0.86rem;color:#CBD5E1;line-height:2.1;margin-top:10px">
                Organisation<span style="float:right;color:#fff;font-weight:600">{COMPANY_NAME}</span><br>
                Product<span style="float:right;color:#fff;font-weight:600">MarketSphere AI Analytics Platform</span><br>
                Support<span style="float:right;color:#fff;font-weight:600">support@marketsphere.ai</span><br>
                Licence<span style="float:right;color:#fff;font-weight:600">Enterprise, seat based</span><br>
                Region<span style="float:right;color:#fff;font-weight:600">Global, multi tenant</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        callout(
            "This application uses the repository's trained segmentation, CLV-proxy and campaign-response "
            "models. Re-run train_models.py after changing the processed dataset.",
            title="Implementation notice",
        )
