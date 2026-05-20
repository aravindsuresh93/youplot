"""
Data utilities for youplot.
Handles array validation, timestamp normalization, gap injection, null handling.
"""

from __future__ import annotations
import math
from typing import Any


def to_float_list(arr: Any) -> list[float | None]:
    """
    Convert any array-like to a list of float | None.
    Handles: list, tuple, numpy array, pandas Series.
    NaN → None.
    """
    try:
        import numpy as np
        if isinstance(arr, np.ndarray):
            return [None if math.isnan(float(v)) else float(v) for v in arr]
    except ImportError:
        pass

    try:
        import pandas as pd
        if isinstance(arr, pd.Series):
            return [None if pd.isna(v) else float(v) for v in arr]
    except ImportError:
        pass

    result = []
    for v in arr:
        if v is None:
            result.append(None)
        else:
            try:
                f = float(v)
                result.append(None if math.isnan(f) else f)
            except (TypeError, ValueError):
                result.append(None)
    return result


def to_timestamp_ms_list(arr: Any) -> list[int]:
    """
    Convert any time array to list of unix milliseconds (int).
    Handles: unix seconds (float/int), unix ms, pandas Timestamp, datetime, numpy datetime64.
    """
    try:
        import pandas as pd
        import numpy as np

        if isinstance(arr, pd.Series):
            arr = arr.values

        if isinstance(arr, np.ndarray) and np.issubdtype(arr.dtype, np.datetime64):
            # numpy datetime64 → ms
            return [int(v) for v in arr.astype("datetime64[ms]").astype("int64")]

        if len(arr) > 0:
            first = arr[0]

            # pandas Timestamp
            if isinstance(first, pd.Timestamp):
                return [int(t.timestamp() * 1000) for t in arr]

    except ImportError:
        pass

    try:
        from datetime import datetime
        result = []
        for v in arr:
            if isinstance(v, datetime):
                result.append(int(v.timestamp() * 1000))
            else:
                f = float(v)
                # Heuristic: if value > 1e12 it's already ms, else seconds
                result.append(int(f) if f > 1e12 else int(f * 1000))
        return result
    except Exception:
        return [int(float(v)) for v in arr]


def inject_gaps(
    x_ms: list[int],
    y: list[float | None],
    gap_threshold_s: float
) -> tuple[list[int], list[float | None]]:
    """
    Insert NaN (None) between consecutive points where the time gap
    exceeds gap_threshold_s seconds. This causes uPlot to break the line.
    """
    if len(x_ms) < 2:
        return x_ms, y

    out_x: list[int] = [x_ms[0]]
    out_y: list[float | None] = [y[0]]

    threshold_ms = gap_threshold_s * 1000

    for i in range(1, len(x_ms)):
        if (x_ms[i] - x_ms[i - 1]) > threshold_ms:
            # insert a None in the middle to break the line
            mid = (x_ms[i - 1] + x_ms[i]) // 2
            out_x.append(mid)
            out_y.append(None)
        out_x.append(x_ms[i])
        out_y.append(y[i])

    return out_x, out_y


def apply_null_handling(
    y: list[float | None],
    mode: str
) -> list[float | None]:
    """
    Apply null handling strategy.
    "gap"    → keep None (uPlot will break line)
    "zero"   → replace None with 0.0
    "ignore" → forward-fill None with previous value
    """
    if mode == "zero":
        return [0.0 if v is None else v for v in y]

    if mode == "ignore":
        out = []
        last = None
        for v in y:
            if v is None:
                out.append(last)
            else:
                last = v
                out.append(v)
        return out

    return y  # "gap" — keep as-is


def validate_xy(x: Any, y: Any, label: str = "") -> None:
    """Raise ValueError if x and y have mismatched lengths."""
    try:
        lx = len(x)
        ly = len(y)
    except TypeError:
        return  # can't check generators etc
    if lx != ly:
        name = f"Series '{label}'" if label else "Series"
        raise ValueError(f"{name}: x has {lx} points but y has {ly} points.")
