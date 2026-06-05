"""
NivesAI — LARF Overlay Research Tool
v1.6 — dark theme, native metrics, billboard impact
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
TEAL        = "#14b8a6"
TEAL_DARK   = "#0d9488"
BNH_COLOR   = "#64748b"
CRASH_COLOR = "rgba(239,68,68,0.15)"
ACTIVE_BAR  = "#14b8a6"
IDLE_BAR    = "#1e293b"
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*, *::before, *::after { font-family: 'Inter', sans-serif !important; }

[data-testid="stSidebar"]      { display: none !important; }
[data-testid="collapsedControl"]{ display: none !important; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; max-width: 1180px; }

/* ── Brand bar ── */
.brand-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 0 18px; border-bottom: 1px solid #1e293b; margin-bottom: 18px;
}
.brand-name { font-size: 1.5rem; font-weight: 900; color: #14b8a6; letter-spacing: -0.5px; }
.brand-tag  { font-size: 0.78rem; color: #64748b; margin-top: 2px; }
.brand-pill {
  font-size: 0.68rem; color: #475569; border: 1px solid #334155;
  border-radius: 20px; padding: 4px 12px;
}

/* ── Impact billboard ── */
.billboard {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 14px;
  padding: 28px 32px 24px;
  margin: 6px 0 22px;
}
.bb-eyebrow { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
              letter-spacing: 1.2px; color: #14b8a6; margin-bottom: 14px; }
.bb-row { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; margin-bottom: 12px; }
.bb-block { text-align: center; }
.bb-label { font-size: 0.68rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.bb-num-bad  { font-size: 3rem; font-weight: 900; color: #f87171; line-height: 1; }
.bb-num-good { font-size: 3rem; font-weight: 900; color: #34d399; line-height: 1; }
.bb-num-neu  { font-size: 3rem; font-weight: 900; color: #e2e8f0; line-height: 1; }
.bb-arrow { font-size: 2rem; color: #475569; padding: 0 4px; }
.bb-saved { font-size: 1rem; font-weight: 700; color: #34d399; }
.bb-sub { font-size: 0.82rem; color: #64748b; border-top: 1px solid #334155;
          padding-top: 12px; margin-top: 4px; line-height: 1.6; }
.bb-sub strong { color: #94a3b8; }

/* ── Section label ── */
.slbl {
  font-size: 0.63rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.3px; color: #475569; margin: 24px 0 12px;
  display: flex; align-items: center; gap: 8px;
}
.slbl::after { content: ''; flex: 1; height: 1px; background: #1e293b; }

/* ── Info row ── */
.info-row { display: flex; flex-wrap: wrap; gap: 24px; margin: 10px 0 0; }
.ir-item  { display: flex; flex-direction: column; gap: 2px; }
.ir-lbl   { font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; }
.ir-val   { font-size: 0.82rem; font-weight: 600; color: #cbd5e1; }

/* ── Callout ── */
.co {
  background: #1e293b; border-left: 3px solid #14b8a6;
  border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 10px 0;
  font-size: 0.83rem; color: #94a3b8; line-height: 1.55;
}

/* ── Validation badges ── */
.vb-y { background: #422006; color: #fbbf24; border: 1px solid #78350f; border-radius: 5px; padding: 3px 10px; font-size: 0.72rem; font-weight: 600; }
.vb-g { background: #052e16; color: #4ade80; border: 1px solid #14532d; border-radius: 5px; padding: 3px 10px; font-size: 0.72rem; font-weight: 600; }
.vb-r { background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; border-radius: 5px; padding: 3px 10px; font-size: 0.72rem; font-weight: 600; }

/* ── Validation checks ── */
.vc { border: 1px solid #1e293b; border-radius: 8px; padding: 12px 15px; margin: 7px 0; background: #1e293b; }
.vc-q { font-size: 0.86rem; font-weight: 600; color: #e2e8f0; margin-bottom: 5px; }
.vc-r { font-size: 0.81rem; color: #94a3b8; }

/* ── Secondary stats ── */
.sstat-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 14px 0 0; }
.sstat { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 10px 16px; }
.sstat-lbl { font-size: 0.59rem; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; display: block; margin-bottom: 3px; }
.sstat-val { font-size: 0.85rem; font-weight: 600; color: #cbd5e1; }

/* ── Note ── */
.note { font-size: 0.7rem; color: #475569; line-height: 1.5; margin-top: 5px; }
.disc { font-size: 0.68rem; color: #334155; line-height: 1.6; }

/* ── Compare ── */
.compare-filter { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px 16px; margin-bottom: 14px; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading …")
def load_master():
    res   = pd.read_csv(f"{DATA_DIR}/larf_regime_results_v2.csv")
    res["scheme_code"] = res["scheme_code"].astype(str)
    val   = pd.read_csv(f"{DATA_DIR}/larf_validation_summary_v1.csv")
    val["scheme_code"] = val["scheme_code"].astype(str)
    sch   = pd.read_csv(f"{DATA_DIR}/scheme_master_v2_FROZEN.csv")
    sch["scheme_code"] = sch["scheme_code"].astype(str)
    beh   = pd.read_csv(f"{DATA_DIR}/behaviour_classification_app.csv")
    beh["scheme_code"] = beh["scheme_code"].astype(str)
    beh["summary_text"] = beh["summary_text"].fillna("")
    crash = pd.read_csv(f"{DATA_DIR}/crash_periods_app.csv")
    crash["scheme_code"] = crash["scheme_code"].astype(str)
    rtl   = pd.read_csv(f"{DATA_DIR}/regime_timeline.csv")
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
    try:
        f = float(v)
        if np.isnan(f): return "—"
        return f"{f*100:.{d}f}%"
    except: return "—"

def inr(v):
    try:
        f = float(v)
        if np.isnan(f): return "—"
        if abs(f) >= 1_00_000: return f"₹{f/1_00_000:.2f}L"
        return f"₹{f:,.0f}"
    except: return "—"

def safe_float(v):
    try:
        f = float(v)
        return None if np.isnan(f) else f
    except: return None

def prepare_curves(fund_curves, amount, start_ts):
    df = fund_curves[fund_curves["date"] >= start_ts].sort_values("date").reset_index(drop=True)
    if len(df) < 5: return pd.DataFrame()
    scale = amount / df["bnh_value"].iloc[0]
    df = df.copy()
    df["bnh_s"] = (df["bnh_value"] * scale).round(0)
    df["v2a_s"] = (df["v2a_value"] * scale).round(0)
    df["ds"]    = df["date"].dt.strftime("%Y-%m-%d")
    return df

def compute_metrics(df, amount, rtl, nifty_ret_df=None):
    if len(df) < 10: return None
    years = max((df["date"].iloc[-1] - df["date"].iloc[0]).days / 365.25, 0.1)

    def cagr(s): return (s.iloc[-1] / amount) ** (1/years) - 1 if amount > 0 else np.nan
    def mdd(s):
        rm = s.cummax(); return float(((s-rm)/rm).min())
    def ann_vol(s): return float(s.pct_change().dropna().std() * np.sqrt(252))
    def calmar(c,d): return c/abs(d) if d and d!=0 else np.nan

    bc = cagr(df["bnh_s"]); vc = cagr(df["v2a_s"])
    bd = mdd(df["bnh_s"]);  vd = mdd(df["v2a_s"])
    bv = ann_vol(df["bnh_s"]); vv = ann_vol(df["v2a_s"])

    try:
        d_min = pd.Timestamp(df["date"].min()).normalize()
        d_max = pd.Timestamp(df["date"].max()).normalize()
        r = rtl[(rtl["date"] >= d_min) & (rtl["date"] <= d_max)]
        reg_pct = float(r["macro_active"].mean()) if len(r) > 0 else np.nan
    except: reg_pct = np.nan

    bnh_beta = np.nan; v2a_beta = np.nan
    if nifty_ret_df is not None:
        try:
            nr = nifty_ret_df[(nifty_ret_df["date"] >= d_min) & (nifty_ret_df["date"] <= d_max)]
            mb = pd.merge(df[["date","bnh_s"]], nr[["date","daily_return"]], on="date", how="inner")
            if len(mb) > 30:
                rb = mb["bnh_s"].pct_change().dropna()
                mk = mb["daily_return"].iloc[1:].reset_index(drop=True)
                vm = mk.var()
                if vm > 0:
                    bnh_beta = float(np.cov(rb, mk)[0,1] / vm)
                    mv = pd.merge(df[["date","v2a_s"]], nr[["date","daily_return"]], on="date", how="inner")
                    rv = mv["v2a_s"].pct_change().dropna()
                    mk2 = mv["daily_return"].iloc[1:].reset_index(drop=True)
                    v2a_beta = float(np.cov(rv, mk2)[0,1] / vm)
        except: pass

    return {
        "years": years,
        "bnh_cagr": bc, "v2a_cagr": vc,
        "bnh_dd":   bd, "v2a_dd":   vd,
        "bnh_vol":  bv, "v2a_vol":  vv,
        "bnh_score": bc - abs(bd)/2, "v2a_score": vc - abs(vd)/2,
        "bnh_calmar": calmar(bc,bd),  "v2a_calmar": calmar(vc,vd),
        "bnh_beta": bnh_beta, "v2a_beta": v2a_beta,
        "final_bnh": float(df["bnh_s"].iloc[-1]),
        "final_v2a": float(df["v2a_s"].iloc[-1]),
        "reg_pct": reg_pct,
    }

def val_badge(score, oos_elig):
    score = int(score) if pd.notna(score) else 0
    mx = 4 if oos_elig else 3
    if score >= mx:  return f'<span class="vb-g">✅ Validated ({score}/{mx})</span>'
    elif score >= 2: return f'<span class="vb-y">⚠️ Partial ({score}/{mx})</span>'
    else:            return f'<span class="vb-r">❌ Low ({score}/{mx})</span>'


# ── Brand bar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-bar">
  <div>
    <div class="brand-name">NivesAI &nbsp;<span style="color:#334155;font-weight:400;font-size:1rem">·</span>&nbsp; LARF</div>
    <div class="brand-tag">Rule-based crash protection tested across 173 Indian mutual funds &nbsp;·&nbsp; Jan 2010–Apr 2026</div>
  </div>
  <div class="brand-pill">Historical simulation · Not investment advice</div>
</div>
""", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────────────────────────────
master_df, crash_df, regime_tl = load_master()
curves_df = load_curves()
nifty_ret = load_nifty_returns()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊  Fund Analysis", "📋  Compare Funds"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
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
        amount = st.number_input("Investment (₹)", min_value=10_000, max_value=10_00_00_000,
                                 value=DEFAULT_AMT, step=10_000, format="%d",
                                 help="Initial investment amount in ₹")
    with fc3:
        inv_date = st.date_input("Start date",
                                 value=datetime.date(2010, 1, 4),
                                 min_value=datetime.date(2010, 1, 1),
                                 max_value=datetime.date(2026, 5, 31),
                                 help="All metrics computed from this date")
    with fc4:
        st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
        go_btn = st.button("Analyse →", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if sel == "— choose a fund —" or not go_btn:
        st.markdown(
            '<div style="margin-top:40px;padding:52px 32px;text-align:center;'
            'border:2px dashed #1e293b;border-radius:14px;background:#0a0f1a">'
            '<div style="font-size:2.5rem;margin-bottom:12px">📊</div>'
            '<div style="font-weight:700;color:#94a3b8;font-size:1rem;margin-bottom:6px">Select a fund and click Analyse</div>'
            '<div style="font-size:0.8rem;color:#475569">Choose from 173 Indian mutual funds — equity, debt, hybrid, sectoral</div>'
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
        st.error("No data for this fund and date range."); st.stop()
    m = compute_metrics(sc, amount, regime_tl, nifty_ret)
    if m is None:
        st.error("Not enough data to compute metrics."); st.stop()

    is_custom = inv_ts > sim_start
    date_from = inv_ts.strftime("%d %b %Y")
    date_to   = sim_end.strftime("%d %b %Y")
    yrs_str   = f"{m['years']:.1f} yrs"

    # ── Billboard ─────────────────────────────────────────────────────────────
    dd_saved_pp = (abs(m["bnh_dd"]) - abs(m["v2a_dd"])) * 100
    val_diff    = m["final_v2a"] - m["final_bnh"]

    bnh_dd_pct = f"−{abs(m['bnh_dd'])*100:.1f}%"
    v2a_dd_pct = f"−{abs(m['v2a_dd'])*100:.1f}%"

    if dd_saved_pp >= 0.5:
        saved_line = f'<div class="bb-saved">▲ {dd_saved_pp:.1f} percentage points less damage</div>'
        dd_good_class = "bb-num-good"
    else:
        saved_line = '<div class="bb-saved" style="color:#f87171">▼ Overlay was deeper</div>'
        dd_good_class = "bb-num-bad"

    val_line  = f"₹{amount/1000:.0f}K → <strong style='color:#e2e8f0'>{inr(m['final_v2a'])}</strong> with overlay &nbsp;·&nbsp; {inr(m['final_bnh'])} without"
    meta_line = f"{fr['scheme_name']} &nbsp;·&nbsp; {date_from} → {date_to}"
    if is_custom: meta_line += " &nbsp;·&nbsp; <em>your chosen start date</em>"

    st.markdown(f"""
    <div class="billboard">
      <div class="bb-eyebrow">Worst Drawdown · {yrs_str}</div>
      <div class="bb-row">
        <div class="bb-block">
          <div class="bb-label">Without overlay</div>
          <div class="bb-num-bad">{bnh_dd_pct}</div>
        </div>
        <div class="bb-arrow">→</div>
        <div class="bb-block">
          <div class="bb-label">With overlay</div>
          <div class="{dd_good_class}">{v2a_dd_pct}</div>
        </div>
        <div style="padding-left:8px;align-self:center">
          {saved_line}
        </div>
      </div>
      <div class="bb-sub">
        {val_line}<br>
        <span style="color:#475569;font-size:0.75rem">{meta_line}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fund meta ──────────────────────────────────────────────────────────────
    hc1, hc2 = st.columns([7, 2.5])
    with hc1:
        cat  = fr.get("scheme_category",""); role = fr.get("final_role","")
        conf = str(fr.get("classification_confidence","")).upper()
        conf_map = {"HIGH":"Strong fit","MEDIUM":"Moderate fit","LOW":"Mixed signals"}
        amc_name = fr.get("amc","")
        role_str = role + (f" · {conf_map.get(conf,'')}" if role and conf else "")
        meta = " · ".join(p for p in [amc_name, cat, role_str] if p)
        st.markdown(f'<div style="font-size:0.8rem;color:#64748b;margin-top:4px">{meta}</div>',
                    unsafe_allow_html=True)
    with hc2:
        oos_e = bool(fr.get("oos_eligible", True)); vs = fr.get("validation_score", 0)
        st.markdown(val_badge(vs, oos_e), unsafe_allow_html=True)

    if ROLE_DESC.get(role,""):
        low_note = " Confidence is mixed — treat the role as directional." if conf=="LOW" else ""
        st.markdown(f'<div class="co"><strong style="color:#14b8a6">{role}:</strong> {ROLE_DESC[role]}{low_note}</div>',
                    unsafe_allow_html=True)

    num_sells = int(fr.get("v2a_num_sells", 0))
    reg_str   = f"{m['reg_pct']*100:.0f}% of days" if pd.notna(m.get("reg_pct")) and not np.isnan(m["reg_pct"]) else "—"
    st.markdown(
        f'<div class="info-row">'
        f'<div class="ir-item"><span class="ir-lbl">Period</span><span class="ir-val">{date_from} → {date_to} ({yrs_str})</span></div>'
        f'<div class="ir-item"><span class="ir-lbl">Overlay trims (full sim)</span><span class="ir-val">{num_sells} rule-based sells</span></div>'
        f'<div class="ir-item"><span class="ir-lbl">Strategy was active</span><span class="ir-val">{reg_str}</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Native metric cards ────────────────────────────────────────────────────
    period_lbl = f"from {date_from}" if is_custom else "2010–2026"
    st.markdown(f'<div class="slbl">Key Numbers · {period_lbl}</div>', unsafe_allow_html=True)

    edge_cagr = m["v2a_cagr"] - m["bnh_cagr"]
    edge_dd   = m["v2a_dd"]   - m["bnh_dd"]
    edge_vol  = m["v2a_vol"]  - m["bnh_vol"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="Annual Return · Overlay",
            value=pct(m["v2a_cagr"], 2),
            delta=f"{edge_cagr*100:+.2f}% vs holding",
        )
        st.caption(f"Holding: {pct(m['bnh_cagr'],2)}")
    with c2:
        st.metric(
            label="Worst Drawdown · Overlay",
            value=f"−{abs(m['v2a_dd'])*100:.1f}%",
            delta=f"{'−' if (m['v2a_dd'] - m['bnh_dd']) < 0 else '+'}{abs(m['v2a_dd'] - m['bnh_dd'])*100:.1f} pp vs holding",
            delta_color="inverse",   # negative delta = green (less drawdown = better)
        )
        st.caption(f"Holding: −{abs(m['bnh_dd'])*100:.1f}%")
    with c3:
        st.metric(
            label="Annualised Volatility · Overlay",
            value=pct(m["v2a_vol"], 1),
            delta=f"{edge_vol*100:+.1f}% vs holding",
            delta_color="inverse",
        )
        st.caption(f"Holding: {pct(m['bnh_vol'],1)}")
    with c4:
        ev = m["final_v2a"] - m["final_bnh"]
        st.metric(
            label=f"Portfolio Value · {period_lbl}",
            value=inr(m["final_v2a"]),
            delta=f"{'+' if ev>=0 else ''}{inr(ev)} vs holding",
        )
        st.caption(f"Holding: {inr(m['final_bnh'])}")

    # Secondary stats
    fmt2 = lambda v: f"{v:.2f}" if v is not None else "—"
    fmt3 = lambda v: f"{v:.3f}" if v is not None else "—"

    def sstat_html(label, bv, ov, fmt, hib=True, tip=""):
        bvs, ovs = fmt(safe_float(bv)), fmt(safe_float(ov))
        arrow = ""
        try:
            bf, of = float(bv), float(ov)
            if not (np.isnan(bf) or np.isnan(of)):
                better = (of > bf and hib) or (of < bf and not hib)
                c = "#34d399" if better else "#f87171"
                arrow = f' <span style="color:{c};font-size:0.7rem">{"↑" if better else "↓"}</span>'
        except: pass
        t = f' title="{tip}"' if tip else ""
        return (f'<div class="sstat"{t}>'
                f'<span class="sstat-lbl">{label}</span>'
                f'<span class="sstat-val">{bvs} → <strong style="color:#14b8a6">{ovs}</strong>{arrow}</span>'
                f'</div>')

    ss = [
        sstat_html("Calmar Ratio", m["bnh_calmar"], m["v2a_calmar"], fmt2, hib=True,
                   tip="Return ÷ worst loss. Higher = better risk-adjusted return."),
        sstat_html("Efficiency Score", m["bnh_score"], m["v2a_score"], fmt3, hib=True,
                   tip="CAGR minus half the max drawdown. Penalises big drops."),
    ]
    if pd.notna(m["bnh_beta"]):
        ss.append(sstat_html("Beta vs Nifty 50", m["bnh_beta"], m["v2a_beta"], fmt2, hib=False,
                             tip="Sensitivity to Nifty moves. Lower = less market risk."))
    st.markdown(f'<div class="sstat-row">{"".join(ss)}</div>', unsafe_allow_html=True)

    # 2024-26 callout
    crash_sw = crash_df[(crash_df["scheme_code"] == code) &
                        crash_df["period_name"].str.contains("Sideways", na=False)]
    if len(crash_sw) > 0:
        sw = crash_sw.iloc[0]
        if pd.notna(sw.get("v2a_beats_bnh")):
            bf = abs(sw["bnh_max_dd"])*100 if pd.notna(sw["bnh_max_dd"]) else None
            vf = abs(sw["v2a_max_dd"])*100 if pd.notna(sw["v2a_max_dd"]) else None
            fr_txt = (f"This fund: {bf:.1f}% without overlay → {vf:.1f}% with. " if bf and vf else "")
            icon = "📈" if sw["v2a_beats_bnh"] else "📉"
            st.markdown(
                f'<div class="co" style="margin-top:14px">'
                f'{icon} <strong style="color:#14b8a6">2024–26 sideways market:</strong> {fr_txt}'
                f'Across all 173 funds, overlay outperformed simple holding in <strong style="color:#e2e8f0">152 of 173 (88%)</strong> cases.</div>',
                unsafe_allow_html=True,
            )

    # ── Chart ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="slbl">Portfolio Growth Over Time</div>', unsafe_allow_html=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.82, 0.18], vertical_spacing=0.04)

    fig.add_trace(go.Scatter(
        x=sc["ds"].tolist(), y=sc["bnh_s"].tolist(), mode="lines",
        name="Simple holding", line=dict(color="#475569", width=1.8),
        hovertemplate="<b>Simple holding</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>"),
        row=1, col=1)
    fig.add_trace(go.Scatter(
        x=sc["ds"].tolist(), y=sc["v2a_s"].tolist(), mode="lines",
        name="With overlay", line=dict(color=TEAL, width=2.5),
        hovertemplate="<b>With overlay</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>"),
        row=1, col=1)

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

    fig.update_layout(
        shapes=shapes, height=520,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=11, color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified", font=dict(family="Inter, sans-serif", color="#94a3b8"),
    )
    fig.update_yaxes(tickprefix="₹", tickformat=",.0f", gridcolor="#1e293b",
                     tickfont=dict(color="#475569"), row=1, col=1)
    fig.update_yaxes(tickvals=[0,1], ticktext=["","Active"], gridcolor="#1e293b",
                     tickfont=dict(color="#475569"), row=2, col=1)
    fig.update_xaxes(type="date", tickformat="%b '%y", gridcolor="#1e293b",
                     tickfont=dict(color="#475569"))

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<div class="note">🔴 Shaded = major crashes (2011, 2015–16, 2018–19, 2020 COVID). '
        'Bottom bar = days the strategy was watching for risk signals.</div>',
        unsafe_allow_html=True,
    )

    # ── Crash table ────────────────────────────────────────────────────────────
    st.markdown('<div class="slbl">Crash-by-Crash Comparison</div>', unsafe_allow_html=True)

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
                "Period": r["period_name"],
                "Without overlay": f"−{b:.1f}%",
                "With overlay":    f"−{v:.1f}%",
                "Overlay helped?": f"✅  {s:.1f} pp shallower" if win else f"❌  {s:.1f} pp deeper",
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
        column_config={
            "Period":          st.column_config.TextColumn(width=175),
            "Without overlay": st.column_config.TextColumn(width=155),
            "With overlay":    st.column_config.TextColumn(width=155),
            "Overlay helped?": st.column_config.TextColumn(width=220),
        })

    # ── Validation ─────────────────────────────────────────────────────────────
    with st.expander("🔍  How reliable are these results? (4 independent checks)"):
        st.markdown("Four tests to check if the overlay's edge is real or a lucky fit to past data.")

        wf_p = bool(fr.get("wf_pass",False)); wf_r = fr.get("wf_pass_rate")
        wf_n = fr.get("wf_windows_pass"); wf_t = fr.get("wf_windows_total")
        if pd.notna(wf_r):
            wf_d = (f"{'✅' if wf_p else '❌'} Beat simple holding in **{int(wf_n or 0)} of {int(wf_t or 0)} windows** ({(wf_r or 0)*100:.0f}%). "
                    + ("Consistent." if wf_p else "Inconsistent — result depends on when you invested."))
        else:
            wf_d = "❌ Not enough history (needs 7+ years)."
        st.markdown(f'<div class="vc"><div class="vc-q">Check 1 — Consistent across time periods?</div>'
                    f'<div class="vc-r">{wf_d}</div></div>', unsafe_allow_html=True)

        oos_e2 = bool(fr.get("oos_eligible",True)); oos_p = bool(fr.get("oos_pass",False))
        if not oos_e2:
            oos_d = "— Not eligible (needs 5+ years of training data)."
        elif oos_p:
            oos_d = "✅ Outperformed on 2023–2026 data the strategy had never seen. Strong evidence the edge is genuine."
        else:
            oos_d = "❌ Did not outperform on fresh 2023–2026 data. May be over-fitted to older patterns."
        st.markdown(f'<div class="vc"><div class="vc-q">Check 2 — Held up on data it had never seen?</div>'
                    f'<div class="vc-r">{oos_d}</div></div>', unsafe_allow_html=True)

        mc_p = bool(fr.get("mc_pass",False)); mc_pct = fr.get("real_percentile")
        if pd.notna(mc_pct):
            mc_d = (f"{'✅' if mc_p else '❌'} Real result ranked **{mc_pct:.1f}th percentile** out of 1,000 random simulations. "
                    + (f"Only ~{100-mc_pct:.0f}% of random runs matched it — very unlikely to be luck." if mc_p
                       else "Random simulations often matched it — may be partly coincidence."))
        else:
            mc_d = "Monte Carlo data not available."
        st.markdown(f'<div class="vc"><div class="vc-q">Check 3 — Could this be luck?</div>'
                    f'<div class="vc-r">{mc_d}</div></div>', unsafe_allow_html=True)

        st_p = bool(fr.get("stability_pass",False)); st_r = fr.get("stability_pass_rate")
        cliff = bool(fr.get("cliff_detected",False))
        if pd.notna(st_r):
            st_d = (f"{'✅' if st_p else '❌'} Held up in **{st_r*100:.0f}%** of 20 parameter variations. "
                    + ("Robust." if st_p else "Sensitive — small rule changes affect outcomes.")
                    + (" ⚠️ One threshold caused a larger-than-expected shift." if cliff else ""))
        else:
            st_d = "Stability data not available."
        st.markdown(f'<div class="vc"><div class="vc-q">Check 4 — Robust to small rule changes?</div>'
                    f'<div class="vc-r">{st_d}</div></div>', unsafe_allow_html=True)

        vs_int = int(fr.get("validation_score",0)) if pd.notna(fr.get("validation_score")) else 0
        mx2 = 4 if oos_e2 else 3
        if vs_int >= mx2:  st.success(f"✅ Passed all {mx2} checks. High confidence.")
        elif vs_int >= 2:  st.warning(f"Passed {vs_int}/{mx2}. Crash protection is solid; return figures are directional.")
        else:              st.error(f"Only {vs_int}/{mx2} passed. Treat results with caution.")

    st.markdown("---")
    st.markdown(
        '<div class="disc" style="text-align:center">'
        "NivesAI · LARF v2a · AMFI NAV data · 173 funds · Jan 2010–Apr 2026 · "
        "<strong>Historical simulations only. Not investment advice. NivesAI is not a SEBI-registered advisor.</strong>"
        "</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Compare Funds
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        '<div style="font-size:0.85rem;color:#64748b;margin-bottom:14px">'
        'Filter by category or AMC. All figures from the full Jan 2010–Apr 2026 simulation.</div>',
        unsafe_allow_html=True,
    )

    def try_col(df, *cands):
        for c in cands:
            if c in df.columns: return c
        return None

    col_vc = try_col(master_df, "v2a_cagr", "overlay_cagr")
    col_bc = try_col(master_df, "bnh_cagr", "hold_cagr")
    col_vd = try_col(master_df, "v2a_max_dd","overlay_max_dd","v2a_mdd")
    col_bd = try_col(master_df, "bnh_max_dd","hold_max_dd","bnh_mdd")
    has_m  = all(x is not None for x in [col_vc, col_bc, col_vd, col_bd])

    st.markdown('<div class="compare-filter">', unsafe_allow_html=True)
    cf1, cf2, cf3 = st.columns([2, 2, 1])
    with cf1:
        cats = ["All categories"] + sorted(master_df["scheme_category"].dropna().unique().tolist())
        sel_cat = st.selectbox("Category", cats, key="cc")
    with cf2:
        amcs = ["All AMCs"] + sorted(master_df["amc"].dropna().unique().tolist())
        sel_amc = st.selectbox("AMC", amcs, key="ca")
    with cf3:
        sort_by = st.selectbox("Sort by", ["Overlay Return ↓","DD Saved ↓","Validation ↓"], key="cs")
    st.markdown('</div>', unsafe_allow_html=True)

    cdf = master_df.copy()
    if sel_cat != "All categories": cdf = cdf[cdf["scheme_category"] == sel_cat]
    if sel_amc != "All AMCs":       cdf = cdf[cdf["amc"] == sel_amc]

    if len(cdf) == 0:
        st.warning("No funds match the selected filters.")
    else:
        rows = []
        for _, r in cdf.iterrows():
            row = {"Fund": r.get("scheme_name","—"), "Category": r.get("scheme_category","—"),
                   "AMC": r.get("amc","—"), "Role": r.get("final_role","—")}
            if has_m:
                vc = safe_float(r.get(col_vc)); bc = safe_float(r.get(col_bc))
                vd = safe_float(r.get(col_vd)); bd = safe_float(r.get(col_bd))
                row["Return · Overlay"]  = f"{vc*100:.1f}%"  if vc else "—"
                row["Return · Holding"]  = f"{bc*100:.1f}%"  if bc else "—"
                row["Return Δ"]          = f"+{(vc-bc)*100:.2f}%" if (vc and bc) else "—"
                row["MaxDD · Overlay"]   = f"−{abs(vd)*100:.1f}%" if vd else "—"
                row["MaxDD · Holding"]   = f"−{abs(bd)*100:.1f}%" if bd else "—"
                row["DD Saved (pp)"]     = round((abs(bd)-abs(vd))*100,1) if (vd and bd) else None
                row["_vc"] = vc or -99; row["_dds"] = (abs(bd)-abs(vd))*100 if (vd and bd) else -99
            vs = safe_float(r.get("validation_score"))
            row["Validation"] = f"{int(vs)}" if vs else "—"; row["_vs"] = vs or -99
            rows.append(row)

        cdf2 = pd.DataFrame(rows)
        sc_map = {"Overlay Return ↓":"_vc","DD Saved ↓":"_dds","Validation ↓":"_vs"}
        sc_col = sc_map.get(sort_by,"_vc")
        if sc_col in cdf2.columns: cdf2 = cdf2.sort_values(sc_col, ascending=False)
        disp = cdf2[[c for c in cdf2.columns if not c.startswith("_")]].reset_index(drop=True)

        st.markdown(f'<div class="note" style="margin-bottom:8px">Showing <strong>{len(disp)}</strong> funds</div>',
                    unsafe_allow_html=True)
        st.dataframe(disp, use_container_width=True, hide_index=True)

        if has_m and len(cdf2) <= 60 and "Return Δ" in cdf2.columns:
            st.markdown('<div class="slbl">Annual Return Delta: Overlay vs Holding</div>', unsafe_allow_html=True)
            cd = cdf2[cdf2["Return Δ"] != "—"].copy()
            cd["_dv"] = cd["Return Δ"].str.replace("%","").str.replace("+","").astype(float)
            cd = cd.sort_values("_dv", ascending=True).tail(40)
            fig2 = go.Figure(go.Bar(
                x=cd["_dv"], y=cd["Fund"].str[:50], orientation="h",
                marker_color=["#14b8a6" if v>=0 else "#ef4444" for v in cd["_dv"]],
                text=[f"+{v:.2f}%" if v>=0 else f"{v:.2f}%" for v in cd["_dv"]],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Delta: %{x:.2f}%<extra></extra>",
            ))
            fig2.update_layout(
                height=max(320, len(cd)*22+60),
                margin=dict(l=0, r=60, t=10, b=30),
                paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                xaxis=dict(title="Return delta (pp)", gridcolor="#1e293b",
                           zeroline=True, zerolinecolor="#475569", zerolinewidth=1.5,
                           tickfont=dict(color="#475569")),
                yaxis=dict(tickfont=dict(size=11, color="#94a3b8")),
                font=dict(family="Inter, sans-serif", color="#94a3b8"),
            )
            st.plotly_chart(fig2, use_container_width=True)

        if not has_m:
            st.info("Detailed metrics not found in results file. Check that larf_regime_results_v2.csv has v2a_cagr and bnh_cagr columns.")

    st.markdown("---")
    st.markdown('<div class="disc">NivesAI · LARF v2a · Historical simulations only. Not investment advice.</div>',
                unsafe_allow_html=True)