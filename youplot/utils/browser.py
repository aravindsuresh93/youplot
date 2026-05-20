"""Browser utilities — open HTML in browser, write to file."""

from __future__ import annotations
import os
import tempfile
import webbrowser


def show(html: str) -> None:
    """Write HTML to a temp file and open in the default browser."""
    fd, path = tempfile.mkstemp(suffix=".html", prefix="youplot_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file://{path}")


def save(html: str, path: str) -> str:
    """Write HTML to path. Returns absolute path."""
    abs_path = os.path.abspath(path)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(html)
    return abs_path
