"""
Pacific SOE Fiscal Risk Monitor (Streamlit + Plotly)
=====================================================

A Python re-implementation of the "Pacific SOE Fiscal Risk Monitor" example
dashboard, built from the figures published in the World Bank policy note
"Between Necessity and Risk: State Owned Enterprises and Fiscal Risk in the
Pacific Islands". This is an independent example, not an official World Bank
product.

Run it
------
    pip install -r requirements.txt
    streamlit run app.py

Keep the `.streamlit/config.toml` file next to app.py; it sets the World Bank
colour theme for Streamlit's own widgets.

Where to change things
----------------------
* All figures from the note live in the DATA section below.
* Colours live in the COLOURS section (World Bank navy #002244, blue #009FDA).
* Illustrative values (calculator presets, "illustrative thresholds", trigger
  rules) are marked as such in the code and on the page.
"""

from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# COLOURS (World Bank palette + semantic status colours)
# ---------------------------------------------------------------------------
NAVY = "#002244"         # World Bank navy: headings, title band, table heads
BLUE = "#009FDA"         # World Bank bright blue: chart marks, accents
BLUE_STRONG = "#0071BC"  # darker blue for text links / hover
INK = "#1C2530"
INK_2 = "#4C5A68"
MUTED = "#76828F"
LINE = "#E1E6EC"
AXIS = "#C2CBD5"
BG = "#F3F5F8"
SURFACE = "#FFFFFF"
SURFACE_2 = "#F5F7FA"
PREV = "#A2ADB9"         # earlier-period marker in the dumbbell chart
NEG = "#D03B3B"
GOOD, WARN, CRIT = "#00A996", "#F7B841", "#D03B3B"
GOOD_INK, WARN_INK, CRIT_INK = "#00796B", "#8A5D00", "#B12F2F"
GOOD_WASH = "rgba(0,169,150,0.10)"
WARN_WASH = "rgba(247,184,65,0.20)"
CRIT_WASH = "rgba(208,59,59,0.09)"
FONT = "Open Sans, Segoe UI, system-ui, -apple-system, Roboto, sans-serif"

# ---------------------------------------------------------------------------
# DATA (all figures from the policy note)
# ---------------------------------------------------------------------------
# Each metric: v = displayed value, d = small detail line, st = status
# (ok / watch / alert). A missing st means "not rated".
SECTORS = [
    dict(s="UTIL", name="Utilities", n=13, gdp=dict(v="14%"),
         roa=dict(v="0.4", d="3.4 → 0.4", st="alert"), roe=dict(v="−12", d="6 → −12", st="alert"),
         cr=dict(v="2.4–3.3", d="full period 2.8", st="watch"), da=dict(v="0.4", st="ok"),
         de=dict(v="13.6", st="alert"), z=dict(v="5.0", d="likely overstated", st="ok")),
    dict(s="DISC", name="Consumer Disc.", n=1, fn="1 SOE", gdp=dict(v="≈1%"),
         roa=dict(v="—"), roe=dict(v="−62", d="2020–21 · 2022–24 n/a", st="alert"),
         cr=dict(v="≈0", st="alert"), da=dict(v="0.9", st="alert"),
         de=dict(v="n/a", d="negative EBITDA", st="alert"), z=dict(v="≈−5", st="alert")),
    dict(s="ENRG", name="Energy", n=3, gdp=dict(v="16%"),
         roa=dict(v="1.3", d="5.0 → 1.3", st="watch"), roe=dict(v="—"),
         cr=dict(v="2.7–3.5", d="range across periods", st="watch"), da=dict(v="0.3", st="ok"),
         de=dict(v="6.5", st="alert"), z=dict(v="7.5", st="ok")),
    dict(s="INDUS", name="Industrials", n=24, gdp=dict(v="—"),
         roa=dict(v="—"), roe=dict(v="−7", d="−1 → −7", st="alert"),
         cr=dict(v="≈6", d="stable", st="ok"), da=dict(v="0.3", st="ok"),
         de=dict(v="—"), z=dict(v="33.2", st="ok")),
    dict(s="COMMS", name="Communications", n=11, gdp=dict(v="—"),
         roa=dict(v="≈1.6", d="stable at ~1.5–1.6", st="ok"), roe=dict(v="7", d="15 → 7", st="watch"),
         cr=dict(v="6.2", d="21.5 → 6.2", st="watch"), da=dict(v="0.3", st="ok"),
         de=dict(v="4.8", st="watch"), z=dict(v="11.0", st="ok")),
    dict(s="STPL", name="Consumer Staples", n=12, gdp=dict(v="≈1%"),
         roa=dict(v="8.1", d="7.3 → 8.1", st="ok"), roe=dict(v="—"),
         cr=dict(v="≈35", d="stable", st="ok"), da=dict(v="0.5", st="watch"),
         de=dict(v="—"), z=dict(v="12.3", st="ok")),
    dict(s="REIT", name="Real Estate", n=7, gdp=dict(v="—"),
         roa=dict(v="—"), roe=dict(v="—"),
         cr=dict(v="≈26", d="stable", st="ok"), da=dict(v="0.3", st="ok"),
         de=dict(v="0.4", st="ok"), z=dict(v="37.5", st="ok")),
]
METRIC_KEYS = ["roa", "roe", "cr", "da", "de", "z"]

