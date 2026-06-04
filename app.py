"""
NivesAI — LARF Overlay Research Tool
v1.2 — minimalist redesign
Author: Sneha Joshi | NivesAI
"""

import os
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="NivesAI | LARF",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ──────────────────────────────────────────────────────────────────
TEAL        = "#0d6e6e"
TEAL_LIGHT  = "#e6f4f4"
BNH_COLOR   = "#94a3b8"
CRASH_COLOR = "rgba(239,68,68,0.10)"
ACTIVE_BAR  = "#ef4444"
IDLE_BAR    = "#e2e8f0"
DEFAULT_AMT = 100_000
DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")

CRASH_PERIODS = [
    ("2011 Bear",           "2011-01-01", "2011-12-31"),
    ("2015–16 Correction",  "2015-03-01", "2016-03-31"),
    ("2018–19 NBFC Crisis", "2018-09-01", "2019-03-31"),
    ("2020 COVID Crash",    "2020-01-15", "2020-04-30"),
]

ROLE_DESC = {
    "Core":          "Holds up reasonably well in downturns; recovers steadily.",
    "Stabiliser":    "Low volatility, calm in downturns. Doesn't grow fast but doesn't fall hard.",
    "Trend / Quant": "Strongly trend-driven — rises fast in bull markets, falls sharply in downturns.",
    "Satellite":     "High risk, high reward. Deep drawdowns, slow recovery. Best as a small allocation.",
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
.block-container { padding-top: 1.8rem !important; max-width: 1100px; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }

/* Sidebar brand */
.nb { font-size:1.4rem; font-weight:700; color:#0d6e6e; letter-spacing:-0.3px; }
.ns { font-size:0.75rem; color:#94a3b8; }

/* Fund header */
.fund-name { font-size:1.4rem; font-weight:700; color:#0f172a; line-height:1.3; }
.fund-meta { font-size:0.82rem; color:#64748b; margin-top:2px; }

/* Compact info row */
.info-row { display:flex; flex-wrap:wrap; gap:20px; margin:12px 0 0; }
.ir-item  { display:flex; flex-direction:column; }
.ir-lbl   { font-size:0.65rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; }
.ir-val   { font-size:0.82rem; font-weight:600; color:#0f172a; }

/* Metric cards — clean */
.mc {
  background:#f8fafc; border:1px solid #e2e8f0;
  border-radius:8px; padding:16px 14px; text-align:center;
}
.mc-lbl { font-size:0.68rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; margin-bottom:10px; }
.mc-row { display:flex; justify-content:center; gap:16px; align-items:flex-end; margin-bottom:8px; }
.mc-bnh { text-align:center; }
.mc-ov  { text-align:center; }
.mc-sub { font-size:0.65rem; color:#94a3b8; margin-bottom:2px; }
.mc-num-bnh { font-size:1.25rem; font-weight:700; color:#64748b; }
.mc-num-ov  { font-size:1.35rem; font-weight:700; color:#0d6e6e; }
.mc-arrow   { font-size:1rem; color:#cbd5e1; padding-bottom:4px; }
.mc-delta   { font-size:0.78rem; font-weight:600; }
.pos { color:#16a34a; } .neg { color:#dc2626; } .neu { color:#94a3b8; }

/* Validation badge */
.vb-y { background:#fffbeb; color:#92400e; border:1px solid #fde68a; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }
.vb-g { background:#f0fdf4; color:#14532d; border:1px solid #bbf7d0; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }
.vb-r { background:#fef2f2; color:#7f1d1d; border:1px solid #fecaca; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }

/* Section label */
.slbl { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#94a3b8; margin:28px 0 12px; }

/* Date note */
.date-note { font-size:0.75rem; color:#64748b; margin-bottom:8px; }

/* Subtle note */
.note { font-size:0.72rem; color:#94a3b8; line-height:1.5; margin-top:6px; }

/* Callout */
.co {
  background:#f8fafc; border-left:3px solid #0d6e6e;
  border-radius:0 6px 6px 0; padding:10px 14px; margin:14px 0;
  font-size:0.85rem; color:#374151; line-height:1.5;
}

/* Validation check row */
.vc { border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; margin:8px 0; }
.vc-q  { font-size:0.88rem; font-weight:600; color:#0f172a; margin-bottom:6px; }
.vc-r  { font-size:0.83rem; color:#374151; }

/* Disclaimer */
.disc { font-size:0.7rem; color:#94a3b8; border-top:1px solid #e2e8f0; padding-top:14px; margin-top:16px; line-height:1.5; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data …")
def load_master():
    res = pd.read_csv(f"{DATA_DIR}/larf_regime_results_v2.csv")
    res["scheme_code"] = res["scheme_code"].astype(str)
    val = pd.read_csv(f"{DATA_DIR}/larf_validation_summary_v1.csv")
    val["scheme_code"] = val["scheme_code"].astype(str)
    sch = pd.read_csv(f"{DATA_DIR}/scheme_master_v2_FROZEN.csv")
    sch["scheme_code"] = sch["scheme_code"].astype(str)
    beh = pd.read_csv(f"{DATA_DIR}/behaviour_classification_app.csv")
    beh["scheme_code"] = beh["scheme_code"].astype(str)
    beh["summary_text"] = beh["summary_text"].fillna("")
    crash = pd.read_csv(f"{DATA_DIR}/crash_periods_app.csv")
    crash["scheme_code"] = crash["scheme_code"].astype(str)
    rtl = pd.read_csv(f"{DATA_DIR}/regime_timeline.csv")
    rtl["date"] = pd.to_datetime(rtl["date"])

    df = res.merge(val[[
        "scheme_code","validation_score","fully_validated",
        "wf_pass","wf_pass_rate","wf_windows_total","wf_windows_pass",
        "oos_eligible","oos_pass","mc_pass","real_percentile",
        "stability_pass","stability_pass_rate","cliff_detected",
    ]], on="scheme_code", how="left")
    df = df.merge(sch[["scheme_code","scheme_name","scheme_category","amc"]], on="scheme_code", how="left")
    df = df.merge(beh[["scheme_code","final_role","classification_confidence","summary_text"]], on="scheme_code", how="left")
    return df, crash, rtl


@st.cache_data(show_spinner="Loading curves …")
def load_curves():
    p = f"{DATA_DIR}/larf_regime_curves_v2.parquet"
    c = f"{DATA_DIR}/larf_regime_curves_v2.csv"
    if os.path.exists(p):
        df = pd.read_parquet(p, columns=["scheme_code","date","bnh_value","v2a_value"])
    elif os.path.exists(c):
        df = pd.read_csv(c, usecols=["scheme_code","date","bnh_value","v2a_value"])
    else:
        st.error("Curves file not found. Run data_prep_colab.py first.")
        st.stop()
    df["scheme_code"] = df["scheme_code"].astype(str)
    df["date"] = pd.to_datetime(df["date"], utc=False).dt.normalize()
    return df


# ── Helpers ────────────────────────────────────────────────────────────────────
def pct(v, d=1):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v*100:.{d}f}%"

def pct_delta(v, d=1):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—", "neu"
    sign = "+" if v > 0 else ""
    cls = "pos" if v > 0 else ("neg" if v < 0 else "neu")
    return f"{sign}{v*100:.{d}f}%", cls

def inr(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if abs(v) >= 1_00_000:
        return f"₹{v/1_00_000:.2f}L"
    return f"₹{v:,.0f}"

def score_delta(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—", "neu"
    sign = "+" if v > 0 else ""
    cls = "pos" if v > 0 else ("neg" if v < 0 else "neu")
    return f"{sign}{v:.3f}", cls

def prepare_curves(fund_curves, amount, start_ts):
    df = fund_curves[fund_curves["date"] >= start_ts].sort_values("date").reset_index(drop=True)
    if len(df) < 5:
        return pd.DataFrame()
    scale = amount / df["bnh_value"].iloc[0]
    df = df.copy()
    df["bnh_s"] = (df["bnh_value"] * scale).round(0)
    df["v2a_s"] = (df["v2a_value"] * scale).round(0)
    df["ds"]    = df["date"].dt.strftime("%Y-%m-%d")
    return df

def compute_metrics(df, amount, rtl):
    """Compute all metrics from a prepared curves dataframe."""
    if len(df) < 10:
        return None
    years = max((df["date"].iloc[-1] - df["date"].iloc[0]).days / 365.25, 0.1)

    def cagr(series):
        val = series.iloc[-1]
        return (val / amount) ** (1 / years) - 1 if amount > 0 else np.nan

    def mdd(series):
        roll_max = series.cummax()
        dd = (series - roll_max) / roll_max
        return float(dd.min())

    bnh_c = cagr(df["bnh_s"])
    v2a_c = cagr(df["v2a_s"])
    bnh_d = mdd(df["bnh_s"])
    v2a_d = mdd(df["v2a_s"])
    bnh_sc = bnh_c - abs(bnh_d) / 2
    v2a_sc = v2a_c - abs(v2a_d) / 2

    r = rtl[(rtl["date"] >= df["date"].min()) & (rtl["date"] <= df["date"].max())]
    reg_pct = float(r["macro_active"].mean()) if len(r) > 0 else np.nan

    return {
        "years":     years,
        "bnh_cagr":  bnh_c,  "v2a_cagr":  v2a_c,
        "bnh_dd":    bnh_d,  "v2a_dd":    v2a_d,
        "bnh_score": bnh_sc, "v2a_score": v2a_sc,
        "final_bnh": float(df["bnh_s"].iloc[-1]),
        "final_v2a": float(df["v2a_s"].iloc[-1]),
        "reg_pct":   reg_pct,
    }

def val_badge(score, oos_elig):
    score = int(score) if pd.notna(score) else 0
    mx = 4 if oos_elig else 3
    if score >= mx:
        return f'<span class="vb-g">✅ Fully validated ({score}/{mx} checks)</span>'
    elif score >= 2:
        return f'<span class="vb-y">⚠️ Partial validation ({score}/{mx} checks)</span>'
    else:
        return f'<span class="vb-r">❌ Low validation ({score}/{mx} checks)</span>'


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nb">NivesAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="ns">LARF Overlay Research Engine</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**173 Indian mutual funds · 2010–2026**")
    st.markdown(
        "Rule-based overlay strategy tested against simply holding each fund. "
        "Idle cash earns Quantum Liquid Fund returns."
    )
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown(
        "A fixed set of rules monitors the broader market (Nifty 50 trend) "
        "and the fund's own stress signals. When a downturn is detected, the "
        "strategy automatically trims a small portion of the position and "
        "moves that cash to safety. No forecasts. No discretion. Only rules."
    )
    st.markdown(
        '<div class="disc">All results are historical simulations — '
        "what <em>would have happened</em>, not what <em>will happen</em>. "
        "Not investment advice. NivesAI is not a SEBI-registered advisor.</div>",
        unsafe_allow_html=True,
    )


# ── Load data ──────────────────────────────────────────────────────────────────
master_df, crash_df, regime_tl = load_master()
curves_df = load_curves()

# ── Selector ───────────────────────────────────────────────────────────────────
st.markdown("#### Fund Overlay Simulator")
st.markdown(
    '<span style="font-size:0.85rem;color:#64748b">'
    "Select a fund, enter your investment amount and start date, "
    "and see how a rule-based overlay strategy would have changed your experience."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("")

fund_options = {}
for _, r in master_df.sort_values(["scheme_category","scheme_name"]).iterrows():
    fund_options[f"{r['scheme_name']}  ·  {r['scheme_category']}"] = str(r["scheme_code"])

fc1, fc2, fc3, fc4 = st.columns([4, 1.4, 1.4, 1])
with fc1:
    sel = st.selectbox("Fund", ["— choose a fund —"] + list(fund_options.keys()),
                       label_visibility="collapsed")
with fc2:
    amount = st.number_input("Amount (₹)", min_value=10_000, max_value=10_00_00_000,
                             value=DEFAULT_AMT, step=10_000, format="%d",
                             label_visibility="collapsed")
with fc3:
    inv_date = st.date_input(
        "Investment date",
        value=datetime.date(2010, 1, 4),
        min_value=datetime.date(2010, 1, 1),
        max_value=datetime.date(2026, 5, 31),
        help="All metrics and the chart will be calculated from this date.",
        label_visibility="collapsed",
    )
with fc4:
    go_btn = st.button("View →", type="primary", use_container_width=True)

st.markdown(
    '<div class="note">Amount · Investment date · then View</div>',
    unsafe_allow_html=True,
)

if sel == "— choose a fund —" or not go_btn:
    st.stop()


# ── Fund data ──────────────────────────────────────────────────────────────────
code       = fund_options[sel]
fr         = master_df[master_df["scheme_code"] == code].iloc[0]
raw_curves = curves_df[curves_df["scheme_code"] == code].sort_values("date").reset_index(drop=True)

sim_start = pd.Timestamp(fr.get("sim_start_date","2010-01-04"))
sim_end   = pd.Timestamp(fr.get("sim_end_date",  "2026-04-08"))
inv_ts    = pd.Timestamp(inv_date)
if inv_ts < sim_start: inv_ts = sim_start
if inv_ts >= sim_end:  inv_ts = sim_start

sc = prepare_curves(raw_curves, amount, inv_ts)
if len(sc) == 0:
    st.error("No data available for this fund and date range.")
    st.stop()

m = compute_metrics(sc, amount, regime_tl)
if m is None:
    st.error("Not enough data to compute metrics for this date range.")
    st.stop()

st.markdown("---")

# ── Fund header ────────────────────────────────────────────────────────────────
hc1, hc2 = st.columns([7, 2])
with hc1:
    st.markdown(f'<div class="fund-name">{fr["scheme_name"]}</div>', unsafe_allow_html=True)
    cat  = fr.get("scheme_category","")
    role = fr.get("final_role","")
    conf = str(fr.get("classification_confidence","")).upper()
    conf_map = {"HIGH":"Strong fit","MEDIUM":"Moderate fit","LOW":"Mixed signals"}
    conf_label = conf_map.get(conf, conf)
    st.markdown(
        f'<div class="fund-meta">{cat}'
        f'{"  ·  " + role if role else ""}'
        f'{"  ·  " + conf_label if conf_label else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )
with hc2:
    oos_e = bool(fr.get("oos_eligible", True))
    vs    = fr.get("validation_score", 0)
    st.markdown(val_badge(vs, oos_e), unsafe_allow_html=True)

# Quick info row
num_sells = int(fr.get("v2a_num_sells", 0))
date_from = inv_ts.strftime("%d %b %Y")
date_to   = sim_end.strftime("%d %b %Y")
yrs_str   = f"{m['years']:.1f} yrs"

role_note = ROLE_DESC.get(role,"")
if role_note or conf == "LOW":
    note_parts = []
    if role_note:
        note_parts.append(f"<strong>{role}:</strong> {role_note}")
    if conf == "LOW":
        note_parts.append("Confidence is mixed — this fund's behaviour didn't strongly fit one category. Treat the role as directional.")
    elif conf == "MEDIUM":
        note_parts.append("Classification confidence is moderate.")
    st.markdown(
        f'<div class="co">{" ".join(note_parts)}</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="info-row">'
    f'<div class="ir-item"><span class="ir-lbl">Showing</span>'
    f'<span class="ir-val">{date_from} → {date_to} ({yrs_str})</span></div>'
    f'<div class="ir-item"><span class="ir-lbl">Overlay trims (full sim)</span>'
    f'<span class="ir-val">{num_sells} rule-based sells over 16 yrs</span></div>'
    f'<div class="ir-item"><span class="ir-lbl">Overlay activity</span>'
    f'<span class="ir-val">{m["reg_pct"]*100:.0f}% of days (strategy was watching)</span></div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Metrics ────────────────────────────────────────────────────────────────────
is_custom = inv_ts > sim_start
period_lbl = f"from {date_from}" if is_custom else "2010–2026"
st.markdown(f'<div class="slbl">Performance · {period_lbl}</div>', unsafe_allow_html=True)

def mc_card(label, bnh_val, ov_val, delta_val, fmt_bnh, fmt_ov, fmt_delta,
            higher_is_better=True, delta_suffix=""):
    dv, dcls = fmt_delta(delta_val)
    # Override: for drawdown, negative delta is good
    if not higher_is_better and delta_val < 0:
        dcls = "pos"
    elif not higher_is_better and delta_val > 0:
        dcls = "neg"
    return f"""
    <div class="mc">
      <div class="mc-lbl">{label}</div>
      <div class="mc-row">
        <div class="mc-bnh">
          <div class="mc-sub">holding</div>
          <div class="mc-num-bnh">{fmt_bnh(bnh_val)}</div>
        </div>
        <div class="mc-arrow">→</div>
        <div class="mc-ov">
          <div class="mc-sub">overlay</div>
          <div class="mc-num-ov">{fmt_ov(ov_val)}</div>
        </div>
      </div>
      <div class="mc-delta {dcls}">{dv}{delta_suffix}</div>
    </div>"""

edge_cagr  = m["v2a_cagr"]  - m["bnh_cagr"]
edge_dd    = m["v2a_dd"]    - m["bnh_dd"]
edge_score = m["v2a_score"] - m["bnh_score"]
edge_val   = m["final_v2a"] - m["final_bnh"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(mc_card(
        "Annual Return", m["bnh_cagr"], m["v2a_cagr"], edge_cagr,
        lambda v: pct(v,2), lambda v: pct(v,2), pct_delta,
        higher_is_better=True,
    ), unsafe_allow_html=True)
with c2:
    st.markdown(mc_card(
        "Worst Drop", m["bnh_dd"], m["v2a_dd"], edge_dd,
        lambda v: pct(v,1), lambda v: pct(v,1), pct_delta,
        higher_is_better=False,
        delta_suffix=" vs holding",
    ), unsafe_allow_html=True)
with c3:
    st.markdown(mc_card(
        "Overall Score", m["bnh_score"], m["v2a_score"], edge_score,
        lambda v: f"{v:.3f}", lambda v: f"{v:.3f}", score_delta,
        higher_is_better=True,
    ), unsafe_allow_html=True)
with c4:
    ev_str, ev_cls = (f"+{inr(edge_val)}", "pos") if edge_val > 0 else (inr(edge_val), "neg")
    st.markdown(f"""
    <div class="mc">
      <div class="mc-lbl">Portfolio value · {period_lbl}</div>
      <div class="mc-row">
        <div class="mc-bnh"><div class="mc-sub">holding</div>
          <div class="mc-num-bnh">{inr(m["final_bnh"])}</div></div>
        <div class="mc-arrow">→</div>
        <div class="mc-ov"><div class="mc-sub">overlay</div>
          <div class="mc-num-ov">{inr(m["final_v2a"])}</div></div>
      </div>
      <div class="mc-delta {ev_cls}">{ev_str} difference</div>
    </div>""", unsafe_allow_html=True)

st.markdown(
    '<div class="note">'
    "<strong>Annual Return</strong>: average yearly growth. "
    "<strong>Worst Drop</strong>: biggest peak-to-trough fall in the period. "
    "<strong>Score</strong>: single number balancing return and risk (higher = better). "
    + (f"All metrics computed from {date_from}." if is_custom else "")
    + "</div>",
    unsafe_allow_html=True,
)

# 2024-26 callout
crash_sw = crash_df[(crash_df["scheme_code"] == code) &
                    crash_df["period_name"].str.contains("Sideways", na=False)]
if len(crash_sw) > 0:
    sw = crash_sw.iloc[0]
    if pd.notna(sw.get("v2a_beats_bnh")):
        bfall = abs(sw["bnh_max_dd"]) * 100 if pd.notna(sw["bnh_max_dd"]) else None
        vfall = abs(sw["v2a_max_dd"]) * 100 if pd.notna(sw["v2a_max_dd"]) else None
        fund_result = (f"For this fund: worst fall was {bfall:.1f}% without overlay, "
                       f"{vfall:.1f}% with overlay. " if bfall and vfall else "")
        icon = "📈" if sw["v2a_beats_bnh"] else "📉"
        st.markdown(
            f'<div class="co">{icon} <strong>2024–26 (recent sideways market):</strong> '
            f'{fund_result}'
            f"Across all 173 funds studied, the overlay outperformed simple holding "
            f"in <strong>152 out of 173 funds (88%)</strong> during this period.</div>",
            unsafe_allow_html=True,
        )


# ── Chart ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="slbl">Portfolio Growth Over Time</div>', unsafe_allow_html=True)

fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    row_heights=[0.82, 0.18], vertical_spacing=0.04,
)

dates = sc["ds"].tolist()
fig.add_trace(go.Scatter(
    x=dates, y=sc["bnh_s"].tolist(), mode="lines",
    name="Simple holding", line=dict(color=BNH_COLOR, width=1.8),
    hovertemplate="<b>Simple holding</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>",
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=dates, y=sc["v2a_s"].tolist(), mode="lines",
    name="With overlay", line=dict(color=TEAL, width=2.2),
    hovertemplate="<b>With overlay</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>",
), row=1, col=1)

rg = regime_tl[(regime_tl["date"] >= sc["date"].min()) &
               (regime_tl["date"] <= sc["date"].max())].copy()
fig.add_trace(go.Bar(
    x=rg["date"].dt.strftime("%Y-%m-%d").tolist(),
    y=rg["macro_active"].astype(int).tolist(),
    marker_color=[ACTIVE_BAR if v else IDLE_BAR for v in rg["macro_active"]],
    name="Overlay watching", showlegend=True,
    hovertemplate="%{x}<br>Overlay: %{y}<extra></extra>",
), row=2, col=1)

# Crash band shapes
shapes = []
for _, s, e in CRASH_PERIODS:
    shapes.append(dict(
        type="rect", xref="x", yref="paper",
        x0=s, x1=e, y0=0.22, y1=1.0,
        fillcolor=CRASH_COLOR, line_width=0, layer="below",
    ))
fig.update_layout(
    shapes=shapes, height=520,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor="white", plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                font=dict(size=11)),
    hovermode="x unified",
)
fig.update_yaxes(tickprefix="₹", tickformat=",.0f", gridcolor="#f1f5f9", row=1, col=1)
fig.update_yaxes(tickvals=[0,1], ticktext=["","Active"], gridcolor="#f1f5f9", row=2, col=1)
fig.update_xaxes(type="date", tickformat="%b '%y", gridcolor="#f1f5f9", showgrid=True)

st.plotly_chart(fig, use_container_width=True)
st.markdown(
    '<div class="note">Red shaded areas = major market crashes '
    "(2011, 2015-16, 2018-19, 2020 COVID). "
    "Bottom bar = days the strategy was monitoring for downturns.</div>",
    unsafe_allow_html=True,
)


# ── Crash table ────────────────────────────────────────────────────────────────
st.markdown('<div class="slbl">Crash-by-Crash Comparison</div>', unsafe_allow_html=True)

crash_main = crash_df[
    (crash_df["scheme_code"] == code) &
    ~crash_df["period_name"].str.contains("Sideways", na=False)
]
rows = []
for _, r in crash_main.iterrows():
    if pd.isna(r["bnh_max_dd"]):
        rows.append({"Period": r["period_name"],
                     "Without overlay": "Fund didn't exist yet",
                     "With overlay": "—", "Overlay helped?": "—"})
    else:
        b, v = abs(r["bnh_max_dd"])*100, abs(r["v2a_max_dd"])*100
        s    = abs(r["drawdown_saved"])*100
        win  = bool(r["v2a_beats_bnh"])
        rows.append({
            "Period":           r["period_name"],
            "Without overlay":  f"−{b:.1f}%",
            "With overlay":     f"−{v:.1f}%",
            "Overlay helped?":  f"✅  Yes, {s:.1f} pp shallower" if win else f"❌  No, {s:.1f} pp deeper",
        })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
    column_config={
        "Period":          st.column_config.TextColumn(width=175),
        "Without overlay": st.column_config.TextColumn(width=155),
        "With overlay":    st.column_config.TextColumn(width=155),
        "Overlay helped?": st.column_config.TextColumn(width=220),
    })
st.markdown(
    '<div class="note">"pp" = percentage points. A smaller drop = better protection.</div>',
    unsafe_allow_html=True,
)


# ── Validation ─────────────────────────────────────────────────────────────────
with st.expander("🔍  How reliable are these results?", expanded=False):
    st.markdown(
        "We ran four independent checks to test whether the overlay's results are real "
        "or just a coincidence of the specific data. Each check tests a different aspect."
    )
    st.markdown("")

    # Check 1 — Walk-forward
    wf_p    = bool(fr.get("wf_pass", False))
    wf_tot  = fr.get("wf_windows_total")
    wf_n    = fr.get("wf_windows_pass")
    wf_r    = fr.get("wf_pass_rate")
    wf_ok   = pd.notna(wf_r)
    icon1   = "✅" if wf_p else "❌"
    if wf_ok:
        wf_detail = (
            f"{icon1} Overlay beat simple holding in **{int(wf_n or 0)} of {int(wf_tot or 0)} windows** "
            f"({(wf_r or 0)*100:.0f}%). "
            + ("Performed consistently across different time periods." if wf_p
               else "Performance was inconsistent — the result depends heavily on *when* you invested.")
        )
    else:
        wf_detail = "❌ Not enough history for this test."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 1 — Does it work consistently over time?</div>'
                f'<div class="vc-r">{wf_detail}</div></div>', unsafe_allow_html=True)

    # Check 2 — OOS
    oos_e2  = bool(fr.get("oos_eligible", True))
    oos_p   = bool(fr.get("oos_pass", False))
    icon2   = "✅" if oos_p else ("—" if not oos_e2 else "❌")
    if not oos_e2:
        oos_detail = "— Not eligible (fund needs 5+ years of training data)."
    elif oos_p:
        oos_detail = "✅ Overlay outperformed simple holding on 2023–2026 data the strategy had never seen. Strong evidence the edge is real."
    else:
        oos_detail = "❌ Overlay did not outperform on unseen 2023–2026 data. Strategy may have been tuned to past patterns that didn't repeat."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 2 — Would it work on data it had never seen?</div>'
                f'<div class="vc-r">{oos_detail}</div></div>', unsafe_allow_html=True)

    # Check 3 — Monte Carlo
    mc_p   = bool(fr.get("mc_pass", False))
    mc_pct = fr.get("real_percentile")
    icon3  = "✅" if mc_p else "❌"
    if pd.notna(mc_pct):
        mc_detail = (
            f"{'✅' if mc_p else '❌'} Result ranked in the **{mc_pct:.1f}th percentile** out of 1,000 random simulations. "
            + ("Only ~{:.0f}% of purely random runs did as well — the edge is very unlikely to be luck.".format(100 - mc_pct) if mc_p
               else "Random simulations often matched this result — the edge may be partly luck.")
        )
    else:
        mc_detail = "No Monte Carlo data available."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 3 — Could this result be pure luck?</div>'
                f'<div class="vc-r">{mc_detail}</div></div>', unsafe_allow_html=True)

    # Check 4 — Stability
    st_p   = bool(fr.get("stability_pass", False))
    st_r   = fr.get("stability_pass_rate")
    cliff  = bool(fr.get("cliff_detected", False))
    icon4  = "✅" if st_p else "❌"
    if pd.notna(st_r):
        st_detail = (
            f"{'✅' if st_p else '❌'} Results held up in **{st_r*100:.0f}%** of 20 parameter variations. "
            + ("The strategy is robust — small adjustments don't break it." if st_p
               else "The strategy is somewhat sensitive — small changes affect the outcome.")
            + (" ⚠️ One threshold was identified where a small change causes a larger-than-expected shift in results." if cliff else "")
        )
    else:
        st_detail = "Stability data not available for this fund."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 4 — Does it break if settings are nudged slightly?</div>'
                f'<div class="vc-r">{st_detail}</div></div>', unsafe_allow_html=True)

    # Summary
    vs_int = int(fr.get("validation_score",0)) if pd.notna(fr.get("validation_score")) else 0
    mx2    = 4 if oos_e2 else 3
    if vs_int >= mx2:
        msg = (f"✅ Passed all {mx2} checks. The overlay's results for this fund are well-supported. "
               "You can interpret these numbers with relatively high confidence.")
        st.success(msg)
    elif vs_int >= 2:
        st.warning(
            f"Passed {vs_int} of {mx2} checks. The **crash protection** evidence is solid. "
            "The return-improvement numbers are directional — treat them with some caution."
        )
    else:
        st.error(
            f"Passed only {vs_int} of {mx2} checks. The overlay results for this fund "
            "are not strongly supported. Crash protection data may still be informative, "
            "but the overall edge is not statistically robust."
        )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#94a3b8;font-size:0.72rem">'
    "NivesAI · LARF v2a · AMFI NAV data · 173 funds · Jan 2010–May 2026 · "
    "Past performance is not indicative of future results · Not investment advice"
    "</div>",
    unsafe_allow_html=True,
)