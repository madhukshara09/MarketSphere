"""MarketSphere AI - enterprise marketing analytics platform (frontend only).

Run with:  streamlit run app.py

Architecture
------------
app.py           Authentication gate, custom sidebar navigation, page router.
pages/           One module per workspace page, each exposing render().
utils/           Reusable components, chart factory and helper functions.
data/            Local mock data generation (300 realistic customers).
assets/          Stylesheet and brand imagery.

No backend, no database and no machine learning models are used. Prediction
surfaces rely on transparent local heuristics and carry integration
placeholders for a future service layer.
"""

from __future__ import annotations

import os
import sys

import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add MarketSphere project root so backend/ and models/ can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pages import (  # noqa: E402
    CLV_Prediction, Customer_Segmentation, Dashboard, Decision_Impact,
    Reports, Response_Prediction, Settings,
)
from utils.components import icon, sidebar_brand, sidebar_footer  # noqa: E402
from utils.helpers import ASSETS_DIR, load_css  # noqa: E402
from backend.data_validator import load_csv  # noqa: E402
from backend.model_service import score_dataset  # noqa: E402

st.set_page_config(
    page_title="MarketSphere AI | Marketing Intelligence Platform",
    page_icon=os.path.join(ASSETS_DIR, "logo.png") if os.path.exists(os.path.join(ASSETS_DIR, "logo.png")) else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css(os.path.join(ASSETS_DIR, "style.css"))

# Navigation registry: label, icon key, render callable.
NAV_ITEMS = [
    ("Dashboard", "dashboard", Dashboard.render),
    ("Customer Segmentation", "segments", Customer_Segmentation.render),
    ("Campaign Response Prediction", "target", Response_Prediction.render),
    ("CLV Prediction", "value", CLV_Prediction.render),
    ("Decision Impact Engine", "engine", Decision_Impact.render),
    ("Reports", "reports", Reports.render),
    ("Settings", "settings", Settings.render),
]

DEMO_CREDENTIALS = {"admin": "admin123", "analyst": "analyst123"}


def init_state() -> None:
    """Initialise session defaults."""
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("active_page", "Dashboard")
    st.session_state.setdefault("active_dataset", None)
    st.session_state.setdefault("active_dataset_name", "Built-in marketing campaign dataset")


def dataset_controls() -> None:
    """Allow a compatible CSV to be used across the whole workspace."""
    st.sidebar.markdown('<div class="ms-nav-label">Data source</div>', unsafe_allow_html=True)
    uploaded = st.sidebar.file_uploader(
        "Upload marketing CSV", type=["csv"], key="marketing_dataset_upload",
        help="Supports the processed project schema or the original marketing-campaign columns.",
    )
    if uploaded is not None:
        st.sidebar.caption(f"Selected: {uploaded.name}")
        if st.sidebar.button("Run models on uploaded data", key="score_uploaded_data", width="stretch"):
            try:
                with st.spinner("Preparing data and running trained models..."):
                    st.session_state["active_dataset"] = score_dataset(load_csv(uploaded))
                st.session_state["active_dataset_name"] = uploaded.name
                st.sidebar.success(f"Scored {len(st.session_state['active_dataset']):,} records")
            except Exception as error:
                st.sidebar.error(f"Upload could not be scored: {error}")

    if st.sidebar.button("Use built-in dataset", key="use_default_dataset", width="stretch"):
        st.session_state["active_dataset"] = None
        st.session_state["active_dataset_name"] = "Built-in marketing campaign dataset"
        st.rerun()
    st.sidebar.caption(f"Active: {st.session_state['active_dataset_name']}")


def login_page() -> None:
    """Render the glassmorphism login screen."""
    st.markdown('<div style="height:4vh"></div>', unsafe_allow_html=True)
    hero, spacer, form = st.columns([1.15, 0.12, 0.85])

    with hero:
        st.markdown(
            f"""
            <div class="ms-hero-panel">
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:22px">
                <div class="ms-brand-mark">{icon('spark', 22, '#0F172A')}</div>
                <div>
                  <div class="ms-brand-title" style="font-size:1.1rem">MarketSphere AI</div>
                  <div class="ms-brand-sub">Marketing Intelligence</div>
                </div>
              </div>
              <div class="ms-hero-title">Decisions backed by<br>every customer signal.</div>
              <div class="ms-hero-text">
                A unified analytics workspace for segmentation, campaign response scoring,
                lifetime value forecasting and executive decision simulation.
              </div>
              <div class="ms-hero-stats">
                <div><div class="ms-hero-stat-v">300+</div><div class="ms-hero-stat-l">Customers tracked</div></div>
                <div><div class="ms-hero-stat-v">6</div><div class="ms-hero-stat-l">Marketing channels</div></div>
                <div><div class="ms-hero-stat-v">5</div><div class="ms-hero-stat-l">Behavioural segments</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with form:
        st.markdown('<div class="ms-login-wrap"><div class="ms-login-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="ms-login-title">Sign in</div>'
            '<div class="ms-login-sub">Access your marketing intelligence workspace.</div>',
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            remember = st.checkbox("Keep me signed in", value=True)
            submitted = st.form_submit_button("Log in", use_container_width=True)

        if submitted:
            if DEMO_CREDENTIALS.get(username.strip()) == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username.strip().title()
                st.session_state["active_page"] = "Dashboard"
                st.rerun()
            else:
                st.markdown(
                    '<div class="ms-callout ms-callout-danger" style="margin-top:12px">'
                    'Invalid credentials. Use one of the demonstration accounts below.</div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<div class="ms-hint">Demonstration accounts &mdash; '
            'admin / admin123 &nbsp;&middot;&nbsp; analyst / analyst123</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div></div>", unsafe_allow_html=True)
        _ = remember  # Placeholder for future persistent session handling.


def sidebar_navigation() -> None:
    """Render the custom sidebar and handle navigation state."""
    sidebar_brand()
    st.sidebar.markdown('<div class="ms-nav-label">Workspace</div>', unsafe_allow_html=True)

    for label, _icon_key, _render in NAV_ITEMS:
        is_active = st.session_state["active_page"] == label
        if st.sidebar.button(label, key=f"nav_{label}", use_container_width=True,
                             type="primary" if is_active else "secondary"):
            st.session_state["active_page"] = label
            st.rerun()

    dataset_controls()

    if sidebar_footer(st.session_state.get("username") or "Guest User"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()


def main() -> None:
    """Application entry point."""
    init_state()

    if not st.session_state["authenticated"]:
        login_page()
        return

    sidebar_navigation()
    active = st.session_state["active_page"]
    renderer = dict((label, fn) for label, _icon_key, fn in NAV_ITEMS).get(active, Dashboard.render)
    renderer()


if __name__ == "__main__":
    main()
