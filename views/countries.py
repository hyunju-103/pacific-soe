"""Countries page: utility zones, economic-structure gap and country profiles."""

from common import *  # noqa: F401,F403  (colours, data, formulas, helpers, charts)

section_head("Country monitor",
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
    show(gap_chart("ALL"))
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

next_page("views/calculator.py", "Next: Early warning calculator")
