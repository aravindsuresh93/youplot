"""
Figure — top-level user API for youplot.
Supports line and scatter series, mixed on the same chart.
"""

from __future__ import annotations
from typing import Any
from datetime import datetime, date

from youplot.series.line import LineSeries
from youplot.series.scatter import ScatterSeries
from youplot.options.annotations import VLine, HLine, Region, Band, Pin
from youplot.colors.palette import ColorCycle, resolve
from youplot.themes.base import get as get_theme
from youplot.utils.data import (
    to_float_list, to_timestamp_ms_list, validate_xy,
    inject_gaps, apply_null_handling,
)
from youplot.render.html import build_html
from youplot.utils.browser import show as _show, save as _save


class Figure:
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        theme: str = "light",
        width: int | str = "100%",
        height: int = 380,
        x_label: str = "",
        y_label: str = "",
        y_right_label: str = "",
        x_format: str = "",
        y_format: str = "",
        x_range: list | None = None,
        y_range: list | None = None,
        y_right_range: list | None = None,
        grid: bool = True,
        zoom: bool = True,
        legend: bool = True,
        hover: bool = True,
    ):
        self.title            = title
        self.subtitle         = subtitle
        self.theme            = get_theme(theme)
        self.width            = width
        self.height           = height
        self.x_label          = x_label
        self.y_label          = y_label
        self.y_right_label    = y_right_label
        self.x_format         = x_format
        self.y_format         = y_format
        self.x_range          = x_range
        self.y_range          = y_range
        self.y_right_range    = y_right_range
        self.grid             = grid
        self.zoom             = zoom
        self.legend           = legend
        self.hover            = hover

        self._line_series: list[LineSeries]       = []
        self._scatter_series: list[ScatterSeries] = []
        self._vlines: list[VLine]                 = []
        self._hlines: list[HLine]                 = []
        self._regions: list[Region]               = []
        self._bands: list[Band]                   = []
        self._pins: list[Pin]                     = []
        self._color_cycle = ColorCycle(dark=(theme == "dark"))

        # insertion order for legend
        self._series_order: list[tuple[str, int]] = []  # ("line"|"scatter", idx)

    # ── Line ──────────────────────────────────────────────────────────────────

    def line(
        self,
        x: Any,
        y: Any,
        label: str = "",
        color: str | None = None,
        width: float = 2.0,
        opacity: float = 1.0,
        dash: bool | list[int] = False,
        fill: bool = False,
        fill_opacity: float = 0.15,
        fill_color: str = "",
        axis: str = "left",
        points: bool = False,
        points_size: float = 4.0,
        points_color: str = "",
        points_filled: bool = True,
        smooth: bool = False,
        step: bool = False,
        gap_threshold: float | None = None,
        null_handling: str = "gap",
        hover_format: str = "",
        hover_unit: str = "",
    ) -> "Figure":
        validate_xy(x, y, label)
        resolved_color = resolve(color) if color else self._color_cycle.next()
        s = LineSeries(
            x=x, y=y, label=label,
            color=resolved_color, width=width, opacity=opacity, dash=dash,
            fill=fill, fill_opacity=fill_opacity, fill_color=fill_color,
            axis=axis,
            points=points, points_size=points_size,
            points_color=points_color, points_filled=points_filled,
            smooth=smooth, step=step,
            gap_threshold=gap_threshold, null_handling=null_handling,
            hover_format=hover_format, hover_unit=hover_unit,
        )
        idx = len(self._line_series)
        self._line_series.append(s)
        self._series_order.append(("line", idx))
        return self

    # ── Scatter ───────────────────────────────────────────────────────────────

    def scatter(
        self,
        x: Any,
        y: Any,
        label: str = "",
        color: str | None = None,
        size: float = 6.0,
        opacity: float = 0.85,
        shape: str = "circle",
        stroke: str = "",
        stroke_width: float = 1.0,
        size_by: Any = None,
        size_range: list[float] | None = None,
        color_by: Any = None,
        color_scale: list[str] | None = None,
        axis: str = "left",
        trendline: bool = False,
        trendline_color: str = "",
        trendline_width: float = 1.5,
        trendline_dash: bool = True,
        hover_format: str = "",
        hover_unit: str = "",
        hover_x_label: str = "x",
        hover_y_label: str = "y",
        labels: Any = None,
        label_font_size: int = 9,
        label_color: str = "",
        jitter_x: float = 0.0,
        jitter_y: float = 0.0,
    ) -> "Figure":
        validate_xy(x, y, label)
        resolved_color = resolve(color) if color else self._color_cycle.next()
        s = ScatterSeries(
            x=x, y=y, label=label,
            color=resolved_color, size=size, opacity=opacity,
            shape=shape, stroke=stroke, stroke_width=stroke_width,
            size_by=size_by, size_range=size_range or [3.0, 18.0],
            color_by=color_by, color_scale=color_scale or ["#6366f1", "#f43f5e"],
            axis=axis,
            trendline=trendline, trendline_color=trendline_color,
            trendline_width=trendline_width, trendline_dash=trendline_dash,
            hover_format=hover_format, hover_unit=hover_unit,
            hover_x_label=hover_x_label, hover_y_label=hover_y_label,
            labels=labels, label_font_size=label_font_size, label_color=label_color,
            jitter_x=jitter_x, jitter_y=jitter_y,
        )
        idx = len(self._scatter_series)
        self._scatter_series.append(s)
        self._series_order.append(("scatter", idx))
        return self

    # ── Annotations ───────────────────────────────────────────────────────────

    def vline(self, x, label="", color="", width=1.5, dash=True) -> "Figure":
        c = resolve(color) if color else self.theme.vline_color
        self._vlines.append(VLine(x=x, label=label, color=c, width=width, dash=dash))
        return self

    def hline(self, y, label="", color="", width=1.5, dash=True, scale="left") -> "Figure":
        c = resolve(color) if color else self.theme.hline_color
        self._hlines.append(HLine(y=y, label=label, color=c, width=width, dash=dash, scale=scale))
        return self

    def region(self, x_start, x_end, label="", color="indigo", opacity=0.08) -> "Figure":
        c = resolve(color) if color else self.theme.region_color
        self._regions.append(Region(x_start=x_start, x_end=x_end, label=label, color=c, opacity=opacity))
        return self

    def tag(
        self,
        x_start,
        x_end,
        label: str = "Tag",
        color: str = "#FF00FF",
        opacity: float = 0.05,
        removable: bool = True,
    ) -> "Figure":
        """Add a named tag region via code (visible without interaction mode).

        Args:
            x_start: Start x value (unix ms for timeseries).
            x_end:   End x value (unix ms for timeseries).
            label:   Tag name shown in the header band and the bubble list.
            color:   Hex colour for the tag (defaults to magenta).
            opacity: Fill opacity of the shaded region (default 0.05).
            removable: If False the tag cannot be deleted from the UI.
        """
        c = resolve(color) if color else "#FF00FF"
        import time as _time
        tag_id = f"tag_code_{int(_time.time()*1000)}_{len(self._regions)}"
        r = Region(x_start=x_start, x_end=x_end, label=label, color=c, opacity=opacity)
        r._tagId = tag_id          # marks it as a tag so the header band is drawn
        r._removable = removable   # passed through to JS
        self._regions.append(r)
        return self

    def band(
        self,
        y_lo: float,
        y_hi: float,
        label: str = "",
        color: str = "indigo",
        opacity: float = 0.12,
        axis: str = "left",
    ) -> "Figure":
        """Add a horizontal threshold band between y_lo and y_hi.

        Args:
            y_lo:    Lower Y bound.
            y_hi:    Upper Y bound.
            label:   Label drawn at top-left of band.
            color:   Fill colour (named or hex).
            opacity: Fill opacity (default 0.12).
            axis:    'left' or 'right' — which Y axis scale to use.
        """
        c = resolve(color) if color else "#6366f1"
        scale = "y" if axis == "left" else "y2"
        self._bands.append(Band(y_lo=y_lo, y_hi=y_hi, label=label, color=c, opacity=opacity, scale=scale))
        return self

    def pin(
        self,
        x,
        label: str = "",
        y_frac: float = 0.2,
        color: str = "",
        y: float | None = None,
        scale: str = "left",
    ) -> "Figure":
        """Add an annotation pin at a specific x position.

        Args:
            x:      X position — unix ms for timeseries, numeric otherwise.
            label:  Text shown on the sticky note and pin popup.
            y_frac: Vertical position as a fraction of plot height (0 = top, 1 = bottom).
            color:  Pin colour. Leave empty to auto-cycle through the palette.

        Example::

            fig.pin(ts_ms[300], label="Anomaly detected", y_frac=0.3)
            fig.pin(ts_ms[600], label="System restart",   color="#f43f5e")
        """
        self._pins.append(Pin(x=x, label=label, y_frac=y_frac, color=color, y=y, scale=scale))
        return self

    # ── Render ────────────────────────────────────────────────────────────────

    def to_html(self) -> str:
        """Render the figure to a self-contained HTML string."""
        from youplot.render.html import build_html
        return build_html(**self._render_kwargs())


    def to_fragment(self) -> str:
        """
        Render as an HTML fragment (no <html>/<head>/<body>).
        Used for embedding multiple charts on one page via combine().
        The caller must include the uPlot CDN script once.
        """
        from youplot.render.html import chart_fragment
        return self._render(chart_fragment)

    def _render(self, render_fn):
        """Shared render logic — calls either build_html or chart_fragment."""
        from youplot.render.html import build_html
        return render_fn(**self._render_kwargs())

    def _render_kwargs(self):
        """Build the kwargs dict for build_html / chart_fragment."""
        all_series = self._line_series + self._scatter_series
        if not all_series:
            raise ValueError("No series added.")

        first_x = all_series[0].x
        is_timeseries = _is_timeseries(first_x)

        x_ms_per_line, y_per_line = [], []
        for s in self._line_series:
            x_ms = to_timestamp_ms_list(s.x) if is_timeseries else [int(v*1000) for v in to_float_list(s.x) if v is not None]
            y = apply_null_handling(to_float_list(s.y), s.null_handling)
            if s.gap_threshold is not None:
                x_ms, y = inject_gaps(x_ms, y, s.gap_threshold)
            x_ms_per_line.append(x_ms)
            y_per_line.append(y)

        # Ensure pins have primitive serializable types
        for p in self._pins:
            if is_timeseries:
                if isinstance(p.x, (datetime, date, str)) or str(type(p.x)).find('Timestamp') > -1:
                    p.x = to_timestamp_ms_list([p.x])[0]
            elif isinstance(p.x, (datetime, date)):
                p.x = p.x.timestamp() * 1000
                
            if isinstance(p.y, (datetime, date)):
                p.y = p.y.timestamp() * 1000

        scale_map: dict[str, str] = {}
        right_scales: set[str] = set()
        scale_names: list[str] = []
        for s in all_series:
            if s.axis not in scale_map:
                scale_name = "y" if s.axis == "left" else "y2"
                scale_map[s.axis] = scale_name
                scale_names.append(scale_name)
                if s.axis == "right":
                    right_scales.add(scale_name)
            s._scale_name = scale_map[s.axis]

        range_map = {}
        for axis, scale_name in scale_map.items():
            range_map[scale_name] = self.y_right_range if axis == "right" else self.y_range

        x_range_s = None
        if self.x_range:
            x_range_s = [self.x_range[0]/1000, self.x_range[1]/1000] if is_timeseries else self.x_range

        return dict(
            line_series=self._line_series,
            scatter_series=self._scatter_series,
            series_order=self._series_order,
            x_ms_per_line=x_ms_per_line,
            y_per_line=y_per_line,
            theme=self.theme,
            title=self.title,
            subtitle=self.subtitle,
            width=self.width,
            height=self.height,
            x_label=self.x_label,
            y_label=self.y_label,
            y_right_label=self.y_right_label,
            x_format=self.x_format,
            y_format=self.y_format,
            x_range=x_range_s,
            range_map=range_map,
            zoom=self.zoom,
            legend=self.legend,
            scale_names=scale_names,
            right_scales=right_scales,
            vlines=self._vlines,
            hlines=self._hlines,
            regions=self._regions,
            bands=self._bands,
            pins=self._pins,
            is_timeseries=is_timeseries,
        )

    def show(self) -> None:
        _show(self.to_html())

    def save(self, path: str) -> str:
        return _save(self.to_html(), path)


