"""
youplot — Extremely fast, lightweight timeseries charts for Python.
Powered by uPlot (https://github.com/leeoniya/uPlot).

Quick start::

    import youplot as fp

    fig1 = fp.Figure(title="Temperature", zoom=True)
    fig1.line(ts_ms, temp, label="°C", color="#f97316", fill=True)
    fig1.band(y_lo=18, y_hi=24, label="Comfort zone", color="#10b981")
    fig1.tag(x_start=ts_ms[0], x_end=ts_ms[3600], label="Night")
    fig1.pin(ts_ms[peak], label="Peak: 38°C", y_frac=0.1)

    fig2 = fp.Figure(title="Humidity", zoom=True)
    fig2.line(ts_ms, humidity, label="%", color="#6366f1")

    # Combine → synced crosshair, one HTML file
    dash = fig1 + fig2                    # or fp.combine(fig1, fig2)
    dash.save("dashboard.html")
    dash.show()
"""

from youplot.figure import Figure, Dashboard, combine
from youplot.options.annotations import VLine, HLine, Region, Band, Pin
from youplot.colors.palette import resolve as resolve_color, NAMED as COLORS
from youplot.themes.base import LIGHT, DARK

__all__ = [
    "Figure", "Dashboard", "combine",
    "VLine", "HLine", "Region", "Band", "Pin",
    "resolve_color", "COLORS", "LIGHT", "DARK",
]

__version__ = "1.0.0"
__author__  = "youplot contributors"
__license__ = "MIT"
