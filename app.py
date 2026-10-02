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

Each tab under the title is its own page with its own address:
    /            Overview
    /sectors     Sector scorecard
    /countries   Country monitor
    /calculator  Early warning calculator
    /recommendations  Policy recommendations

Files
-----
    app.py       this file: page setup, title band, tab bar, footer
    common.py    colours, data from the note, formulas, CSS, chart builders
    views/       one file per page
"""

import streamlit as st

from common import CSS, H, PRESETS, tab_css

st.set_page_config(page_title="Pacific SOE Fiscal Risk Monitor", layout="wide")
H(CSS)

# ---------------------------------------------------------------------------
# Starting values, and keeping them when the reader switches pages.
# Streamlit forgets a widget's value when its page is not shown, so every key
# is copied back onto itself here, on every page run.
# ---------------------------------------------------------------------------
DEFAULTS = {k: PRESETS["median"][k] for k in ("x1", "x2", "x3", "x4")}  # Table 1 sample medians
DEFAULTS.update(assets=None, preset="median", dis=0.0, fx=0.0, highlight="All")
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value
    st.session_state[key] = st.session_state[key]

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
# (key, page): the key names the tab's container so the current tab can be underlined
pages = {
    "overview": st.Page("views/overview.py", title="Overview", url_path="overview", default=True),
    "sectors": st.Page("views/sectors.py", title="Sectors", url_path="sectors"),
    "countries": st.Page("views/countries.py", title="Countries", url_path="countries"),
    "calculator": st.Page("views/calculator.py", title="Early warning calculator", url_path="calculator"),
    "recommendations": st.Page("views/recommendations.py", title="Recommendations", url_path="recommendations"),
}
# Streamlit's own menu is hidden; the tab bar below the title band replaces it.
current = st.navigation(list(pages.values()), position="hidden")
current_key = next(k for k, p in pages.items() if p.url_path == current.url_path)

# ---------------------------------------------------------------------------
# Title band (the long description only on the Overview page)
# ---------------------------------------------------------------------------
intro = ""
if current.title == "Overview":
    intro = ("<p>An Early Warning System dashboard built from the figures published in the World Bank policy "
             "note <i>Between Necessity and Risk</i>. Every figure on this page comes from the note. Independently "
             "made; not an official World Bank product.</p>")
H(f"""
{tab_css(current_key)}
<div class="band">
  <div class="eyebrow">Fiscal risk management · Policy note dashboard</div>
  <h1>Pacific SOE Fiscal Risk Monitor</h1>
  {intro}
  <div class="meta">
    <span>Sample <b>83 SOEs · 11 countries</b></span>
    <span>Z″ computed for <b>38 SOEs</b> (2021–2024)</span>
    <span>KPI period <b>2020–2024</b></span>
    <span>Financials excluded</span>
    <span>Source <b>World Bank policy note</b></span>
  </div>
</div>
""")

# Tab bar: every tab always visible; clicking one opens that page
with st.container(key="tabbar", horizontal=True, gap=None):
    for key, page in pages.items():
        with st.container(key=f"tab_{key}", width="content"):
            st.page_link(page, label=page.title)

current.run()

# ---------------------------------------------------------------------------
# Footer (same on every page)
# ---------------------------------------------------------------------------
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
<li>Scorecard ratings use only thresholds stated in the note. The calculator applies the note's published
coefficients (Z″ weights, Equation (1) and the shock estimates) to the ratios entered, starting from the sample
medians in Table 1.</li>
</ul></div>
""")
