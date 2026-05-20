"""
Color palette for youplot.
Named colors resolve to hex. Default cycle ensures series never clash.
Inspired by Tailwind + Observable's categorical palette.
"""

# ── Named color map ────────────────────────────────────────────────────────────
# Tailwind-derived but tuned for data viz (slightly more saturated)

NAMED = {
    # Blues / purples
    "indigo":   "#6366f1",
    "violet":   "#7c3aed",
    "purple":   "#9333ea",
    "blue":     "#3b82f6",
    "sky":      "#0ea5e9",
    "cyan":     "#06b6d4",

    # Greens
    "emerald":  "#10b981",
    "green":    "#22c55e",
    "teal":     "#14b8a6",

    # Warm
    "amber":    "#f59e0b",
    "orange":   "#f97316",
    "yellow":   "#eab308",

    # Reds / pinks
    "rose":     "#f43f5e",
    "red":      "#ef4444",
    "pink":     "#ec4899",

    # Neutrals
    "slate":    "#64748b",
    "gray":     "#6b7280",
    "zinc":     "#71717a",
    "white":    "#ffffff",
    "black":    "#000000",
}

# ── Default series cycle ────────────────────────────────────────────────────────
# Ordered for max visual separation. Observable-inspired but warmer.

DEFAULT_CYCLE = [
    "#6366f1",   # indigo
    "#f59e0b",   # amber
    "#10b981",   # emerald
    "#f43f5e",   # rose
    "#0ea5e9",   # sky
    "#9333ea",   # purple
    "#f97316",   # orange
    "#14b8a6",   # teal
    "#ec4899",   # pink
    "#3b82f6",   # blue
]

# Dark theme variants — slightly lighter/more saturated for dark bg legibility
DEFAULT_CYCLE_DARK = [
    "#818cf8",   # indigo-400
    "#fbbf24",   # amber-400
    "#34d399",   # emerald-400
    "#fb7185",   # rose-400
    "#38bdf8",   # sky-400
    "#c084fc",   # purple-400
    "#fb923c",   # orange-400
    "#2dd4bf",   # teal-400
    "#f472b6",   # pink-400
    "#60a5fa",   # blue-400
]


def resolve(color: str | None, dark: bool = False) -> str:
    """
    Resolve a color name or passthrough a hex/rgb string.

    resolve("indigo")      → "#6366f1"
    resolve("#ff0000")     → "#ff0000"
    resolve("rgb(0,0,0)")  → "rgb(0,0,0)"
    resolve(None)          → raises ValueError
    """
    if color is None:
        raise ValueError("Color cannot be None — use next_color() to get default")
    if color in NAMED:
        return NAMED[color]
    if color.startswith("#") or color.startswith("rgb"):
        return color
    raise ValueError(
        f"Unknown color '{color}'. Use a named color ({', '.join(NAMED)}) or a hex string."
    )


class ColorCycle:
    """Stateful iterator over the default color cycle. One per Figure."""

    def __init__(self, dark: bool = False):
        self._cycle = DEFAULT_CYCLE_DARK if dark else DEFAULT_CYCLE
        self._idx = 0

    def next(self) -> str:
        color = self._cycle[self._idx % len(self._cycle)]
        self._idx += 1
        return color

    def reset(self):
        self._idx = 0
