"""Plotly chart factory. Every chart shares one dark enterprise theme."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from utils.helpers import SEGMENT_COLORS

FONT = "Inter, sans-serif"
GRID = "rgba(51, 65, 85, 0.55)"
TEXT = "#CBD5E1"
PRIMARY = "#2563EB"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"
SERIES = ["#2563EB", "#10B981", "#38BDF8", "#F59E0B", "#EF4444", "#A78BFA"]


def _base_layout(fig: go.Figure, height: int = 320, show_legend: bool = True) -> go.Figure:
    """Apply the shared dark theme to a figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=18, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=TEXT, size=12),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor="#111827", bordercolor="#334155", font=dict(family=FONT, color="#fff")),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(size=11))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(size=11))
    return fig


def pie_chart(labels, values, height: int = 320, hole: float = 0.0, colors=None) -> go.Figure:
    """Pie chart (set hole > 0 for a donut)."""
    colors = colors or [SEGMENT_COLORS.get(str(l), SERIES[i % len(SERIES)]) for i, l in enumerate(labels)]
    fig = go.Figure(go.Pie(
        labels=list(labels), values=list(values), hole=hole,
        marker=dict(colors=colors, line=dict(color="#0F172A", width=2)),
        textinfo="percent", textfont=dict(size=12, color="#fff"),
        hovertemplate="<b>%{label}</b><br>%{value:,} customers<br>%{percent}<extra></extra>",
    ))
    return _base_layout(fig, height)


def donut_chart(labels, values, height: int = 320, center_text: str = "") -> go.Figure:
    """Donut chart with optional centred label."""
    fig = pie_chart(labels, values, height, hole=0.62)
    if center_text:
        fig.add_annotation(text=center_text, x=0.5, y=0.5, showarrow=False,
                           font=dict(size=17, color="#fff", family=FONT))
    return fig


def bar_chart(x, y, height: int = 320, name: str = "Value", color: str = PRIMARY,
              horizontal: bool = False, text_format: str = "%{y:,.0f}") -> go.Figure:
    """Vertical or horizontal bar chart with rounded caps."""
    if horizontal:
        trace = go.Bar(x=list(y), y=list(x), orientation="h", name=name,
                       marker=dict(color=color, line=dict(width=0)),
                       hovertemplate="<b>%{y}</b><br>%{x:,.2f}<extra></extra>")
    else:
        trace = go.Bar(x=list(x), y=list(y), name=name,
                       marker=dict(color=color, line=dict(width=0)),
                       texttemplate=text_format, textposition="outside",
                       textfont=dict(color=TEXT, size=11),
                       hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>")
    fig = go.Figure(trace)
    fig.update_traces(marker_cornerradius=8)
    return _base_layout(fig, height, show_legend=False)


def grouped_bar_chart(categories, series: dict, height: int = 320) -> go.Figure:
    """Multi-series grouped bar chart."""
    fig = go.Figure()
    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Bar(
            x=list(categories), y=list(values), name=name,
            marker=dict(color=SERIES[i % len(SERIES)]), marker_cornerradius=7,
            hovertemplate="<b>%{x}</b><br>" + name + ": %{y:,.2f}<extra></extra>",
        ))
    fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.08)
    return _base_layout(fig, height)


def line_chart(x, series: dict, height: int = 320, fill: bool = False) -> go.Figure:
    """Multi-series line chart."""
    fig = go.Figure()
    for i, (name, values) in enumerate(series.items()):
        color = SERIES[i % len(SERIES)]
        fig.add_trace(go.Scatter(
            x=list(x), y=list(values), name=name, mode="lines+markers",
            line=dict(color=color, width=3, shape="spline", smoothing=0.6),
            marker=dict(size=6, color=color, line=dict(color="#0F172A", width=2)),
            fill="tozeroy" if fill else None,
            fillcolor=f"rgba(37,99,235,0.16)" if fill else None,
            hovertemplate="<b>%{x}</b><br>" + name + ": %{y:,.2f}<extra></extra>",
        ))
    return _base_layout(fig, height)


