"""
NivesAI — LARF Overlay Research Tool
v1.4 — impact-first design
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
TEAL_DARK   = "#0a4f4f"
BNH_COLOR   = "#94a3b8"
CRASH_COLOR = "rgba(239,68,68,0.10)"
ACTIVE_BAR  = "#0d6e6e"
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 1160px; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 24px 0; }
[data-testid="stButton"] > button {
  background: #0d6e6e !important; color: white !important;
  border: none !important; font-weight: 600 !important;
  font-size: 0.95rem !important;
}
[data-testid="stButton"] > button:hover { background: #0a5555 !important; }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, #0a4f4f 0%, #0f172a 100%);
  border-radius: 16px; padding: 34px 40px 30px; margin-bottom: 24px;
}
.hero-top { display: flex; align-items: flex-start; justify-content: space-between; }
.hero-brand { font-size: 2.2rem; font-weight: 800; color: #fff; letter-spacing: -0.8px; }
.hero-sub   { font-size: 1rem; color: #5eead4; margin-top: 4px; font-weight: 500; }
.hero-meta  { font-size: 0.75rem; color: rgba(255,255,255,0.38); margin-top: 10px; }
.hero-tagline {
  margin-top: 20px; padding-top: 18px;
  border-top: 1px solid rgba(255,255,255,0.1);
  font-size: 0.9rem; color: rgba(255,255,255,0.6); line-height: 1.6;
  max-width: 680px;
}
.hero-pill {
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px; padding: 4px 12px;
  font-size: 0.72rem; color: rgba(255,255,255,0.5); white-space: nowrap;
}

/* ── Selector ── */
.sel-wrap {
  background: #fff; border: 1.5px solid #e2e8f0;
  border-radius: 12px; padding: 18px 20px 14px; margin-bottom: 6px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.05);
}
.sel-title {
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.8px; color: #94a3b8; margin-bottom: 12px;
}

/* ── Impact banner ── */
.impact {
  background: linear-gradient(135deg, #0a4f4f 0%, #134e4a 100%);
  border-radius: 14px; padding: 26px 32px; margin: 8px 0 24px;
  position: relative; overflow: hidden;
}
.impact::before {
  content: ''; position: absolute; top: -40px; right: -40px;
  width: 180px; height: 180px; border-radius: 50%;
  background: rgba(255,255,255,0.04);
}
.impact-headline {
  font-size: 1.45rem; font-weight: 700; color: #fff; line-height: 1.45;
}
.impact-sub { font-size: 0.88rem; color: rgba(255,255,255,0.55); margin-top: 8px; }
.hl-good  { color: #6ee7b7; }
.hl-bad   { color: #fca5a5; }
.hl-money { color: #fff; font-weight: 800; font-size: 1.65rem; }

/* ── Metric cards ── */
.mc-wrap { display: flex; flex-direction: column; height: 100%; }

.mc {
  border-radius: 12px; padding: 20px 18px 16px;
  border: 1.5px solid #e2e8f0; background: #fff;
  box-shadow: 0 2px 8px rgba(15,23,42,0.05);
  flex: 1;
}
.mc.win {
  background: linear-gradient(160deg, #f0fdfa 0%, #ccfbf1 100%);
  border-color: #99f6e4;
}
.mc.neutral { background: #f8fafc; border-color: #e2e8f0; }

.mc-lbl { font-size:0.65rem; font-weight:700; text-transform:uppercase;
          letter-spacing:0.7px; color:#94a3b8; margin-bottom:12px; }

.mc-main { display: flex; align-items: baseline; gap: 4px; margin-bottom: 4px; }
.mc-big  { font-size: 2.2rem; font-weight: 800; color: #0d6e6e; line-height: 1; }
.mc-big-neutral { font-size: 2.2rem; font-weight: 800; color: #0f172a; line-height: 1; }
.mc-unit { font-size: 0.85rem; font-weight: 600; color: #64748b; }

.mc-vs   { font-size: 0.78rem; color: #94a3b8; margin-bottom: 8px; }
.mc-delta { font-size: 0.8rem; font-weight: 600; }

.pos { color: #16a34a; } .neg { color: #dc2626; } .neu { color: #94a3b8; }

/* ── Secondary stats ── */
.sstat-row { display:flex; flex-wrap:wrap; gap:10px; margin:16px 0 0; }
.sstat {
  background:#f8fafc; border:1px solid #e2e8f0;
  border-radius:8px; padding:10px 16px;
  display:flex; flex-direction:column; gap:3px;
}
.sstat-lbl { font-size:0.62rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; }
.sstat-val { font-size:0.88rem; font-weight:600; color:#0f172a; }

/* ── Section label ── */
.slbl {
  font-size:0.68rem; font-weight:700; text-transform:uppercase;
  letter-spacing:1.2px; color:#94a3b8; margin:28px 0 14px;
  display: flex; align-items: center; gap: 8px;
}
.slbl::after {
  content: ''; flex: 1; height: 1px; background: #f1f5f9;
}

/* ── Fund header ── */
.fund-name { font-size:1.35rem; font-weight:800; color:#0f172a; line-height:1.3; }
.fund-meta { font-size:0.82rem; color:#64748b; margin-top:4px; }

/* ── Info row ── */
.info-row { display:flex; flex-wrap:wrap; gap:24px; margin:14px 0 0; }
.ir-item  { display:flex; flex-direction:column; gap:2px; }
.ir-lbl   { font-size:0.62rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; }
.ir-val   { font-size:0.84rem; font-weight:600; color:#0f172a; }

/* ── Callout ── */
.co {
  background:#f0fdfd; border-left:3px solid #0d6e6e;
  border-radius:0 8px 8px 0; padding:10px 14px; margin:12px 0;
  font-size:0.84rem; color:#374151; line-height:1.55;
}

/* ── Validation ── */
.vb-y { background:#fffbeb; color:#92400e; border:1px solid #fde68a; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }
.vb-g { background:#f0fdf4; color:#14532d; border:1px solid #bbf7d0; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }
.vb-r { background:#fef2f2; color:#7f1d1d; border:1px solid #fecaca; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:600; }

.vc { border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; margin:8px 0; background:#fff; }
.vc-q { font-size:0.88rem; font-weight:600; color:#0f172a; margin-bottom:6px; }
.vc-r { font-size:0.83rem; color:#374151; }

/* ── Note ── */
.note { font-size:0.72rem; color:#94a3b8; line-height:1.5; margin-top:6px; }
.disc { font-size:0.7rem; color:#94a3b8; line-height:1.6; }
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
        return (series.iloc[-1] / amount) ** (1 / years) - 1 if amount > 0 else np.nan

    def mdd(series):
        roll_max = series.cummax()
        dd = (series - roll_max) / roll_max
        return float(dd.min())

    def ann_vol(series):
        return float(series.pct_change().dropna().std() * np.sqrt(252))

    def calmar(c, d):
        return c / abs(d) if d != 0 and not np.isnan(d) else np.nan

    bnh_c  = cagr(df["bnh_s"]);   v2a_c  = cagr(df["v2a_s"])
    bnh_d  = mdd(df["bnh_s"]);    v2a_d  = mdd(df["v2a_s"])
    bnh_sc = bnh_c - abs(bnh_d)/2; v2a_sc = v2a_c - abs(v2a_d)/2
    bnh_v  = ann_vol(df["bnh_s"]); v2a_v  = ann_vol(df["v2a_s"])
    bnh_ca = calmar(bnh_c, bnh_d); v2a_ca = calmar(v2a_c, v2a_d)

    r = rtl[(rtl["date"] >= df["date"].min()) & (rtl["date"] <= df["date"].max())]
    reg_pct = float(r["macro_active"].mean()) if len(r) > 0 else np.nan

    bnh_beta = np.nan; v2a_beta = np.nan
    if nifty_ret_df is not None:
        try:
            nr = nifty_ret_df[(nifty_ret_df["date"] >= df["date"].min()) &
                              (nifty_ret_df["date"] <= df["date"].max())].copy()
            m_bnh = pd.merge(df[["date","bnh_s"]], nr[["date","daily_return"]], on="date", how="inner")
            m_v2a = pd.merge(df[["date","v2a_s"]], nr[["date","daily_return"]], on="date", how="inner")
            if len(m_bnh) > 30:
                rb = m_bnh["bnh_s"].pct_change().dropna()
                rv = m_v2a["v2a_s"].pct_change().dropna()
                mk = m_bnh["daily_return"].iloc[1:].reset_index(drop=True)
                var_m = mk.var()
                if var_m > 0:
                    bnh_beta = float(np.cov(rb, mk)[0,1] / var_m)
                    v2a_beta = float(np.cov(rv, m_v2a["daily_return"].iloc[1:].reset_index(drop=True))[0,1] / var_m)
        except Exception:
            pass

    return {
        "years": years,
        "bnh_cagr": bnh_c,   "v2a_cagr": v2a_c,
        "bnh_dd":   bnh_d,   "v2a_dd":   v2a_d,
        "bnh_score":bnh_sc,  "v2a_score":v2a_sc,
        "bnh_vol":  bnh_v,   "v2a_vol":  v2a_v,
        "bnh_calmar":bnh_ca, "v2a_calmar":v2a_ca,
        "bnh_beta": bnh_beta,"v2a_beta":  v2a_beta,
        "final_bnh":float(df["bnh_s"].iloc[-1]),
        "final_v2a":float(df["v2a_s"].iloc[-1]),
        "reg_pct":  reg_pct,
    }

def val_badge(score, oos_elig):
    score = int(score) if pd.notna(score) else 0
    mx = 4 if oos_elig else 3
    if score >= mx:
        return f'<span class="vb-g">✅ Fully validated ({score}/{mx})</span>'
    elif score >= 2:
        return f'<span class="vb-y">⚠️ Partial ({score}/{mx})</span>'
    else:
        return f'<span class="vb-r">❌ Low validation ({score}/{mx})</span>'


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-top">
    <div>
      <div class="hero-brand">NivesAI</div>
      <div class="hero-sub">LARF Overlay Research Engine</div>
      <div class="hero-meta">173 Indian mutual funds &nbsp;·&nbsp; Jan 2010 – Apr 2026 &nbsp;·&nbsp; AMFI NAV data</div>
    </div>
    <div class="hero-pill">Research Preview</div>
  </div>
  <div class="hero-tagline">
    What if a simple, rule-based system had automatically protected a portion of your investment during market downturns —
    no forecasts, no guesswork, just rules? This tool shows exactly what would have happened across
    173 Indian mutual funds over 16 years.
  </div>
</div>
""", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────────────────────────────
master_df, crash_df, regime_tl = load_master()
curves_df = load_curves()
nifty_ret = load_nifty_returns()


