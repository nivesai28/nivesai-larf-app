"""
NivesAI — LARF Overlay Research Tool
Streamlit app — v1.1
Author: Sneha Joshi | NivesAI

All outputs are retrospective research simulations based on historical NAV data.
This is not investment advice.
"""

import os
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NivesAI | LARF Research Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
BRAND_TEAL    = "#0d6e6e"
BNH_COLOR     = "#9ca3af"
OVERLAY_COLOR = "#0d6e6e"
CRASH_COLOR   = "rgba(239, 68, 68, 0.13)"
ACTIVE_BAR    = "#ef4444"
IDLE_BAR      = "#e5e7eb"
DEFAULT_AMOUNT = 100_000

# Exact crash period dates — must match engine definitions
CRASH_PERIODS = [
    ("2011 Bear",            "2011-01-01", "2011-12-31"),
    ("2015-16 Correction",   "2015-03-01", "2016-03-31"),
    ("2018-19 NBFC Crisis",  "2018-09-01", "2019-03-31"),
    ("2020 COVID Crash",     "2020-01-15", "2020-04-30"),
]

CONFIDENCE_LABELS = {
    "HIGH":   ("Strong fit",    "#dcfce7", "#15803d"),
    "MEDIUM": ("Moderate fit",  "#fef9c3", "#854d0e"),
    "LOW":    ("Mixed signals", "#fee2e2", "#991b1b"),
}

