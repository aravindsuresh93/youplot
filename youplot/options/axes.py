"""Axis and Scale configuration."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AxisOptions:
    label: str = ""
    format: str = ""             # tick format string e.g. "%d %b", ".2f"
    range: list | None = None    # [min, max] — None = auto
    ticks: int | list | None = None
    tick_size: int = 11
    side: str = "left"           # "left" or "right"
    show: bool = True


@dataclass
class ScaleOptions:
    name: str = ""               # internal scale id
    range: list | None = None
    auto: bool = True
