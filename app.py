"""
Pacific SOE Fiscal Risk Monitor (Streamlit + Plotly, multipage)
================================================================

A Python re-implementation of the "Pacific SOE Fiscal Risk Monitor" example
dashboard, built from the figures published in the World Bank policy note
"Between Necessity and Risk: State Owned Enterprises and Fiscal Risk in the
Pacific Islands". This is an independent example, not an official World Bank
product.

Run it
------
    pip install -r requirements.txt
    streamlit run app.py

Each menu item at the top is its own page with its own address:
    /            Overview
    /sectors     Sector scorecard
    /countries   Country monitor
    /calculator  Early warning calculator
    /triggers    Trigger rules

Files
-----
    app.py       this file: page setup, top menu, title band, footer
    common.py    colours, data from the note, formulas, CSS, chart builders
    views/       one file per page
"""

import streamlit as st

from common import CSS, H, PRESETS

st.set_page_config(page_title="Pacific SOE Fiscal Risk Monitor", layout="wide")
H(CSS)

# ---------------------------------------------------------------------------
# Starting values, and keeping them when the reader switches pages.
# Streamlit forgets a widget's value when its page is not shown, so every key
# is copied back onto itself here, on every page run.
# ---------------------------------------------------------------------------
DEFAULTS = {k: PRESETS["median"][k] for k in ("x1", "x2", "x3", "x4", "assets")}
DEFAULTS.update(preset="median", dis=0.0, fx=0.0, highlight="All")
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value
    st.session_state[key] = st.session_state[key]

# ---------------------------------------------------------------------------
# Pages and the top menu
# ---------------------------------------------------------------------------
pages = [
    st.Page("views/overview.py", title="Overview", url_path="overview", default=True),
    st.Page("views/sectors.py", title="Sectors", url_path="sectors"),
    st.Page("views/countries.py", title="Countries", url_path="countries"),
    st.Page("views/calculator.py", title="Early warning calculator", url_path="calculator"),
    st.Page("views/triggers.py", title="Trigger rules", url_path="triggers"),
]
current = st.navigation(pages, position="top")

# ---------------------------------------------------------------------------
# Title band (the long description only on the Overview page)
# ---------------------------------------------------------------------------
intro = ""
if current.title == "Overview":
    intro = ("<p>An example Early Warning System built from the figures published in the World Bank policy note "
             "<i>Between Necessity and Risk</i>. The note does not publish SOE-level names, so the calculator "
             "presets and trigger rules are illustrative. This is an independent example, not an official World "
             "Bank product.</p>")
H(f"""
<div class="band">
  <div class="eyebrow">Fiscal risk management · Example dashboard</div>
  <h1>Pacific SOE Fiscal Risk Monitor</h1>
  {intro}
  <div class="meta">
    <span>Sample <b>83 SOEs · 11 countries</b></span>
    <span>Z″ computed for <b>38 SOEs</b> (2021–2024)</span>
    <span>KPI period <b>2020–2024</b></span>
    <span>Financials excluded</span>
    <span class="flag">▲ Illustrative values are flagged</span>
  </div>
</div>
""")

current.run()

# ---------------------------------------------------------------------------
# Footer (same on every page)
# ---------------------------------------------------------------------------
FOOTER_PLACEHOLDER = None