ROLE_EXPLAIN = {
    "Core":         "Holds up reasonably well in downturns, recovers steadily. A fund you can stay invested in through cycles.",
    "Stabiliser":   "Calm and low-volatility. Doesn't fall much but also doesn't grow fast. Good for reducing portfolio swings.",
    "Trend / Quant": "Strongly driven by market trends — rises fast in bull runs but also falls sharply in downturns. Needs careful timing.",
    "Satellite":    "High risk, high reward. Deep drawdowns, slow recovery. Best used as a small part of a portfolio, not the core.",
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.nives-brand { font-size:1.5rem; font-weight:700; color:#0d6e6e; letter-spacing:-0.5px; }
.nives-sub   { font-size:0.78rem; color:#6b7280; margin-top:-4px; }

.metric-card {
    background:#f9fafb; border:1px solid #e5e7eb;
    border-radius:10px; padding:14px 16px; text-align:center;
}
.metric-label { font-size:0.72rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.5px; }
.metric-val   { font-size:1.35rem; font-weight:700; color:#111827; margin:4px 0 2px; }
.metric-delta { font-size:0.82rem; font-weight:600; }
.delta-pos    { color:#16a34a; }
.delta-neg    { color:#dc2626; }
.delta-neu    { color:#6b7280; }

.quick-strip {
    display:flex; flex-wrap:wrap; gap:8px; align-items:center;
    background:#f9fafb; border:1px solid #e5e7eb;
    border-radius:8px; padding:10px 16px; margin:8px 0 16px;
    font-size:0.83rem; color:#374151;
}
.qs-item { display:flex; flex-direction:column; gap:1px; }
.qs-label { font-size:0.68rem; color:#9ca3af; text-transform:uppercase; letter-spacing:0.4px; }
.qs-val   { font-weight:600; color:#111827; }
.qs-sep   { color:#d1d5db; font-size:1rem; margin:0 2px; }

.val-badge-green  { background:#dcfce7; color:#15803d; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600; }
.val-badge-yellow { background:#fef9c3; color:#854d0e; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600; }
.val-badge-red    { background:#fee2e2; color:#991b1b; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600; }

.callout-green {
    background:#f0fdf4; border-left:4px solid #16a34a;
    border-radius:0 8px 8px 0; padding:10px 16px; margin:12px 0;
    font-size:0.88rem; color:#15803d; line-height:1.5;
}
.callout-warn {
    background:#fff7ed; border-left:4px solid #f97316;
    border-radius:0 8px 8px 0; padding:10px 16px; margin:12px 0;
    font-size:0.88rem; color:#9a3412; line-height:1.5;
}
.callout-blue {
    background:#eff6ff; border-left:4px solid #3b82f6;
    border-radius:0 8px 8px 0; padding:10px 16px; margin:12px 0;
    font-size:0.88rem; color:#1e40af; line-height:1.5;
}

.section-hdr {
    font-size:0.82rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.8px; color:#374151; margin:28px 0 10px;
    border-bottom:2px solid #0d6e6e; padding-bottom:4px;
}
.disclaimer {
    font-size:0.72rem; color:#9ca3af; line-height:1.5;
    border-top:1px solid #e5e7eb; margin-top:20px; padding-top:14px;
}
.block-container { padding-top:1.5rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading research data …")
def load_master():
    results = pd.read_csv(f"{DATA_DIR}/larf_regime_results_v2.csv")
    results["scheme_code"] = results["scheme_code"].astype(str)

    val = pd.read_csv(f"{DATA_DIR}/larf_validation_summary_v1.csv")
    val["scheme_code"] = val["scheme_code"].astype(str)

    scheme = pd.read_csv(f"{DATA_DIR}/scheme_master_v2_FROZEN.csv")
    scheme["scheme_code"] = scheme["scheme_code"].astype(str)

    beh = pd.read_csv(f"{DATA_DIR}/behaviour_classification_app.csv")
    beh["scheme_code"] = beh["scheme_code"].astype(str)
    beh["summary_text"] = beh["summary_text"].fillna("")

    crash = pd.read_csv(f"{DATA_DIR}/crash_periods_app.csv")
    crash["scheme_code"] = crash["scheme_code"].astype(str)

    regime_tl = pd.read_csv(f"{DATA_DIR}/regime_timeline.csv")
    regime_tl["date"] = pd.to_datetime(regime_tl["date"])

    df = results.merge(
        val[["scheme_code", "validation_score", "fully_validated",
             "wf_pass", "wf_pass_rate", "wf_windows_total", "wf_windows_pass",
             "oos_eligible", "oos_pass", "mc_pass", "real_percentile",
             "stability_pass", "cliff_detected"]],
        on="scheme_code", how="left"
    ).merge(
        scheme[["scheme_code", "scheme_name", "scheme_category", "amc"]],
        on="scheme_code", how="left"
    ).merge(
        beh[["scheme_code", "final_role", "classification_confidence", "summary_text"]],
        on="scheme_code", how="left"
    )
    return df, crash, regime_tl


@st.cache_data(show_spinner="Loading equity curves …")
def load_curves():
    parquet = f"{DATA_DIR}/larf_regime_curves_v2.parquet"
    csv_p   = f"{DATA_DIR}/larf_regime_curves_v2.csv"
    if os.path.exists(parquet):
        df = pd.read_parquet(parquet, columns=["scheme_code","date","bnh_value","v2a_value"])
    elif os.path.exists(csv_p):
        df = pd.read_csv(csv_p, usecols=["scheme_code","date","bnh_value","v2a_value"])
    else:
        st.error("Curves data not found. Please run data_prep_colab.py first.")
        st.stop()
    df["scheme_code"] = df["scheme_code"].astype(str)
    # Force datetime — critical for Plotly date axis
    df["date"] = pd.to_datetime(df["date"], utc=False).dt.normalize()
    return df


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_pct(v, decimals=1, sign=True):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    prefix = "+" if sign and v > 0 else ""
    return f"{prefix}{v * 100:.{decimals}f}%"

def fmt_inr(v):
    if v is None or np.isnan(v):
        return "—"
    if v >= 1_00_000:
        return f"₹{v/1_00_000:.2f}L"
    return f"₹{v:,.0f}"

def scale_curves(fund_curves, amount, start_date=None):
    df = fund_curves.copy().sort_values("date").reset_index(drop=True)
    if start_date is not None:
        df = df[df["date"] >= pd.Timestamp(start_date)].reset_index(drop=True)
    if len(df) == 0:
        return df
    initial = df["bnh_value"].iloc[0]
    if initial == 0 or np.isnan(initial):
        return df
    scale = amount / initial
    df["bnh_scaled"] = (df["bnh_value"] * scale).round(0)
    df["v2a_scaled"] = (df["v2a_value"] * scale).round(0)
    # Convert dates to ISO strings — Plotly renders these perfectly
    df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
    return df

def validation_badge_html(score, oos_eligible):
    score = int(score) if pd.notna(score) else 0
    max_s = 4 if oos_eligible else 3
    if score >= max_s:
        return f'<span class="val-badge-green">✅ Fully Validated ({score}/{max_s} tests)</span>'
    elif score >= 2:
        return f'<span class="val-badge-yellow">⚠️ Partially Validated ({score}/{max_s} tests)</span>'
    else:
        return f'<span class="val-badge-red">❌ Not Validated ({score}/{max_s} tests)</span>'


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nives-brand">NivesAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="nives-sub">LARF — Overlay Research Engine</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Engine:** v2a · Regime-Gated")
    st.markdown("**Funds covered:** 173 Indian mutual funds")
    st.markdown("**History:** Jan 2010 – May 2026 (16 years)")
    st.markdown("**Comparison:** Rule-based overlay vs simply holding the fund")
    st.markdown("**When overlay is idle:** Cash earns Quantum Liquid Fund returns")

    st.markdown("---")
    st.markdown("**How the overlay works**")
    st.markdown(
        "A set of rules monitors the broader market (Nifty 50) and the fund's "
        "own stress signals. When the market enters a downturn, the strategy "
        "automatically trims a small portion of the fund position and moves "
        "that cash to a liquid fund. When conditions recover, it stays put. "
        "No predictions, no discretion — only rules."
    )

    st.markdown("---")
    st.markdown(
        '<div class="disclaimer">'
        "<strong>Important:</strong> All results shown are historical simulations. "
        "They show what <em>would have happened</em> — not what <em>will happen</em>. "
        "This is a research tool, not investment advice. "
        "NivesAI is not a SEBI-registered investment advisor."
        "</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
master_df, crash_df, regime_tl = load_master()
curves_df = load_curves()

# ─────────────────────────────────────────────────────────────────────────────
# FUND SELECTOR FORM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## LARF Overlay Research Tool")
st.markdown(
    "Choose a fund and see how a rule-based overlay strategy would have affected "
    "your returns and losses over 16 years of Indian market history — compared to "
    "simply holding the fund."
)

fund_options = {}
for _, row in master_df.sort_values(["scheme_category", "scheme_name"]).iterrows():
    label = f"{row['scheme_name']}  ·  {row['scheme_category']}"
    fund_options[label] = str(row["scheme_code"])

row1_c1, row1_c2 = st.columns([5, 2])
with row1_c1:
    selected_label = st.selectbox(
        "Fund",
        options=["— choose a fund —"] + list(fund_options.keys()),
        label_visibility="collapsed",
    )
with row1_c2:
    amount = st.number_input(
        "Initial investment (₹)",
        min_value=10_000, max_value=10_00_00_000,
        value=DEFAULT_AMOUNT, step=10_000, format="%d",
        label_visibility="collapsed",
    )

row2_c1, row2_c2, row2_c3 = st.columns([2.5, 2.5, 1])
with row2_c1:
    inv_date = st.date_input(
        "Your investment start date",
        value=datetime.date(2010, 1, 4),
        min_value=datetime.date(2010, 1, 1),
        max_value=datetime.date(2026, 5, 31),
        help="Change this to see results from a different investment start date. "
             "The chart will rebase to show your portfolio value from that date.",
    )
with row2_c2:
    st.markdown(
        '<div style="font-size:0.78rem;color:#9ca3af;padding-top:10px">'
        "Set to the date you actually invested (or any date you want to explore). "
        "Results above the chart always show the full 2010–2026 simulation."
        "</div>",
        unsafe_allow_html=True,
    )
with row2_c3:
    run = st.button("View Results →", type="primary", use_container_width=True)

if selected_label == "— choose a fund —" or not run:
    st.markdown("---")
    st.markdown("👆 Select a fund and click **View Results** to begin.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# FUND DATA
# ─────────────────────────────────────────────────────────────────────────────
scheme_code  = fund_options[selected_label]
fund_row     = master_df[master_df["scheme_code"] == scheme_code].iloc[0]
fund_curves  = curves_df[curves_df["scheme_code"] == scheme_code].sort_values("date").reset_index(drop=True)
fund_crash   = crash_df[crash_df["scheme_code"] == scheme_code]
crash_main   = fund_crash[~fund_crash["period_name"].str.contains("Sideways", na=False)]
crash_sw     = fund_crash[fund_crash["period_name"].str.contains("Sideways", na=False)]

# Clamp investment date to fund's actual start
sim_start_dt = pd.Timestamp(fund_row.get("sim_start_date", "2010-01-04"))
sim_end_dt   = pd.Timestamp(fund_row.get("sim_end_date",   "2026-04-08"))
inv_date_ts  = pd.Timestamp(inv_date)
if inv_date_ts < sim_start_dt:
    inv_date_ts = sim_start_dt
if inv_date_ts >= sim_end_dt:
    inv_date_ts = sim_start_dt

scaled = scale_curves(fund_curves, amount, start_date=inv_date_ts)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# FUND HEADER
# ─────────────────────────────────────────────────────────────────────────────
hc1, hc2 = st.columns([6, 2])
with hc1:
    st.markdown(f"### {fund_row['scheme_name']}")
    cat   = fund_row.get("scheme_category", "")
    role  = fund_row.get("final_role", "")
    conf  = str(fund_row.get("classification_confidence", "")).upper()
    conf_label, conf_bg, conf_fg = CONFIDENCE_LABELS.get(conf, ("—", "#f3f4f6", "#6b7280"))
    role_desc = ROLE_EXPLAIN.get(role, "")
    st.markdown(
        f'<span style="color:#6b7280;font-size:0.85rem">{cat}</span>',
        unsafe_allow_html=True,
    )
with hc2:
    oos_elig = bool(fund_row.get("oos_eligible", True))
    val_score = fund_row.get("validation_score", 0)
    st.markdown(
        validation_badge_html(val_score, oos_elig),
        unsafe_allow_html=True,
    )

# ── Quick-facts strip (replaces bottom Fund Behaviour Profile) ────────────────
role_conf_html = (
    f'<span style="background:{conf_bg};color:{conf_fg};border-radius:4px;'
    f'padding:2px 8px;font-size:0.78rem;font-weight:600">{conf_label}</span>'
)
st.markdown(f"""
<div class="quick-strip">
  <div class="qs-item">
    <span class="qs-label">Fund role</span>
    <span class="qs-val">{role}</span>
  </div>
  <span class="qs-sep">·</span>
  <div class="qs-item">
    <span class="qs-label">Role confidence</span>
    <span class="qs-val">{role_conf_html}</span>
  </div>
  <span class="qs-sep">·</span>
  <div class="qs-item">
    <span class="qs-label">Data available from</span>
    <span class="qs-val">{sim_start_dt.strftime("%d %b %Y")} → {sim_end_dt.strftime("%d %b %Y")}</span>
  </div>
  <span class="qs-sep">·</span>
  <div class="qs-item">
    <span class="qs-label">Total rule-based trims</span>
    <span class="qs-val">{int(fund_row.get("v2a_num_sells", 0))} sells over {fund_row.get("years", 16):.0f} years</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Role + confidence explanation callout
if role or conf:
    role_note = f"<strong>{role}</strong>: {role_desc} " if role_desc else ""
    conf_note = {
        "HIGH":   "The fund's behaviour strongly fits this role.",
        "MEDIUM": "The fund fits this role in most conditions, with some mixed signals.",
        "LOW":    "The fund's behaviour was mixed — it didn't cleanly fit one category. "
                  "Treat this role as directional, not definitive.",
    }.get(conf, "")
    st.markdown(
        f'<div class="callout-blue">{role_note}{conf_note}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PANEL A — METRICS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Performance Summary (full 2010–2026 simulation)</div>',
            unsafe_allow_html=True)

bnh_cagr   = fund_row["bnh_cagr"]
v2a_cagr   = fund_row["v2a_cagr"]
bnh_dd     = fund_row["bnh_max_dd"]
v2a_dd     = fund_row["v2a_max_dd"]
bnh_score  = bnh_cagr - abs(bnh_dd) / 2
v2a_score  = fund_row["v2a_score"]
edge_cagr  = fund_row["v2a_edge_cagr"]
edge_dd    = fund_row["v2a_edge_dd"]   # negative = overlay shallower = good
edge_score = v2a_score - bnh_score
regime_pct = fund_row.get("v2a_regime_pct", 0)
num_sells  = fund_row.get("v2a_num_sells", 0)

final_bnh = scaled["bnh_scaled"].iloc[-1] if len(scaled) > 0 else amount
final_v2a = scaled["v2a_scaled"].iloc[-1] if len(scaled) > 0 else amount

def metric_html(label, bnh_val, v2a_val, delta, fmt_fn,
                higher_is_better=True, delta_note="vs simple holding"):
    good = (higher_is_better and delta > 0) or (not higher_is_better and delta < 0)
    bad  = (higher_is_better and delta < 0) or (not higher_is_better and delta > 0)
    dcls = "delta-pos" if good else ("delta-neg" if bad else "delta-neu")
    sign = "+" if delta > 0 else ""
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div style="display:flex;justify-content:center;gap:18px;align-items:baseline;margin:6px 0 4px">
        <div>
          <div style="font-size:0.7rem;color:#9ca3af">Simple holding</div>
          <div class="metric-val" style="font-size:1.2rem">{fmt_fn(bnh_val)}</div>
        </div>
        <div>
          <div style="font-size:0.7rem;color:#0d6e6e;font-weight:600">With overlay</div>
          <div class="metric-val" style="font-size:1.2rem;color:#0d6e6e">{fmt_fn(v2a_val)}</div>
        </div>
      </div>
      <div class="metric-delta {dcls}">{sign}{fmt_fn(delta)} {delta_note}</div>
    </div>"""

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(metric_html(
        "Annual Return (CAGR)",
        bnh_cagr, v2a_cagr, edge_cagr,
        lambda v: fmt_pct(v, 2),
        higher_is_better=True,
    ), unsafe_allow_html=True)
with m2:
    st.markdown(metric_html(
        "Worst Drop (Max Drawdown)",
        bnh_dd, v2a_dd, edge_dd,
        lambda v: fmt_pct(v, 1, sign=False),
        higher_is_better=False,
        delta_note="less severe",
    ), unsafe_allow_html=True)
with m3:
    st.markdown(metric_html(
        "Overall Score",
        bnh_score, v2a_score, edge_score,
        lambda v: f"{v:+.3f}" if pd.notna(v) else "—",
        higher_is_better=True,
        delta_note="improvement",
    ), unsafe_allow_html=True)
with m4:
    inv_label = f"from {inv_date_ts.strftime('%d %b %Y')}"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Your portfolio value</div>
      <div style="display:flex;justify-content:center;gap:18px;align-items:baseline;margin:6px 0 4px">
        <div>
          <div style="font-size:0.7rem;color:#9ca3af">Simple holding</div>
          <div class="metric-val" style="font-size:1.2rem">{fmt_inr(final_bnh)}</div>
        </div>
        <div>
          <div style="font-size:0.7rem;color:#0d6e6e;font-weight:600">With overlay</div>
          <div class="metric-val" style="font-size:1.2rem;color:#0d6e6e">{fmt_inr(final_v2a)}</div>
        </div>
      </div>
      <div class="metric-delta delta-neu">₹{amount:,.0f} invested {inv_label}</div>
    </div>""", unsafe_allow_html=True)
with m5:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Overlay activity</div>
      <div class="metric-val" style="margin:10px 0 4px">{regime_pct*100:.0f}%</div>
      <div style="color:#6b7280;font-size:0.82rem">of days overlay was watching</div>
      <div style="color:#9ca3af;font-size:0.78rem;margin-top:4px">
        Made {int(num_sells)} rule-based trims<br>over {fund_row.get('years',16):.0f} years
      </div>
    </div>""", unsafe_allow_html=True)

# Score explanation
st.markdown(
    '<div style="font-size:0.75rem;color:#9ca3af;margin-top:6px">'
    "<strong>Annual Return (CAGR)</strong>: average yearly growth rate. "
    "<strong>Worst Drop</strong>: the biggest fall from peak to trough in the 16-year period. "
    "<strong>Overall Score</strong>: a single number that balances return against risk "
    "(higher is better). "
    "<strong>Overlay Activity</strong>: the rule-based strategy was only active "
    f"{regime_pct*100:.0f}% of the time — it stayed out of the way in bull markets."
    "</div>",
    unsafe_allow_html=True,
)

# 2024-26 callout — plain language
if len(crash_sw) > 0:
    sw = crash_sw.iloc[0]
    if pd.notna(sw.get("v2a_beats_bnh")):
        bnh_fall = abs(sw["bnh_max_dd"]) * 100 if pd.notna(sw["bnh_max_dd"]) else None
        v2a_fall = abs(sw["v2a_max_dd"]) * 100 if pd.notna(sw["v2a_max_dd"]) else None
        if sw["v2a_beats_bnh"]:
            fall_text = (f"the fund fell {bnh_fall:.1f}% at its worst; "
                         f"with the overlay it fell only {v2a_fall:.1f}%. "
                         if bnh_fall and v2a_fall else "")
            st.markdown(
                f'<div class="callout-green">📈 <strong>Recent market (2024–26):</strong> '
                f'Markets were choppy and went largely sideways. During this period, '
                f'{fall_text}'
                f'Across all 173 funds studied, the rule-based overlay outperformed '
                f'simple holding in <strong>152 out of 173 funds (88%)</strong>.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="callout-warn">📉 <strong>Recent market (2024–26):</strong> '
                f'For this specific fund, the overlay did not outperform simple holding in '
                f'the 2024–26 sideways period. However, across all 173 funds studied, '
                f'the overlay still outperformed in <strong>152 out of 173 funds (88%)</strong>.</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# PANEL B — EQUITY CURVE + REGIME ACTIVATION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Portfolio Growth Over Time</div>', unsafe_allow_html=True)

date_range_note = (
    f"Chart shows ₹{amount:,.0f} invested from {inv_date_ts.strftime('%d %b %Y')}. "
    if inv_date_ts > sim_start_dt else
    f"Chart shows full simulation from {sim_start_dt.strftime('%d %b %Y')}. "
)
st.markdown(
    f'<span style="font-size:0.78rem;color:#6b7280">{date_range_note}'
    f'Grey shaded areas = major market crashes. '
    f'Bottom bar = when the overlay strategy was "watching" (non-bull market conditions).'
    f'</span>',
    unsafe_allow_html=True,
)

if len(scaled) == 0:
    st.warning("No chart data available for this fund and date range.")
else:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.82, 0.18],
        vertical_spacing=0.04,
        subplot_titles=("", "Overlay active (red = strategy watching market)"),
    )

    # Date strings for Plotly (avoids all datetime parsing issues)
    dates = scaled["date_str"].tolist()

    # ── Equity curves ──────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=dates, y=scaled["bnh_scaled"].tolist(),
        mode="lines", name="Simple holding (Buy & Hold)",
        line=dict(color=BNH_COLOR, width=2),
        hovertemplate="<b>Simple holding</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=dates, y=scaled["v2a_scaled"].tolist(),
        mode="lines", name="With LARF overlay",
        line=dict(color=OVERLAY_COLOR, width=2.5),
        hovertemplate="<b>With overlay</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>",
    ), row=1, col=1)

    # ── Regime activation bar ──────────────────────────────────
    regime_fund = regime_tl[
        (regime_tl["date"] >= scaled["date"].min()) &
        (regime_tl["date"] <= scaled["date"].max())
    ].copy()
    regime_dates = regime_fund["date"].dt.strftime("%Y-%m-%d").tolist()

    fig.add_trace(go.Bar(
        x=regime_dates,
        y=regime_fund["macro_active"].astype(int).tolist(),
        marker_color=[ACTIVE_BAR if v else IDLE_BAR
                      for v in regime_fund["macro_active"]],
        name="Overlay watching",
        showlegend=True,
        hovertemplate="<b>%{x}</b><br>Overlay active: %{y}<extra></extra>",
    ), row=2, col=1)

    # ── Crash period shading — using shapes on paper coordinates ──
    # Top chart (row 1) occupies roughly paper y: 0.22 → 1.0
    shapes = []
    for _, start, end in CRASH_PERIODS:
        shapes.append(dict(
            type="rect",
            xref="x", yref="paper",
            x0=start, x1=end,
            y0=0.22, y1=1.0,
            fillcolor=CRASH_COLOR,
            line_width=0,
            layer="below",
        ))
    fig.update_layout(shapes=shapes)

    # ── Layout ─────────────────────────────────────────────────
    fig.update_layout(
        height=540,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0, font=dict(size=12),
        ),
        hovermode="x unified",
    )
    fig.update_yaxes(
        tickprefix="₹", tickformat=",.0f",
        gridcolor="#f3f4f6", row=1, col=1,
    )
    fig.update_yaxes(
        tickvals=[0, 1], ticktext=["Idle", "Active"],
        gridcolor="#f3f4f6", row=2, col=1,
    )
    fig.update_xaxes(
        type="date",
        gridcolor="#f3f4f6",
        tickformat="%b '%y",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Crash period labels below chart
    crash_label_parts = [f"<strong>{n}</strong>: {s[:4]}–{e[:4]}" for n, s, e in CRASH_PERIODS]
    st.markdown(
        '<span style="font-size:0.75rem;color:#9ca3af">'
        "Shaded crash periods: " + " · ".join(crash_label_parts) +
        "</span>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PANEL D — CRASH TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">How the Overlay Performed in Each Market Crash</div>',
            unsafe_allow_html=True)
st.markdown(
    '<span style="font-size:0.78rem;color:#6b7280">'
    "Numbers show the worst portfolio drop during each crash period. "
    "A smaller number = a shallower loss = better crash protection."
    "</span>",
    unsafe_allow_html=True,
)

crash_rows_display = []
for _, row in crash_main.iterrows():
    if pd.isna(row["bnh_max_dd"]):
        crash_rows_display.append({
            "Crash period":           row["period_name"],
            "Worst drop — holding":   "Fund didn't exist yet",
            "Worst drop — with overlay": "—",
            "Did overlay help?":      "—",
        })
    else:
        bnh_pct = abs(row["bnh_max_dd"]) * 100
        v2a_pct = abs(row["v2a_max_dd"]) * 100
        beats   = bool(row["v2a_beats_bnh"])
        saved   = abs(row["drawdown_saved"]) * 100
        crash_rows_display.append({
            "Crash period":              row["period_name"],
            "Worst drop — holding":      f"-{bnh_pct:.1f}%",
            "Worst drop — with overlay": f"-{v2a_pct:.1f}%",
            "Did overlay help?": (
                f"✅  Yes — loss was {saved:.1f}pp shallower"
                if beats else
                f"❌  No — loss was {saved:.1f}pp deeper"
            ),
        })

st.dataframe(
    pd.DataFrame(crash_rows_display),
    use_container_width=True, hide_index=True,
    column_config={
        "Crash period":              st.column_config.TextColumn(width=180),
        "Worst drop — holding":      st.column_config.TextColumn(width=175),
        "Worst drop — with overlay": st.column_config.TextColumn(width=190),
        "Did overlay help?":         st.column_config.TextColumn(width=250),
    },
)
st.markdown(
    '<span style="font-size:0.75rem;color:#9ca3af">'
    '"pp" = percentage points of difference. '
    '"Fund didn\'t exist yet" = this fund launched after the crash period ended.'
    "</span>",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# PANEL E — VALIDATION (plain English)
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🔍  How reliable are these results? — click to expand", expanded=False):
    val_score_int = int(fund_row.get("validation_score", 0)) if pd.notna(fund_row.get("validation_score")) else 0
    oos_elig = bool(fund_row.get("oos_eligible", True))
    max_tests = 4 if oos_elig else 3

    st.markdown(
        "Before trusting any research result, we need to check whether it's real or "
        "just a coincidence of the specific data used. We ran four independent checks. "
        "Each one tests the strategy in a different way."
    )
    st.markdown("---")

    # Walk-forward
    wf_pass      = bool(fund_row.get("wf_pass", False))
    wf_total     = fund_row.get("wf_windows_total", None)
    wf_pass_n    = fund_row.get("wf_windows_pass", None)
    wf_rate      = fund_row.get("wf_pass_rate", None)
    wf_valid     = pd.notna(wf_rate)

    st.markdown(f"**{'✅' if wf_pass else '❌'}  Check 1 — Does the strategy work consistently over time?**")
    st.markdown(
        "We split the 16-year history into 9 rolling windows and checked: in each window, "
        "did the overlay do better than simply holding the fund?"
    )
    if wf_valid:
        wf_n = int(wf_pass_n or 0)
        wf_t = int(wf_total or 0)
        wf_r = (wf_rate or 0) * 100
        if wf_pass:
            st.markdown(
                f"**Result:** ✅ The overlay beat simple holding in **{wf_n} out of {wf_t} windows** "
                f"({wf_r:.0f}%). The strategy performed consistently across different time periods."
            )
        else:
            st.markdown(
                f"**Result:** ❌ The overlay beat simple holding in only **{wf_n} out of {wf_t} windows** "
                f"({wf_r:.0f}%). The overlay helped in some periods but not consistently enough. "
                f"This means the result may depend heavily on *when* you invested."
            )
    else:
        st.markdown("**Result:** ❌ This fund doesn't have enough history for this test.")

    st.markdown("---")

    # OOS
    oos_pass = bool(fund_row.get("oos_pass", False))
    st.markdown(f"**{'✅' if (oos_pass and oos_elig) else ('—' if not oos_elig else '❌')}  Check 2 — Would it have worked on data it had never seen before?**")
    st.markdown(
        "We trained the strategy only on 2010–2022 data, then tested it on 2023–2026 — "
        "years the strategy had never 'seen'. This is the toughest test."
    )
    if not oos_elig:
        st.markdown("**Result:** — This fund doesn't have enough history for this test (needs 5+ years of training data).")
    elif oos_pass:
        st.markdown(
            "**Result:** ✅ Even on completely new data (2023–2026), the overlay still outperformed "
            "simple holding. This is strong evidence the edge is real."
        )
    else:
        st.markdown(
            "**Result:** ❌ When tested on 2023–2026 data (which the strategy never trained on), "
            "the overlay did not outperform simple holding. The strategy may have been tuned to "
            "past market patterns that didn't repeat."
        )

    st.markdown("---")

    # Monte Carlo
    mc_pass = bool(fund_row.get("mc_pass", False))
    mc_pct  = fund_row.get("real_percentile", None)
    mc_str  = f"{mc_pct:.1f}th" if pd.notna(mc_pct) else "—"
    st.markdown(f"**{'✅' if mc_pass else '❌'}  Check 3 — Could this result be explained by pure luck?**")
    st.markdown(
        "We ran 1,000 simulations with the fund's daily returns randomly shuffled. "
        "If the overlay still produces similar results on random data, the edge is just luck. "
        "If the real result is much better than the random versions, the strategy is exploiting "
        "something real in how this fund moves."
    )
    if mc_pass:
        st.markdown(
            f"**Result:** ✅ The real result ranked in the **{mc_str} percentile** out of 1,000 random "
            f"simulations. In other words, only about {100 - (mc_pct or 95):.0f}% of random scenarios "
            f"did as well. The overlay's edge is very unlikely to be pure luck."
        )
    else:
        st.markdown(
            f"**Result:** ❌ The real result ranked in the **{mc_str} percentile** — meaning random "
            f"scenarios often matched or beat it. The overlay's edge on this fund may be partly luck."
        )

    st.markdown("---")

    # Stability
    stab_pass = bool(fund_row.get("stability_pass", False))
    stab_rate = fund_row.get("stability_pass_rate", None)
    cliff     = bool(fund_row.get("cliff_detected", False))
    stab_str  = f"{stab_rate*100:.0f}%" if pd.notna(stab_rate) else "—"
    st.markdown(f"**{'✅' if stab_pass else '❌'}  Check 4 — Does changing the settings slightly break everything?**")
    st.markdown(
        "A good strategy should be robust — if you nudge its threshold settings up or down "
        "slightly, the results shouldn't collapse. We tested this across 20 variations."
    )
    cliff_note = (
        " ⚠️ We also detected a 'cliff' — one specific threshold where a small change "
        "causes a large drop in results. This means the strategy is sensitive near that point."
        if cliff else ""
    )
    if stab_pass:
        st.markdown(
            f"**Result:** ✅ Results held up in **{stab_str}** of the 20 variations tested. "
            f"The strategy is robust — small adjustments don't change the outcome much.{cliff_note}"
        )
    else:
        st.markdown(
            f"**Result:** ❌ Results only held up in **{stab_str}** of the 20 variations tested. "
            f"The strategy is somewhat brittle — small changes to settings noticeably affect the outcome.{cliff_note}"
        )

    st.markdown("---")

    # Summary
    if val_score_int >= max_tests:
        overall_msg = (
            f"✅ **Passed all {max_tests} checks.** The overlay's results for this fund are well-supported. "
            f"The edge is consistent over time, works on unseen data, is unlikely to be luck, and is robust to "
            f"small changes. You can interpret these results with relatively high confidence."
        )
    elif val_score_int >= 2:
        passed_desc = f"{val_score_int} out of {max_tests}"
        overall_msg = (
            f"⚠️ **Passed {passed_desc} checks.** The overlay provides genuine value for this fund in "
            f"some areas — but not across the board. The results are most reliable as evidence of "
            f"**crash protection** (how the overlay limited losses in downturns). "
            f"Treat the return-improvement numbers with more caution."
        )
    else:
        overall_msg = (
            f"❌ **Passed only {val_score_int} of {max_tests} checks.** The overlay's results for this "
            f"fund are not well-supported by the reliability tests. The crash protection data may still "
            f"be useful, but the overall edge is not statistically robust."
        )
    st.info(overall_msg)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#9ca3af;font-size:0.75rem">'
    "NivesAI · LARF Research Engine v2a · Data: AMFI NAV history · "
    "173 Indian mutual funds · Jan 2010–May 2026 · "
    "Past performance is not indicative of future results · Not investment advice"
    "</div>",
    unsafe_allow_html=True,
)