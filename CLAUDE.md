# youplot — Agent Guide

This document helps AI agents (Claude, Cursor, Copilot, etc.) understand and work effectively with the youplot codebase.

## What is youplot?

A Python charting library that wraps [uPlot](https://github.com/leeoniya/uPlot) (a fast JS timeseries library) and generates self-contained interactive HTML files. No server required to view charts.

**User-facing package name:** `youplot`  
**Internal package folder:** `youplot/`  
**Import alias convention:** `import youplot as fp`  
**PyPI:** `pip install youplot`

---

## Repo Structure

```
youplot/                  ← Python package (the actual library)
  __init__.py               ← Public API exports + __version__
  figure.py                 ← Figure, Dashboard, combine() — MAIN ENTRY POINT
  options/
    annotations.py          ← VLine, HLine, Region, Band, Pin dataclasses
    axes.py                 ← Axis config dataclasses
  series/
    line.py                 ← LineSeries dataclass
    scatter.py              ← ScatterSeries dataclass
  render/
    html.py                 ← _build_internals(), build_html(), chart_fragment(), chart_fragment_parts()
    css.py                  ← build_css(theme) → CSS string
    js.py                   ← JS constant (the entire chart JS as a raw string)
    scatter_js.py           ← Scatter-specific JS plugin
    serializer.py           ← Python data → JS variable declarations
  themes/
    base.py                 ← LIGHT, DARK theme objects; get(name) → theme
  colors/
    palette.py              ← resolve(color) → hex; NAMED color map; ColorCycle
  vendor/
    uplot.iife.min.js       ← uPlot JS runtime (50KB, bundled — no CDN)
    uplot.min.css           ← uPlot base CSS
    __init__.py             ← uplot_js() and uplot_css() loader functions
  utils/
    browser.py              ← show(html), save(html, path)
    data.py                 ← validate_xy, align helpers
  examples/
    basic_line.py           ← ISS telemetry demo (run with python -m youplot.examples.basic_line)
benchmark.py                ← Benchmarks youplot vs Plotly, Bokeh, Matplotlib
pyproject.toml              ← Build config + PyPI metadata
README.md
MANIFEST.in
LICENSE
docs/index.html             ← Project website (single-file, self-contained)
CLAUDE.md                   ← This file
```

---

## Architecture: How a Chart Gets Made

```
User calls fp.Figure() methods
        ↓
figure.py builds Figure object
  _line_series, _scatter_series, _regions, _bands, _pins, _vlines, _hlines
        ↓
fig.save() / fig.to_html() calls _render_kwargs() then build_html()
        ↓
render/html.py: _build_internals(...)
  → serializer.py: Python data → JS const declarations (UP_X_DATA, UP_Y_DATA, etc.)
  → css.py: theme → CSS string
  → html.py: assembles <body> HTML (chart container, toolbar, prompts, pins layer)
  → Inlines: uPlot CSS + JS (from vendor/), chart data JS, chart logic JS (from js.py)
        ↓
Single self-contained HTML string returned
```

For multi-chart dashboards, `Dashboard.to_html()` calls `chart_fragment_parts()` per figure (returns css, body, script separately) then assembles all CSS into `<head>` and all body+scripts into `<body>`.

---

## Key Files to Edit for Common Tasks

| Task | File(s) |
|------|---------|
| Add a new Figure method (e.g. `fig.candlestick()`) | `figure.py`, `options/annotations.py` or `series/` |
| Change chart interactivity (zoom, tags, pins, tooltips) | `render/js.py` |
| Change chart appearance / CSS | `render/css.py` |
| Change HTML structure (toolbar buttons, prompts, layout) | `render/html.py` |
| Add a new serialized data field | `render/serializer.py` + `render/html.py` (add to js_data) |
| Add a new annotation type | `options/annotations.py` + `figure.py` + `render/serializer.py` + `render/js.py` |
| Change themes | `themes/base.py` |
| Change auto color cycle | `colors/palette.py` |

---

## X-Axis: Timeseries vs Numeric

Timeseries is auto-detected in `figure.py: _is_timeseries()`:
- If the first x value > `1e11` → treated as Unix **milliseconds**
- uPlot internally works in Unix **seconds** — the serializer divides ms by 1000 when writing `UP_X_DATA`
- All Python-side x values (regions, vlines, tags, pins) are stored in **milliseconds**
- In JS: `UP_IS_TIMESERIES` is set; all x comparisons in JS use seconds

---

## JS Architecture (render/js.py)

The entire chart JS is one large raw string `JS` in `render/js.py`. It's wrapped in an IIFE per chart:

```js
(function() {
  // Injected by serializer.py:
  const UP_CONTAINER_ID = "up-chart-abc123";
  const UP_X_DATA = new Float64Array([...]);
  // ... more consts ...

  // The JS string from js.py:
  function buildChart() { ... }
  window.addEventListener('load', function() { buildChart(); });
})()
```

Each chart's IIFE is isolated — state doesn't leak between charts on the same page.

**Global shared state** (explicitly on `window`):
- `window._UP_SYNC_REGISTRY` — array of `{u, show, hide}` for crosshair sync
- `window._UP_PIN_COLOR_IDX` — global annotation color counter
- `window._UP_REGIONS_PATCH` / `window._UP_PINS_PATCH` — export state restoration

---

## Data Flow for Pins (Annotations)

```
Python: fig.pin(x_ms, label, y_frac, color)
  → stores Pin(x, label, y_frac, color) in fig._pins
  → serializer.pins_to_js(pins) → "const UP_CODE_PINS = [...]"

JS on load:
  UP_CODE_PINS.forEach → buildPinEl(u, pin, pinsLayer, tagsList)
    → positionPinEl(u, el, pin):
        xSec = pin.x / 1000 (ms → sec)
        hide if xSec outside u.scales.x.min/max
        xPos = u.valToPos(xSec, 'x', true)  → canvas px
        yPos = b.top + pin.y_frac * b.height → canvas px
        el.style.left = (xPos - b.left) / dpr - 10 + 'px'
        el.style.top  = (yPos - b.top)  / dpr - 10 + 'px'
    → builds sticky note in tagsList (.up-ann-section)
```

Interactive pins (placed via Annotate tool):
- Captured as `y_frac = cy / u.over.offsetHeight` (CSS px / plot height)
- Stored in `UP_PINS` array (in-memory)
- On Export: serialized into `window._UP_PINS_PATCH` script tag in `<head>`
- On re-open: restored before `UP_CODE_PINS` loop; `builtPinIds` prevents duplication

---

## Export Mechanism

`exportAsHtml()` in js.py:
1. `document.documentElement.cloneNode(true)` — deep clone, never touches live DOM
2. Clear chart containers in clone (`[id^="up-chart-"]`)
3. Clear pins layer and tags list in clone
4. Serialize `UP_REGIONS` (interactive tags) and interactive-only `UP_PINS` into a `<script>` patch in `<head>`
5. Move any `<style>` from `<body>` to `<head>` (chart fragments inline CSS in body)
6. Trigger file download

---

## Adding a New Interactive Feature

1. Add button to toolbar in `render/html.py` (in `toolbar_html`)
2. Add CSS in `render/css.py`
3. Handle button click, tool state, and draw hook in `render/js.py`
4. If the feature needs Python-side config, add to `figure.py` and `render/serializer.py`

---

## Running Examples

```bash
# From repo root:
python -m youplot.examples.basic_line
python -m youplot.examples.comprehensive
python -m youplot.examples.scatter_comprehensive

# Benchmark:
pip install plotly bokeh matplotlib
python benchmark.py
```

---

## Testing a Change

```python
# Quick smoke test from repo root:
import sys; sys.path.insert(0, '.')
import youplot as fp, time, math

n = 500
ts = [(int(time.time()) - n + i) * 1000 for i in range(n)]
y  = [math.sin(i / 30) * 10 + 50 for i in range(n)]

fig = fp.Figure(title="Test", zoom=True, legend=True)
fig.line(ts, y, label="Signal", color="indigo", fill=True)
fig.band(y_lo=45, y_hi=55, color="green")
fig.tag(x_start=ts[100], x_end=ts[200], label="Region")
fig.pin(ts[150], label="Peak", y_frac=0.1)

html = fig.to_html()
assert len(html) > 50_000
assert 'UP_CODE_PINS' in html
assert 'youplot' in html
open('/tmp/fp_test.html', 'w').write(html)
print("OK —", len(html) // 1024, "KB")
```

---

## Common Pitfalls

- **X values**: always pass Unix **milliseconds** for timeseries (not seconds, not datetime objects)
- **Multiple figures**: use `fp.combine()` or `+` operator — do NOT concatenate raw `to_html()` strings (CSS will duplicate and JS IIFEs may conflict)
- **Font/CDN**: the library is fully offline — never reference external URLs in generated HTML
- **uPlot `bbox`**: coordinates are in **canvas pixels** (physical px, affected by DPR). CSS pixel conversions require dividing by `window.devicePixelRatio`
- **JS IIFE scope**: variables in `js.py` are per-chart-instance. State that must survive across charts (like `_UP_SYNC_REGISTRY`) must live on `window`
- **`chart_fragment()` vs `chart_fragment_parts()`**: the former inlines `<style>` in the body (legacy, for `to_fragment()`), the latter returns separate `(css, body, script)` — use the latter in `Dashboard.to_html()` to keep all CSS in `<head>`

---

## Version and Release

Version is in `youplot/__init__.py: __version__` and `pyproject.toml: version`. Keep them in sync.

```bash
# Build and publish:
pip install build twine
python -m build
twine upload dist/*
```
