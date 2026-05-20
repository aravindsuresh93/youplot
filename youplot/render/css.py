"""
CSS generation for youplot.
All values come from the Theme — nothing hardcoded here.
Design: Precision & Density + Data & Analysis personality.
Linear/Stripe-inspired: borders-only depth, 4px grid, tabular nums for data.
"""

from __future__ import annotations
from youplot.themes.base import Theme


def build_css(theme: Theme) -> str:
    t = theme
    return f"""
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}

body{{
  font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Roboto,sans-serif;
  background:{t.bg_page};
  color:{t.text_title};
  font-size:13px;
  line-height:1.5;
  -webkit-font-smoothing:antialiased;
}}

/* ── Page wrapper ──────────────────────────────────────────────────────── */
.up-page{{
  max-width:100%;
  padding:24px 28px 48px;
}}

/* ── Chart card ────────────────────────────────────────────────────────── */
.up-card{{
  background:{t.bg_chart};
  border:0.5px solid {t.border};
  border-radius:8px;
  padding:20px 24px 16px;
  margin-bottom:16px;
  box-shadow:0 1px 3px rgba(0,0,0,0.04);
  position:relative;
}}

/* ── Header ────────────────────────────────────────────────────────────── */
.up-header{{
  margin-bottom:16px;
}}
.up-title{{
  font-size:14px;
  font-weight:600;
  letter-spacing:-0.02em;
  color:{t.text_title};
  margin-bottom:2px;
}}
.up-subtitle{{
  font-size:11px;
  color:{t.text_subtitle};
  letter-spacing:0;
}}

/* ── Legend ────────────────────────────────────────────────────────────── */
.up-legend{{
  display:flex;
  flex-wrap:wrap;
  gap:16px;
  margin-bottom:14px;
}}
.up-leg-item{{
  display:flex;
  align-items:center;
  gap:6px;
  font-size:11px;
  color:{t.text_legend};
  cursor:pointer;
  user-select:none;
  transition:opacity 0.15s;
  padding:2px 0;
}}
.up-leg-item:hover{{
  color:{t.text_title};
}}
.up-leg-item.up-leg-off{{
  opacity:0.3;
}}
.up-leg-swatch{{
  width:16px;
  height:2px;
  border-radius:2px;
  flex-shrink:0;
  transition:opacity 0.15s;
}}
.up-leg-swatch.dashed{{
  background:repeating-linear-gradient(
    90deg,
    currentColor 0,currentColor 4px,transparent 4px,transparent 7px
  );
  height:0;
  border-top:2px solid;
}}
.up-leg-label{{
  font-variant-numeric:tabular-nums;
}}

/* ── Chart container ───────────────────────────────────────────────────── */
#up-chart-container{{
  width:100%;
  overflow:hidden;
  position:relative;
}}
#up-chart-container .uplot,
#up-chart-container .uplot canvas{{
  width:100%!important;
}}

/* ── Toolbar (updated for right group) ─────────────────────────────────── */
.up-toolbar{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom:12px;
  flex-wrap:wrap;
  gap:8px;
}}
.up-toolbar-right{{
  display:flex;
  gap:6px;
  align-items:center;
}}
.up-btn{{
  font-size:11px;
  font-weight:500;
  padding:4px 12px;
  border-radius:5px;
  border:0.5px solid {t.border};
  background:transparent;
  color:{t.text_subtitle};
  cursor:pointer;
  transition:all 0.12s;
  letter-spacing:0.01em;
}}
.up-btn:hover{{
  background:{t.grid_color};
  color:{t.text_title};
}}
.up-zoom-hint{{
  font-size:11px;
  color:{t.text_subtitle};
  opacity:0.6;
}}
.uplot .u-select{{
  background:rgba(99,102,241,0.10);
  border:1px solid rgba(99,102,241,0.35);
}}

/* ── Tooltip — glass morphism ──────────────────────────────────────────── */
.up-tooltip{{
  position:fixed;
  background:{t.tooltip_bg};
  -webkit-backdrop-filter:blur(24px) saturate(180%);
  backdrop-filter:blur(24px) saturate(180%);
  border:1px solid {t.tooltip_border};
  color:{t.text_title};
  font-size:11.5px;
  padding:11px 15px 13px;
  border-radius:10px;
  pointer-events:none;
  display:none;
  z-index:9999;
  line-height:1.85;
  min-width:170px;
  max-width:290px;
  box-shadow:{t.tooltip_shadow};
  font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Roboto,sans-serif;
}}
.up-tooltip-time{{
  font-size:10px;
  color:{t.text_tooltip_label};
  margin-bottom:8px;
  font-variant-numeric:tabular-nums;
  letter-spacing:0.02em;
  text-transform:uppercase;
  border-bottom:0.5px solid {t.tooltip_border};
  padding-bottom:6px;
}}
.up-tooltip-row{{
  display:flex;
  align-items:center;
  gap:8px;
  padding:1.5px 0;
}}
.up-tooltip-dot{{
  width:7px;
  height:7px;
  border-radius:50%;
  flex-shrink:0;
  box-shadow:0 0 0 2px rgba(255,255,255,0.15);
}}
.up-tooltip-name{{
  color:{t.text_tooltip_label};
  font-size:10.5px;
  flex:1;
  min-width:0;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  letter-spacing:0.01em;
}}
.up-tooltip-val{{
  font-weight:600;
  font-variant-numeric:tabular-nums;
  font-size:12px;
  letter-spacing:-0.01em;
}}

/* ── Annotation labels ─────────────────────────────────────────────────── */
.up-ann-label{{
  position:absolute;
  font-size:10px;
  font-weight:500;
  color:{t.text_subtitle};
  pointer-events:none;
  white-space:nowrap;
  letter-spacing:0.02em;
}}

/* ── Toolbar Tools ─────────────────────────────────────────────────────── */
.up-tools {{
  display:flex;
  gap:4px;
  background:rgba(0,0,0,0.03);
  padding:3px;
  border-radius:6px;
  border:0.5px solid {t.border};
}}
.up-tool-btn {{
  border:none;
  background:transparent;
}}
.up-tool-btn.active {{
  background:{t.bg_chart};
  box-shadow:0 1px 2px rgba(0,0,0,0.05);
  color:{t.text_title};
}}

/* ── Tags — bubble style ───────────────────────────────────────────────── */
.up-tags-list {{
  margin-top:14px;
}}
.up-tag-bubbles {{
  display:flex;
  flex-wrap:wrap;
  gap:6px;
  margin-top:4px;
}}
.up-tag-bubble {{
  display:inline-flex;
  align-items:center;
  gap:5px;
  padding:3px 9px 3px 10px;
  border-radius:999px;
  border:1px solid;
  font-size:11px;
  font-weight:500;
  cursor:pointer;
  user-select:none;
  transition:filter 0.12s, transform 0.1s;
  white-space:nowrap;
  max-width:220px;
}}
.up-tag-bubble:hover {{
  filter:brightness(1.1);
  transform:translateY(-1px);
}}
.up-tag-bubble-name {{
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  max-width:160px;
}}
.up-tag-bubble-del {{
  background:transparent;
  border:none;
  cursor:pointer;
  font-size:13px;
  line-height:1;
  padding:0;
  opacity:0.6;
  flex-shrink:0;
  color:inherit;
}}
.up-tag-bubble-del:hover {{
  opacity:1;
}}

/* ── Custom Prompt ─────────────────────────────────────────────────────── */
.up-tag-prompt {{
  position:absolute;
  top:0; left:0; right:0; bottom:0;
  background:rgba(0,0,0,0.2);
  -webkit-backdrop-filter:blur(2px);
  backdrop-filter:blur(2px);
  display:none; /* active toggles flex */
  align-items:center;
  justify-content:center;
  z-index:9999;
  border-radius:8px;
}}
.up-tag-prompt-box {{
  background:{t.bg_chart};
  padding:20px;
  border-radius:10px;
  box-shadow:{t.tooltip_shadow};
  border:1px solid {t.border};
  width:260px;
}}
.up-tag-prompt-title {{
  font-weight:600;
  margin-bottom:12px;
  font-size:13px;
  color:{t.text_title};
}}
.up-tag-input {{
  width:100%;
  padding:8px;
  border:1px solid {t.border};
  border-radius:6px;
  background:{t.bg_page};
  color:{t.text_title};
  margin-bottom:16px;
  font-size:12px;
  outline:none;
}}
.up-tag-input:focus {{
  border-color:rgba(99,102,241,0.5);
}}
.up-tag-prompt-actions {{
  display:flex;
  justify-content:flex-end;
  gap:8px;
}}
.up-btn-primary {{
  background:rgba(99,102,241,0.1);
  color:#6366f1;
  border-color:rgba(99,102,241,0.3);
}}
.up-btn-primary:hover {{
  background:rgba(99,102,241,0.15);
  color:#4f46e5;
}}

/* ── Annotation Pins (Figma-style) ─────────────────────────────────────── */
.up-pins-layer{{
  position:absolute;
  pointer-events:none;
  z-index:100;
}}
.up-pin{{
  position:absolute;
  pointer-events:all;
  cursor:pointer;
  z-index:101;
}}
.up-pin-icon{{
  width:20px;
  height:20px;
  border-radius:50% 50% 50% 0;
  transform:rotate(-45deg);
  background:#6366f1;
  display:flex;
  align-items:center;
  justify-content:center;
  color:#fff;
  font-size:9px;
  font-weight:700;
  box-shadow:0 2px 6px rgba(0,0,0,0.25);
  transition:transform 0.15s;
}}
.up-pin:hover .up-pin-icon{{
  transform:rotate(-45deg) scale(1.2);
}}
.up-pin-popup{{
  display:none;
  position:absolute;
  left:22px;
  top:-4px;
  background:{t.bg_chart};
  border:1px solid {t.border};
  border-radius:8px;
  padding:8px 12px;
  min-width:160px;
  max-width:240px;
  box-shadow:{t.tooltip_shadow};
  z-index:200;
  pointer-events:none;
}}
.up-pin:hover .up-pin-popup{{
  display:block;
}}
.up-pin-popup-label{{
  font-weight:600;
  font-size:12px;
  color:{t.text_title};
  margin-bottom:3px;
}}
.up-pin-popup-time{{
  font-size:10px;
  color:{t.text_subtitle};
  font-variant-numeric:tabular-nums;
}}
.up-pin-del{{
  display:none;
  position:absolute;
  top:-6px;
  right:-6px;
  width:16px;
  height:16px;
  border-radius:50%;
  background:#f43f5e;
  border:none;
  color:#fff;
  font-size:11px;
  line-height:1;
  cursor:pointer;
  align-items:center;
  justify-content:center;
  padding:0;
  z-index:202;
}}
.up-pin:hover .up-pin-del{{
  display:flex;
}}


/* ── Export button ──────────────────────────────────────────────────────── */
.up-export-btn{{
  font-size:11px;
}}
.up-export-btn:hover{{
  background:{t.grid_color};
  color:{t.text_title};
}}

/* ── Annotate mode cursor ──────────────────────────────────────────────── */
.u-over{{ cursor: default; }}

/* ── Annotation prompt ─────────────────────────────────────────────────── */
.up-ann-prompt{{
  position:absolute;
  top:0; left:0; right:0; bottom:0;
  background:rgba(0,0,0,0.2);
  -webkit-backdrop-filter:blur(2px);
  backdrop-filter:blur(2px);
  display:none;
  align-items:center;
  justify-content:center;
  z-index:9999;
  border-radius:8px;
}}
/* ── Annotation sticky notes ────────────────────────────────────────────── */
.up-ann-section {{
  margin-top:14px;
}}
.up-list-section-label {{
  font-size:10px;
  font-weight:600;
  letter-spacing:0.06em;
  text-transform:uppercase;
  color:{t.text_subtitle};
  margin-bottom:8px;
  padding-left:2px;
}}
.up-ann-notes-wrap {{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  align-items:flex-start;
}}
.up-ann-item {{
  position:relative;
  width:100px;
  min-height:80px;
  padding:10px 10px 18px 10px;
  border-radius:2px 8px 8px 2px;
  cursor:pointer;
  transition:transform 0.15s, box-shadow 0.15s;
  box-shadow:2px 3px 8px rgba(0,0,0,0.13), 0 1px 2px rgba(0,0,0,0.08);
  /* folded corner via gradient */
  background-image:linear-gradient(
    135deg,
    rgba(0,0,0,0.10) 0px,
    rgba(0,0,0,0.10) 12px,
    transparent 12px
  );
  overflow:hidden;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
  /* slight alternating tilt set per-item via JS */
}}
.up-ann-item:hover {{
  transform:translateY(-3px) rotate(0deg) !important;
  box-shadow:3px 8px 18px rgba(0,0,0,0.18), 0 2px 4px rgba(0,0,0,0.1);
  z-index:10;
}}
.up-ann-item-dot {{
  display:none;
}}
.up-ann-item-body {{
  flex:1;
}}
.up-ann-item-label {{
  font-size:11px;
  font-weight:600;
  line-height:1.35;
  color:rgba(0,0,0,0.75);
  word-break:break-word;
  margin-bottom:4px;
}}
.up-ann-item-time {{
  font-size:9px;
  color:rgba(0,0,0,0.45);
  font-variant-numeric:tabular-nums;
  line-height:1.3;
}}
.up-ann-item .up-tag-del {{
  position:absolute;
  top:3px;
  right:4px;
  background:transparent;
  border:none;
  color:rgba(0,0,0,0.3);
  font-size:13px;
  padding:0;
  cursor:pointer;
  line-height:1;
  opacity:0;
  transition:opacity 0.15s;
}}
.up-ann-item:hover .up-tag-del {{
  opacity:1;
}}
.up-ann-item .up-tag-del:hover {{
  color:rgba(0,0,0,0.7);
}}
.up-measure-mode .u-over {{
  cursor: crosshair !important;
}}
.up-measure-bar {{
  background: rgba(10,10,10,0.95);
  color: #fff;
  padding: 8px 16px;
  display: none; /* flex when active */
  align-items: center;
  justify-content: space-between;
  border-radius: 8px;
  margin-top: 8px;
  margin-bottom: 8px;
  font-size: 11px;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}}
.up-measure-details {{
  display: flex;
  gap: 16px;
  overflow-x: auto;
  white-space: nowrap;
  flex: 1;
  padding-right: 16px;
  scrollbar-width: none;
}}
.up-measure-details::-webkit-scrollbar {{ display: none; }}
.up-m-stat {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
}}
.up-m-val {{ font-weight: 600; font-variant-numeric: tabular-nums; }}
"""
