"""Serializer — Python data to JS strings for uPlot."""

from __future__ import annotations
import json
from youplot.series.line import LineSeries


def series_to_js_array(values: list, var_name: str) -> str:
    nums = ["NaN" if v is None else repr(round(v, 6)) for v in values]
    return f"const {var_name} = new Float64Array([{','.join(nums)}]);"


def timestamps_to_js_array(ts_ms, var_name: str) -> str:
    secs = [str(t / 1000) for t in ts_ms]
    return f"const {var_name} = new Float64Array([{','.join(secs)}]);"


def numeric_to_js_array(vals, var_name: str) -> str:
    nums = [repr(float(v)) for v in vals]
    return f"const {var_name} = new Float64Array([{','.join(nums)}]);"


def series_config_to_js(series: list) -> str:
    parts = ["{}"]
    for s in series:
        dash = s.resolved_dash()
        dash_js = f"[{','.join(map(str, dash))}]" if dash else "[]"
        cfg = (
            "{"
            f'label:{json.dumps(s.label)},'
            f'scale:{json.dumps(s._scale_name)},'
            f'stroke:{json.dumps(s.color)},'
            f'width:{s.width},'
            f'dash:{dash_js},'
            f'points:{{show:{"true" if s.points else "false"},size:{s.points_size*2},fill:{json.dumps(s.resolved_points_color())}}},'
            f'_fill:{json.dumps(s.fill)},'
            f'_fillOpacity:{s.fill_opacity},'
            f'_fillColor:{json.dumps(s.resolved_fill_color())},'
            f'_hoverUnit:{json.dumps(s.hover_unit)},'
            f'_hoverFormat:{json.dumps(s.hover_format)},'
            "}"
        )
        parts.append(cfg)
    return "[" + ",".join(parts) + "]"


def scales_config_to_js(scale_names, right_scales, x_range, range_map, is_timeseries=True) -> str:
    """
    Put min/max in scale config for correct initial render.
    uPlot scale config min/max sets the initial range but does NOT lock it —
    setScale() and drag-zoom can always override it afterward.
    """
    parts = []
    if x_range:
        time_flag = '"time":true,' if is_timeseries else ''
        parts.append(f'"x":{{{time_flag}"min":{x_range[0]},"max":{x_range[1]}}}')
    else:
        time_flag = '"time":true' if is_timeseries else '"time":false'
        parts.append(f'"x":{{{time_flag}}}')
    for name in scale_names:
        rng = range_map.get(name)
        if rng:
            parts.append(f'{json.dumps(name)}:{{"auto":false,"min":{rng[0]},"max":{rng[1]}}}')
        else:
            parts.append(f'{json.dumps(name)}:{{"auto":true}}')
    return "{" + ",".join(parts) + "}"


def initial_ranges_to_js(x_range, range_map, is_timeseries) -> str:
    """
    Returns a JS object of scale→range pairs to apply in the ready hook.
    e.g. {"x":[0,100],"y":[0,100]}
    """
    ranges = {}
    if x_range:
        ranges["x"] = [x_range[0], x_range[1]]
    for name, rng in range_map.items():
        if rng:
            ranges[name] = [rng[0], rng[1]]
    return json.dumps(ranges)


def axes_config_to_js(
    scale_names, right_scales, theme,
    x_label, y_label, y_right_label,
    x_format, y_format,
    is_timeseries=True,
) -> str:
    t = theme
    axes = []
    x_cfg = (
        "{"
        f'stroke:{json.dumps(t.text_tick)},'
        f'grid:{{stroke:{json.dumps(t.grid_color)},width:1}},'
        f'ticks:{{stroke:{json.dumps(t.tick_stroke)},width:1,size:5}},'
        f'font:"11px -apple-system,BlinkMacSystemFont,Inter,sans-serif",'
        + (f'label:{json.dumps(x_label)},' if x_label else '')
        + "}"
    )
    axes.append(x_cfg)
    for name in scale_names:
        is_right = name in right_scales
        side  = 1 if is_right else 3
        label = y_right_label if is_right else y_label
        cfg = (
            "{"
            f'scale:{json.dumps(name)},'
            f'side:{side},'
            f'stroke:{json.dumps(t.text_tick)},'
            f'grid:{{stroke:{json.dumps(t.grid_color)},width:1}},'
            f'ticks:{{stroke:{json.dumps(t.tick_stroke)},width:1,size:5}},'
            f'font:"11px -apple-system,BlinkMacSystemFont,Inter,sans-serif",'
            + (f'label:{json.dumps(label)},' if label else '')
            + "}"
        )
        axes.append(cfg)
    return "[" + ",".join(axes) + "]"


