"""HTML renderer — handles line, scatter, and mixed charts."""

from __future__ import annotations
import uuid
from youplot.render.css import build_css
from youplot.render.js import UPLOT_CDN, UPLOT_CSS, JS
from youplot.render.scatter_js import SCATTER_JS
from youplot.render import serializer as ser


def _build_internals(
    line_series, scatter_series, series_order,
    x_ms_per_line, y_per_line,
    theme, title, subtitle, width, height,
    x_label, y_label, y_right_label,
    x_format, y_format,
    x_range, range_map,
    zoom, legend,
    scale_names, right_scales,
    vlines, hlines, regions, bands, pins,
    is_timeseries,
    cid,
):
    """Core render logic shared by build_html and chart_fragment."""
    container_id = f"up-chart-{cid}"
    tooltip_id   = f"up-tooltip-{cid}"
    reset_fn     = f"upReset_{cid}"

    css = build_css(theme)
    has_scatter = len(scatter_series) > 0
    has_line    = len(line_series) > 0

    # X data
    if has_line:
        x_ms   = x_ms_per_line[0]
        x_decl = ser.timestamps_to_js_array(x_ms, "UP_X_DATA")
        x_len  = len(x_ms)
    else:
        from youplot.utils.data import to_float_list
        x_raw  = [v for v in to_float_list(scatter_series[0].x) if v is not None]
        x_decl = ser.numeric_to_js_array(x_raw, "UP_X_DATA")
        x_len  = len(x_raw)

    # Y data
    y_decls, y_var_names = [], []
    for i, y in enumerate(y_per_line):
        name = f"UP_Y_{i}"
        y_var_names.append(name)
        y_decls.append(ser.series_to_js_array(y, name))

    if not has_line and has_scatter:
        y_decls.append(ser.series_to_js_array([None] * x_len, "UP_Y_0"))
        y_var_names.append("UP_Y_0")

    # uPlot series
    if has_line:
        uplot_series = list(line_series)
    else:
        from youplot.series.line import LineSeries
        dummy_s = LineSeries(x=[], y=[], label="", color="rgba(0,0,0,0)", width=0)
        dummy_s._scale_name = scatter_series[0]._scale_name
        uplot_series = [dummy_s]

    series_cfg_js = ser.series_config_to_js(uplot_series)
    scales_cfg_js = ser.scales_config_to_js(scale_names, right_scales, x_range, range_map, is_timeseries)
    axes_cfg_js   = ser.axes_config_to_js(
        scale_names, right_scales, theme,
        x_label, y_label, y_right_label, x_format, y_format, is_timeseries
    )
    ann_js = ser.annotations_to_js(vlines, hlines, regions)

    scatter_decls_js, scatter_cfg_js = "", "[]"
    if has_scatter:
        scatter_decls_js, scatter_cfg_js = ser.scatter_configs_to_js(
            scatter_series, draw_si=1, is_timeseries=is_timeseries
        )

    # Legend
    legend_html = ""
    if legend:
        items = []
        for kind, idx in series_order:
            if kind == "line":
                s = line_series[idx]
                si = idx + 1
                dash_cls = " dashed" if s.resolved_dash() else ""
                items.append(
                    f'<span class="up-leg-item" data-si="{si}" data-kind="line" '
                    f'title="Click toggle · Double-click isolate">'
                    f'<span class="up-leg-swatch{dash_cls}" style="background:{s.color};color:{s.color}"></span>'
                    f'<span class="up-leg-label">{s.label or f"Series {si}"}</span></span>'
                )
            else:
                s = scatter_series[idx]
                items.append(
                    f'<span class="up-leg-item" data-si="sc-{idx}" data-kind="scatter" '
                    f'title="Click toggle · Double-click isolate">'
                    f'{_shape_svg(s.shape, s.color)}'
                    f'<span class="up-leg-label">{s.label or f"Scatter {idx+1}"}</span></span>'
                )
        legend_html = '<div class="up-legend">' + "".join(items) + '</div>'

    toolbar_html = ""
    if zoom:
        toolbar_html = (
            '<div class="up-toolbar">'
            '<div class="up-tools">'
            f'<button class="up-btn up-tool-btn active" data-tool="zoom" id="up-tool-zoom-{cid}" title="Drag to zoom · Right-drag to zoom Y · Dbl-click to reset">Zoom</button>'
            + ('' if has_scatter and not has_line else
               f'<button class="up-btn up-tool-btn" data-tool="tag" id="up-tool-tag-{cid}" title="Drag to create a named region tag">Tag</button>'
               f'<button class="up-btn up-tool-btn" data-tool="measure" id="up-tool-measure-{cid}" title="Click anchor · right-click to save measurement">Measure</button>')
            + f'<button class="up-btn up-tool-btn" data-tool="annotate" id="up-tool-annotate-{cid}" title="Click to drop an annotation pin">Annotate</button>'
            '</div>'
            '<div class="up-toolbar-right">'
            f'<button class="up-btn up-export-btn" title="Export current state as HTML">⬇ Export</button>'
            f'<button class="up-btn" onclick="{reset_fn}()">Reset zoom</button>'
            '</div>'
            '</div>'
        )

    prompt_html = (
        f'<div id="up-tag-prompt-{cid}" class="up-tag-prompt">'
        '<div class="up-tag-prompt-box">'
        '<div class="up-tag-prompt-title">Name this region</div>'
        f'<input type="text" id="up-tag-input-{cid}" class="up-tag-input" placeholder="Tag name"/>'
        '<div class="up-tag-prompt-actions">'
        f'<button class="up-btn" id="up-tag-cancel-{cid}">Cancel</button>'
        f'<button class="up-btn up-btn-primary" id="up-tag-save-{cid}">Save</button>'
        '</div>'
        '</div></div>'
    )
    ann_prompt_html = (
        f'<div id="up-ann-prompt-{cid}" class="up-ann-prompt">'
        '<div class="up-tag-prompt-box">'
        '<div class="up-tag-prompt-title">Add annotation</div>'
        f'<input type="text" id="up-ann-input-{cid}" class="up-tag-input up-ann-input" placeholder="Annotation text"/>'
        '<div class="up-tag-prompt-actions">'
        f'<button class="up-btn" id="up-ann-cancel-{cid}">Cancel</button>'
        f'<button class="up-btn up-btn-primary" id="up-ann-save-{cid}">Add pin</button>'
        '</div>'
        '</div></div>'
    )
    pins_layer_html = f'<div class="up-pins-layer" id="up-pins-{cid}"></div>'
    tags_list_html = f'<div id="up-tags-{cid}" class="up-tags-list"></div>'

    header_html = ""
    if title or subtitle:
        header_html = '<div class="up-header">'
        if title:    header_html += f'<div class="up-title">{title}</div>'
        if subtitle: header_html += f'<div class="up-subtitle">{subtitle}</div>'
        header_html += '</div>'

    w_style = f"width:{width}px" if isinstance(width, int) else f"width:{width}"

    js_data = "\n".join([
        f'const UP_CONTAINER_ID = "{container_id}";',
        f'const UP_TOOLTIP_ID   = "{tooltip_id}";',
        f'const UP_RESET_FN     = "{reset_fn}";',
        x_decl, *y_decls,
        f"const UP_Y_DATA       = [{','.join(y_var_names)}];",
        f"const UP_SERIES_CFG   = {series_cfg_js};",
        f"const UP_SCALES       = {scales_cfg_js};",
        f"const UP_AXES         = {axes_cfg_js};",
        f"const UP_HEIGHT       = {height};",
        f"const UP_IS_TIMESERIES = {'true' if is_timeseries else 'false'};",
        f"const UP_HAS_SCATTER  = {'true' if has_scatter else 'false'};",
        scatter_decls_js,
        f"const UP_SCATTER_CFG  = {scatter_cfg_js};",
        f"const UP_INITIAL_RANGES = {ser.initial_ranges_to_js(x_range, range_map, is_timeseries)};",
        ann_js,
        f"const UP_BANDS = {ser.bands_to_js(bands)};",
        f"const UP_CODE_PINS = {ser.pins_to_js(pins)};",
    ])

    measure_bar_html = (
        f'<div id="up-measure-bar-{cid}" class="up-measure-bar">'
        f'<div class="up-measure-details" id="up-measure-details-{cid}"></div>'
        '</div>'
    )

    body_html = (
        f'<div class="up-page"><div class="up-card" style="{w_style}">'
        + header_html + legend_html + toolbar_html
        + f'<div style="position:relative"><div id="{container_id}"></div>{pins_layer_html}</div>'
        + measure_bar_html
        + tags_list_html
        + f'<div id="{tooltip_id}" class="up-tooltip"></div>'
        + prompt_html
        + ann_prompt_html
        + '</div></div>'
    )

    # Each chart gets its own IIFE so variables don't clash across charts
    script = (
        (f'<script>{SCATTER_JS}</script>' if has_scatter else '')
        + f'<script>(function(){{\n{js_data}\n{JS}\n}})()</script>'
    )

    return css, body_html, script, has_scatter


