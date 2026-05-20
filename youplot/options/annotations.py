"""Annotation types — overlays drawn on top of the chart."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class VLine:
    """Vertical line at a specific x value (timestamp or numeric)."""
    x: float | int
    label: str = ""
    color: str = "#94a3b8"
    width: float = 1.5
    dash: bool = True


@dataclass
class HLine:
    """Horizontal reference line at a specific y value."""
    y: float
    label: str = ""
    color: str = "#94a3b8"
    width: float = 1.5
    dash: bool = True
    scale: str = "left"


@dataclass
class Region:
    """Shaded vertical band between x_start and x_end."""
    x_start: float | int
    x_end: float | int
    label: str = ""
    color: str = "#6366f1"
    opacity: float = 0.08
    _tagId: str = ""
    _removable: bool = True


@dataclass
class Band:
    """Horizontal shaded band between y_lo and y_hi (threshold zone)."""
    y_lo: float
    y_hi: float
    label: str = ""
    color: str = "#6366f1"
    opacity: float = 0.12
    scale: str = "left"


@dataclass
class Pin:
    """Annotation pin dropped on the chart at a specific x position."""
    x: float | int          # unix ms for timeseries, numeric otherwise
    label: str = ""
    y_frac: float = 0.2    # vertical position as fraction of plot height (0=top, 1=bottom)
    color: str = ""         # empty = auto-assigned from palette
    y: float | None = None
    scale: str = "left"