def _is_timeseries(x: Any) -> bool:
    try:
        import pandas as pd, numpy as np
        if isinstance(x, pd.Series):
            if pd.api.types.is_datetime64_any_dtype(x): return True
            x = x.values
        if isinstance(x, np.ndarray) and np.issubdtype(x.dtype, np.datetime64): return True
    except ImportError:
        pass
    try:
        first = x[0]
    except (IndexError, KeyError, TypeError):
        return False
    try:
        from datetime import datetime
        if isinstance(first, datetime): return True
    except ImportError:
        pass
    try:
        import pandas as pd
        if isinstance(first, pd.Timestamp): return True
    except ImportError:
        pass
    try:
        return float(first) > 1e9
    except (TypeError, ValueError):
        return False


class Dashboard:
    """A collection of figures rendered together with shared crosshair sync."""

    def __init__(self, title: str = "", theme: str = "light"):
        self.title  = title
        self.theme  = theme
        self._figs: list[Figure] = []

    def add(self, fig: "Figure") -> "Dashboard":
        """Add a figure to the dashboard. Returns self for chaining."""
        self._figs.append(fig)
        return self

    def __add__(self, other: "Figure") -> "Dashboard":
        """Support: dashboard = fig1 + fig2  or  dashboard + fig3."""
        if isinstance(other, Figure):
            self.add(other)
        elif isinstance(other, Dashboard):
            for f in other._figs:
                self.add(f)
        return self

    def to_html(self) -> str:
        """Render all figures into a single standalone HTML page."""
        from youplot.render.html import chart_fragment_parts
        from youplot.render.css import build_css
        from youplot.render.js import UPLOT_CDN, UPLOT_CSS
        from youplot.themes.base import get as get_theme

        theme = get_theme(self.theme)
        css = build_css(theme)

        try:
            from youplot.vendor import uplot_js as _ujs, uplot_css as _ucss
            uplot_head = f'<style>{_ucss()}</style><script>{_ujs()}</script>'
        except Exception:
            uplot_head = (
                f'<link rel="stylesheet" href="{UPLOT_CSS}">'
                f'<script src="{UPLOT_CDN}"></script>'
            )

        # Collect CSS separately from body so everything lands in <head>
        all_css = [css]
        all_body = []
        all_scripts = []
        for fig in self._figs:
            fig_css, fig_body, fig_script = chart_fragment_parts(**fig._render_kwargs())
            all_css.append(fig_css)
            all_body.append(fig_body)
            all_scripts.append(fig_script)

        title_html = f'<div class="up-dash-title">{self.title}</div>' if self.title else ''
        extra_css = (
            f'.up-dash-title{{font-size:16px;font-weight:600;letter-spacing:-0.02em;'
            f'color:{theme.text_title};padding:20px 28px 0;}}'
        )
        all_css.append(extra_css)

        return (
            "<!DOCTYPE html><html lang='en'><head>"
            '<meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
            + uplot_head
            + f'<title>{self.title or "youplot"}</title>'
            + ''.join(f'<style>{c}</style>' for c in all_css)
            + '</head><body>'
            + title_html
            + '\n'.join(all_body)
            + '\n'.join(all_scripts)
            + '</body></html>'
        )

    def show(self) -> None:
        from youplot.utils.browser import show as _show
        _show(self.to_html())

    def save(self, path: str) -> str:
        from youplot.utils.browser import save as _save
        return _save(self.to_html(), path)


def combine(*figs, title: str = "", theme: str = "light") -> Dashboard:
    """Combine multiple figures into a synced dashboard.

    Usage::

        dash = up.combine(fig1, fig2, fig3, title="My Dashboard")
        dash.show()
        dash.save("out.html")

    Or using + operator::

        dash = fig1 + fig2
        dash.show()
    """
    db = Dashboard(title=title, theme=theme)
    for f in figs:
        if isinstance(f, Figure):
            db.add(f)
        elif isinstance(f, Dashboard):
            for inner in f._figs:
                db.add(inner)
    return db


# Allow fig1 + fig2 to produce a Dashboard directly
def _figure_add(self, other):
    db = Dashboard()
    db.add(self)
    if isinstance(other, Figure):
        db.add(other)
    elif isinstance(other, Dashboard):
        for f in other._figs:
            db.add(f)
    return db

Figure.__add__ = _figure_add
