"""Reusable presentation components rendered with custom HTML + CSS."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from utils.helpers import APP_VERSION

# Inline SVG icon set (no emojis anywhere in the product).
ICONS = {
    "dashboard": '<path d="M3 3h8v8H3V3zm10 0h8v5h-8V3zM3 13h8v8H3v-8zm10 3h8v5h-8v-5z"/>',
    "segments": '<path d="M12 2a10 10 0 1 0 10 10h-10V2z"/><path d="M14 2v8h8A10 10 0 0 0 14 2z" opacity=".55"/>',
    "target": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="1.4"/>',
    "value": '<path d="M12 1v22M17 6.5c0-2-2.2-3.2-5-3.2S7 4.5 7 6.4c0 4.6 10 2.6 10 7.2 0 2-2.2 3.3-5 3.3s-5-1.3-5-3.3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "engine": '<path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm9.4 4a9.4 9.4 0 0 0-.14-1.6l2.06-1.6-2-3.46-2.44 1a9.5 9.5 0 0 0-2.77-1.6L15.7 2h-4l-.4 2.74a9.5 9.5 0 0 0-2.77 1.6l-2.44-1-2 3.46 2.06 1.6a9.6 9.6 0 0 0 0 3.2L4.09 15.2l2 3.46 2.44-1a9.5 9.5 0 0 0 2.77 1.6l.4 2.74h4l.4-2.74a9.5 9.5 0 0 0 2.77-1.6l2.44 1 2-3.46-2.06-1.6c.09-.52.14-1.06.14-1.6z" opacity=".9"/>',
    "reports": '<path d="M6 2h8l6 6v14H6V2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M14 2v6h6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 13h7M9 17h7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "settings": '<circle cx="12" cy="12" r="3.2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 12h2M18 12h2M12 4v2M12 18v2M6.3 6.3l1.4 1.4M16.3 16.3l1.4 1.4M17.7 6.3l-1.4 1.4M7.7 16.3l-1.4 1.4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "users": '<path d="M8 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm0 2c-3.3 0-6 1.8-6 4v3h12v-3c0-2.2-2.7-4-6-4zm9-2a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm5 9v-2.5c0-1.9-2-3.5-4.6-3.5-.7 0-1.4.1-2 .3 1 .9 1.6 2 1.6 3.2V20h5z"/>',
    "revenue": '<path d="M3 17l6-6 4 4 8-8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 7h6v6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
    "check": '<path d="M20 6L9 17l-5-5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
    "shield": '<path d="M12 2l8 3.5v6c0 5-3.4 9.3-8 10.5-4.6-1.2-8-5.5-8-10.5v-6L12 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    "logout": '<path d="M14 3h5a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M10 17l-5-5 5-5M5 12h11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "spark": '<path d="M12 2l2.2 6.1L20 10l-5.8 1.9L12 18l-2.2-6.1L4 10l5.8-1.9L12 2z"/>',
    "bell": '<path d="M18 15V10a6 6 0 0 0-12 0v5l-2 3h16l-2-3zM10 21h4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
}


def icon(name: str, size: int = 18, color: str = "#93C5FD") -> str:
    """Return an inline SVG icon string."""
    path = ICONS.get(name, ICONS["spark"])
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" '
        f'style="display:block">{path}</svg>'
    )


def page_header(title: str, subtitle: str, chip: str | None = None) -> None:
    """Render a consistent page title block."""
    chip_html = (
        f'<div class="ms-chip"><span class="ms-dot"></span>{html.escape(chip)}</div>' if chip else ""
    )
    st.markdown(
        f"""
        <div class="ms-page-head ms-anim">
          <div>
            <h1 class="ms-page-title">{html.escape(title)}</h1>
            <p class="ms-page-sub">{html.escape(subtitle)}</p>
          </div>
          {chip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str = "") -> None:
    """Render a small section divider heading."""
    note_html = f'<div class="ms-section-sub">{html.escape(note)}</div>' if note else ""
    st.markdown(
        f'<div class="ms-section"><div class="ms-section-bar"></div>'
        f'<div class="ms-section-title">{html.escape(title)}</div>{note_html}</div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, description: str, trend: float | None = None,
                icon_name: str = "spark", trend_suffix: str = "vs last month") -> None:
    """Premium KPI card with trend indicator and hover animation."""
    trend_html = ""
    if trend is not None:
        if trend > 0:
            cls, arrow = "ms-trend-up", "&#9650;"
        elif trend < 0:
            cls, arrow = "ms-trend-down", "&#9660;"
        else:
            cls, arrow = "ms-trend-flat", "&#9644;"
        trend_html = (
            f'<div class="ms-trend {cls}">{arrow} {abs(trend):.1f}% '
            f'<span style="opacity:.75;font-weight:500">{html.escape(trend_suffix)}</span></div>'
        )
    st.markdown(
        f"""
        <div class="ms-card ms-kpi ms-anim">
          <div class="ms-kpi-top">
            <div class="ms-kpi-label">{html.escape(label)}</div>
            <div class="ms-kpi-icon">{icon(icon_name)}</div>
          </div>
          <div class="ms-kpi-value">{html.escape(value)}</div>
          <div class="ms-kpi-desc">{html.escape(description)}</div>
          {trend_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, note: str = "", tone: str = "primary") -> None:
    """Compact statistic card."""
    colors = {"primary": "#60A5FA", "success": "#34D399", "warning": "#FBBF24", "danger": "#F87171", "neutral": "#CBD5E1"}
    color = colors.get(tone, colors["primary"])
    note_html = f'<div class="ms-kpi-desc" style="margin-top:6px">{html.escape(note)}</div>' if note else ""
    st.markdown(
        f"""
        <div class="ms-card ms-anim">
          <div class="ms-kpi-label">{html.escape(label)}</div>
          <div style="font-size:1.5rem;font-weight:700;color:{color};margin-top:8px">{html.escape(value)}</div>
          {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_open(padding: str = "20px 22px") -> None:
    """Open a glass card container."""
    st.markdown(f'<div class="ms-card ms-anim" style="padding:{padding}">', unsafe_allow_html=True)


def card_close() -> None:
    """Close a glass card container."""
    st.markdown("</div>", unsafe_allow_html=True)


def list_card(title: str, items: list[dict], subtitle: str = "") -> None:
    """Card containing a list of titled entries (insights, activity, recommendations)."""
    tone_colors = {"primary": "#2563EB", "success": "#10B981", "warning": "#F59E0B",
                   "danger": "#EF4444", "neutral": "#64748B"}
    rows = []
    for item in items:
        color = tone_colors.get(item.get("tone", "primary"), tone_colors["primary"])
        meta = f'<div class="ms-item-meta">{html.escape(item["meta"])}</div>' if item.get("meta") else ""
        rows.append(
            f'<div class="ms-list-item"><div class="ms-bullet" style="background:{color}"></div>'
            f'<div style="flex:1"><div class="ms-item-title">{html.escape(item["title"])}</div>'
            f'<div class="ms-item-text">{html.escape(item.get("text", ""))}</div></div>{meta}</div>'
        )
    sub = f'<div class="ms-kpi-desc" style="margin-bottom:6px">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="ms-card ms-anim"><div class="ms-section" style="margin-top:0">'
        f'<div class="ms-section-bar"></div><div class="ms-section-title">{html.escape(title)}</div></div>'
        f'{sub}{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def progress_bar(name: str, value: float, display: str | None = None, tone: str = "primary") -> str:
    """Return HTML for a single labelled progress bar (0-100)."""
    tone_colors = {
        "primary": "linear-gradient(90deg,#2563EB,#60A5FA)",
        "success": "linear-gradient(90deg,#10B981,#6EE7B7)",
        "warning": "linear-gradient(90deg,#F59E0B,#FCD34D)",
        "danger": "linear-gradient(90deg,#EF4444,#FCA5A5)",
    }
    pct = max(0.0, min(float(value), 100.0))
    text = display if display is not None else f"{pct:.0f}%"
    return (
        f'<div class="ms-progress-row"><div class="ms-progress-top">'
        f'<span class="ms-progress-name">{html.escape(name)}</span>'
        f'<span class="ms-progress-val">{html.escape(text)}</span></div>'
        f'<div class="ms-progress-track"><div class="ms-progress-fill" '
        f'style="width:{pct}%;background:{tone_colors.get(tone, tone_colors["primary"])}"></div></div></div>'
    )


def progress_card(title: str, rows: list[tuple], tone: str = "primary") -> None:
    """Card of progress bars. Each row is (name, value 0-100, optional display)."""
    bars = "".join(
        progress_bar(row[0], row[1], row[2] if len(row) > 2 else None, tone) for row in rows
    )
    st.markdown(
        f'<div class="ms-card ms-anim"><div class="ms-section" style="margin-top:0">'
        f'<div class="ms-section-bar"></div><div class="ms-section-title">{html.escape(title)}</div></div>'
        f'{bars}</div>',
        unsafe_allow_html=True,
    )


def badge(text: str, tone: str = "primary") -> str:
    """Return badge HTML."""
    return f'<span class="ms-badge ms-badge-{tone}">{html.escape(str(text))}</span>'


def callout(text: str, tone: str = "primary", title: str = "") -> None:
    """Render a coloured callout block."""
    suffix = "" if tone == "primary" else f" ms-callout-{tone}"
    title_html = f'<div style="font-weight:650;color:#fff;margin-bottom:4px">{html.escape(title)}</div>' if title else ""
    st.markdown(
        f'<div class="ms-callout{suffix} ms-anim">{title_html}{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def data_table(frame: pd.DataFrame, badge_columns: dict | None = None, max_rows: int = 200) -> None:
    """Render a styled HTML table with optional badge-rendered columns.

    badge_columns maps a column name to a callable returning a tone string.
    """
    badge_columns = badge_columns or {}
    head = "".join(f"<th>{html.escape(str(col))}</th>" for col in frame.columns)
    body = []
    for _, row in frame.head(max_rows).iterrows():
        cells = []
        for col in frame.columns:
            raw = row[col]
            if col in badge_columns:
                cells.append(f"<td>{badge(raw, badge_columns[col](raw))}</td>")
            else:
                cells.append(f"<td>{html.escape(str(raw))}</td>")
        body.append(f"<tr>{''.join(cells)}</tr>")
    st.markdown(
        f'<div class="ms-table-wrap ms-anim"><table class="ms-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    """Render the sidebar logo and product name."""
    st.sidebar.markdown(
        f'<div class="ms-brand"><div class="ms-brand-mark">{icon("spark", 21, "#0F172A")}</div>'
        f'<div><div class="ms-brand-title">MarketSphere AI</div>'
        f'<div class="ms-brand-sub">Marketing Intelligence</div></div></div>',
        unsafe_allow_html=True,
    )


def sidebar_footer(user: str, role: str = "Marketing Director") -> bool:
    """Render the sidebar profile block. Returns True when logout is clicked."""
    initials = "".join(part[0] for part in user.split()[:2]).upper() or "MS"
    st.sidebar.markdown('<div class="ms-side-foot">', unsafe_allow_html=True)
    st.sidebar.markdown(
        f'<div class="ms-profile"><div class="ms-avatar">{html.escape(initials)}</div>'
        f'<div><div class="ms-profile-name">{html.escape(user)}</div>'
        f'<div class="ms-profile-role">{html.escape(role)}</div></div></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f'<div class="ms-version">Version {APP_VERSION} &middot; Enterprise</div>',
        unsafe_allow_html=True,
    )
    clicked = st.sidebar.button("Sign out", key="ms_logout", use_container_width=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    return clicked
