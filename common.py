"""
Shared pieces for every page of the dashboard: colours, data from the policy
note, formulas, CSS and chart builders. Change figures here and every page
picks them up.
"""

from __future__ import annotations

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
# CSS
# ---------------------------------------------------------------------------
# Streamlit's own top menu (st.navigation(position="top")): white bar, the
# current page in navy with a blue underline.
TOPNAV_CSS = f"""
header[data-testid="stHeader"] {{ background: {SURFACE}; border-bottom: 1px solid {LINE}; }}
a[data-testid="stTopNavLink"] {{ background: transparent !important; border-radius: 0; border-bottom: 3px solid transparent; padding-left: 4px; padding-right: 4px; margin-right: 14px; }}
a[data-testid="stTopNavLink"] p {{ color: {INK_2}; font-weight: 600; font-size: 14px; }}
a[data-testid="stTopNavLink"]:hover p {{ color: {NAVY}; }}
a[data-testid="stTopNavLink"][aria-current="page"] {{ border-bottom-color: {BLUE}; }}
a[data-testid="stTopNavLink"][aria-current="page"] p {{ color: {NAVY}; }}
div[data-testid="stPageLink"] p {{ color: {BLUE_STRONG}; font-weight: 600; }}
"""

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
html, body, .stApp, .stMarkdown, button, input, textarea {{ font-family: {FONT}; }}
.stApp {{ background: {BG}; }}
[data-testid="stMainBlockContainer"], .block-container {{ max-width: 1240px; padding-top: 5rem; padding-bottom: 3rem; }}
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
{TOPNAV_CSS}

/* section headings */
.sec-head {{ margin: 22px 0 6px; }}
.sec-head h2 {{ color: {NAVY}; font-size: 22px; font-weight: 700; margin: 0; padding: 0; }}
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


def section_head(title: str, text: str) -> None:
    H(f'<div class="sec-head"><h2>{title}</h2><p>{text}</p></div>')


def next_page(path: str, label: str) -> None:
    """Link to the next page at the bottom of each page."""
    st.write("")
    st.page_link(path, label=label, icon=":material/arrow_forward:", icon_position="right")


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