# ── Selector ──────────────────────────────────────────────────────────────────
st.markdown('<div class="sel-wrap"><div class="sel-title">① Pick a fund &nbsp; ② Enter amount &nbsp; ③ Choose start date &nbsp; ④ Analyse</div>', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

if sel == "— choose a fund —" or not go_btn:
    st.markdown(
        '<div style="margin-top:40px;padding:48px 32px;text-align:center;color:#94a3b8;'
        'border:2px dashed #e2e8f0;border-radius:16px;font-size:0.9rem;background:#fafafa">'
        '<div style="font-size:2rem;margin-bottom:12px">📊</div>'
        '<div style="font-weight:600;color:#64748b;margin-bottom:4px">Select a fund to see the full analysis</div>'
        '<div style="font-size:0.8rem">Choose any of the 173 funds above — equity, debt, hybrid, or sectoral</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ── Fund data ─────────────────────────────────────────────────────────────────
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


# ── Impact banner ─────────────────────────────────────────────────────────────
is_custom  = inv_ts > sim_start
date_from  = inv_ts.strftime("%d %b %Y")
date_to    = sim_end.strftime("%d %b %Y")
yrs_str    = f"{m['years']:.1f} yrs"

# Build the headline sentence
dd_improved  = m["v2a_dd"] > m["bnh_dd"]   # True = overlay shallower (less negative = better)
ret_improved = m["v2a_cagr"] > m["bnh_cagr"]

bnh_dd_str = f"{abs(m['bnh_dd'])*100:.1f}%"
v2a_dd_str = f"{abs(m['v2a_dd'])*100:.1f}%"
bnh_ret_str = f"{m['bnh_cagr']*100:.1f}%"
v2a_ret_str = f"{m['v2a_cagr']*100:.1f}%"

if dd_improved:
    dd_part = (f'worst loss dropped from <span class="hl-bad">{bnh_dd_str}</span> '
               f'to <span class="hl-good">{v2a_dd_str}</span>')
else:
    dd_part = (f'worst loss was <span class="hl-bad">{bnh_dd_str}</span> '
               f'(overlay: <span class="hl-bad">{v2a_dd_str}</span>)')

val_bnh = inr(m["final_bnh"])
val_v2a = inr(m["final_v2a"])

if ret_improved:
    val_part = (f'₹{amount/1000:.0f}K grew to <span class="hl-money">{val_v2a}</span> '
                f'vs {val_bnh} without')
else:
    val_part = (f'₹{amount/1000:.0f}K grew to {val_bnh}; overlay produced {val_v2a}')

st.markdown(
    f'<div class="impact">'
    f'<div class="impact-headline">Over {yrs_str}, {dd_part} — and {val_part} the overlay.</div>'
    f'<div class="impact-sub">{fr["scheme_name"]} &nbsp;·&nbsp; {date_from} → {date_to}'
    f'{"&nbsp; · &nbsp;Your chosen start date" if is_custom else ""}</div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Fund subheader ────────────────────────────────────────────────────────────
hc1, hc2 = st.columns([7, 2.5])
with hc1:
    cat  = fr.get("scheme_category","")
    role = fr.get("final_role","")
    conf = str(fr.get("classification_confidence","")).upper()
    conf_map = {"HIGH":"Strong profile fit","MEDIUM":"Moderate fit","LOW":"Mixed signals"}
    conf_label = conf_map.get(conf, conf)
    amc_name = fr.get("amc","")
    meta_parts = [p for p in [amc_name, cat, (role + (f" · {conf_label}" if role else "")) if role else ""] if p]
    st.markdown(f'<div class="fund-meta">{" &nbsp;·&nbsp; ".join(meta_parts)}</div>', unsafe_allow_html=True)
with hc2:
    oos_e = bool(fr.get("oos_eligible", True))
    vs    = fr.get("validation_score", 0)
    st.markdown(val_badge(vs, oos_e), unsafe_allow_html=True)

role_note = ROLE_DESC.get(role,"")
if role_note or conf == "LOW":
    parts = []
    if role_note:
        parts.append(f"<strong>{role}:</strong> {role_note}")
    if conf == "LOW":
        parts.append("Confidence is mixed — this fund didn't strongly fit one behaviour category. Treat the role as directional, not definitive.")
    elif conf == "MEDIUM" and role_note:
        parts.append("Classification confidence is moderate.")
    st.markdown(f'<div class="co">{"&nbsp; ".join(parts)}</div>', unsafe_allow_html=True)

num_sells = int(fr.get("v2a_num_sells", 0))
st.markdown(
    f'<div class="info-row">'
    f'<div class="ir-item"><span class="ir-lbl">Period shown</span>'
    f'<span class="ir-val">{date_from} → {date_to} ({yrs_str})</span></div>'
    f'<div class="ir-item"><span class="ir-lbl">Rule-based trims (full sim)</span>'
    f'<span class="ir-val">{num_sells} sells over 16 yrs</span></div>'
    f'<div class="ir-item"><span class="ir-lbl">Days overlay was watching</span>'
    f'<span class="ir-val">{m["reg_pct"]*100:.0f}% of the period</span></div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Metric cards ──────────────────────────────────────────────────────────────
period_lbl = f"from {date_from}" if is_custom else "2010 – 2026"
st.markdown(f'<div class="slbl">Key Numbers · {period_lbl}</div>', unsafe_allow_html=True)

edge_cagr = m["v2a_cagr"] - m["bnh_cagr"]
edge_dd   = m["v2a_dd"]   - m["bnh_dd"]    # positive = overlay shallower = good
edge_vol  = m["v2a_vol"]  - m["bnh_vol"]   # negative = overlay smoother = good
edge_val  = m["final_v2a"] - m["final_bnh"]

def dc(v, d=1): return f"{v*100:.{d}f}"
def di(v): return inr(v)

# Card 1: Annual Return
r_win = edge_cagr > 0
r_d, r_cls = (f"+{dc(edge_cagr,2)}%", "pos") if r_win else (f"{dc(edge_cagr,2)}%", "neg")

# Card 2: Worst Drawdown
dd_win = edge_dd > 0
dd_d = f"−{abs(edge_dd)*100:.1f} pp shallower" if dd_win else f"+{abs(edge_dd)*100:.1f} pp deeper"
dd_cls = "pos" if dd_win else "neg"

# Card 3: Volatility
vl_win = edge_vol < 0
vl_d, vl_cls = (f"−{abs(edge_vol)*100:.1f} pp smoother", "pos") if vl_win else (f"+{abs(edge_vol)*100:.1f} pp rougher", "neg")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="mc {'win' if r_win else 'neutral'}">
      <div class="mc-lbl">Annual Return</div>
      <div class="mc-main"><span class="mc-big">{dc(m['v2a_cagr'],2)}%</span></div>
      <div class="mc-vs">vs {dc(m['bnh_cagr'],2)}% holding</div>
      <div class="mc-delta {r_cls}">{r_d} vs holding</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="mc {'win' if dd_win else 'neutral'}">
      <div class="mc-lbl">Worst Drawdown</div>
      <div class="mc-main"><span class="mc-big">−{abs(m['v2a_dd'])*100:.1f}%</span></div>
      <div class="mc-vs">vs −{abs(m['bnh_dd'])*100:.1f}% holding</div>
      <div class="mc-delta {dd_cls}">{dd_d}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="mc {'win' if vl_win else 'neutral'}">
      <div class="mc-lbl">Annualised Volatility</div>
      <div class="mc-main"><span class="mc-big">{dc(m['v2a_vol'],1)}%</span></div>
      <div class="mc-vs">vs {dc(m['bnh_vol'],1)}% holding</div>
      <div class="mc-delta {vl_cls}">{vl_d}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    v_win = edge_val >= 0
    ev_str = (f"+{inr(edge_val)}" if v_win else inr(edge_val))
    ev_cls = "pos" if v_win else "neg"
    st.markdown(f"""
    <div class="mc {'win' if v_win else 'neutral'}">
      <div class="mc-lbl">Portfolio Value · {period_lbl}</div>
      <div class="mc-main"><span class="mc-big" style="font-size:1.7rem">{inr(m['final_v2a'])}</span></div>
      <div class="mc-vs">vs {inr(m['final_bnh'])} holding</div>
      <div class="mc-delta {ev_cls}">{ev_str} difference</div>
    </div>""", unsafe_allow_html=True)

# Secondary stats
def sstat(label, bnh_v, ov_v, fmt_fn, higher_is_better=True):
    bv, ov = fmt_fn(bnh_v), fmt_fn(ov_v)
    better = False
    if pd.notna(bnh_v) and pd.notna(ov_v) and not np.isnan(bnh_v) and not np.isnan(ov_v):
        delta = ov_v - bnh_v
        better = (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better)
    arrow = f'<span class="{"pos" if better else "neg"}" style="font-size:0.7rem;margin-left:4px">{"↑" if better else "↓"}</span>'
    return (f'<div class="sstat">'
            f'<span class="sstat-lbl">{label}</span>'
            f'<span class="sstat-val">{bv} → <strong style="color:#0d6e6e">{ov}</strong>{arrow}</span>'
            f'</div>')

fmt_f = lambda v: f"{v:.2f}" if pd.notna(v) and not np.isnan(v) else "—"
fmt_3 = lambda v: f"{v:.3f}" if pd.notna(v) else "—"

ss = [
    sstat("Calmar Ratio", m["bnh_calmar"], m["v2a_calmar"], fmt_f, higher_is_better=True),
    sstat("Score (CAGR − MaxDD/2)", m["bnh_score"], m["v2a_score"], fmt_3, higher_is_better=True),
]
if pd.notna(m["bnh_beta"]):
    ss.append(sstat("Beta vs Nifty 50", m["bnh_beta"], m["v2a_beta"], fmt_f, higher_is_better=False))

st.markdown(f'<div class="sstat-row">{"".join(ss)}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="note" style="margin-top:10px">'
    "<strong>Calmar:</strong> return divided by worst loss — higher is better. &nbsp;"
    "<strong>Score:</strong> NivesAI's single-number efficiency measure."
    + (" &nbsp;<strong>Beta:</strong> how much this fund moves relative to Nifty 50 (1.0 = moves with the market)." if pd.notna(m["bnh_beta"]) else "")
    + ("" if pd.notna(m["bnh_beta"]) else " &nbsp;Beta: re-run the Colab data prep to enable.")
    + "</div>",
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
        fund_result = (f"For this fund: worst fall was {bfall:.1f}% without the overlay, {vfall:.1f}% with it. "
                       if bfall and vfall else "")
        icon = "📈" if sw["v2a_beats_bnh"] else "📉"
        st.markdown(
            f'<div class="co" style="margin-top:18px">'
            f'{icon} <strong>Recent sideways market (2024–26):</strong> '
            f'{fund_result}Across all 173 funds, the overlay outperformed simple holding in '
            f'<strong>152 of 173 cases (88%)</strong> during this period.</div>',
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
    name="Simple holding", line=dict(color="#94a3b8", width=1.8),
    hovertemplate="<b>Simple holding</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>",
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=dates, y=sc["v2a_s"].tolist(), mode="lines",
    name="With overlay", line=dict(color=TEAL, width=2.5),
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
    name="Strategy active", showlegend=True,
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
    paper_bgcolor="white", plot_bgcolor="#fafeff",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=11), bgcolor="rgba(255,255,255,0)"),
    hovermode="x unified",
    font=dict(family="Inter, sans-serif"),
)
fig.update_yaxes(tickprefix="₹", tickformat=",.0f", gridcolor="#f1f5f9", row=1, col=1)
fig.update_yaxes(tickvals=[0,1], ticktext=["","Active"], gridcolor="#f1f5f9", row=2, col=1)
fig.update_xaxes(type="date", tickformat="%b '%y", gridcolor="#f1f5f9", showgrid=True)

st.plotly_chart(fig, use_container_width=True)
st.markdown(
    '<div class="note">🔴 Shaded = major crashes (2011, 2015–16, 2018–19, 2020 COVID). '
    'Bottom bar = days the strategy was actively monitoring risk signals.</div>',
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
        rows.append({"Period": r["period_name"], "Without overlay": "Fund didn't exist yet",
                     "With overlay": "—", "Overlay helped?": "—"})
    else:
        b = abs(r["bnh_max_dd"])*100; v = abs(r["v2a_max_dd"])*100
        s = abs(r["drawdown_saved"])*100; win = bool(r["v2a_beats_bnh"])
        rows.append({
            "Period":          r["period_name"],
            "Without overlay": f"−{b:.1f}%",
            "With overlay":    f"−{v:.1f}%",
            "Overlay helped?": f"✅  Yes, {s:.1f} pp shallower" if win else f"❌  No, {s:.1f} pp deeper",
        })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
    column_config={
        "Period":          st.column_config.TextColumn(width=175),
        "Without overlay": st.column_config.TextColumn(width=155),
        "With overlay":    st.column_config.TextColumn(width=155),
        "Overlay helped?": st.column_config.TextColumn(width=230),
    })
st.markdown(
    '<div class="note">"pp" = percentage points. A shallower drop means less portfolio damage during the crash.</div>',
    unsafe_allow_html=True,
)


# ── Validation ─────────────────────────────────────────────────────────────────
with st.expander("🔍  How reliable are these results? (4 independent checks)", expanded=False):
    st.markdown(
        "Before trusting any strategy's historical results, it's essential to ask: "
        "is this a real edge, or just a lucky fit to past data? "
        "We ran four independent checks."
    )

    wf_p   = bool(fr.get("wf_pass", False))
    wf_tot = fr.get("wf_windows_total"); wf_n = fr.get("wf_windows_pass"); wf_r = fr.get("wf_pass_rate")
    if pd.notna(wf_r):
        wf_d = (f"{'✅' if wf_p else '❌'} Beat simple holding in **{int(wf_n or 0)} of {int(wf_tot or 0)} windows** "
                f"({(wf_r or 0)*100:.0f}%). "
                + ("Consistent across different time periods." if wf_p else "Performance varied depending on when you invested."))
    else:
        wf_d = "❌ Not enough history (needs 7+ years)."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 1 — Does it work consistently across different time periods?</div>'
                f'<div class="vc-r">{wf_d}</div></div>', unsafe_allow_html=True)

    oos_e2 = bool(fr.get("oos_eligible", True)); oos_p = bool(fr.get("oos_pass", False))
    if not oos_e2:
        oos_d = "— Not eligible (needs 5+ years of training data)."
    elif oos_p:
        oos_d = "✅ Outperformed on 2023–2026 data the strategy had never seen. Strong evidence the edge is genuine."
    else:
        oos_d = "❌ Did not outperform on fresh 2023–2026 data. The strategy may have been over-fitted to older patterns."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 2 — Would it hold up on data it had never seen?</div>'
                f'<div class="vc-r">{oos_d}</div></div>', unsafe_allow_html=True)

    mc_p = bool(fr.get("mc_pass", False)); mc_pct = fr.get("real_percentile")
    if pd.notna(mc_pct):
        mc_d = (f"{'✅' if mc_p else '❌'} Real result ranked in the **{mc_pct:.1f}th percentile** "
                f"out of 1,000 random simulations. "
                + (f"Only ~{100 - mc_pct:.0f}% of random runs matched it — very unlikely to be luck." if mc_p
                   else "Random simulations often matched it — the edge may be partly coincidence."))
    else:
        mc_d = "Monte Carlo data not available."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 3 — Could this just be luck?</div>'
                f'<div class="vc-r">{mc_d}</div></div>', unsafe_allow_html=True)

    st_p = bool(fr.get("stability_pass", False)); st_r = fr.get("stability_pass_rate"); cliff = bool(fr.get("cliff_detected", False))
    if pd.notna(st_r):
        st_d = (f"{'✅' if st_p else '❌'} Held up in **{st_r*100:.0f}%** of 20 parameter variations. "
                + ("Robust — small rule changes don't break it." if st_p else "Sensitive — small rule changes affect outcomes.")
                + (" ⚠️ One threshold caused a larger-than-expected shift when changed." if cliff else ""))
    else:
        st_d = "Stability data not available."
    st.markdown(f'<div class="vc"><div class="vc-q">Check 4 — Does it break if the rules are nudged slightly?</div>'
                f'<div class="vc-r">{st_d}</div></div>', unsafe_allow_html=True)

    vs_int = int(fr.get("validation_score",0)) if pd.notna(fr.get("validation_score")) else 0
    mx2 = 4 if oos_e2 else 3
    if vs_int >= mx2:
        st.success(f"✅ Passed all {mx2} checks. You can interpret these results with relatively high confidence.")
    elif vs_int >= 2:
        st.warning(f"Passed {vs_int} of {mx2} checks. Crash protection evidence is solid; return improvement numbers are directional.")
    else:
        st.error(f"Only {vs_int} of {mx2} checks passed. Treat the results for this fund with caution.")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="disc" style="text-align:center">'
    "NivesAI &nbsp;·&nbsp; LARF v2a &nbsp;·&nbsp; AMFI NAV data &nbsp;·&nbsp; 173 funds &nbsp;·&nbsp; Jan 2010 – Apr 2026<br>"
    "<strong>All results are retrospective research simulations based on historical NAV data. "
    "This is not investment advice. NivesAI is not a SEBI-registered investment advisor.</strong>"
    "</div>",
    unsafe_allow_html=True,
)