def build_html(
    line_series, scatter_series, series_order,
    x_ms_per_line, y_per_line,
    theme, title, subtitle, width, height,
    x_label, y_label, y_right_label,
    x_format, y_format,
    x_range, range_map,
    zoom, legend,
    scale_names, right_scales,
    vlines, hlines, regions, bands, pins,
    is_timeseries,
) -> str:
    """Full standalone HTML page for a single chart."""
    cid = "upc" + uuid.uuid4().hex[:8]
    css, body_html, script, _ = _build_internals(
        line_series, scatter_series, series_order,
        x_ms_per_line, y_per_line,
        theme, title, subtitle, width, height,
        x_label, y_label, y_right_label,
        x_format, y_format,
        x_range, range_map,
        zoom, legend,
        scale_names, right_scales,
        vlines, hlines, regions, bands, pins,
        is_timeseries, cid,
    )
    try:
        from youplot.vendor import uplot_js as _uplot_js, uplot_css as _uplot_css
        uplot_js_inline  = f'<script>{_uplot_js()}</script>'
        uplot_css_inline = f'<style>{_uplot_css()}</style>'
    except Exception:
        uplot_js_inline  = f'<script src="{UPLOT_CDN}"></script>'
        uplot_css_inline = f'<link rel="stylesheet" href="{UPLOT_CSS}">'
    return (
        "<!DOCTYPE html><html lang='en'><head>"
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        + uplot_css_inline
        + uplot_js_inline
        + f'<title>{title or "youplot"}</title>'
        f'<style>{css}</style>'
        f'</head><body>{body_html}{script}</body></html>'
    )


