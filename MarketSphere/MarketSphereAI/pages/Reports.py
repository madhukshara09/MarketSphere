"""Reporting centre with generation, preview and export actions."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from utils import charts
from utils.components import badge, callout, data_table, page_header, section_header
from utils.helpers import (
    campaign_performance, format_currency, format_percent, load_customers, monthly_revenue,
)

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}

REPORT_DEFINITIONS = [
    {
        "key": "customer",
        "title": "Customer Report",
        "summary": "Segment composition, lifetime value distribution and engagement recency across the full customer base.",
        "pages": 14,
        "tone": "primary",
    },
    {
        "key": "campaign",
        "title": "Campaign Report",
        "summary": "Channel level spend, conversion, revenue and return on investment for the current reporting period.",
        "pages": 11,
        "tone": "success",
    },
    {
        "key": "executive",
        "title": "Executive Report",
        "summary": "Board ready overview combining revenue trajectory, retention health and prioritised recommendations.",
        "pages": 8,
        "tone": "warning",
    },
]


def _dummy_pdf(title: str) -> bytes:
    """Return a minimal valid single-page PDF containing the report title."""
    text = f"{title} - MarketSphere AI - {datetime.today():%d %B %Y}"
    content = f"BT /F1 14 Tf 60 760 Td ({text}) Tj ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        "/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = "%PDF-1.4\n"
    offsets = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n{body}\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    out += "".join(f"{offset:010d} 00000 n \n" for offset in offsets)
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF")
    return out.encode("latin-1")


def _report_frame(key: str) -> pd.DataFrame:
    """Build the preview table for a report type."""
    customers = load_customers()
    if key == "customer":
        frame = customers.groupby("Customer_Segment").agg(
            Customers=("ID", "count"),
            AvgCLV=("Predicted_CLV", "mean"),
            AvgIncome=("Income", "mean"),
            AvgRecency=("Recency", "mean"),
        ).reset_index()
        frame["AvgCLV"] = frame["AvgCLV"].apply(format_currency)
        frame["AvgIncome"] = frame["AvgIncome"].apply(format_currency)
        frame["AvgRecency"] = frame["AvgRecency"].round(0).astype(int).astype(str) + " days"
        return frame.rename(columns={
            "Customer_Segment": "Segment", "AvgCLV": "Average CLV",
            "AvgIncome": "Average Income", "AvgRecency": "Average Recency",
        })
    if key == "campaign":
        frame = campaign_performance().copy()
        frame["Spend"] = frame["Spend"].apply(format_currency)
        frame["Revenue"] = frame["Revenue"].apply(format_currency)
        frame["Conversion Rate"] = frame["Conversion Rate"].apply(lambda v: format_percent(v))
        frame["ROI"] = frame["ROI"].apply(lambda v: format_percent(v, 0))
        return frame[["Channel", "Reached", "Converted", "Conversion Rate", "Spend", "Revenue", "ROI"]]
    revenue = monthly_revenue()
    frame = revenue.copy()
    frame["Variance"] = ((frame["Revenue"] - frame["Target"]) / frame["Target"] * 100).round(1).astype(str) + "%"
    frame["Revenue"] = frame["Revenue"].apply(format_currency)
    frame["Target"] = frame["Target"].apply(format_currency)
    return frame


def render() -> None:
    """Render the reports page."""
    page_header(
        "Reports",
        "Generate, preview and export analytical reports for internal distribution.",
        chip="Export centre",
    )

    section_header("Report Library", "Three standard templates")
    columns = st.columns(3)
    for column, definition in zip(columns, REPORT_DEFINITIONS):
        with column:
            st.markdown(
                f"""
                <div class="ms-card ms-anim">
                  <div style="display:flex;align-items:center;justify-content:space-between">
                    <div class="ms-section-title">{definition['title']}</div>
                    {badge(f"{definition['pages']} pages", definition['tone'])}
                  </div>
                  <div class="ms-item-text" style="margin-top:10px;min-height:66px">{definition['summary']}</div>
                  <div class="ms-note" style="margin-top:8px">Last generated {datetime.today():%d %b %Y}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Generate Report", key=f"gen_{definition['key']}", use_container_width=True):
                st.session_state["active_report"] = definition["key"]

            frame = _report_frame(definition["key"])
            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "Download PDF", data=_dummy_pdf(definition["title"]),
                    file_name=f"marketsphere_{definition['key']}_report.pdf",
                    mime="application/pdf", key=f"pdf_{definition['key']}", use_container_width=True,
                )
            with d2:
                st.download_button(
                    "Download CSV", data=frame.to_csv(index=False).encode("utf-8"),
                    file_name=f"marketsphere_{definition['key']}_report.csv",
                    mime="text/csv", key=f"csv_{definition['key']}", use_container_width=True,
                )

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    active = st.session_state.get("active_report")
    if not active:
        callout("Select a template and generate a report to display the preview below.",
                title="No report generated")
        return

    definition = next(d for d in REPORT_DEFINITIONS if d["key"] == active)
    section_header(f"{definition['title']} Preview", f"Generated {datetime.today():%d %B %Y at %H:%M}")

    p1, p2 = st.columns([1.4, 1])
    with p1:
        data_table(_report_frame(active))
    with p2:
        if active == "customer":
            counts = load_customers()["Customer_Segment"].value_counts()
            st.plotly_chart(charts.pie_chart(counts.index.tolist(), counts.values.tolist(), height=340),
                            use_container_width=True, config=PLOT_CONFIG)
        elif active == "campaign":
            frame = campaign_performance()
            st.plotly_chart(charts.bar_chart(frame["Channel"], frame["ROI"], height=340, text_format="%{y:.0f}%"),
                            use_container_width=True, config=PLOT_CONFIG)
        else:
            revenue = monthly_revenue()
            st.plotly_chart(charts.area_chart(revenue["Month"], {"Revenue": revenue["Revenue"]}, height=340),
                            use_container_width=True, config=PLOT_CONFIG)

    callout(
        "This preview is generated from the local demonstration dataset. Exported documents are "
        "placeholder artefacts intended for interface demonstration only.",
        title="Preview notice",
    )
