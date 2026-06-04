"""
NivesAI — LARF Overlay Research Tool
v1.3 — redesigned: hero header, collapsed sidebar, extended metrics
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
    initial_sidebar_state="collapsed",
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
[data-testid="stSidebar"] { display: none; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 1140px; }
section[data-testid="stSidebar"] > div { padding-top: 1rem; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 22px 0; }
a { color: #0d6e6e !important; }

/* ── Hero header ── */
.hero {
  background: linear-gradient(135deg, #0a4f4f 0%, #0f172a 100%);
  border-radius: 14px;
  padding: 32px 36px 28px;
  margin-bottom: 26px;
}
.hero-brand  { font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1; }
.hero-sub    { font-size: 1rem; color: #7dd3d3; margin-top: 6px; font-weight: 500; }
.hero-meta   { font-size: 0.78rem; color: rgba(255,255,255,0.45); margin-top: 10px; letter-spacing: 0.2px; }
.hero-tagline {
  margin-top: 18px; padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.12);
  font-size: 0.88rem; color: rgba(255,255,255,0.65); line-height: 1.55;
}

/* ── Fund header ── */
.fund-name { font-size: 1.35rem; font-weight: 700; color: #0f172a; line-height: 1.3; }
.fund-meta { font-size: 0.82rem; color: #64748b; margin-top: 3px; }

/* ── Info row ── */
.info-row { display:flex; flex-wrap:wrap; gap:22px; margin:12px 0 0; }
.ir-item  { display:flex; flex-direction:column; }
.ir-lbl   { font-size:0.63rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; }
.ir-val   { font-size:0.82rem; font-weight:600; color:#0f172a; }

/* ── Metric cards ── */
.mc {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 18px 14px 14px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(15,23,42,0.06);
  height: 100%;
}
.mc-lbl { font-size:0.66rem; text-transform:uppercase; letter-spacing:0.6px; color:#94a3b8; margin-bottom:12px; }
.mc-row { display:flex; justify-content:center; gap:14px; align-items:flex-end; margin-bottom:8px; }
.mc-bnh { text-align:center; }
.mc-ov  { text-align:center; }
.mc-sub { font-size:0.63rem; color:#94a3b8; margin-bottom:2px; }
.mc-num-bnh { font-size:1.2rem; font-weight:700; color:#64748b; }
.mc-num-ov  { font-size:1.3rem; font-weight:800; color:#0d6e6e; }
.mc-arrow   { font-size:0.9rem; color:#cbd5e1; padding-bottom:4px; }
.mc-delta   { font-size:0.78rem; font-weight:600; margin-top:2px; }
.pos { color:#16a34a; } .neg { color:#dc2626; } .neu { color:#94a3b8; }

/* ── Secondary stats row ── */
.sstat-row { display:flex; flex-wrap:wrap; gap:12px; margin:14px 0 0; }
.sstat {
  background:#f8fafc; border:1px solid #e2e8f0;
  border-radius:8px; padding:10px 16px;
  display:flex; flex-direction:column;
}
.sstat-lbl { font-size:0.63rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; margin-bottom:4px; }
.sstat-val { font-size:0.88rem; font-weight:600; color:#0f172a; }

/* ── Validation badge ── */
.vb-y { background:#fffbeb; color:#92400e; border:1px solid #fde68a; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }
.vb-g { background:#f0fdf4; color:#14532d; border:1px solid #bbf7d0; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }
.vb-r { background:#fef2f2; color:#7f1d1d; border:1px solid #fecaca; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }

/* ── Section label ── */
.slbl { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#94a3b8; margin:28px 0 12px; }

/* ── Callout ── */
.co {
  background:#f0fdfd; border-left:3px solid #0d6e6e;
  border-radius:0 8px 8px 0; padding:10px 14px; margin:12px 0;
  font-size:0.85rem; color:#374151; line-height:1.55;
}

/* ── Validation check row ── */
.vc { border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; margin:8px 0; background:#fff; }
.vc-q  { font-size:0.88rem; font-weight:600; color:#0f172a; margin-bottom:6px; }
.vc-r  { font-size:0.83rem; color:#374151; }

/* ── Note / disclaimer ── */
.note { font-size:0.72rem; color:#94a3b8; line-height:1.5; margin-top:6px; }
.disc { font-size:0.7rem; color:#94a3b8; line-height:1.5; }

/* ── Selector container ── */
.sel-wrap {
  background:#f8fafc; border:1px solid #e2e8f0;
  border-radius:10px; padding:16px 18px 14px;
  margin-bottom:6px;
}
.sel-title { font-size:0.72rem; font-weight:700; text-transform:uppercase;
             letter-spacing:0.7px; color:#64748b; margin-bottom:10px; }
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


@st.cache_data(show_spinner=False)
def load_nifty_returns():
    p = f"{DATA_DIR}/nifty_returns.csv"
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"])
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

def fmt_x(v, d=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v:.{d}f}x"

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

def compute_metrics(df, amount, rtl, nifty_ret_df=None):
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

    def ann_vol(series):
        daily_ret = series.pct_change().dropna()
        return float(daily_ret.std() * np.sqrt(252))

    def calmar(cagr_val, mdd_val):
        return cagr_val / abs(mdd_val) if mdd_val != 0 and not np.isnan(mdd_val) else np.nan

    bnh_c  = cagr(df["bnh_s"])
    v2a_c  = cagr(df["v2a_s"])
    bnh_d  = mdd(df["bnh_s"])
    v2a_d  = mdd(df["v2a_s"])
    bnh_sc = bnh_c - abs(bnh_d) / 2
    v2a_sc = v2a_c - abs(v2a_d) / 2
    bnh_v  = ann_vol(df["bnh_s"])
    v2a_v  = ann_vol(df["v2a_s"])
    bnh_ca = calmar(bnh_c, bnh_d)
    v2a_ca = calmar(v2a_c, v2a_d)

    r = rtl[(rtl["date"] >= df["date"].min()) & (rtl["date"] <= df["date"].max())]
    reg_pct = float(r["macro_active"].mean()) if len(r) > 0 else np.nan

    # Beta vs Nifty (optional — only if nifty_returns.csv exists)
    bnh_beta = np.nan
    v2a_beta = np.nan
    if nifty_ret_df is not None:
        try:
            nr = nifty_ret_df[
                (nifty_ret_df["date"] >= df["date"].min()) &
                (nifty_ret_df["date"] <= df["date"].max())
            ].copy()
            merged_bnh = pd.merge(df[["date","bnh_s"]], nr[["date","daily_return"]], on="date", how="inner")
            merged_v2a = pd.merge(df[["date","v2a_s"]], nr[["date","daily_return"]], on="date", how="inner")
            if len(merged_bnh) > 30:
                fund_ret_bnh = merged_bnh["bnh_s"].pct_change().dropna()
                fund_ret_v2a = merged_v2a["v2a_s"].pct_change().dropna()
                mkt_ret_bnh  = merged_bnh["daily_return"].iloc[1:].reset_index(drop=True)
                mkt_ret_v2a  = merged_v2a["daily_return"].iloc[1:].reset_index(drop=True)
                var_m = mkt_ret_bnh.var()
                if var_m > 0:
                    bnh_beta = float(np.cov(fund_ret_bnh, mkt_ret_bnh)[0,1] / var_m)
                    v2a_beta = float(np.cov(fund_ret_v2a, mkt_ret_v2a)[0,1] / var_m)
        except Exception:
            pass

    return {
        "years":     years,
        "bnh_cagr":  bnh_c,   "v2a_cagr":  v2a_c,
        "bnh_dd":    bnh_d,   "v2a_dd":    v2a_d,
        "bnh_score": bnh_sc,  "v2a_score": v2a_sc,
        "bnh_vol":   bnh_v,   "v2a_vol":   v2a_v,
        "bnh_calmar":bnh_ca,  "v2a_calmar":v2a_ca,
        "bnh_beta":  bnh_beta,"v2a_beta":  v2a_beta,
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
        return f'<span class="vb-y">⚠️ Partial ({score}/{mx} checks)</span>'
    else:
        return f'<span class="vb-r">❌ Low validation ({score}/{mx})</span>'

def mc_card(label, bnh_val, ov_val, delta_val, fmt_bnh, fmt_ov, fmt_delta,
            higher_is_better=True, delta_suffix=""):
    dv, dcls = fmt_delta(delta_val)
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


# ── Hero header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-brand">NivesAI</div>
  <div class="hero-sub">LARF Overlay Research Engine</div>
  <div class="hero-meta">173 Indian mutual funds &nbsp;·&nbsp; Jan 2010 – Apr 2026 &nbsp;·&nbsp; AMFI NAV data &nbsp;·&nbsp; Rule-based strategy</div>
  <div class="hero-tagline">
    What if a simple set of rules — watching the market and the fund — had automatically moved a small portion
    of your investment to safety during downturns, and back again when markets recovered?
    No forecasts. No guesswork. Just rules. This tool shows what would have happened across 173 Indian mutual funds.
  </div>
</div>
""", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────────────────────────────
master_df, crash_df, regime_tl = load_master()
curves_df  = load_curves()
nifty_ret  = load_nifty_returns()   # None if file doesn't exist yet


