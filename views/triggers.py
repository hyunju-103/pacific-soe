"""Trigger rules page: example fiscal triggers and the Air Vanuatu case."""

from common import *  # noqa: F401,F403  (colours, data, formulas, helpers, charts)

section_head("Fiscal trigger rules",
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
