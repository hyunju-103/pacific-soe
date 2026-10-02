"""Calculator page: Z″, predicted grants and stress test for one SOE."""

from common import *  # noqa: F401,F403  (colours, data, formulas, helpers, charts)

section_head("Early warning calculator and stress test",
             "Enter four financial ratios to get the Z″ score and zone, and the next year's predicted grants from "
             "Equation (1). The shock sliders apply the note's external-shock coefficients.")


def apply_preset(name: str) -> None:
    for k in ("x1", "x2", "x3", "x4", "assets"):
        st.session_state[k] = PRESETS[name][k]
    st.session_state["preset"] = name


def clear_preset() -> None:
    st.session_state["preset"] = None


# Starting values (the "Sample median" preset) are set in app.py.

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
    disaster = st.slider("Increase in disaster intensity index", 0.0, 10.0, step=0.5, key="dis",
                         help="Z″ −0.23 per unit · index = (deaths + 0.3 × affected) ÷ population × 100")
    fx = st.slider("Depreciation (rise in LCU per USD)", 0.0, 5.0, step=0.1, key="fx",
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

next_page("views/triggers.py", "Next: Trigger rules")