# ── Fund selector ─────────────────────────────────────────────────────────────
st.markdown('<div class="sel-wrap"><div class="sel-title">Select a fund to explore</div>', unsafe_allow_html=True)

fund_options = {}
for _, r in master_df.sort_values(["scheme_category","scheme_name"]).iterrows():
    fund_options[f"{r['scheme_name']}  ·  {r['scheme_category']}"] = str(r["scheme_code"])

fc1, fc2, fc3, fc4 = st.columns([4, 1.5, 1.5, 0.9])
with fc1:
    sel = st.selectbox("Fund", ["— choose a fund —"] + list(fund_options.keys()),
                       label_visibility="collapsed")
with fc2:
    amount = st.number_input(
        "Amount (₹)", min_value=10_000, max_value=10_00_00_000,
        value=DEFAULT_AMT, step=10_000, format="%d",
        label_visibility="collapsed",
        help="Initial investment amount in ₹",
    )
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
    go_btn = st.button("Analyse →", type="primary", use_container_width=True)

st.markdown(
    '<div style="font-size:0.72rem;color:#94a3b8;margin:6px 0 4px">'
    '① Pick a fund &nbsp; ② Enter amount &nbsp; ③ Choose your investment start date &nbsp; ④ Hit Analyse'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

if sel == "— choose a fund —" or not go_btn:
    st.markdown(
        '<div style="margin-top:32px;padding:32px;text-align:center;color:#94a3b8;'
        'border:1px dashed #e2e8f0;border-radius:12px;font-size:0.88rem">'
        '↑ &nbsp; Select a fund above to see the full analysis'
        '</div>',
        unsafe_allow_html=True,
    )
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

m = compute_metrics(sc, amount, regime_tl, nifty_ret)
if m is None:
    st.error("Not enough data to compute metrics for this date range.")
    st.stop()

st.markdown("---")


# ── Fund header ────────────────────────────────────────────────────────────────
hc1, hc2 = st.columns([7, 2.5])
with hc1:
    st.markdown(f'<div class="fund-name">{fr["scheme_name"]}</div>', unsafe_allow_html=True)
    cat  = fr.get("scheme_category","")
    role = fr.get("final_role","")
    conf = str(fr.get("classification_confidence","")).upper()
    conf_map = {"HIGH":"Strong profile fit","MEDIUM":"Moderate profile fit","LOW":"Mixed signals"}
    conf_label = conf_map.get(conf, conf)
    amc_name = fr.get("amc","")
    meta_parts = [p for p in [amc_name, cat, role + (f" · {conf_label}" if role else "")] if p]
    st.markdown(
        f'<div class="fund-meta">{" &nbsp;·&nbsp; ".join(meta_parts)}</div>',
        unsafe_allow_html=True,
    )
with hc2:
    oos_e = bool(fr.get("oos_eligible", True))
    vs    = fr.get("validation_score", 0)
    st.markdown(val_badge(vs, oos_e), unsafe_allow_html=True)

# Role callout
role_note = ROLE_DESC.get(role,"")
note_parts = []
if role_note:
    note_parts.append(f"<strong>{role}:</strong> {role_note}")
if conf == "LOW":
    note_parts.append("Confidence is mixed — this fund's behaviour didn't strongly fit one category. Treat the role as directional.")
elif conf == "MEDIUM" and role_note:
    note_parts.append("Classification confidence is moderate.")
if note_parts:
    st.markdown(f'<div class="co">{"&nbsp; ".join(note_parts)}</div>', unsafe_allow_html=True)

# Info row
num_sells = int(fr.get("v2a_num_sells", 0))
date_from = inv_ts.strftime("%d %b %Y")
date_to   = sim_end.strftime("%d %b %Y")
yrs_str   = f"{m['years']:.1f} yrs"
is_custom = inv_ts > sim_start

st.markdown(
    f'<div class="info-row">'
    f'<div class="ir-item"><span class="ir-lbl">Simulation period</span>'
    f'<span class="ir-val">{date_from} → {date_to} ({yrs_str})</span></div>'
    f'<div class="ir-item"><span class="ir-lbl">Overlay trims (full 16-yr sim)</span>'
    f'<span class="ir-val">{num_sells} rule-based sells</span></div>'
    f'<div class="ir-item"><span class="ir-lbl">Days strategy was active</span>'
    f'<span class="ir-val">{m["reg_pct"]*100:.0f}% of the period</span></div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Main metrics ───────────────────────────────────────────────────────────────
period_lbl = f"from {date_from}" if is_custom else "2010 – 2026"
st.markdown(f'<div class="slbl">Performance Comparison · {period_lbl}</div>', unsafe_allow_html=True)

edge_cagr = m["v2a_cagr"] - m["bnh_cagr"]
edge_dd   = m["v2a_dd"]   - m["bnh_dd"]
edge_vol  = m["v2a_vol"]  - m["bnh_vol"]
edge_val  = m["final_v2a"] - m["final_bnh"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(mc_card(
        "Annual Return (CAGR)", m["bnh_cagr"], m["v2a_cagr"], edge_cagr,
        lambda v: pct(v,2), lambda v: pct(v,2), pct_delta,
        higher_is_better=True,
    ), unsafe_allow_html=True)
with c2:
    st.markdown(mc_card(
        "Worst Drawdown", m["bnh_dd"], m["v2a_dd"], edge_dd,
        lambda v: pct(v,1), lambda v: pct(v,1), pct_delta,
        higher_is_better=False,
        delta_suffix=" vs holding",
    ), unsafe_allow_html=True)
with c3:
    st.markdown(mc_card(
        "Annualised Volatility", m["bnh_vol"], m["v2a_vol"], edge_vol,
        lambda v: pct(v,1), lambda v: pct(v,1), pct_delta,
        higher_is_better=False,
        delta_suffix=" vs holding",
    ), unsafe_allow_html=True)
with c4:
    ev_str, ev_cls = (f"+{inr(edge_val)}", "pos") if edge_val >= 0 else (inr(edge_val), "neg")
    st.markdown(f"""
    <div class="mc">
      <div class="mc-lbl">Portfolio Value · {period_lbl}</div>
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
    "<strong>Annual Return (CAGR):</strong> average yearly growth compounded. &nbsp;"
    "<strong>Worst Drawdown:</strong> biggest peak-to-trough fall. &nbsp;"
    "<strong>Volatility:</strong> how much the portfolio value moves day-to-day (lower = smoother ride)."
    + (f"&nbsp; All metrics computed from {date_from}." if is_custom else "")
    + "</div>",
    unsafe_allow_html=True,
)

# Secondary stats
def sstat(label, bnh_v, ov_v, fmt_fn, higher_is_better=True):
    bnh_s = fmt_fn(bnh_v)
    ov_s  = fmt_fn(ov_v)
    if pd.notna(bnh_v) and pd.notna(ov_v):
        delta = ov_v - bnh_v
        better = (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better)
        arrow = "↑" if better else "↓"
        cls = "pos" if better else "neg"
        delta_html = f'<span class="{cls}" style="font-size:0.72rem;margin-left:6px">{arrow}</span>'
    else:
        delta_html = ""
    return (
        f'<div class="sstat">'
        f'<span class="sstat-lbl">{label}</span>'
        f'<span class="sstat-val">{bnh_s} → <strong style="color:#0d6e6e">{ov_s}</strong>{delta_html}</span>'
        f'</div>'
    )

ss_parts = []
ss_parts.append(sstat("Calmar Ratio (CAGR ÷ |Max Drawdown|)", m["bnh_calmar"], m["v2a_calmar"],
                       lambda v: f"{v:.2f}" if pd.notna(v) and not np.isnan(v) else "—",
                       higher_is_better=True))
ss_parts.append(sstat("Score (CAGR − MaxDD/2)", m["bnh_score"], m["v2a_score"],
                       lambda v: f"{v:.3f}" if pd.notna(v) else "—",
                       higher_is_better=True))
if pd.notna(m["bnh_beta"]):
    ss_parts.append(sstat("Beta vs Nifty 50", m["bnh_beta"], m["v2a_beta"],
                           lambda v: f"{v:.2f}" if pd.notna(v) else "—",
                           higher_is_better=False))

st.markdown(
    f'<div class="sstat-row">{"".join(ss_parts)}</div>',
    unsafe_allow_html=True,
)
if pd.isna(m["bnh_beta"]):
    st.markdown(
        '<div class="note">Beta vs Nifty: re-run the Colab data prep (data_prep_colab.py) to enable this metric.</div>',
        unsafe_allow_html=True,
    )


# 2024-26 sideways callout
crash_sw = crash_df[(crash_df["scheme_code"] == code) &
                    crash_df["period_name"].str.contains("Sideways", na=False)]
if len(crash_sw) > 0:
    sw = crash_sw.iloc[0]
    if pd.notna(sw.get("v2a_beats_bnh")):
        bfall = abs(sw["bnh_max_dd"]) * 100 if pd.notna(sw["bnh_max_dd"]) else None
        vfall = abs(sw["v2a_max_dd"]) * 100 if pd.notna(sw["v2a_max_dd"]) else None
        fund_result = (f"For this fund: worst fall was {bfall:.1f}% without the overlay, "
                       f"{vfall:.1f}% with it. " if bfall and vfall else "")
        icon = "📈" if sw["v2a_beats_bnh"] else "📉"
        st.markdown(
            f'<div class="co" style="margin-top:18px">{icon} <strong>How did it perform in the recent sideways market (2024–26)?</strong><br>'
            f'{fund_result}'
            f"Across all 173 funds, the overlay outperformed simple holding in "
            f"<strong>152 of 173 cases (88%)</strong> during this period.</div>",
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
    name="With overlay", line=dict(color=TEAL, width=2.4),
    hovertemplate="<b>With overlay</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>",
), row=1, col=1)

rg = regime_tl[
    (regime_tl["date"] >= sc["date"].min()) &
    (regime_tl["date"] <= sc["date"].max())
].copy()
fig.add_trace(go.Bar(
    x=rg["date"].dt.strftime("%Y-%m-%d").tolist(),
    y=rg["macro_active"].astype(int).tolist(),
    marker_color=[ACTIVE_BAR if v else IDLE_BAR for v in rg["macro_active"]],
    name="Strategy watching", showlegend=True,
    hovertemplate="%{x}<br>Overlay active: %{y}<extra></extra>",
), row=2, col=1)

shapes = []
for _, s, e in CRASH_PERIODS:
    shapes.append(dict(
        type="rect", xref="x", yref="paper",
        x0=s, x1=e, y0=0.22, y1=1.0,
        fillcolor=CRASH_COLOR, line_width=0, layer="below",
    ))

fig.update_layout(
    shapes=shapes, height=540,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor="white", plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                font=dict(size=11), bgcolor="rgba(255,255,255,0)"),
    hovermode="x unified",
    font=dict(family="Inter, sans-serif"),
)
fig.update_yaxes(tickprefix="₹", tickformat=",.0f", gridcolor="#f1f5f9", row=1, col=1)
fig.update_yaxes(tickvals=[0,1], ticktext=["","Active"], gridcolor="#f1f5f9", row=2, col=1)
fig.update_xaxes(type="date", tickformat="%b '%y", gridcolor="#f1f5f9", showgrid=True)

st.plotly_chart(fig, use_container_width=True)
st.markdown(
    '<div class="note">🔴 Shaded areas = major market crashes (2011, 2015–16, 2018–19, 2020 COVID). '
    'Bottom bar = days the strategy was actively monitoring for risk signals.</div>',
    unsafe_allow_html=True,
)


# ── Crash table ────────────────────────────────────────────────────────────────
st.markdown('<div class="slbl">How Did It Hold Up During Each Crash?</div>', unsafe_allow_html=True)

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
        "Overlay helped?": st.column_config.TextColumn(width=230),
    })
st.markdown(
    '<div class="note">"pp" = percentage points. A shallower drop means less damage to your portfolio during the crash.</div>',
    unsafe_allow_html=True,
)


# ── Validation ─────────────────────────────────────────────────────────────────
with st.expander("🔍  How reliable are these results? (4 independent checks)", expanded=False):
    st.markdown(
        "Before trusting any strategy's historical results, it's essential to ask: "
        "is this a real edge, or did the strategy just happen to fit the past data? "
        "We ran four independent tests to answer that question."
    )
    st.markdown("")

    # Check 1 — Walk-forward
    wf_p   = bool(fr.get("wf_pass", False))
    wf_tot = fr.get("wf_windows_total")
    wf_n   = fr.get("wf_windows_pass")
    wf_r   = fr.get("wf_pass_rate")
    wf_ok  = pd.notna(wf_r)
    icon1  = "✅" if wf_p else "❌"
    if wf_ok:
        wf_detail = (
            f"{icon1} Overlay beat simple holding in **{int(wf_n or 0)} of {int(wf_tot or 0)} time windows** "
            f"({(wf_r or 0)*100:.0f}%). "
            + ("Consistent performance across different time periods." if wf_p
               else "Performance was inconsistent — the result depends heavily on *when* you invested.")
        )
    else:
        wf_detail = "❌ Not enough history for this test (need at least 7 years of data)."
    st.markdown(
        f'<div class="vc"><div class="vc-q">Check 1 — Does it work consistently across different time periods?</div>'
        f'<div class="vc-r">{wf_detail}</div></div>',
        unsafe_allow_html=True,
    )

    # Check 2 — OOS
    oos_e2 = bool(fr.get("oos_eligible", True))
    oos_p  = bool(fr.get("oos_pass", False))
    if not oos_e2:
        oos_detail = "— This fund doesn't yet have enough history for a proper out-of-sample test (needs 5+ years of training data)."
    elif oos_p:
        oos_detail = "✅ The overlay outperformed on 2023–2026 data that was completely excluded during strategy design. Strong evidence the edge is genuine."
    else:
        oos_detail = "❌ The overlay did not outperform on fresh 2023–2026 data. The strategy may have been too well-fitted to older patterns."
    st.markdown(
        f'<div class="vc"><div class="vc-q">Check 2 — Would it hold up on data it had never seen?</div>'
        f'<div class="vc-r">{oos_detail}</div></div>',
        unsafe_allow_html=True,
    )

    # Check 3 — Monte Carlo
    mc_p   = bool(fr.get("mc_pass", False))
    mc_pct = fr.get("real_percentile")
    if pd.notna(mc_pct):
        mc_detail = (
            f"{'✅' if mc_p else '❌'} The real result ranked in the **{mc_pct:.1f}th percentile** "
            f"out of 1,000 randomly shuffled simulations. "
            + (f"Only ~{100 - mc_pct:.0f}% of random runs did as well — very unlikely to be luck." if mc_p
               else "Random simulations frequently matched this result — the edge may be partly coincidence.")
        )
    else:
        mc_detail = "Monte Carlo data not available for this fund."
    st.markdown(
        f'<div class="vc"><div class="vc-q">Check 3 — Could this just be luck?</div>'
        f'<div class="vc-r">{mc_detail}</div></div>',
        unsafe_allow_html=True,
    )

    # Check 4 — Stability
    st_p  = bool(fr.get("stability_pass", False))
    st_r  = fr.get("stability_pass_rate")
    cliff = bool(fr.get("cliff_detected", False))
    if pd.notna(st_r):
        st_detail = (
            f"{'✅' if st_p else '❌'} Results held up in **{st_r*100:.0f}%** of 20 parameter variations. "
            + ("The strategy is robust — small adjustments don't break it." if st_p
               else "The strategy is sensitive — small changes in the rules affect the outcome.")
            + (" ⚠️ One threshold caused a larger-than-expected shift when changed." if cliff else "")
        )
    else:
        st_detail = "Stability data not available for this fund."
    st.markdown(
        f'<div class="vc"><div class="vc-q">Check 4 — Does it break if the rules are nudged slightly?</div>'
        f'<div class="vc-r">{st_detail}</div></div>',
        unsafe_allow_html=True,
    )

    # Summary
    vs_int = int(fr.get("validation_score",0)) if pd.notna(fr.get("validation_score")) else 0
    mx2    = 4 if oos_e2 else 3
    if vs_int >= mx2:
        st.success(
            f"✅ Passed all {mx2} checks. The overlay results for this fund are well-supported. "
            "You can interpret these numbers with relatively high confidence."
        )
    elif vs_int >= 2:
        st.warning(
            f"Passed {vs_int} of {mx2} checks. The crash protection evidence is solid. "
            "The return-improvement figures are directional — treat them with some caution."
        )
    else:
        st.error(
            f"Passed only {vs_int} of {mx2} checks. The results for this fund are not strongly supported. "
            "Crash protection data may still be informative, but the overall edge is not statistically robust."
        )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="disc" style="text-align:center">'
    "NivesAI &nbsp;·&nbsp; LARF v2a &nbsp;·&nbsp; AMFI NAV data &nbsp;·&nbsp; 173 funds &nbsp;·&nbsp; Jan 2010 – Apr 2026<br>"
    "<strong>All results are retrospective research simulations based on historical NAV data. "
    "This is not investment advice. NivesAI is not a SEBI-registered investment advisor.</strong>"
    "</div>",
    unsafe_allow_html=True,
)