def chart_fragment(
    line_series, scatter_series, series_order,
    x_ms_per_line, y_per_line,
    theme, title, subtitle, width, height,
    x_label, y_label, y_right_label,
    x_format, y_format,
    x_range, range_map,
    zoom, legend,
    scale_names, right_scales,
    vlines, hlines, regions, bands, pins,
    is_timeseries,
) -> str:
    """
    HTML fragment only — no <html>/<head>/<body>.
    Use this to embed multiple charts on one page.
    The caller is responsible for including uPlot CDN once.
    """
    cid = "upc" + uuid.uuid4().hex[:8]
    css, body_html, script, _ = _build_internals(
        line_series, scatter_series, series_order,
        x_ms_per_line, y_per_line,
        theme, title, subtitle, width, height,
        x_label, y_label, y_right_label,
        x_format, y_format,
        x_range, range_map,
        zoom, legend,
        scale_names, right_scales,
        vlines, hlines, regions, bands, pins,
        is_timeseries, cid,
    )
    return f'<style>{css}</style>{body_html}{script}'


def chart_fragment_parts(
    line_series, scatter_series, series_order,
    x_ms_per_line, y_per_line,
    theme, title, subtitle, width, height,
    x_label, y_label, y_right_label,
    x_format, y_format,
    x_range, range_map,
    zoom, legend,
    scale_names, right_scales,
    vlines, hlines, regions, bands, pins,
    is_timeseries,
) -> tuple:
    """Return (css, body_html, script) separately so Dashboard can put CSS in <head>."""
    cid = "upc" + uuid.uuid4().hex[:8]
    css, body_html, script, _ = _build_internals(
        line_series, scatter_series, series_order,
        x_ms_per_line, y_per_line,
        theme, title, subtitle, width, height,
        x_label, y_label, y_right_label,
        x_format, y_format,
        x_range, range_map,
        zoom, legend,
        scale_names, right_scales,
        vlines, hlines, regions, bands, pins,
        is_timeseries, cid,
    )
    return css, body_html, script


def _shape_svg(shape: str, color: str) -> str:
    s, h = 10, 5
    shapes = {
        "circle":   f'<circle cx="{h}" cy="{h}" r="{h-1}" fill="{color}" opacity="0.85"/>',
        "square":   f'<rect x="1" y="1" width="{s-2}" height="{s-2}" fill="{color}" opacity="0.85"/>',
        "triangle": f'<polygon points="{h},1 {s-1},{s-1} 1,{s-1}" fill="{color}" opacity="0.85"/>',
        "diamond":  f'<polygon points="{h},1 {s-1},{h} {h},{s-1} 1,{h}" fill="{color}" opacity="0.85"/>',
        "cross":    f'<path d="M3,1h4v2h2v4h-2v2h-4v-2h-2v-4h2z" fill="{color}" opacity="0.85"/>',
        "star":     f'<polygon points="{h},1 6,4 9,4 7,6 8,9 5,7 2,9 3,6 1,4 4,4" fill="{color}" opacity="0.85"/>',
    }
    inner = shapes.get(shape, shapes["circle"])
    return f'<svg width="{s}" height="{s}" viewBox="0 0 {s} {s}" style="flex-shrink:0;margin-right:2px">{inner}</svg>'