Z_BY_SECTOR = [  # 2021–24 average Z″, 38 SOEs
    ("REIT", "Real Estate", 37.5, False), ("INDUS", "Industrials", 33.2, False),
    ("STPL", "Consumer Staples", 12.3, False), ("COMMS", "Communications", 11.0, False),
    ("ENRG", "Energy", 7.5, False), ("UTIL", "Utilities", 5.0, False),
    ("DISC", "Consumer Disc.", -5.0, True),  # True = approximate value ("≈")
]
ROA = [  # (sector, 2020–21, 2022–24, note)
    ("STPL", 7.3, 8.1, ""), ("ENRG", 5.0, 1.3, ""), ("UTIL", 3.4, 0.4, ""),
    ("COMMS", 1.5, 1.6, "Note reports ~1.5–1.6%"),
]
ROE = [
    ("COMMS", 15, 7, "2020–21 reported as ~15%"), ("UTIL", 6, -12, ""), ("INDUS", -1, -7, ""),
]
SR_TR_GAP = [  # sovereign-rent mean minus tourism-remittance mean, Z″ points
    ("COMMS", "Communications", 12.4), ("INDUS", "Industrials", 11.7),
    ("UTIL", "Utilities", 8.4), ("ALL", "All sectors", 9.1),
]
UTILITY_ZONES = {  # 2022–24 utility Z″; the note names only some countries
    "alert": dict(total=5, items=[("PNG", -0.3, "only negative score"), ("PLW", 0.8, "")]),
    "watch": dict(total=2, items=[("MHL", 1.7, "full period 4.7")]),
    "ok": dict(total=2, items=[("KIR", 53.3, ""), ("SLB", 10.2, "")]),
}
COUNTRIES = [
    dict(c="KIR", name="Kiribati", own="Dual", eco="Sovereign rent", n=22, gdp="max above 50%",
         gr=dict(v="16% → 15%"), uz=dict(v="53.3", st="ok")),
    dict(c="MHL", name="Marshall Islands", own="Centralized", eco="Sovereign rent", n=9, gdp="—",
         gr=dict(v="38% → 35%", st="alert"), uz=dict(v="1.7", st="watch", d="full period 4.7")),
    dict(c="FSM", name="Micronesia", own="Unknown", eco="Sovereign rent", n=5, gdp="—",
         gr=dict(v="↑ rising", st="watch"), uz=dict(v="—")),
    dict(c="NRU", name="Nauru", own="Dual", eco="Sovereign rent&#42;", n=1, gdp="about 30%",
         gr=dict(v="—"), uz=dict(v="—")),
    dict(c="WSM", name="Samoa", own="Centralized", eco="Tourism &amp; remittance", n=4, gdp="—",
         gr=dict(v="↑ rising", st="watch"), uz=dict(v="near/below threshold", st="alert")),
    dict(c="TON", name="Tonga", own="Centralized", eco="Tourism &amp; remittance", n=5, gdp="—",
         gr=dict(v="↓ falling"), uz=dict(v="near/below threshold", st="alert")),
    dict(c="VUT", name="Vanuatu", own="Decentralized", eco="Tourism &amp; remittance", n=6, gdp="—",
         gr=dict(v="—"), uz=dict(v="—")),
    dict(c="SLB", name="Solomon Islands", own="Dual", eco="Tourism &amp; remittance&#42;", n=8, gdp="—",
         gr=dict(v="—"), uz=dict(v="10.2", st="ok")),
    dict(c="FJI", name="Fiji", own="Centralized", eco="Not classified", n=12, gdp="—",
         gr=dict(v="—"), uz=dict(v="near/below threshold", st="alert")),
    dict(c="PLW", name="Palau", own="Decentralized", eco="Not classified", n=3, gdp="about 21%",
         gr=dict(v="↓ falling"), uz=dict(v="0.8", st="alert")),
    dict(c="PNG", name="Papua New Guinea", own="Centralized", eco="Not classified", n=8, gdp="about 2%",
         gr=dict(v="≈0%"), uz=dict(v="−0.3", st="alert")),
]

# Altman Z″ (emerging-market model without the 3.25 constant, Eidelman 1995)
Z_COEF = dict(x1=6.56, x2=3.26, x3=6.72, x4=1.05)
# Equation (1): predicted grants (% of total assets) from previous-year Z″
INJ_CONST, INJ_SLOPE = 18.2, -0.767
# External shocks: change in Z″ per unit of each shock
SHOCK_DISASTER, SHOCK_FX = -0.23, -0.37

# ILLUSTRATIVE calculator presets (hypothetical SOEs, not from the note)
PRESETS = {
    "median": dict(label="Sample median", x1=0.133, x2=0.108, x3=0.022, x4=1.61, assets=50.0),
    "grey": dict(label="Grey zone", x1=0.05, x2=0.02, x3=0.01, x4=1.20, assets=50.0),
    "distress": dict(label="Distress", x1=-0.10, x2=-0.30, x3=-0.05, x4=0.20, assets=50.0),
}

GLYPH = {"ok": "●", "watch": "▲", "alert": "■"}
STATUS_LABEL = {"ok": "Good", "watch": "Watch", "alert": "Alert"}
ZONE_LABEL = {"ok": "Safe", "watch": "Grey zone", "alert": "Distress"}


def zone_of(z: float) -> str:
    """Distress < 1.1, grey zone 1.1–2.6, safe > 2.6."""
    return "alert" if z < 1.1 else ("watch" if z <= 2.6 else "ok")


def z_score(x1: float, x2: float, x3: float, x4: float) -> float:
    return Z_COEF["x1"] * x1 + Z_COEF["x2"] * x2 + Z_COEF["x3"] * x3 + Z_COEF["x4"] * x4


def injection(z: float) -> float:
    """Equation (1). Can go negative above Z″ ≈ 23.7."""
    return INJ_CONST + INJ_SLOPE * z


def injection_shown(z: float) -> float:
    return max(0.0, injection(z))


def fmt(v: float, d: int = 1) -> str:
    return f"{v:.{d}f}".replace("-", "−")


def usd(v: float) -> str:
    return f"USD {v:.1f}M"


