"""Sectors page: KPI scorecard, Z″ by sector and profitability change."""

from common import *  # noqa: F401,F403  (colours, data, formulas, helpers, charts)

section_head("Sector scorecard",
             "Each KPI is marked good, watch or alert by GICS sector. Sectors with the most alerts come first.")
# default "All" is set in app.py so the choice survives switching pages
picked = st.segmented_control("Highlight a sector", ["All", "UTIL", "DISC", "ENRG", "INDUS", "COMMS", "STPL", "REIT"],
                              key="highlight")
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

next_page("views/countries.py", "Next: Country monitor")
