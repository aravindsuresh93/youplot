"""
LineSeries — represents one line on the chart.
All fields are optional except x and y.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LineSeries:
    # ── Required ──────────────────────────────────────────────────────────────
    x: Any                          # array-like: timestamps (ms), numeric, or datetime
    y: Any                          # array-like: numeric values

    # ── Identity ──────────────────────────────────────────────────────────────
    label: str = ""                 # legend + tooltip label

    # ── Appearance ────────────────────────────────────────────────────────────
    color: str = ""                 # resolved hex — set by Figure if empty
    width: float = 2.0             # stroke width in px
    opacity: float = 1.0           # line opacity 0–1

    # Dash pattern
    dash: bool | list[int] = False  # False=solid, True=[6,3], or custom [on,off]

    # Fill under line
    fill: bool = False              # gradient fill under line
    fill_opacity: float = 0.15     # max opacity of fill gradient
    fill_color: str = ""            # defaults to line color

    # ── Axis binding ──────────────────────────────────────────────────────────
    axis: str = "left"             # "left" or "right"
    scale: str = ""                # explicit scale name — auto-set if empty

    # ── Points ────────────────────────────────────────────────────────────────
    points: bool = False           # show dots at each data point
    points_size: float = 4.0      # dot radius in px
    points_color: str = ""         # defaults to line color
    points_filled: bool = True     # filled vs outline

    # ── Smoothing / shape ─────────────────────────────────────────────────────
    smooth: bool = False           # spline interpolation (uPlot path: spline)
    step: bool = False             # step line

    # ── Nulls & gaps ─────────────────────────────────────────────────────────
    gap_threshold: float | None = None   # seconds — break line if gap exceeds this
    null_handling: str = "gap"           # "gap" | "zero" | "ignore"

    # ── Tooltip ───────────────────────────────────────────────────────────────
    hover_format: str = ""         # e.g. ".2f" — python format spec
    hover_unit: str = ""           # suffix shown in tooltip e.g. "V", "%", "A"

    # ── Internal (set by Figure, not user) ────────────────────────────────────
    _scale_name: str = field(default="", init=False, repr=False)

    def resolved_dash(self) -> list[int] | None:
        """Return JS dash array or None for solid."""
        if self.dash is False:
            return None
        if self.dash is True:
            return [6, 3]
        return self.dash

    def resolved_fill_color(self) -> str:
        return self.fill_color if self.fill_color else self.color

    def resolved_points_color(self) -> str:
        return self.points_color if self.points_color else self.color