def area_chart(x, series: dict, height: int = 320, stacked: bool = False) -> go.Figure:
    """Filled area chart."""
    fills = ["rgba(37,99,235,0.28)", "rgba(16,185,129,0.24)", "rgba(245,158,11,0.22)"]
    fig = go.Figure()
    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Scatter(
            x=list(x), y=list(values), name=name, mode="lines",
            line=dict(color=SERIES[i % len(SERIES)], width=2.6, shape="spline", smoothing=0.6),
            fill="tonexty" if (stacked and i > 0) else "tozeroy",
            fillcolor=fills[i % len(fills)],
            stackgroup="one" if stacked else None,
            hovertemplate="<b>%{x}</b><br>" + name + ": %{y:,.2f}<extra></extra>",
        ))
    return _base_layout(fig, height)


def scatter_chart(frame: pd.DataFrame, x: str, y: str, color: str,
                  size: str | None = None, height: int = 420, hover: str | None = None) -> go.Figure:
    """Cluster scatter plot coloured by a categorical column."""
    fig = go.Figure()
    for i, group in enumerate(sorted(frame[color].unique())):
        subset = frame[frame[color] == group]
        marker_size = (
            np.clip(subset[size] / subset[size].max() * 22, 7, 24) if size else 11
        )
        fig.add_trace(go.Scatter(
            x=subset[x], y=subset[y], mode="markers", name=str(group),
            marker=dict(
                size=marker_size,
                color=SEGMENT_COLORS.get(str(group), SERIES[i % len(SERIES)]),
                opacity=0.82, line=dict(color="rgba(15,23,42,0.85)", width=1),
            ),
            text=subset[hover] if hover else None,
            hovertemplate=(
                (("<b>%{text}</b><br>") if hover else "")
                + f"{x}: %{{x:,.0f}}<br>{y}: %{{y:,.0f}}<extra>{group}</extra>"
            ),
        ))
    fig.update_layout(xaxis_title=x, yaxis_title=y)
    return _base_layout(fig, height)


def gauge_chart(value: float, title: str = "", maximum: float = 100,
                suffix: str = "%", height: int = 280, thresholds=(35, 70)) -> go.Figure:
    """Radial gauge with graded colour bands."""
    low, high = thresholds
    if value >= high:
        color = SUCCESS
    elif value >= low:
        color = WARNING
    else:
        color = DANGER
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix=suffix, font=dict(size=34, color="#fff", family=FONT)),
        title=dict(text=title, font=dict(size=13, color=TEXT, family=FONT)),
        gauge=dict(
            axis=dict(range=[0, maximum], tickcolor=TEXT, tickfont=dict(size=10, color="#64748B")),
            bar=dict(color=color, thickness=0.26),
            bgcolor="rgba(15,23,42,0.6)",
            borderwidth=0,
            steps=[
                dict(range=[0, maximum * low / 100], color="rgba(239,68,68,0.14)"),
                dict(range=[maximum * low / 100, maximum * high / 100], color="rgba(245,158,11,0.14)"),
                dict(range=[maximum * high / 100, maximum], color="rgba(16,185,129,0.14)"),
            ],
            threshold=dict(line=dict(color="#fff", width=3), thickness=0.8, value=value),
        ),
    ))
    return _base_layout(fig, height, show_legend=False)


def histogram(values, height: int = 300, bins: int = 24, color: str = PRIMARY, name: str = "") -> go.Figure:
    """Distribution histogram."""
    fig = go.Figure(go.Histogram(
        x=list(values), nbinsx=bins, name=name,
        marker=dict(color=color, line=dict(color="#0F172A", width=1)),
        hovertemplate="Range: %{x}<br>Customers: %{y}<extra></extra>",
    ))
    return _base_layout(fig, height, show_legend=False)
