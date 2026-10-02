"""Recommendations page: the note's five policy recommendations, its thresholds, and the Air Vanuatu case."""

from common import *  # noqa: F401,F403  (colours, data, formulas, helpers, charts)

section_head("Policy recommendations",
             "The note's five recommendations, the thresholds it uses to flag distress, and the Air Vanuatu case "
             "from Box 1.")
c1, c2 = st.columns([7, 5], gap="medium")
with c1, st.container(key="card_recs"):
    H(f"""
    <p class="card-title">Five recommendations</p>
    <p class="card-sub">From the note's conclusion</p>
    <ol class="recs">
      <li><b>Quantify and budget for SOE contingent liabilities</b> as explicit line items in national fiscal
      frameworks, moving beyond ad hoc bailouts toward transparent fiscal provisioning.</li>
      <li><b>Establish fiscal triggers linked to SOE financial health</b>, using the Early Warning System Z-score
      thresholds to activate pre-agreed intervention protocols before distress becomes a fiscal crisis.</li>
      <li><b>Introduce explicit community service obligation (CSO) compensation</b>, replacing untransparent
      subsidies with budgeted transfers to improve fiscal accountability and SOE incentives.</li>
      <li><b>Integrate exchange rate and natural disaster stress-testing</b> into SOE fiscal oversight, since these
      shocks are the dominant external drivers of SOE distress and fiscal injections.</li>
      <li><b>Build countercyclical fiscal buffers.</b> Sovereign rent-led economies: buffers built in good years and
      earmarked for SOE shocks. Tourism and remittance-led economies: contingent financing such as catastrophe
      deferred drawdown options and sovereign parametric insurance (for example through the Pacific Catastrophe Risk
      Insurance Company).</li>
    </ol>
    <p class="note">The note adds that these reforms will need sustained technical assistance and capacity building
    from development partners. Its proposed Early Warning System combines the Altman Z-score, sector-specific KPIs
    and the macro vulnerability indicators from the shock analysis.</p>
    <hr style="margin:16px 0;border:none;border-top:1px solid {LINE}">
    <p class="card-title">Thresholds the note uses</p>
    <p class="card-sub">The same thresholds rate the sector scorecard</p>
    <div class="tbl-wrap"><table class="dash"><thead><tr><th>Indicator</th><th>Threshold</th>
    <th>Meaning in the note</th></tr></thead><tbody>
      <tr><td>Altman Z″</td><td>{chip("alert", "below 1.1")}</td><td>Distress</td></tr>
      <tr><td>Altman Z″</td><td>{chip("watch", "1.1 to 2.6")}</td><td>Grey zone (vulnerable)</td></tr>
      <tr><td>Altman Z″</td><td>{chip("ok", "above 2.6")}</td><td>Safe</td></tr>
      <tr><td>Debt/EBITDA</td><td>below 2 · 2–4 · above 4 · above 6</td>
      <td>Low risk · moderate · elevated leverage · distress threshold</td></tr>
      <tr><td>Current ratio</td><td>below 1</td><td>Current liabilities exceed current assets</td></tr>
      <tr><td>Debt/assets</td><td>above 0.5</td><td>More than half of assets are debt-financed</td></tr>
    </tbody></table></div>
    """)
with c2, st.container(key="card_case"):
    H("""
    <p class="card-title">Case: Air Vanuatu</p>
    <p class="card-sub">How a contingent liability became real (Box 1)</p>
    <ol class="tl">
      <li><span class="when">2021</span><span class="rail"></span><div class="what">IMF–World Bank DSA flags
      contingent liabilities of <b>up to 22% of GDP</b> under a combined stress scenario</div></li>
      <li><span class="when">Reporting</span><span class="rail"></span><div class="what">Financial statements filed on
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
