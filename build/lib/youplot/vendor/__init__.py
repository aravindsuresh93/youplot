"""Vendored assets — loaded at import time so they're always available."""
import os

_DIR = os.path.dirname(__file__)

def uplot_js() -> str:
    with open(os.path.join(_DIR, "uplot.iife.min.js"), encoding="utf-8") as f:
        return f.read()

def uplot_css() -> str:
    with open(os.path.join(_DIR, "uplot.min.css"), encoding="utf-8") as f:
        return f.read()
