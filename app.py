"""
NivesAI — LARF Overlay Research Tool
v1.5 — compare funds tab, hero trim, NaN fix, impact fix
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
hr { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }
[data-testid="stButton"] > button {
  background: #0d6e6e !important; color: white !important;
  border: none !important; font-weight: 600 !important;
}
[data-testid="stButton"] > button:hover { background: #0a5555 !important; }

/* ── Hero (slim) ── */
.hero {
  background: linear-gradient(135deg, #0a4f4f 0%, #0f172a 100%);
  border-radius: 14px; padding: 20px 28px; margin-bottom: 18px;
  display: flex; align-items: center; justify-content: space-between;
}
.hero-left {}
.hero-brand { font-size: 1.6rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
.hero-sub   { font-size: 0.82rem; color: #5eead4; margin-top: 2px; }
.hero-meta  { font-size: 0.68rem; color: rgba(255,255,255,0.35); margin-top: 6px; }
.hero-pill  {
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px; padding: 5px 14px;
  font-size: 0.72rem; color: rgba(255,255,255,0.5);
}

/* ── Impact banner ── */
.impact {
  background: linear-gradient(135deg, #0a4f4f 0%, #134e4a 100%);
  border-radius: 12px; padding: 22px 28px; margin: 6px 0 20px;
}
.impact-headline { font-size: 1.3rem; font-weight: 700; color: #fff; line-height: 1.45; }
.impact-sub { font-size: 0.82rem; color: rgba(255,255,255,0.5); margin-top: 6px; }
.hl-good  { color: #6ee7b7; }
.hl-bad   { color: #fca5a5; }
.hl-white { color: #fff; font-weight: 800; }

/* ── Metric cards ── */
.mc {
  border-radius: 10px; padding: 18px 16px 14px;
  border: 1.5px solid #e2e8f0; background: #fff;
  box-shadow: 0 1px 6px rgba(15,23,42,0.05);
}
.mc.win  { background: linear-gradient(160deg, #f0fdfa 0%, #ccfbf1 100%); border-color: #99f6e4; }
.mc.flat { background: #f8fafc; border-color: #e2e8f0; }
.mc-lbl  { font-size:0.63rem; font-weight:700; text-transform:uppercase; letter-spacing:0.7px; color:#94a3b8; margin-bottom:10px; }
.mc-big  { font-size:2rem; font-weight:800; color:#0d6e6e; line-height:1.1; }
.mc-big-flat { font-size:2rem; font-weight:800; color:#0f172a; line-height:1.1; }
.mc-vs   { font-size:0.75rem; color:#94a3b8; margin:4px 0 6px; }
.mc-delta { font-size:0.78rem; font-weight:600; }
.pos { color:#16a34a; } .neg { color:#dc2626; } .neu { color:#94a3b8; }

/* ── Secondary stats ── */
.sstat-row { display:flex; flex-wrap:wrap; gap:10px; margin:14px 0 0; }
.sstat { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 16px; }
.sstat-lbl { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; display:block; margin-bottom:3px; }
.sstat-val { font-size:0.86rem; font-weight:600; color:#0f172a; }

/* ── Section label ── */
.slbl {
  font-size:0.65rem; font-weight:700; text-transform:uppercase;
  letter-spacing:1.2px; color:#94a3b8; margin:24px 0 12px;
  display:flex; align-items:center; gap:8px;
}
.slbl::after { content:''; flex:1; height:1px; background:#f1f5f9; }

/* ── Fund meta ── */
.fund-name { font-size:1.25rem; font-weight:800; color:#0f172a; line-height:1.3; }
.fund-meta { font-size:0.8rem; color:#64748b; margin-top:4px; }
.info-row  { display:flex; flex-wrap:wrap; gap:22px; margin:12px 0 0; }
.ir-item   { display:flex; flex-direction:column; gap:1px; }
.ir-lbl    { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; }
.ir-val    { font-size:0.82rem; font-weight:600; color:#0f172a; }

/* ── Callout ── */
.co {
  background:#f0fdfd; border-left:3px solid #0d6e6e;
  border-radius:0 8px 8px 0; padding:10px 14px; margin:10px 0;
  font-size:0.83rem; color:#374151; line-height:1.55;
}

/* ── Validation ── */
.vb-y { background:#fffbeb; color:#92400e; border:1px solid #fde68a; border-radius:5px; padding:3px 10px; font-size:0.73rem; font-weight:600; }
.vb-g { background:#f0fdf4; color:#14532d; border:1px solid #bbf7d0; border-radius:5px; padding:3px 10px; font-size:0.73rem; font-weight:600; }
.vb-r { background:#fef2f2; color:#7f1d1d; border:1px solid #fecaca; border-radius:5px; padding:3px 10px; font-size:0.73rem; font-weight:600; }
.vc { border:1px solid #e2e8f0; border-radius:8px; padding:13px 15px; margin:7px 0; background:#fff; }
.vc-q { font-size:0.86rem; font-weight:600; color:#0f172a; margin-bottom:5px; }
.vc-r { font-size:0.81rem; color:#374151; }

/* ── Note ── */
.note { font-size:0.71rem; color:#94a3b8; line-height:1.5; margin-top:5px; }
.disc { font-size:0.69rem; color:#94a3b8; line-height:1.6; }

/* ── Compare ── */
.compare-filter { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px 16px; margin-bottom:14px; }
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
    rtl["date"] = pd.to_datetime(rtl["date"]).dt.normalize()

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
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    return df


# ── Helpers ────────────────────────────────────────────────────────────────────
def pct(v, d=1):
    if v is None or not isinstance(v, (int, float)) or np.isnan(v):
        return "—"
    return f"{v*100:.{d}f}%"

def inr(v):
    if v is None or not isinstance(v, (int, float)) or np.isnan(v):
        return "—"
    if abs(v) >= 1_00_000:
        return f"₹{v/1_00_000:.2f}L"
    return f"₹{v:,.0f}"

def safe_float(v):
    try:
        f = float(v)
        return f if not np.isnan(f) else None
    except Exception:
        return None

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

    def cagr(s):
        return (s.iloc[-1] / amount) ** (1 / years) - 1 if amount > 0 else np.nan

    def mdd(s):
        roll_max = s.cummax()
        return float(((s - roll_max) / roll_max).min())

    def ann_vol(s):
        return float(s.pct_change().dropna().std() * np.sqrt(252))

    def calmar(c, d):
        return c / abs(d) if d and d != 0 and not np.isnan(d) else np.nan

    bnh_c = cagr(df["bnh_s"]); v2a_c = cagr(df["v2a_s"])
    bnh_d = mdd(df["bnh_s"]);  v2a_d = mdd(df["v2a_s"])
    bnh_v = ann_vol(df["bnh_s"]); v2a_v = ann_vol(df["v2a_s"])

    # Regime activity — normalize dates before comparing to avoid tz mismatch
    try:
        d_min = pd.Timestamp(df["date"].min()).normalize()
        d_max = pd.Timestamp(df["date"].max()).normalize()
        rtl_n = rtl.copy()
        rtl_n["date"] = pd.to_datetime(rtl_n["date"]).dt.normalize()
        r = rtl_n[(rtl_n["date"] >= d_min) & (rtl_n["date"] <= d_max)]
        reg_pct = float(r["macro_active"].mean()) if len(r) > 0 else np.nan
    except Exception:
        reg_pct = np.nan

    # Beta (optional)
    bnh_beta = np.nan; v2a_beta = np.nan
    if nifty_ret_df is not None:
        try:
            nr = nifty_ret_df[(nifty_ret_df["date"] >= d_min) & (nifty_ret_df["date"] <= d_max)].copy()
            mb = pd.merge(df[["date","bnh_s"]], nr[["date","daily_return"]], on="date", how="inner")
            mv = pd.merge(df[["date","v2a_s"]], nr[["date","daily_return"]], on="date", how="inner")
            if len(mb) > 30:
                rb = mb["bnh_s"].pct_change().dropna()
                mk = mb["daily_return"].iloc[1:].reset_index(drop=True)
                vm = mk.var()
                if vm > 0:
                    bnh_beta = float(np.cov(rb, mk)[0,1] / vm)
                    rv = mv["v2a_s"].pct_change().dropna()
                    mk2 = mv["daily_return"].iloc[1:].reset_index(drop=True)
                    v2a_beta = float(np.cov(rv, mk2)[0,1] / vm)
        except Exception:
            pass

    return {
        "years":     years,
        "bnh_cagr":  bnh_c,    "v2a_cagr":  v2a_c,
        "bnh_dd":    bnh_d,    "v2a_dd":    v2a_d,
        "bnh_vol":   bnh_v,    "v2a_vol":   v2a_v,
        "bnh_score": bnh_c - abs(bnh_d)/2,
        "v2a_score": v2a_c - abs(v2a_d)/2,
        "bnh_calmar":calmar(bnh_c, bnh_d),
        "v2a_calmar":calmar(v2a_c, v2a_d),
        "bnh_beta":  bnh_beta, "v2a_beta":  v2a_beta,
        "final_bnh": float(df["bnh_s"].iloc[-1]),
        "final_v2a": float(df["v2a_s"].iloc[-1]),
        "reg_pct":   reg_pct,
    }

def val_badge(score, oos_elig):
    score = int(score) if pd.notna(score) else 0
    mx = 4 if oos_elig else 3
    if score >= mx:   return f'<span class="vb-g">✅ Validated ({score}/{mx})</span>'
    elif score >= 2:  return f'<span class="vb-y">⚠️ Partial ({score}/{mx})</span>'
    else:             return f'<span class="vb-r">❌ Low ({score}/{mx})</span>'


# ── Hero (slim) ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-left">
    <div><span class="hero-brand">NivesAI</span></div>
    <div class="hero-sub">LARF · Rule-based crash protection tested across 173 Indian mutual funds</div>
    <div class="hero-meta">Jan 2010 – Apr 2026 &nbsp;·&nbsp; AMFI NAV data &nbsp;·&nbsp; Historical simulation only, not investment advice</div>
  </div>
  <div class="hero-pill">Research Preview</div>
</div>
""", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────────────────────────────
master_df, crash_df, regime_tl = load_master()
curves_df = load_curves()
nifty_ret = load_nifty_returns()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Fund Analysis", "📋 Compare Funds"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single fund analysis
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    fund_options = {}
    for _, r in master_df.sort_values(["scheme_category","scheme_name"]).iterrows():
        fund_options[f"{r['scheme_name']}  ·  {r['scheme_category']}"] = str(r["scheme_code"])

    fc1, fc2, fc3, fc4 = st.columns([4, 1.5, 1.5, 0.9])
    with fc1:
        sel = st.selectbox("Fund", ["— choose a fund —"] + list(fund_options.keys()),
                           label_visibility="visible")
    with fc2:
        amount = st.number_input(
            "Investment (₹)", min_value=10_000, max_value=10_00_00_000,
            value=DEFAULT_AMT, step=10_000, format="%d",
            help="Initial investment amount",
        )
    with fc3:
        inv_date = st.date_input(
            "Start date",
            value=datetime.date(2010, 1, 4),
            min_value=datetime.date(2010, 1, 1),
            max_value=datetime.date(2026, 5, 31),
            help="All metrics computed from this date",
        )
    with fc4:
        st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
        go_btn = st.button("Analyse →", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if sel == "— choose a fund —" or not go_btn:
        st.markdown(
            '<div style="margin-top:32px;padding:44px 32px;text-align:center;color:#94a3b8;'
            'border:2px dashed #e2e8f0;border-radius:14px;font-size:0.88rem;background:#fafafa">'
            '<div style="font-size:2rem;margin-bottom:10px">📊</div>'
            '<div style="font-weight:600;color:#64748b;margin-bottom:4px">Select a fund and click Analyse</div>'
            '<div style="font-size:0.78rem">Choose any of the 173 funds — equity, debt, hybrid, or sectoral</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    # ── Fund data ──────────────────────────────────────────────────────────────
    code       = fund_options[sel]
    fr         = master_df[master_df["scheme_code"] == code].iloc[0]
    raw_curves = curves_df[curves_df["scheme_code"] == code].sort_values("date").reset_index(drop=True)

    sim_start = pd.Timestamp(fr.get("sim_start_date","2010-01-04"))
    sim_end   = pd.Timestamp(fr.get("sim_end_date",  "2026-04-08"))
    inv_ts    = pd.Timestamp(inv_date).normalize()
    if inv_ts < sim_start: inv_ts = sim_start
    if inv_ts >= sim_end:  inv_ts = sim_start

    sc = prepare_curves(raw_curves, amount, inv_ts)
    if len(sc) == 0:
        st.error("No data for this fund and date range.")
        st.stop()

    m = compute_metrics(sc, amount, regime_tl, nifty_ret)
    if m is None:
        st.error("Not enough data to compute metrics.")
        st.stop()

    is_custom = inv_ts > sim_start
    date_from = inv_ts.strftime("%d %b %Y")
    date_to   = sim_end.strftime("%d %b %Y")
    yrs_str   = f"{m['years']:.1f} yrs"

    # ── Impact banner ──────────────────────────────────────────────────────────
    dd_saved_pp = (abs(m["bnh_dd"]) - abs(m["v2a_dd"])) * 100  # positive = good
    dd_bnh_str  = f"{abs(m['bnh_dd'])*100:.1f}%"
    dd_v2a_str  = f"{abs(m['v2a_dd'])*100:.1f}%"
    val_bnh     = inr(m["final_bnh"])
    val_v2a     = inr(m["final_v2a"])

    if dd_saved_pp > 0.5:
        headline = (
            f"Over {yrs_str}, the overlay cut the worst loss from "
            f"<span class='hl-bad'>{dd_bnh_str}</span> to "
            f"<span class='hl-good'>{dd_v2a_str}</span> "
            f"— that's <span class='hl-good'>{dd_saved_pp:.1f} percentage points</span> less damage."
        )
    else:
        headline = (
            f"Over {yrs_str}, worst loss was <span class='hl-bad'>{dd_bnh_str}</span> "
            f"(holding) vs <span class='hl-good'>{dd_v2a_str}</span> (overlay)."
        )

    val_diff = m["final_v2a"] - m["final_bnh"]
    if val_diff > 0:
        val_line = f"₹{amount/1000:.0f}K grew to <span class='hl-white'>{val_v2a}</span> with overlay vs {val_bnh} without."
    else:
        val_line = f"₹{amount/1000:.0f}K grew to {val_bnh} (holding) and {val_v2a} (overlay)."

    st.markdown(
        f'<div class="impact">'
        f'<div class="impact-headline">{headline}</div>'
        f'<div class="impact-sub">'
        f'{val_line} &nbsp;·&nbsp; {fr["scheme_name"]} &nbsp;·&nbsp; {date_from} → {date_to}'
        f'{"&nbsp; · Your chosen start date" if is_custom else ""}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Fund meta row ──────────────────────────────────────────────────────────
    hc1, hc2 = st.columns([7, 2.5])
    with hc1:
        cat  = fr.get("scheme_category","")
        role = fr.get("final_role","")
        conf = str(fr.get("classification_confidence","")).upper()
        conf_map = {"HIGH":"Strong fit","MEDIUM":"Moderate fit","LOW":"Mixed signals"}
        amc_name = fr.get("amc","")
        role_str = role + (f" · {conf_map.get(conf,'')}" if role and conf else "")
        meta = " · ".join(p for p in [amc_name, cat, role_str] if p)
        st.markdown(f'<div class="fund-meta">{meta}</div>', unsafe_allow_html=True)
    with hc2:
        oos_e = bool(fr.get("oos_eligible", True))
        vs    = fr.get("validation_score", 0)
        st.markdown(val_badge(vs, oos_e), unsafe_allow_html=True)

    if ROLE_DESC.get(role,""):
        role_txt = ROLE_DESC[role]
        low_note = " Confidence is mixed — treat the role as directional." if conf == "LOW" else ""
        st.markdown(f'<div class="co"><strong>{role}:</strong> {role_txt}{low_note}</div>',
                    unsafe_allow_html=True)

    num_sells = int(fr.get("v2a_num_sells", 0))
    reg_str   = f"{m['reg_pct']*100:.0f}% of the period" if pd.notna(m.get("reg_pct")) and not np.isnan(m["reg_pct"]) else "—"
    st.markdown(
        f'<div class="info-row">'
        f'<div class="ir-item"><span class="ir-lbl">Period shown</span><span class="ir-val">{date_from} → {date_to} ({yrs_str})</span></div>'
        f'<div class="ir-item"><span class="ir-lbl">Rule-based trims (full sim)</span><span class="ir-val">{num_sells} sells over 16 yrs</span></div>'
        f'<div class="ir-item"><span class="ir-lbl">Days strategy was active</span><span class="ir-val">{reg_str}</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Metric cards ──────────────────────────────────────────────────────────
    period_lbl = f"from {date_from}" if is_custom else "2010–2026"
    st.markdown(f'<div class="slbl">Key Numbers · {period_lbl}</div>', unsafe_allow_html=True)

    edge_cagr = m["v2a_cagr"] - m["bnh_cagr"]
    edge_dd   = m["v2a_dd"]   - m["bnh_dd"]   # positive = shallower = good
    edge_vol  = m["v2a_vol"]  - m["bnh_vol"]  # negative = smoother = good

    r_win  = edge_cagr > 0
    dd_win = edge_dd   > 0
    vl_win = edge_vol  < 0
    v_win  = m["final_v2a"] >= m["final_bnh"]

    def delta_tag(val, cls):
        sign = "+" if val > 0 else ""
        return f'<div class="mc-delta {cls}">{sign}{val*100:.2f}% vs holding</div>'

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="mc {'win' if r_win else 'flat'}">
          <div class="mc-lbl">Annual Return (CAGR)</div>
          <div class="mc-big">{pct(m['v2a_cagr'],2)}</div>
          <div class="mc-vs">holding: {pct(m['bnh_cagr'],2)}</div>
          <div class="mc-delta {'pos' if r_win else 'neg'}">{"+" if r_win else ""}{edge_cagr*100:.2f}% vs holding</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        dd_delta = abs(m['bnh_dd'])*100 - abs(m['v2a_dd'])*100
        st.markdown(f"""
        <div class="mc {'win' if dd_win else 'flat'}">
          <div class="mc-lbl">Worst Drawdown</div>
          <div class="mc-big">−{abs(m['v2a_dd'])*100:.1f}%</div>
          <div class="mc-vs">holding: −{abs(m['bnh_dd'])*100:.1f}%</div>
          <div class="mc-delta {'pos' if dd_win else 'neg'}">{"" if dd_win else "−"}{abs(dd_delta):.1f} pp {"shallower ✓" if dd_win else "deeper"}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        vl_delta = abs(m['bnh_vol'])*100 - abs(m['v2a_vol'])*100
        st.markdown(f"""
        <div class="mc {'win' if vl_win else 'flat'}">
          <div class="mc-lbl">Annualised Volatility</div>
          <div class="mc-big">{pct(m['v2a_vol'],1)}</div>
          <div class="mc-vs">holding: {pct(m['bnh_vol'],1)}</div>
          <div class="mc-delta {'pos' if vl_win else 'neg'}">{"" if vl_win else "−"}{abs(vl_delta):.1f} pp {"smoother ✓" if vl_win else "rougher"}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        ev = m["final_v2a"] - m["final_bnh"]
        st.markdown(f"""
        <div class="mc {'win' if v_win else 'flat'}">
          <div class="mc-lbl">Portfolio Value · {period_lbl}</div>
          <div class="mc-big" style="font-size:1.65rem">{inr(m['final_v2a'])}</div>
          <div class="mc-vs">holding: {inr(m['final_bnh'])}</div>
          <div class="mc-delta {'pos' if v_win else 'neg'}">{'+' if ev>=0 else ''}{inr(ev)} difference</div>
        </div>""", unsafe_allow_html=True)

    # Secondary stats
    def sstat_html(label, bnh_v, ov_v, fmt_fn, higher_is_better=True, tooltip=""):
        bv, ov = fmt_fn(bnh_v), fmt_fn(ov_v)
        arrow = ""
        try:
            if bnh_v is not None and ov_v is not None and not np.isnan(bnh_v) and not np.isnan(ov_v):
                d = ov_v - bnh_v
                better = (d > 0 and higher_is_better) or (d < 0 and not higher_is_better)
                arrow = f' <span class="{"pos" if better else "neg"}" style="font-size:0.7rem">{"↑" if better else "↓"}</span>'
        except Exception:
            pass
        tip = f' title="{tooltip}"' if tooltip else ""
        return (f'<div class="sstat"{tip}>'
                f'<span class="sstat-lbl">{label}</span>'
                f'<span class="sstat-val">{bv} → <strong style="color:#0d6e6e">{ov}</strong>{arrow}</span>'
                f'</div>')

    fmt2 = lambda v: f"{v:.2f}" if v is not None and not np.isnan(v) else "—"
    fmt3 = lambda v: f"{v:.3f}" if v is not None and not np.isnan(v) else "—"

    ss = [
        sstat_html("Calmar Ratio",
                   safe_float(m["bnh_calmar"]), safe_float(m["v2a_calmar"]),
                   fmt2, higher_is_better=True,
                   tooltip="Return ÷ worst loss. Higher = better risk-adjusted return."),
        sstat_html("Efficiency Score",
                   safe_float(m["bnh_score"]), safe_float(m["v2a_score"]),
                   fmt3, higher_is_better=True,
                   tooltip="CAGR minus half the max drawdown. A single number that penalises big drops."),
    ]
    if pd.notna(m["bnh_beta"]):
        ss.append(sstat_html("Beta vs Nifty 50",
                             safe_float(m["bnh_beta"]), safe_float(m["v2a_beta"]),
                             fmt2, higher_is_better=False,
                             tooltip="How much the fund moves per 1% move in Nifty 50. Overlay typically reduces this."))

    st.markdown(f'<div class="sstat-row">{"".join(ss)}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="note">'
        '<strong>Calmar:</strong> return ÷ worst loss — higher is better. &nbsp;'
        '<strong>Efficiency Score:</strong> single number that rewards return and penalises big drops — higher is better.'
        + (' &nbsp;<strong>Beta:</strong> moves per 1% Nifty move (overlay reduces market sensitivity).' if pd.notna(m["bnh_beta"]) else '')
        + '</div>',
        unsafe_allow_html=True,
    )

    # 2024-26 sideways callout
    crash_sw = crash_df[(crash_df["scheme_code"] == code) &
                        crash_df["period_name"].str.contains("Sideways", na=False)]
    if len(crash_sw) > 0:
        sw = crash_sw.iloc[0]
        if pd.notna(sw.get("v2a_beats_bnh")):
            bf = abs(sw["bnh_max_dd"])*100 if pd.notna(sw["bnh_max_dd"]) else None
            vf = abs(sw["v2a_max_dd"])*100 if pd.notna(sw["v2a_max_dd"]) else None
            fund_r = (f"This fund: {bf:.1f}% drop without overlay vs {vf:.1f}% with it. " if bf and vf else "")
            icon = "📈" if sw["v2a_beats_bnh"] else "📉"
            st.markdown(
                f'<div class="co" style="margin-top:14px">'
                f'{icon} <strong>Recent sideways market (2024–26):</strong> {fund_r}'
                f'Across all 173 funds, overlay outperformed simple holding in <strong>152 of 173 (88%)</strong> of cases.</div>',
                unsafe_allow_html=True,
            )

    # ── Chart ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="slbl">Portfolio Growth Over Time</div>', unsafe_allow_html=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.82, 0.18], vertical_spacing=0.04)

    dates = sc["ds"].tolist()
    fig.add_trace(go.Scatter(x=dates, y=sc["bnh_s"].tolist(), mode="lines",
        name="Simple holding", line=dict(color="#94a3b8", width=1.8),
        hovertemplate="<b>Simple holding</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=sc["v2a_s"].tolist(), mode="lines",
        name="With overlay", line=dict(color=TEAL, width=2.5),
        hovertemplate="<b>With overlay</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>"), row=1, col=1)

    rg = regime_tl[(regime_tl["date"] >= sc["date"].min()) &
                   (regime_tl["date"] <= sc["date"].max())].copy()
    fig.add_trace(go.Bar(
        x=rg["date"].dt.strftime("%Y-%m-%d").tolist(),
        y=rg["macro_active"].astype(int).tolist(),
        marker_color=[ACTIVE_BAR if v else IDLE_BAR for v in rg["macro_active"]],
        name="Strategy active", showlegend=True,
        hovertemplate="%{x}<br>Overlay active: %{y}<extra></extra>"), row=2, col=1)

    shapes = [dict(type="rect", xref="x", yref="paper", x0=s, x1=e,
                   y0=0.22, y1=1.0, fillcolor=CRASH_COLOR, line_width=0, layer="below")
              for _, s, e in CRASH_PERIODS]

    fig.update_layout(shapes=shapes, height=520,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="white", plot_bgcolor="#fafeff",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=11), bgcolor="rgba(255,255,255,0)"),
        hovermode="x unified", font=dict(family="Inter, sans-serif"))
    fig.update_yaxes(tickprefix="₹", tickformat=",.0f", gridcolor="#f1f5f9", row=1, col=1)
    fig.update_yaxes(tickvals=[0,1], ticktext=["","Active"], gridcolor="#f1f5f9", row=2, col=1)
    fig.update_xaxes(type="date", tickformat="%b '%y", gridcolor="#f1f5f9")

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<div class="note">🔴 Shaded = major crashes (2011, 2015–16, 2018–19, 2020 COVID). '
        'Bottom bar = days the strategy was actively watching for risk signals.</div>',
        unsafe_allow_html=True,
    )

    # ── Crash table ────────────────────────────────────────────────────────────
    st.markdown('<div class="slbl">How Did It Hold Up During Each Crash?</div>', unsafe_allow_html=True)

    crash_main = crash_df[(crash_df["scheme_code"] == code) &
                          ~crash_df["period_name"].str.contains("Sideways", na=False)]
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
    st.markdown('<div class="note">"pp" = percentage points. Shallower = less portfolio damage.</div>',
                unsafe_allow_html=True)

    # ── Validation ─────────────────────────────────────────────────────────────
    with st.expander("🔍  How reliable are these results? (4 independent checks)", expanded=False):
        st.markdown("We ran four independent checks to test whether the overlay's edge is real or just a lucky fit to past data.")

        wf_p = bool(fr.get("wf_pass",False)); wf_r = fr.get("wf_pass_rate")
        wf_n = fr.get("wf_windows_pass"); wf_t = fr.get("wf_windows_total")
        if pd.notna(wf_r):
            wf_d = (f"{'✅' if wf_p else '❌'} Beat simple holding in **{int(wf_n or 0)} of {int(wf_t or 0)} windows** ({(wf_r or 0)*100:.0f}%). "
                    + ("Consistent across different time periods." if wf_p else "Performance varied — depends heavily on when you invested."))
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
            oos_d = "❌ Did not outperform on fresh 2023–2026 data. Strategy may be over-fitted to older patterns."
        st.markdown(f'<div class="vc"><div class="vc-q">Check 2 — Would it hold up on data it had never seen?</div>'
                    f'<div class="vc-r">{oos_d}</div></div>', unsafe_allow_html=True)

        mc_p = bool(fr.get("mc_pass",False)); mc_pct = fr.get("real_percentile")
        if pd.notna(mc_pct):
            mc_d = (f"{'✅' if mc_p else '❌'} Real result ranked in the **{mc_pct:.1f}th percentile** out of 1,000 random simulations. "
                    + (f"Only ~{100-mc_pct:.0f}% of random runs matched it — very unlikely to be luck." if mc_p
                       else "Random simulations often matched it — the edge may be partly coincidence."))
        else:
            mc_d = "Monte Carlo data not available."
        st.markdown(f'<div class="vc"><div class="vc-q">Check 3 — Could this just be luck?</div>'
                    f'<div class="vc-r">{mc_d}</div></div>', unsafe_allow_html=True)

        st_p = bool(fr.get("stability_pass",False)); st_r = fr.get("stability_pass_rate"); cliff = bool(fr.get("cliff_detected",False))
        if pd.notna(st_r):
            st_d = (f"{'✅' if st_p else '❌'} Held up in **{st_r*100:.0f}%** of 20 parameter variations. "
                    + ("Robust — small rule changes don't break it." if st_p else "Sensitive — small changes affect outcomes.")
                    + (" ⚠️ One threshold caused a larger-than-expected shift." if cliff else ""))
        else:
            st_d = "Stability data not available."
        st.markdown(f'<div class="vc"><div class="vc-q">Check 4 — Does it break if the rules are nudged slightly?</div>'
                    f'<div class="vc-r">{st_d}</div></div>', unsafe_allow_html=True)

        vs_int = int(fr.get("validation_score",0)) if pd.notna(fr.get("validation_score")) else 0
        mx2 = 4 if oos_e2 else 3
        if vs_int >= mx2:     st.success(f"✅ Passed all {mx2} checks. High confidence in these results.")
        elif vs_int >= 2:     st.warning(f"Passed {vs_int}/{mx2} checks. Crash protection evidence is solid; return figures are directional.")
        else:                 st.error(f"Only {vs_int}/{mx2} checks passed. Treat results with caution.")

    # Footer
    st.markdown("---")
    st.markdown(
        '<div class="disc" style="text-align:center">'
        "NivesAI · LARF v2a · AMFI NAV data · 173 funds · Jan 2010–Apr 2026<br>"
        "<strong>All results are retrospective research simulations. Not investment advice. NivesAI is not a SEBI-registered advisor.</strong>"
        "</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Compare Funds
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        '<div style="font-size:0.88rem;color:#64748b;margin-bottom:16px">'
        'Filter by category or AMC to compare how the overlay performed across multiple funds. '
        'Uses full simulation results (Jan 2010–Apr 2026).</div>',
        unsafe_allow_html=True,
    )

    # Determine which columns are available for comparison
    # Try common names; fall back gracefully
    def try_col(df, *candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    col_v2a_cagr  = try_col(master_df, "v2a_cagr",  "overlay_cagr")
    col_bnh_cagr  = try_col(master_df, "bnh_cagr",  "hold_cagr")
    col_v2a_dd    = try_col(master_df, "v2a_max_dd","overlay_max_dd","v2a_mdd")
    col_bnh_dd    = try_col(master_df, "bnh_max_dd","hold_max_dd",  "bnh_mdd")
    col_v2a_score = try_col(master_df, "v2a_score")
    col_bnh_score = try_col(master_df, "bnh_score")
    has_metrics   = all(x is not None for x in [col_v2a_cagr, col_bnh_cagr, col_v2a_dd, col_bnh_dd])

    # Filter controls
    st.markdown('<div class="compare-filter">', unsafe_allow_html=True)
    cf1, cf2, cf3 = st.columns([2, 2, 1])
    with cf1:
        cats = ["All categories"] + sorted(master_df["scheme_category"].dropna().unique().tolist())
        sel_cat = st.selectbox("Filter by Category", cats, key="compare_cat")
    with cf2:
        amcs = ["All AMCs"] + sorted(master_df["amc"].dropna().unique().tolist())
        sel_amc = st.selectbox("Filter by AMC", amcs, key="compare_amc")
    with cf3:
        sort_opts = ["Overlay Return ↓", "DD Saved ↓", "Validation Score ↓"]
        sort_by = st.selectbox("Sort by", sort_opts, key="compare_sort")
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters
    cdf = master_df.copy()
    if sel_cat != "All categories":
        cdf = cdf[cdf["scheme_category"] == sel_cat]
    if sel_amc != "All AMCs":
        cdf = cdf[cdf["amc"] == sel_amc]

    if len(cdf) == 0:
        st.warning("No funds match the selected filters.")
        st.stop()

    # Build comparison table
    rows = []
    for _, r in cdf.iterrows():
        row = {
            "Fund": r.get("scheme_name","—"),
            "Category": r.get("scheme_category","—"),
            "AMC": r.get("amc","—"),
            "Role": r.get("final_role","—"),
        }
        if has_metrics:
            vc = safe_float(r.get(col_v2a_cagr)) ; bc = safe_float(r.get(col_bnh_cagr))
            vd = safe_float(r.get(col_v2a_dd))  ; bd = safe_float(r.get(col_bnh_dd))
            row["Return · Overlay"]  = f"{vc*100:.1f}%" if vc is not None else "—"
            row["Return · Holding"]  = f"{bc*100:.1f}%" if bc is not None else "—"
            row["Return Δ"]          = f"+{(vc-bc)*100:.2f}%" if (vc and bc) else "—"
            row["MaxDD · Overlay"]   = f"−{abs(vd)*100:.1f}%" if vd is not None else "—"
            row["MaxDD · Holding"]   = f"−{abs(bd)*100:.1f}%" if bd is not None else "—"
            row["DD Saved (pp)"]     = round((abs(bd)-abs(vd))*100, 1) if (vd and bd) else None
            # Sort helpers
            row["_vc"] = vc if vc else -99
            row["_dd_saved"] = (abs(bd)-abs(vd))*100 if (vd and bd) else -99
        vs = safe_float(r.get("validation_score"))
        row["Validation"] = f"{int(vs)}" if vs is not None else "—"
        row["_vs"] = vs if vs is not None else -99
        rows.append(row)

    compare_df = pd.DataFrame(rows)

    # Sort
    sort_col = {"Overlay Return ↓": "_vc", "DD Saved ↓": "_dd_saved", "Validation Score ↓": "_vs"}.get(sort_by, "_vc")
    if sort_col in compare_df.columns:
        compare_df = compare_df.sort_values(sort_col, ascending=False)

    # Drop internal sort columns
    display_cols = [c for c in compare_df.columns if not c.startswith("_")]
    compare_df = compare_df[display_cols].reset_index(drop=True)

    st.markdown(f'<div class="note" style="margin-bottom:8px">Showing <strong>{len(compare_df)}</strong> funds</div>',
                unsafe_allow_html=True)
    st.dataframe(compare_df, use_container_width=True, hide_index=True)

    # Chart — only if metrics available and not too many funds
    if has_metrics and len(compare_df) <= 60 and "Return Δ" in compare_df.columns:
        st.markdown('<div class="slbl">Return Delta: Overlay vs Simple Holding (full sim)</div>', unsafe_allow_html=True)

        chart_df = compare_df[compare_df["Return Δ"] != "—"].copy()
        chart_df["delta_num"] = chart_df["Return Δ"].str.replace("%","").str.replace("+","").astype(float)
        chart_df = chart_df.sort_values("delta_num", ascending=True).tail(40)  # top 40 for readability

        colors = ["#0d6e6e" if v >= 0 else "#ef4444" for v in chart_df["delta_num"]]
        fig2 = go.Figure(go.Bar(
            x=chart_df["delta_num"],
            y=chart_df["Fund"].str[:45],  # truncate long names
            orientation="h",
            marker_color=colors,
            text=[f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%" for v in chart_df["delta_num"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Return delta: %{x:.2f}%<extra></extra>",
        ))
        fig2.update_layout(
            height=max(300, len(chart_df) * 22 + 60),
            margin=dict(l=0, r=60, t=10, b=30),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(title="Return delta (pp)", gridcolor="#f1f5f9", zeroline=True,
                       zerolinecolor="#94a3b8", zerolinewidth=1.5),
            yaxis=dict(tickfont=dict(size=11)),
            font=dict(family="Inter, sans-serif", size=11),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="note">Positive (teal) = overlay delivered higher annual return than simple holding. '
                    'Based on full Jan 2010–Apr 2026 simulation.</div>', unsafe_allow_html=True)

    if not has_metrics:
        st.info("Detailed metrics (CAGR, MaxDD) not found in results file — showing metadata only. "
                "Check that larf_regime_results_v2.csv contains v2a_cagr and bnh_cagr columns.")

    st.markdown("---")
    st.markdown('<div class="disc">NivesAI · LARF v2a · All results are historical simulations. Not investment advice.</div>',
                unsafe_allow_html=True)