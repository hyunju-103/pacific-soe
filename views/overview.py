"""Overview page: portfolio health at a glance."""

from common import *  # noqa: F401,F403  (colours, data, formulas, helpers, charts)

section_head("Portfolio overview",
             "Financial health distribution on the Altman Z″ score, and the utility indicators the note "
             "flags as the largest risk.")
left, right = st.columns([5, 7], gap="medium")
with left:
    with st.container(key="card_hero"):
        H(f"""
        <div class="hero-label">SOEs in distress or the grey zone</div>
        <div class="hero-value">39%<small>29% distress + 10% grey zone · 15 of 38 · nearly 4 in 10</small></div>
        <div class="zonebar">
          <div style="width:61%;background:{GOOD};border-radius:2px 0 0 2px"></div>
          <div style="width:10%;background:{WARN}"></div>
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
        ("Predicted grants to the most distressed SOEs", "21.9%", "of total assets / year",
         "Z″ at the 5th percentile (−4.7) · 8.4% at the 75th percentile (12.78), so more than double (Figure 10)"),
        ("Utilities debt-to-EBITDA", "13.6", "years", "Above the note's distress threshold of 6 · highest of any sector"),
        ("Countries with distressed utilities", "5", "of 9", "Grey zone 2 · safe 2 (2022–24 Z″)"),
        ("Utilities return on assets", "0.4%", "2022–24", "Down from 3.4% in 2020–21, during the recovery"),
    ]
    for row in (tiles[:2], tiles[2:]):
        cols = st.columns(2, gap="medium")
        for col, (label, value, unit, sub) in zip(cols, row):
            with col, st.container(key=f"tile_{label[:12].replace(' ', '_')}"):
                H(f"""
                <div class="tile-top"><span class="tile-label">{label}</span></div>
                <div class="tile-value">{value}<small>{unit}</small></div>
                <div class="tile-sub">{sub}</div>
                """)

next_page("views/sectors.py", "Next: Sector scorecard")