# ---------------------------------------------------------------------------
# PAGE SETUP + CSS
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Pacific SOE Fiscal Risk Monitor", layout="wide")

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
html, body, .stApp, .stMarkdown, button, input, textarea {{ font-family: {FONT}; }}
.stApp {{ background: {BG}; }}
header[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"], .block-container {{ max-width: 1240px; padding-top: 1.2rem; padding-bottom: 3rem; }}
[data-testid="stMarkdownContainer"] p {{ margin-bottom: 0; }}
div[data-testid="stMarkdownContainer"] p.note {{ font-size: 12.5px; line-height: 1.55; color: {INK_2}; margin-top: 6px; }}
div[data-testid="stMarkdownContainer"] p.card-sub {{ font-size: 12.5px; line-height: 1.5; color: {MUTED}; margin: 2px 0 6px; }}
div[data-testid="stMarkdownContainer"] p.card-title {{ font-size: 15px; line-height: 1.4; color: {NAVY}; font-weight: 700; }}
div[data-testid="stMarkdownContainer"] .sec-head p {{ font-size: 14px; line-height: 1.55; color: {INK_2}; margin-top: 4px; }}
div[data-testid="stMarkdownContainer"] .band p {{ font-size: 14px; line-height: 1.55; }}
div[data-testid="stMarkdownContainer"] p.lead {{ font-size: 13.5px; line-height: 1.55; margin-top: 6px; }}
div[class*="st-key-tile"] {{ min-height: 150px; }}

/* containers created with st.container(key="card_...") become white cards */
div[class*="st-key-card"] {{ background: {SURFACE}; border: 1px solid rgba(0,34,68,.10); border-radius: 4px; padding: 18px; }}
div[class*="st-key-tile"] {{ background: {SURFACE}; border: 1px solid rgba(0,34,68,.10); border-top: 3px solid {NAVY}; border-radius: 4px; padding: 16px 18px; }}

/* title band + nav */
.band {{ background: {NAVY}; color: #fff; border-radius: 4px; padding: 28px 30px 24px; display: grid; gap: 10px; }}
.band .eyebrow {{ font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: {BLUE}; font-weight: 700; }}
.band h1 {{ color: #fff; font-size: 32px; font-weight: 700; margin: 0; padding: 0; line-height: 1.2; }}
.band p {{ color: rgba(255,255,255,.80); margin: 0; max-width: 78ch; font-size: 14px; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }}
.meta span {{ font-size: 12px; color: rgba(255,255,255,.80); background: rgba(255,255,255,.10); border-radius: 2px; padding: 3px 9px; }}
.meta span b {{ color: #fff; font-weight: 600; }}
.meta .flag {{ background: {WARN}; color: {INK}; font-weight: 600; }}
.secnav {{ display: flex; flex-wrap: wrap; gap: 4px 20px; background: {SURFACE}; border: 1px solid {LINE}; border-radius: 4px; padding: 10px 16px; margin-top: 10px; }}
.secnav a {{ color: {INK_2} !important; text-decoration: none !important; font-weight: 600; font-size: 13px; }}
.secnav a:hover {{ color: {NAVY} !important; }}

/* section headings */
.sec-head {{ margin: 26px 0 4px; }}
.sec-head h2 {{ color: {NAVY}; font-size: 20px; font-weight: 700; margin: 0; padding: 0; scroll-margin-top: 70px; }}
.sec-head p {{ color: {INK_2}; margin: 4px 0 0; font-size: 14px; max-width: 72ch; }}
.card-title {{ color: {NAVY}; font-size: 15px; font-weight: 700; margin: 0; }}
.card-sub {{ color: {MUTED}; font-size: 12.5px; margin: 2px 0 6px; }}
.note {{ font-size: 12.5px; color: {INK_2}; margin: 6px 0 0; }}
.note b {{ color: {INK}; }}

/* status chips */
.st {{ display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; padding: 2px 8px 2px 7px; border-radius: 2px; white-space: nowrap; color: {INK}; }}
.st i {{ font-style: normal; font-size: 9px; }}
.st.ok {{ background: {GOOD_WASH}; }} .st.ok i {{ color: {GOOD_INK}; }}
.st.watch {{ background: {WARN_WASH}; }} .st.watch i {{ color: {WARN_INK}; }}
.st.alert {{ background: {CRIT_WASH}; }} .st.alert i {{ color: {CRIT_INK}; }}

/* overview */
.hero-label, .tile-label {{ font-size: 13px; color: {INK_2}; font-weight: 600; }}
.hero-value {{ font-size: 56px; font-weight: 700; line-height: 1; color: {NAVY}; display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 10px; margin: 10px 0 14px; }}
.hero-value small {{ font-size: 14px; font-weight: 400; color: {INK_2}; }}
.zonebar {{ display: flex; gap: 2px; height: 12px; margin-bottom: 12px; }}
.zonelegend {{ display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 13px; margin-bottom: 10px; }}
.zonelegend span {{ display: inline-flex; align-items: center; gap: 6px; }}
.tile-top {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
.tile-value {{ font-size: 30px; font-weight: 700; line-height: 1.15; color: {NAVY}; margin: 6px 0 4px; }}
.tile-value small {{ font-size: 13px; font-weight: 400; color: {INK_2}; margin-left: 4px; }}
.tile-sub {{ font-size: 12.5px; color: {MUTED}; }}

/* tables */
.tbl-wrap {{ position: relative; overflow-x: auto; }}
table.dash {{ border-collapse: collapse; width: 100%; font-size: 13px; border: none; }}
table.dash th {{ text-align: left; font-size: 11.5px; font-weight: 700; color: {NAVY}; padding: 8px 10px; border: none; border-bottom: 2px solid {NAVY}; white-space: nowrap; vertical-align: bottom; background: transparent; }}
table.dash td {{ padding: 9px 10px; border: none; border-bottom: 1px solid {LINE}; vertical-align: top; font-variant-numeric: tabular-nums; }}
table.dash tr:last-child td {{ border-bottom: none; }}
table.dash td.name .code {{ font-weight: 700; letter-spacing: .02em; font-size: 12.5px; color: {NAVY}; display: block; }}
table.dash td.name .nm {{ color: {INK_2}; font-size: 12.5px; }}
table.dash td.name .fn {{ color: {MUTED}; font-size: 11.5px; margin-left: 4px; }}
.cell {{ display: inline-flex; flex-direction: column; gap: 1px; }}
.cell .v {{ display: inline-flex; align-items: center; gap: 6px; font-weight: 600; white-space: nowrap; }}
.cell .v i {{ font-style: normal; font-size: 9px; }}
.cell .d {{ font-size: 11.5px; color: {MUTED}; max-width: 14ch; }}
td.ok .v i {{ color: {GOOD_INK}; }} td.watch .v i {{ color: {WARN_INK}; }} td.alert .v i {{ color: {CRIT_INK}; }}
td.alert {{ background: {CRIT_WASH}; }} td.watch {{ background: {WARN_WASH}; }}
td.na .v {{ color: {MUTED}; font-weight: 400; }}
tr.dim td {{ opacity: .35; }}
.pips {{ display: inline-flex; gap: 2px; margin-right: 6px; vertical-align: middle; }}
.pips span {{ width: 6px; height: 12px; border-radius: 1px; background: {LINE}; display: inline-block; }}
.pips span.on {{ background: {CRIT}; }}
.legend-row {{ display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 12px; color: {INK_2}; margin-top: 12px; }}
.legend-row .lt b {{ color: {INK}; }}

/* zone board */
.zboard {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }}
.zcol {{ border-radius: 3px; padding: 10px; display: grid; gap: 8px; align-content: start; min-height: 132px; }}
.zcol.alert {{ background: {CRIT_WASH}; }} .zcol.watch {{ background: {WARN_WASH}; }} .zcol.ok {{ background: {GOOD_WASH}; }}
.zcol h4 {{ margin: 0; padding: 0; font-size: 12px; font-weight: 700; display: flex; justify-content: space-between; color: {NAVY}; }}
.zcol h4 i {{ font-style: normal; font-size: 9px; }}
.zcol.alert h4 i {{ color: {CRIT_INK}; }} .zcol.watch h4 i {{ color: {WARN_INK}; }} .zcol.ok h4 i {{ color: {GOOD_INK}; }}
.zcol h4 .cnt {{ color: {INK_2}; font-weight: 400; }}
.ctry {{ background: {SURFACE}; border-radius: 2px; padding: 6px 8px; display: flex; justify-content: space-between; align-items: baseline; gap: 6px; box-shadow: 0 0 0 1px rgba(0,34,68,.10); font-size: 13px; }}
.ctry .cd {{ font-weight: 600; letter-spacing: .02em; color: {NAVY}; }}
.ctry .zv {{ font-weight: 700; }}
.ctry .zs {{ display: block; font-size: 11px; color: {MUTED}; }}
.ctry.slot {{ box-shadow: inset 0 0 0 1px {AXIS}; background: transparent; color: {MUTED}; font-size: 11.5px; justify-content: center; }}
.unk {{ margin-top: 10px; font-size: 12.5px; color: {INK_2}; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }}
.unk .cd {{ background: {SURFACE_2}; border: 1px dashed {AXIS}; border-radius: 2px; padding: 1px 7px; font-size: 12px; font-weight: 600; color: {NAVY}; }}

/* calculator */
.contrib-row {{ display: grid; grid-template-columns: 118px minmax(0, 1fr) 56px; gap: 8px; align-items: center; font-size: 12.5px; margin: 4px 0; }}
.contrib-row .lbl {{ color: {INK_2}; white-space: nowrap; }}
.contrib-row .val {{ text-align: right; font-weight: 700; }}
.track {{ position: relative; height: 12px; }}
.track::before {{ content: ""; position: absolute; left: 50%; top: -2px; bottom: -2px; width: 1px; background: {AXIS}; }}
.track span {{ position: absolute; top: 1px; height: 10px; }}
.track span.pos {{ left: 50%; background: {BLUE}; border-radius: 0 2px 2px 0; }}
.track span.neg {{ right: 50%; background: {NEG}; border-radius: 2px 0 0 2px; }}
.results {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 10px 0 8px; }}
.res {{ border-radius: 3px; padding: 12px; background: {SURFACE_2}; display: grid; gap: 6px; }}
.res.base {{ box-shadow: inset 3px 0 0 {BLUE}; }} .res.stress {{ box-shadow: inset 3px 0 0 {CRIT}; }}
.res-h {{ font-size: 12px; color: {INK_2}; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; }}
.res-z {{ display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }}
.res-z b {{ font-size: 28px; font-weight: 700; line-height: 1.1; color: {NAVY}; }}
.res-line {{ font-size: 13px; color: {INK_2}; }} .res-line b {{ color: {INK}; }}
.delta {{ font-size: 13px; padding: 8px 12px; border-radius: 3px; margin-bottom: 8px; }}

/* timeline */
.tl {{ list-style: none; margin: 0; padding: 0; }}
.tl li {{ display: grid; grid-template-columns: 74px 14px minmax(0, 1fr); gap: 10px; margin: 0; }}
.tl .when {{ font-size: 12px; font-weight: 600; color: {NAVY}; text-align: right; }}
.tl .rail {{ position: relative; }}
.tl .rail::before {{ content: ""; position: absolute; left: 6px; top: 0; bottom: 0; width: 2px; background: {LINE}; }}
.tl li:first-child .rail::before {{ top: 8px; }} .tl li:last-child .rail::before {{ bottom: calc(100% - 8px); }}
.tl .rail::after {{ content: ""; position: absolute; left: 2px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: {SURFACE}; box-shadow: 0 0 0 2px {AXIS}; }}
.tl li.hot .rail::after {{ background: {CRIT}; box-shadow: 0 0 0 2px {SURFACE}, 0 0 0 3px {CRIT}; }}
.tl .what {{ padding-bottom: 14px; font-size: 13px; }}

.foot {{ margin-top: 30px; padding-top: 16px; border-top: 2px solid {NAVY}; color: {INK_2}; font-size: 12.5px; }}
.foot h2 {{ color: {NAVY}; font-size: 14px; margin: 0 0 8px; padding: 0; }}
.foot ul {{ margin: 0; padding-left: 18px; }}

@media (max-width: 640px) {{ .zboard, .results {{ grid-template-columns: minmax(0, 1fr); }} .hero-value {{ font-size: 46px; }} }}
</style>
"""


def H(snippet: str) -> None:
    """Render an HTML snippet. Lines are flattened into one so Markdown treats
    the whole snippet as raw HTML (no code blocks, no stray formatting)."""
    st.markdown(" ".join(line.strip() for line in snippet.splitlines() if line.strip()),
                unsafe_allow_html=True)


def chip(status: str, text: str | None = None) -> str:
    return f'<span class="st {status}"><i>{GLYPH[status]}</i>{text or STATUS_LABEL[status]}</span>'


def metric_cell(m: dict | None) -> str:
    m = m or {"v": "—"}
    status = m.get("st")
    classes = [status] if status else []
    if m["v"] == "—":
        classes.append("na")
    glyph = f"<i>{GLYPH[status]}</i>" if status else ""
    title = f' title="{STATUS_LABEL[status]}"' if status else ""
    detail = f'<span class="d">{m["d"]}</span>' if m.get("d") else ""
    return (f'<td class="{" ".join(classes)}"{title}><span class="cell">'
            f'<span class="v">{glyph}{m["v"]}</span>{detail}</span></td>')


def plotly_base(height: int) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        height=height, margin=dict(l=6, r=16, t=6, b=6),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=INK), showlegend=False,
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=LINE, font=dict(family=FONT, color=INK, size=12)),
        barcornerradius=4,
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, theme=None, config={"displayModeBar": False})


def section_head(anchor: str, title: str, text: str) -> None:
    H(f'<div class="sec-head"><h2 id="{anchor}">{title}</h2><p>{text}</p></div>')


# ---------------------------------------------------------------------------
# CHARTS
# ---------------------------------------------------------------------------
def z_sector_chart(highlight: str) -> go.Figure:
    fig = plotly_base(300)
    fig.update_layout(margin=dict(l=10, r=44, t=6, b=30))
    labels = [f'<span style="color:{NAVY}"><b>{s}</b></span>   {name}' for s, name, _, _ in Z_BY_SECTOR]
    zs = [z for _, _, z, _ in Z_BY_SECTOR]
    texts = [("≈" if approx else "") + fmt(z) for _, _, z, approx in Z_BY_SECTOR]
    opac = [1.0 if highlight in ("ALL", s) else 0.28 for s, _, _, _ in Z_BY_SECTOR]
    fig.add_vrect(x0=-10, x1=1.1, fillcolor=CRIT_WASH, line_width=0, layer="below")
    fig.add_vrect(x0=1.1, x1=2.6, fillcolor=WARN_WASH, line_width=0, layer="below")
    fig.add_bar(
        y=labels, x=zs, orientation="h", width=0.48,
        marker=dict(color=[NEG if z < 0 else BLUE for z in zs], opacity=opac),
        text=texts, textposition="outside", textfont=dict(color=INK, size=12), cliponaxis=False,
        customdata=[ZONE_LABEL[zone_of(z)] for z in zs],
        hovertemplate="<b>%{text}</b> Z″ (2021–24 average)<br>%{customdata}<extra></extra>",
    )
    fig.update_yaxes(autorange="reversed", showgrid=False, ticks="", ticklabelstandoff=8)
    fig.update_xaxes(range=[-10, 43], tickvals=[-10, 0, 10, 20, 30, 40], gridcolor=LINE,
                     zeroline=True, zerolinecolor=INK_2, zerolinewidth=1, tickfont=dict(color=MUTED, size=11))
    return fig


def dumbbell_chart(highlight: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, subplot_titles=("ROA (%)", "ROE (%)"), vertical_spacing=0.2)
    panels = [(ROA, 1, [0, 9], [0, 3, 6, 9]), (ROE, 2, [-15, 20], [-10, 0, 10, 20])]  # (data, row, range, ticks)
    for data, row, rng, ticks in panels:
        for sector, a, b, note in data:
            op = 1.0 if highlight in ("ALL", sector) else 0.28
            fig.add_scatter(x=[a, b], y=[sector, sector], mode="lines", line=dict(color=PREV, width=2),
                            opacity=op, hoverinfo="skip", row=row, col=1)
            fig.add_scatter(x=[a], y=[sector], mode="markers", opacity=op, row=row, col=1,
                            marker=dict(size=9, color=SURFACE, line=dict(color=PREV, width=2)),
                            hovertemplate=f"{sector}<br><b>{fmt(a)}%</b> 2020–21<extra></extra>")
            # label position: right of the dot if rising, left if falling, above if too close to the axis
            if b >= a:
                pos = "middle right"
            elif (b - rng[0]) / (rng[1] - rng[0]) < 0.2:
                pos = "top center"
            else:
                pos = "middle left"
            extra = f"<br>{note}" if note else ""
            fig.add_scatter(x=[b], y=[sector], mode="markers+text", opacity=op, row=row, col=1,
                            marker=dict(size=11, color=BLUE, line=dict(color=SURFACE, width=2)),
                            text=[f"<b>{fmt(b)}</b>"], textposition=pos, textfont=dict(color=INK, size=11.5),
                            cliponaxis=False,
                            hovertemplate=(f"{sector}<br><b>{fmt(b)}%</b> 2022–24<br>"
                                           f"change {'+' if b - a >= 0 else ''}{fmt(b - a)} pp{extra}<extra></extra>"))
        fig.update_xaxes(range=rng, tickvals=ticks, gridcolor=LINE, zeroline=True, zerolinecolor=INK_2,
                         zerolinewidth=1, tickfont=dict(color=MUTED, size=11), row=row, col=1)
        fig.update_yaxes(autorange="reversed", showgrid=False, ticks="", automargin=True,
                         tickfont=dict(color=NAVY, size=12, weight=600), row=row, col=1)
    fig.update_layout(height=400, margin=dict(l=52, r=24, t=30, b=30), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(family=FONT, size=12, color=INK), showlegend=False,
                      hoverlabel=dict(bgcolor=SURFACE, bordercolor=LINE, font=dict(family=FONT, color=INK)))
    for ann, axis in zip(fig.layout.annotations, (fig.layout.xaxis, fig.layout.xaxis2)):  # subplot titles
        ann.update(font=dict(color=NAVY, size=12.5, weight=700), x=axis.domain[0], xanchor="left")
    return fig


def gap_chart(highlight: str) -> go.Figure:
    fig = plotly_base(210)
    fig.update_layout(margin=dict(l=10, r=44, t=6, b=30))
    labels = [(f'<span style="color:{NAVY}"><b>{k}</b></span>   {name}' if k != "ALL"
               else f'<span style="color:{NAVY}"><b>All sectors</b></span>') for k, name, _ in SR_TR_GAP]
    vals = [v for _, _, v in SR_TR_GAP]
    opac = [1.0 if (highlight == "ALL" or k == highlight) else 0.28 for k, _, _ in SR_TR_GAP]
    fig.add_bar(y=labels, x=vals, orientation="h", width=0.48, marker=dict(color=BLUE, opacity=opac),
                text=[f"+{fmt(v)}" for v in vals], textposition="outside", textfont=dict(color=INK, size=12),
                cliponaxis=False,
                hovertemplate="<b>+%{x:.1f} pts</b><br>sovereign rent − tourism &amp; remittance<extra></extra>")
    fig.add_hline(y=2.5, line=dict(color=LINE, width=1))
    fig.update_yaxes(autorange="reversed", showgrid=False, ticks="", ticklabelstandoff=8)
    fig.update_xaxes(range=[0, 16], tickvals=[0, 5, 10, 15], gridcolor=LINE, zeroline=True,
                     zerolinecolor=INK_2, tickfont=dict(color=MUTED, size=11))
    return fig


def curve_chart(z_base: float, z_stress: float) -> go.Figure:
    fig = plotly_base(270)
    fig.update_layout(margin=dict(l=48, r=16, t=10, b=44))
    fig.add_vrect(x0=-6, x1=1.1, fillcolor=CRIT_WASH, line_width=0, layer="below")
    fig.add_vrect(x0=1.1, x1=2.6, fillcolor=WARN_WASH, line_width=0, layer="below")
    zs = [-6 + i * 0.1 for i in range(298)]  # up to ≈23.7, where Equation (1) reaches 0
    fig.add_scatter(x=zs, y=[injection(z) for z in zs], mode="lines", line=dict(color=BLUE, width=2),
                    hovertemplate="Z″ = %{x:.1f}<br><b>%{y:.1f}%</b> predicted grants<extra></extra>")
    for z, p, label in [(-4.7, 21.9, "5th pct  21.9%"), (12.78, 8.4, "75th pct  8.4%")]:
        fig.add_scatter(x=[z], y=[p], mode="markers+text", text=[label], textposition="top right",
                        textfont=dict(color=INK_2, size=11), cliponaxis=False,
                        marker=dict(size=10, color=SURFACE, line=dict(color=NAVY, width=2)),
                        hovertemplate=f"Figure 10 reference<br>Z″ {fmt(z, 2)} → <b>{fmt(p)}%</b><extra></extra>")

    def clamp(z: float) -> float:
        return max(-6.0, min(24.0, z))

    if abs(z_stress - z_base) > 1e-9:
        fig.add_scatter(x=[clamp(z_stress)], y=[min(25, injection_shown(z_stress))], mode="markers",
                        marker=dict(size=13, color=CRIT, line=dict(color=SURFACE, width=2)),
                        hovertemplate="After stress<br>Z″ %{x:.2f} → <b>%{y:.1f}%</b><extra></extra>")
    fig.add_scatter(x=[clamp(z_base)], y=[min(25, injection_shown(z_base))], mode="markers",
                    marker=dict(size=13, color=BLUE, line=dict(color=SURFACE, width=2)),
                    hovertemplate="Current input<br>Z″ %{x:.2f} → <b>%{y:.1f}%</b><extra></extra>")
    fig.update_xaxes(range=[-6, 24], tickvals=[-5, 0, 5, 10, 15, 20], gridcolor=LINE, zeroline=False,
                     tickfont=dict(color=MUTED, size=11), title=dict(text="Previous-year Z″",
                                                                      font=dict(color=INK_2, size=11.5)))
    fig.update_yaxes(range=[0, 25], tickvals=[0, 5, 10, 15, 20, 25], ticksuffix="%", gridcolor=LINE,
                     zeroline=False, tickfont=dict(color=MUTED, size=11))
    return fig


# ---------------------------------------------------------------------------
# PAGE
# ---------------------------------------------------------------------------
H(CSS)

H(f"""
<div class="band">
  <div class="eyebrow">Fiscal risk management · Example dashboard</div>
  <h1>Pacific SOE Fiscal Risk Monitor</h1>
  <p>An example Early Warning System built from the figures published in the World Bank policy note
  <i>Between Necessity and Risk</i>. The note does not publish SOE-level names, so the calculator presets
  and trigger rules are illustrative. This is an independent example, not an official World Bank product.</p>
  <div class="meta">
    <span>Sample <b>83 SOEs · 11 countries</b></span>
    <span>Z″ computed for <b>38 SOEs</b> (2021–2024)</span>
    <span>KPI period <b>2020–2024</b></span>
    <span>Financials excluded</span>
    <span class="flag">▲ Illustrative values are flagged</span>
  </div>
</div>
<div class="secnav">
  <a href="#overview">Overview</a><a href="#sectors">Sectors</a><a href="#countries">Countries</a>
  <a href="#calculator">Early warning calculator</a><a href="#triggers">Trigger rules</a>
</div>
""")

# ---- Overview --------------------------------------------------------------
section_head("overview", "Portfolio overview",
             "Financial health distribution on the Altman Z″ score, and the utility indicators the note "
             "flags as the largest risk.")
left, right = st.columns([5, 7], gap="medium")
with left:
    with st.container(key="card_hero"):
        H(f"""
        <div class="hero-label">SOEs in distress or the grey zone</div>
        <div class="hero-value">39%<small>15 of 38 · about 4 in 10</small></div>
        <div class="zonebar">
          <div style="width:60.5%;background:{GOOD};border-radius:2px 0 0 2px"></div>
          <div style="width:10.5%;background:{WARN}"></div>
          <div style="width:29%;background:{CRIT};border-radius:0 2px 2px 0"></div>
        </div>
        <div class="zonelegend">
          <span>{chip("ok", "Safe")}<b>23</b> (61%)</span>
          <span>{chip("watch", "Grey zone")}<b>4</b> (10%)</span>
          <span>{chip("alert", "Distress")}<b>11</b> (29%)</span>
        </div>
        <p class="note">More SOEs sit in distress than in the grey zone. Once an SOE starts to deteriorate,
        the <b>slide tends to be rapid</b>, which leaves governments little time to intervene.</p>
        """)
with right:
    tiles = [
        ("Predicted transfers to distressed SOEs", "21.9%", "of total assets / year",
         "8.4% for healthy SOEs · about 2.6× (Z″ 5th vs 75th percentile)"),
        ("Utilities debt-to-EBITDA", "13.6", "years", "Distress threshold is 6 · highest of any sector"),
        ("Countries with distressed utilities", "5", "of 9", "Grey zone 2 · safe 2 (2022–24 Z″)"),
        ("Utilities return on assets", "0.4%", "2022–24", "Down from 3.4% in 2020–21, during the recovery"),
    ]
    for row in (tiles[:2], tiles[2:]):
        cols = st.columns(2, gap="medium")
        for col, (label, value, unit, sub) in zip(cols, row):
            with col, st.container(key=f"tile_{label[:12].replace(' ', '_')}"):
                H(f"""
                <div class="tile-top"><span class="tile-label">{label}</span>{chip("alert")}</div>
                <div class="tile-value">{value}<small>{unit}</small></div>
                <div class="tile-sub">{sub}</div>
                """)

# ---- Sectors ---------------------------------------------------------------
section_head("sectors", "Sector scorecard",
             "Each KPI is marked good, watch or alert by GICS sector. Sectors with the most alerts come first.")
picked = st.segmented_control("Highlight a sector", ["All", "UTIL", "DISC", "ENRG", "INDUS", "COMMS", "STPL", "REIT"],
                              default="All", key="highlight")
highlight = "ALL" if picked in (None, "All") else picked

with st.container(key="card_scorecard"):
    rows_html = []
    ranked = sorted(SECTORS, key=lambda r: -sum(r[k].get("st") == "alert" for k in METRIC_KEYS))
    for r in ranked:
        alerts = sum(r[k].get("st") == "alert" for k in METRIC_KEYS)
        dim = ' class="dim"' if highlight not in ("ALL", r["s"]) else ""
        pips = "".join(f'<span class="{"on" if i < alerts else ""}"></span>' for i in range(6))
        fn = f'<span class="fn">{r["fn"]}</span>' if r.get("fn") else ""
        cells = "".join(metric_cell(r[k]) for k in METRIC_KEYS)
        rows_html.append(
            f'<tr{dim}><td class="name"><span class="code">{r["s"]}</span><span class="nm">{r["name"]}</span>{fn}</td>'
            f'<td>{r["n"]}</td>{metric_cell(r["gdp"])}{cells}'
            f'<td><span class="pips">{pips}</span><b>{alerts} / 6</b></td></tr>')
    H(f"""
    <div class="tbl-wrap"><table class="dash"><thead><tr>
      <th>Sector</th><th>SOEs</th><th>Footprint<br>assets/GDP</th><th>ROA (%)<br>2022–24</th>
      <th>ROE (%)<br>2022–24</th><th>Current ratio<br>2022–24</th><th>Debt/assets<br>2020–24</th>
      <th>Debt/EBITDA (yrs)<br>2020–24</th><th>Z″<br>2021–24</th><th>Alerts</th>
    </tr></thead><tbody>{"".join(rows_html)}</tbody></table></div>
    <div class="legend-row">
      {chip("ok")} {chip("watch")} {chip("alert")}
      <span class="lt"><b>Thresholds from the note</b>: Z″ &lt; 1.1 alert, 1.1–2.6 watch · debt/EBITDA &gt; 6 alert,
      4–6 watch · debt/assets &gt; 0.5 alert, 0.5 watch</span>
      <span class="lt"><b>Illustrative thresholds</b>: ROA below 1% alert, drop of 2 pp or more watch · negative ROE
      alert, falling ROE watch · current ratio below 1 alert, below 3.5 or halved watch</span>
      <span class="lt">— not reported in the note · DISC is a single SOE in the Marshall Islands</span>
    </div>
    """)

c1, c2 = st.columns([7, 5], gap="medium")
with c1, st.container(key="card_zchart"):
    H('<p class="card-title">Z″ score by sector</p><p class="card-sub">2021–2024 average · 38 SOEs · '
      'shading marks distress (&lt;1.1) and grey zone (1.1–2.6)</p>')
    show(z_sector_chart(highlight))
    with st.expander("Show table"):
        st.dataframe(pd.DataFrame([(f"{s} {n}", ("≈" if a else "") + fmt(z), ZONE_LABEL[zone_of(z)])
                                   for s, n, z, a in Z_BY_SECTOR], columns=["Sector", "Z″ (2021–24)", "Zone"]),
                     hide_index=True)
    H('<p class="note"><b>UTIL at 5.0</b> sits in the safe zone, but alongside an ROE of −12% and debt-to-EBITDA of '
      '13.6 years, the score most likely reflects an asset-heavy balance sheet and <b>overstates</b> resilience.</p>')
with c2, st.container(key="card_dumbbell"):
    H(f'<p class="card-title">Change in profitability</p><p class="card-sub">COVID shock (2020–21) to recovery '
      f'(2022–24) · sectors the note reports</p><div class="legend-row" style="margin:0 0 4px">'
      f'<span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;border:2px solid {PREV}">'
      f'</span> 2020–21</span><span><span style="display:inline-block;width:11px;height:11px;border-radius:50%;'
      f'background:{BLUE}"></span> 2022–24</span></div>')
    show(dumbbell_chart(highlight))
    with st.expander("Show table"):
        st.dataframe(pd.DataFrame([("ROA (%)", s, a, b) for s, a, b, _ in ROA] +
                                  [("ROE (%)", s, a, b) for s, a, b, _ in ROE],
                                  columns=["Metric", "Sector", "2020–21", "2022–24"]), hide_index=True)
    H('<p class="note">Profitability fell while the economy was recovering, which points to <b>structural</b> '
      'rather than cyclical causes.</p>')

# ---- Countries -------------------------------------------------------------
section_head("countries", "Country monitor",
             "Utility health, the gap by economic structure, and each country's ownership model and transfer trend.")
c1, c2 = st.columns([7, 5], gap="medium")
with c1, st.container(key="card_zones"):
    cols_html = []
    for key in ("alert", "watch", "ok"):
        g = UTILITY_ZONES[key]
        items = "".join(
            f'<div class="ctry"><span><span class="cd">{c}</span>'
            f'{f"<span class=zs>{sub}</span>" if sub else ""}</span><span class="zv">{fmt(z)}</span></div>'
            for c, z, sub in g["items"])
        slots = '<div class="ctry slot">not named</div>' * (g["total"] - len(g["items"]))
        cols_html.append(f'<div class="zcol {key}"><h4><span><i>{GLYPH[key]}</i> {ZONE_LABEL[key]}</span>'
                         f'<span class="cnt">{g["total"]} countries</span></h4>{items}{slots}</div>')
    H(f"""
    <p class="card-title">Utility Z″ zones (2022–24)</p>
    <p class="card-sub">9 countries with utility data · distress 5, grey zone 2, safe 2</p>
    <div class="zboard">{"".join(cols_html)}</div>
    <div class="unk"><span>No value published, described only as below or near the distress threshold:</span>
    <span class="cd">FJI</span><span class="cd">WSM</span><span class="cd">TON</span></div>
    <p class="note">Empty slots are places where the note gives a zone count without naming the country.
    <b>MHL</b> fell sharply from 4.7 over the full period to 1.7.</p>
    """)
with c2, st.container(key="card_gap"):
    H('<p class="card-title">Z″ gap by economic structure</p><p class="card-sub">Sovereign-rent mean minus '
      "tourism-remittance mean (points) · Welch's t-test</p>")
    show(gap_chart(highlight))
    with st.expander("Show table"):
        st.dataframe(pd.DataFrame([(n, f"+{fmt(v)}") for _, n, v in SR_TR_GAP],
                                  columns=["Sector", "Z″ gap (points)"]), hide_index=True)
    H("<p class=\"note\">SOEs in <b>sovereign-rent economies</b> are consistently healthier. Their revenues are "
      "largely independent of the domestic cycle and are smoothed by institutions such as Kiribati's RERF and the "
      "Compact trust funds.</p>")

with st.container(key="card_countries"):
    body = "".join(
        f'<tr><td class="name"><span class="code">{c["c"]}</span><span class="nm">{c["name"]}</span></td>'
        f'<td>{c["own"]}</td><td>{c["eco"]}</td><td>{c["n"]}</td>{metric_cell({"v": c["gdp"]})}'
        f'{metric_cell(c["gr"])}{metric_cell(c["uz"])}</tr>' for c in COUNTRIES)
    H(f"""
    <p class="card-title">Country profiles</p>
    <p class="card-sub">Ownership model · economy type · sample size · transfer trend · utility Z″</p>
    <div class="tbl-wrap"><table class="dash"><thead><tr><th>Country</th><th>Ownership model</th>
    <th>Economy type</th><th>SOEs in sample</th><th>SOE assets/GDP</th>
    <th>Grants / SOE assets<br>2020–21 → 2020–24</th><th>Utility Z″<br>2022–24</th></tr></thead>
    <tbody>{body}</tbody></table></div>
    <p class="note">&#42; The note of Figure 14 classifies Nauru as tourism-remittance and excludes Solomon Islands,
    which differs from the main text. This dashboard follows the main text. ↑ and ↓ mark cases where the note gives
    only a direction.</p>
    """)

# ---- Calculator ------------------------------------------------------------
section_head("calculator", "Early warning calculator and stress test",
             "Enter four financial ratios to get the Z″ score and zone, and the next year's predicted grants from "
             "Equation (1). The shock sliders apply the note's external-shock coefficients.")


def apply_preset(name: str) -> None:
    for k in ("x1", "x2", "x3", "x4", "assets"):
        st.session_state[k] = PRESETS[name][k]
    st.session_state["preset"] = name


def clear_preset() -> None:
    st.session_state["preset"] = None


if "x1" not in st.session_state:
    apply_preset("median")

c1, c2 = st.columns([5, 7], gap="medium")
with c1, st.container(key="card_inputs"):
    H('<p class="card-title">SOE financial ratios</p><p class="card-sub">Presets are hypothetical example SOEs (illustrative)</p>')
    pcols = st.columns(3)
    for col, (key, p) in zip(pcols, PRESETS.items()):
        col.button(p["label"], key=f"btn_{key}", on_click=apply_preset, args=(key,), width="stretch",
                   type="primary" if st.session_state.get("preset") == key else "secondary")
    x1 = st.number_input("Working capital / total assets", key="x1", step=0.01, format="%.3f",
                         help="X1 · short-term liquidity buffer", on_change=clear_preset)
    x2 = st.number_input("Retained earnings / total assets", key="x2", step=0.01, format="%.3f",
                         help="X2 · cumulative profitability", on_change=clear_preset)
    x3 = st.number_input("EBIT / total assets", key="x3", step=0.01, format="%.3f",
                         help="X3 · operating efficiency", on_change=clear_preset)
    x4 = st.number_input("Book equity / total liabilities", key="x4", step=0.01, format="%.3f",
                         help="X4 · leverage", on_change=clear_preset)
    assets = st.number_input("Total assets (USD million)", key="assets", step=1.0, min_value=0.0, format="%.0f",
                             help="Converts the grant share to dollars", on_change=clear_preset)

    terms = [("6.56 × WC/TA", Z_COEF["x1"] * x1), ("3.26 × RE/TA", Z_COEF["x2"] * x2),
             ("6.72 × EBIT/TA", Z_COEF["x3"] * x3), ("1.05 × Equity/TL", Z_COEF["x4"] * x4)]
    max_abs = max([2.0] + [abs(t) for _, t in terms])
    contrib = "".join(
        f'<div class="contrib-row"><span class="lbl">{lbl}</span><div class="track">'
        f'<span class="{"pos" if t >= 0 else "neg"}" style="width:{abs(t) / max_abs * 50:.1f}%"></span></div>'
        f'<span class="val">{"+" if t >= 0 else ""}{fmt(t, 2)}</span></div>' for lbl, t in terms)
    H(f'<hr style="margin:14px 0;border:none;border-top:1px solid {LINE}"><p class="card-title">Contribution to Z″</p>'
      f'<p class="card-sub">Z″ = 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4</p>{contrib}'
      f'<hr style="margin:14px 0;border:none;border-top:1px solid {LINE}"><p class="card-title">External shocks</p>'
      f'<p class="card-sub">Coefficients from regressions controlling for SOE size, GDP growth, and country and '
      f'sector fixed effects</p>')
    disaster = st.slider("Increase in disaster intensity index", 0.0, 10.0, 0.0, 0.5, key="dis",
                         help="Z″ −0.23 per unit · index = (deaths + 0.3 × affected) ÷ population × 100")
    fx = st.slider("Depreciation (rise in LCU per USD)", 0.0, 5.0, 0.0, 0.1, key="fx",
                   help="Z″ −0.37 per unit · one unit means different things for each currency, so treat as "
                        "illustrative · not applicable to USD users (PLW, FSM, MHL)")
    H('<p class="note">Terms of trade has a positive but statistically insignificant coefficient, so it is left out.</p>')

z_base = z_score(x1, x2, x3, x4)
dz = SHOCK_DISASTER * disaster + SHOCK_FX * fx
z_stress = z_base + dz
p_base, p_stress = injection_shown(z_base), injection_shown(z_stress)
amt_base, amt_stress = assets * p_base / 100, assets * p_stress / 100

with c2, st.container(key="card_results"):
    zone = zone_of(z_base)
    negative_note = " (The equation gives a negative value, shown as 0%.)" if injection(z_base) < 0 else ""
    if disaster == 0 and fx == 0:
        delta = (f'<div class="delta" style="background:{SURFACE_2}">Move a shock slider to see the extra fiscal '
                 f'burden after stress.</div>')
    else:
        zone_drop = " · zone drops, so trigger rule 3 applies" if zone_of(z_stress) != zone else ""
        delta = (f'<div class="delta" style="background:{CRIT_WASH}">Shocks change Z″ by <b>{fmt(dz, 2)}</b> · '
                 f'extra fiscal burden <b>+{usd(amt_stress - amt_base)} (+{fmt(p_stress - p_base)} pp)</b>'
                 f'{zone_drop}</div>')
    H(f"""
    <p class="card-title">Results</p>
    <p class="card-sub">Predicted grants = 18.2 − 0.767 × previous-year Z″ (% of total assets)</p>
    <p class="lead">This SOE is in the <b>{ZONE_LABEL[zone].lower()}</b> zone
    (Z″ {fmt(z_base, 2)}). Equation (1) predicts grants of <b>{fmt(p_base)}%</b> of total assets next year,
    about {usd(amt_base)}.{negative_note}</p>
    <div class="results">
      <div class="res base"><div class="res-h">Current</div>
        <div class="res-z"><b>{fmt(z_base, 2)}</b>{chip(zone_of(z_base), ZONE_LABEL[zone_of(z_base)])}</div>
        <div class="res-line">Predicted grants <b>{fmt(p_base)}% of total assets</b></div>
        <div class="res-line">Amount <b>{usd(amt_base)}</b></div></div>
      <div class="res stress"><div class="res-h">After stress</div>
        <div class="res-z"><b>{fmt(z_stress, 2)}</b>{chip(zone_of(z_stress), ZONE_LABEL[zone_of(z_stress)])}</div>
        <div class="res-line">Predicted grants <b>{fmt(p_stress)}% of total assets</b></div>
        <div class="res-line">Amount <b>{usd(amt_stress)}</b></div></div>
    </div>
    {delta}
    <p class="card-title" style="margin-top:8px">Z″ and predicted grants</p>
    <p class="card-sub">Prediction line from Equation (1) · reference points from the note's Figure 10 ·
    blue dot = current input, red dot = after stress</p>
    """)
    show(curve_chart(z_base, z_stress))
    with st.expander("Show table"):
        st.dataframe(pd.DataFrame([
            ("Note: 5th percentile", "−4.70", "21.9"), ("Note: 75th percentile", "12.78", "8.4"),
            ("Current input", fmt(z_base, 2), fmt(p_base)), ("After stress", fmt(z_stress, 2), fmt(p_stress)),
        ], columns=["Case", "Z″", "Predicted grants (%)"]), hide_index=True)
    H('<p class="note">The coefficient is a <b>predictive relationship</b> significant at the 10% level, not a causal '
      'effect. Above a Z″ of about 23.7 the equation turns negative, so the dashboard shows 0%.</p>')

# ---- Trigger rules ---------------------------------------------------------
section_head("triggers", "Fiscal trigger rules",
             "Example rules that make the note's recommendation (ii), fiscal triggers linked to SOE financial "
             "health, concrete.")
TRIGGERS = [  # ILLUSTRATIVE rules
    ("alert", "Z″ &lt; 1.1 (distress)", "Activate the intervention protocol · require a restructuring plan · budget "
     "the expected grants explicitly for next year"),
    ("alert", "Debt/EBITDA &gt; 6 years", "Prior approval for new borrowing and guarantees · review tariffs and CSO "
     "compensation"),
    ("alert", "Stress test drops the SOE one zone or more", "Record the contingent liability in the fiscal risk "
     "statement · consider disaster risk financing such as a Cat DDO"),
    ("watch", "1.1 ≤ Z″ ≤ 2.6 (grey zone)", "Quarterly financial monitoring · require a performance improvement plan"),
    ("watch", "Financial statements filed more than 180 days after year end", "Disclosure warning · consider "
     "withholding transfers"),
    ("ok", "Z″ &gt; 2.6 and no other alerts", "Routine annual monitoring"),
]
c1, c2 = st.columns([7, 5], gap="medium")
with c1, st.container(key="card_triggers"):
    rows = "".join(f"<tr><td>{chip(s)}</td><td>{cond}</td><td>{act}</td></tr>" for s, cond, act in TRIGGERS)
    H(f"""
    <div class="tbl-wrap"><table class="dash"><thead><tr><th>Signal</th><th>Condition</th>
    <th>Pre-agreed action (example)</th></tr></thead><tbody>{rows}</tbody></table></div>
    <p class="note">The 180-day threshold is illustrative. Air Vanuatu filed an average of 280 days late, so the
    government could not see its exposure in time.</p>
    """)
with c2, st.container(key="card_case"):
    H("""
    <p class="card-title">Case: Air Vanuatu</p>
    <p class="card-sub">How a contingent liability became real (Box 1)</p>
    <ol class="tl">
      <li><span class="when">2021</span><span class="rail"></span><div class="what">IMF–World Bank DSA flags
      contingent liabilities of <b>up to 22% of GDP</b> under a combined stress scenario</div></li>
      <li><span class="when">Pre-2024</span><span class="rail"></span><div class="what">Financial statements filed on
      average <b>280 days</b> after year end</div></li>
      <li class="hot"><span class="when">May 2024</span><span class="rail"></span><div class="what">Voluntary
      liquidation of the sole international and domestic carrier</div></li>
      <li class="hot"><span class="when">2024</span><span class="rail"></span><div class="what">Secured debt assumed
      at <b>about 2% of GDP</b>, restructuring costs of <b>2.3%</b>. Deficit rises from about 3% projected to
      <b>6.7%</b>; growth revised down 2 pp</div></li>
      <li><span class="when">After</span><span class="rail"></span><div class="what">Restructured into AV3 Limited.
      Debt absorbed into public debt, with ongoing operating subsidies</div></li>
    </ol>
    """)

# ---- Footer ----------------------------------------------------------------
H("""
<div class="foot"><h2>Sources and caveats</h2><ul>
<li>Source: Francois, Blanco, Chowdhury, De Weerdt and Vasquez Ahued, <i>Between Necessity and Risk: State Owned
Enterprises and Fiscal Risk in the Pacific Islands</i>, World Bank policy note. All figures come from the note's
text, figures and annexes.</li>
<li>Z″ is the emerging-market model with the 3.25 constant removed, following Eidelman (1995). Distress &lt; 1.1,
grey zone 1.1–2.6, safe &gt; 2.6.</li>
<li>The Z″ analysis covers 38 of 83 SOEs (46%), and only 14 SOEs have 2024 statements. Some balance sheet data were
estimated.</li>
<li>The transfer regression uses 99 observations, a coefficient of −0.767 (significant at 10%), and country and
sector fixed effects. The note's Figure 10 value (21.9%) includes fixed effects and differs slightly from the plain
Equation (1) result (21.8%).</li>
<li>Inconsistency in the note: the summary says 5 of 11 utility SOEs are in distress, while the main text says 5 of
9 countries. This dashboard follows the main text (countries).</li>
<li>Calculator presets, the illustrative thresholds and the trigger rules are hypothetical values for
demonstration.</li>
</ul></div>
""")
