"""
Theme tokens for youplot.
Each theme defines colors for every visual element.
CSS and JS pull from these — nothing is hardcoded elsewhere.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Theme:
    name: str

    # Page / container
    bg_page: str          # outer page background
    bg_chart: str         # chart card background
    border: str           # card border color

    # Text
    text_title: str
    text_subtitle: str
    text_axis_label: str
    text_tick: str
    text_legend: str
    text_tooltip: str
    text_tooltip_label: str

    # Grid & axes
    grid_color: str
    axis_stroke: str
    tick_stroke: str

    # Tooltip
    tooltip_bg: str
    tooltip_border: str
    tooltip_shadow: str

    # Annotation defaults
    vline_color: str
    hline_color: str
    region_color: str


LIGHT = Theme(
    name="light",

    bg_page="#f8fafc",        # cool slate-50 — not warm, not pure white
    bg_chart="#ffffff",
    border="rgba(0,0,0,0.07)",

    text_title="#0f172a",     # slate-900
    text_subtitle="#64748b",  # slate-500
    text_axis_label="#475569",# slate-600
    text_tick="#94a3b8",      # slate-400
    text_legend="#64748b",
    text_tooltip="#f1f5f9",   # light on dark tooltip
    text_tooltip_label="#94a3b8",

    grid_color="rgba(0,0,0,0.05)",
    axis_stroke="#cbd5e1",    # slate-300
    tick_stroke="#e2e8f0",    # slate-200

    tooltip_bg="rgba(255,255,255,0.72)",  # glass: frosted white
    tooltip_border="rgba(0,0,0,0.08)",
    tooltip_shadow="0 4px 24px rgba(0,0,0,0.12), 0 1px 0 rgba(255,255,255,0.9) inset",

    vline_color="#94a3b8",
    hline_color="#94a3b8",
    region_color="#6366f1",
)

DARK = Theme(
    name="dark",

    bg_page="#0a0a0f",        # near-black with slight blue tint
    bg_chart="#111118",       # slightly lighter than page
    border="rgba(255,255,255,0.07)",

    text_title="#f1f5f9",     # slate-100
    text_subtitle="#64748b",
    text_axis_label="#475569",
    text_tick="#334155",      # slate-700
    text_legend="#64748b",
    text_tooltip="#f1f5f9",
    text_tooltip_label="#475569",

    grid_color="rgba(255,255,255,0.04)",
    axis_stroke="#1e293b",    # slate-800
    tick_stroke="#1e293b",

    tooltip_bg="rgba(15,20,40,0.72)",  # glass: dark frosted
    tooltip_border="rgba(255,255,255,0.15)",
    tooltip_shadow="0 4px 24px rgba(0,0,0,0.4), 0 1px 0 rgba(255,255,255,0.07) inset",

    vline_color="#334155",
    hline_color="#334155",
    region_color="#6366f1",
)


def get(name: str) -> Theme:
    if name == "dark":
        return DARK
    return LIGHT
