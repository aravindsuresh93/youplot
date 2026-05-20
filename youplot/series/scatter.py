"""
ScatterSeries — represents one scatter series on the chart.
Scatter in uPlot is rendered via a custom canvas plugin (no native scatter).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScatterSeries:
    # ── Required ──────────────────────────────────────────────────────────────
    x: Any                              # array-like: x values
    y: Any                              # array-like: y values

    # ── Identity ──────────────────────────────────────────────────────────────
    label: str = ""

    # ── Point appearance ──────────────────────────────────────────────────────
    color: str = ""                     # resolved hex — set by Figure if empty
    size: float = 6.0                   # dot radius in px
    opacity: float = 0.85               # fill opacity

    # Shape: "circle" | "square" | "triangle" | "diamond" | "cross" | "star"
    shape: str = "circle"

    # Outline
    stroke: str = ""                    # border color — defaults to color (darker)
    stroke_width: float = 1.0          # border width (0 = no border)

    # ── Size encoding — map a third array to point size ───────────────────────
    size_by: Any = None                 # array-like — values mapped to point sizes
    size_range: list[float] = field(default_factory=lambda: [3.0, 18.0])  # [min_px, max_px]

    # ── Color encoding — map a third array to point color (gradient) ──────────
    color_by: Any = None                # array-like — values mapped to color scale
    color_scale: list[str] = field(default_factory=lambda: ["#6366f1", "#f43f5e"])  # [low, high]

    # ── Axis binding ──────────────────────────────────────────────────────────
    axis: str = "left"
    scale: str = ""

    # ── Regression line ───────────────────────────────────────────────────────
    trendline: bool = False             # draw linear regression line
    trendline_color: str = ""           # defaults to series color
    trendline_width: float = 1.5
    trendline_dash: bool = True

    # ── Hover ─────────────────────────────────────────────────────────────────
    hover_format: str = ""
    hover_unit: str = ""
    hover_x_label: str = "x"           # label for x value in tooltip
    hover_y_label: str = "y"           # label for y value in tooltip

    # ── Labels on points ──────────────────────────────────────────────────────
    labels: Any = None                  # array-like of strings — shown next to each point
    label_font_size: int = 9
    label_color: str = ""               # defaults to color

    # ── Jitter — avoid overplotting ───────────────────────────────────────────
    jitter_x: float = 0.0              # random x offset in data units
    jitter_y: float = 0.0              # random y offset in data units

    # ── Internal ──────────────────────────────────────────────────────────────
    _scale_name: str = field(default="", init=False, repr=False)

    def resolved_stroke(self) -> str:
        """Border color — slightly darker version of fill color if not set."""
        return self.stroke if self.stroke else self.color

    def resolved_trendline_color(self) -> str:
        return self.trendline_color if self.trendline_color else self.color

    def resolved_label_color(self) -> str:
        return self.label_color if self.label_color else self.color