def annotations_to_js(vlines, hlines, regions) -> str:
    # Map user-facing axis names to the internal uPlot scale keys used in UP_SCALES
    _AXIS_TO_SCALE = {"left": "y", "right": "y2"}

    def dc(obj):
        d = {k: v for k, v in vars(obj).items()}
        # ensure _tagId and _removable are always present
        d.setdefault('_tagId', '')
        d.setdefault('_removable', True)
        return d

    def dc_hline(h):
        d = dc(h)
        # Translate "left"/"right" to the actual uPlot scale key ("y"/"y2")
        if d.get('scale') in _AXIS_TO_SCALE:
            d['scale'] = _AXIS_TO_SCALE[d['scale']]
        return d

    return (
        f"const UP_VLINES = {json.dumps([dc(v) for v in vlines])};\n"
        f"const UP_HLINES = {json.dumps([dc_hline(h) for h in hlines])};\n"
        f"let UP_REGIONS = {json.dumps([dc(r) for r in regions])};\n"
    )


def bands_to_js(bands) -> str:
    """Serialize threshold bands to JS array."""
    _AXIS_TO_SCALE = {"left": "y", "right": "y2"}

    def dc(b):
        d = {k: v for k, v in vars(b).items()}
        if d.get('scale') in _AXIS_TO_SCALE:
            d['scale'] = _AXIS_TO_SCALE[d['scale']]
        return d
    return json.dumps([dc(b) for b in bands])
    from youplot.utils.data import to_float_list

    all_decls = []
    cfg_parts = []

    for i, s in enumerate(scatter_series):
        x_var  = f"SC_X_{i}"
        y_var  = f"SC_Y_{i}"
        sz_var = f"SC_SZ_{i}"
        cv_var = f"SC_COL_{i}"
        lv_var = f"SC_LBL_{i}"

        x_vals = to_float_list(s.x)
        if is_timeseries:
            x_nums = [str(v/1000) if v is not None else "NaN" for v in x_vals]
        else:
            x_nums = [repr(float(v)) if v is not None else "NaN" for v in x_vals]
        all_decls.append(f"const {x_var} = [{','.join(x_nums)}];")

        y_vals = to_float_list(s.y)
        y_nums = [repr(float(v)) if v is not None else "NaN" for v in y_vals]
        all_decls.append(f"const {y_var} = [{','.join(y_nums)}];")

        def opt_arr(data, var):
            if data is None:
                return f"const {var} = null;"
            vals = to_float_list(data)
            nums = [repr(float(v)) if v is not None else "NaN" for v in vals]
            return f"const {var} = [{','.join(nums)}];"

        all_decls.append(opt_arr(s.size_by,  sz_var))
        all_decls.append(opt_arr(s.color_by, cv_var))

        if s.labels is not None:
            all_decls.append(f"const {lv_var} = {json.dumps([str(l) for l in s.labels])};")
        else:
            all_decls.append(f"const {lv_var} = null;")

        cfg = (
            "{"
            f"_scatterIdx:{i},"
            f"label:{json.dumps(s.label)},"
            f"color:{json.dumps(s.color)},"
            f"size:{s.size},"
            f"opacity:{s.opacity},"
            f"shape:{json.dumps(s.shape)},"
            f"stroke:{json.dumps(s.resolved_stroke())},"
            f"strokeWidth:{s.stroke_width},"
            f"sizeRange:[{s.size_range[0]},{s.size_range[1]}],"
            f"colorScale:[{','.join(json.dumps(c) for c in s.color_scale)}],"
            f"trendline:{'true' if s.trendline else 'false'},"
            f"trendlineColor:{json.dumps(s.resolved_trendline_color())},"
            f"trendlineWidth:{s.trendline_width},"
            f"trendlineDash:{'true' if s.trendline_dash else 'false'},"
            f"hoverFormat:{json.dumps(s.hover_format)},"
            f"hoverUnit:{json.dumps(s.hover_unit)},"
            f"hoverXLabel:{json.dumps(s.hover_x_label)},"
            f"hoverYLabel:{json.dumps(s.hover_y_label)},"
            f"labelFontSize:{s.label_font_size},"
            f"labelColor:{json.dumps(s.resolved_label_color())},"
            f"scale:{json.dumps(s._scale_name)},"
            f"visible:true,"
            f"_xData:{x_var},"
            f"_yData:{y_var},"
            f"_sizeData:{sz_var},"
            f"_colorData:{cv_var},"
            f"_labelData:{lv_var},"
            "}"
        )
        cfg_parts.append(cfg)

    return "\n".join(all_decls), "[" + ",".join(cfg_parts) + "]"

def pins_to_js(pins) -> str:
    """Serialize code-defined annotation pins to a JS array."""
    import json as _json
    out = []
    for p in pins:
        out.append({
            'id':    f'code_pin_{id(p)}',
            'x':     p.x,
            'label': p.label,
            'y_frac': getattr(p, 'y_frac', 0.2),
            'y': getattr(p, 'y', None),
            'scale': getattr(p, 'scale', 'left'),
            'color': p.color or None,   # None → auto-assigned in JS
        })
    return _json.dumps(out)
