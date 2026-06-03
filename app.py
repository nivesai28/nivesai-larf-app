"""
NivesAI — LARF Overlay Research Tool
Streamlit app — v1.0
Author: Sneha Joshi | NivesAI

All outputs are retrospective research simulations based on historical NAV data.
This is not investment advice.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
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
BRAND_LIGHT   = "#e6f4f4"
BNH_COLOR     = "#9ca3af"
OVERLAY_COLOR = "#0d6e6e"
CRASH_SHADE   = "rgba(252, 165, 165, 0.18)"
ACTIVE_BAR    = "#ef4444"
IDLE_BAR      = "#e5e7eb"

CRASH_PERIODS = [
    ("2011 Bear",            "2011-01-01", "2011-12-31"),
    ("2015-16 Correction",   "2015-03-01", "2016-03-31"),
    ("2018-19 NBFC Crisis",  "2018-09-01", "2019-03-31"),
    ("2020 COVID Crash",     "2020-01-15", "2020-04-30"),
]

DEFAULT_AMOUNT = 100_000
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Brand header */
.nives-brand { font-size: 1.5rem; font-weight: 700; color: #0d6e6e; letter-spacing: -0.5px; }
.nives-sub   { font-size: 0.78rem; color: #6b7280; margin-top: -6px; }

/* Metric cards */
.metric-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-label  { font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-val    { font-size: 1.5rem; font-weight: 700; color: #111827; margin: 4px 0 2px; }
.metric-delta  { font-size: 0.85rem; font-weight: 600; }
.delta-pos     { color: #16a34a; }
.delta-neg     { color: #dc2626; }
.delta-neu     { color: #6b7280; }

/* Validation badge */
.badge-green  { background:#dcfce7; color:#15803d; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600; }
.badge-yellow { background:#fef9c3; color:#854d0e; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600; }
.badge-red    { background:#fee2e2; color:#991b1b; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600; }

/* Role chip */
.role-chip { background:#e0f2fe; color:#075985; border-radius:20px; padding:3px 12px; font-size:0.8rem; font-weight:600; }

/* Callout box */
.callout-box {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    border-radius: 0 8px 8px 0;
    padding: 10px 16px;
    margin: 12px 0;
    font-size: 0.88rem;
    color: #15803d;
}
.callout-box-warn {
    background: #fff7ed;
    border-left: 4px solid #f97316;
    border-radius: 0 8px 8px 0;
    padding: 10px 16px;
    margin: 12px 0;
    font-size: 0.88rem;
    color: #9a3412;
}

/* Disclaimer */
.disclaimer {
    font-size: 0.72rem;
    color: #9ca3af;
    line-height: 1.5;
    border-top: 1px solid #e5e7eb;
    margin-top: 20px;
    padding-top: 14px;
}

/* Section header */
.section-hdr {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #374151;
    margin: 24px 0 10px;
    border-bottom: 2px solid #0d6e6e;
    padding-bottom: 4px;
}

/* Hide Streamlit default top padding */
.block-container { padding-top: 1.5rem !important; }
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

    regime_tl = pd.read_csv(f"{DATA_DIR}/regime_timeline.csv", parse_dates=["date"])

    # Join into one fund-level master
    df = results.merge(
        val[[
            "scheme_code", "validation_score", "fully_validated",
            "wf_pass", "wf_pass_rate", "wf_windows_total", "wf_windows_pass",
            "oos_eligible", "oos_pass", "mc_pass", "real_percentile",
            "stability_pass", "cliff_detected",
        ]],
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
    csv_path = f"{DATA_DIR}/larf_regime_curves_v2.csv"
    if os.path.exists(parquet):
        df = pd.read_parquet(parquet, columns=["scheme_code", "date", "bnh_value", "v2a_value"])
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path, usecols=["scheme_code", "date", "bnh_value", "v2a_value"],
                         parse_dates=["date"])
    else:
        st.error("Curves data not found. Please run data_prep_colab.py first.")
        st.stop()
    df["scheme_code"] = df["scheme_code"].astype(str)
    df["date"] = pd.to_datetime(df["date"])
    return df


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_pct(v, decimals=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v * 100:+.{decimals}f}%"

def fmt_pct_plain(v, decimals=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v * 100:.{decimals}f}%"

def fmt_inr(v):
    if v is None or np.isnan(v):
        return "—"
    if v >= 1_00_000:
        return f"₹{v/1_00_000:.2f}L"
    return f"₹{v:,.0f}"

def delta_class(v):
    if v is None or np.isnan(v):
        return "delta-neu"
    return "delta-pos" if v > 0 else ("delta-neg" if v < 0 else "delta-neu")

def validation_badge(row):
    score = row.get("validation_score", 0)
    if pd.isna(score):
        score = 0
    score = int(score)
    eligible = row.get("oos_eligible", True)
    max_score = 4 if eligible else 3
    if score >= max_score:
        return f'<span class="badge-green">✅ Fully Validated ({score}/{max_score} tests)</span>'
    elif score >= 2:
        return f'<span class="badge-yellow">⚠️ Partially Validated ({score}/{max_score} tests)</span>'
    else:
        return f'<span class="badge-red">❌ Not Validated ({score}/{max_score} tests)</span>'

def scale_curves(fund_curves, amount, start_date=None):
    """Scale curves to user's investment amount, optionally rebased from start_date."""
    df = fund_curves.copy().sort_values("date").reset_index(drop=True)
    if start_date is not None:
        start_ts = pd.Timestamp(start_date)
        df = df[df["date"] >= start_ts].reset_index(drop=True)
    if len(df) == 0:
        return df
    # Scale: multiply by (amount / initial_bnh_value)
    scale = amount / df["bnh_value"].iloc[0]
    df["bnh_scaled"]  = df["bnh_value"]  * scale
    df["v2a_scaled"]  = df["v2a_value"]  * scale
    return df


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nives-brand">NivesAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="nives-sub">LARF — Overlay Research Engine</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**Engine:** v2a · Regime-Gated Overlay")
    st.markdown("**Universe:** 173 Indian Mutual Funds")
    st.markdown("**Period:** Jan 2010 – May 2026")
    st.markdown("**Benchmark:** Buy-and-Hold (BnH)")
    st.markdown("**Idle cash:** Quantum Liquid Fund returns")

    st.markdown("---")
    st.markdown("**How the overlay works**")
    st.markdown(
        "A rule-based engine monitors the Nifty 50 TRI regime (200-day MA) "
        "and fund-level stress signals. When conditions are met, it trims a "
        "fixed fraction of the position and parks cash in a liquid fund. "
        "It never exits fully. There is no prediction — only rules.",
        unsafe_allow_html=False,
    )

    st.markdown("---")
    st.markdown(
        '<div class="disclaimer">'
        "All outputs are <strong>retrospective research simulations</strong> based on "
        "historical NAV data sourced from AMFI. Results are not indicative of future "
        "performance. This tool is not investment advice. NivesAI is not a "
        "SEBI-registered investment advisor. Do not use this output to make "
        "investment decisions without consulting a qualified financial advisor."
        "</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
master_df, crash_df, regime_tl = load_master()
curves_df = load_curves()

# ─────────────────────────────────────────────────────────────────────────────
# FUND SELECTOR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## LARF Overlay Research Tool")
st.markdown(
    "Select a fund to see how the LARF regime-gated overlay would have performed "
    "versus a buy-and-hold strategy over 16 years of Indian market history."
)

# Build dropdown options: "Fund Name (Category)"
fund_options = {}
for _, row in master_df.sort_values(["scheme_category", "scheme_name"]).iterrows():
    label = f"{row['scheme_name']}  ·  {row['scheme_category']}"
    fund_options[label] = str(row["scheme_code"])

col_sel, col_amt, col_btn = st.columns([4, 1.5, 1])
with col_sel:
    selected_label = st.selectbox(
        "Select a fund",
        options=["— choose a fund —"] + list(fund_options.keys()),
        label_visibility="collapsed",
    )
with col_amt:
    amount = st.number_input(
        "Initial investment (₹)",
        min_value=10_000,
        max_value=10_00_00_000,
        value=DEFAULT_AMOUNT,
        step=10_000,
        format="%d",
        label_visibility="collapsed",
    )
with col_btn:
    run = st.button("View Results →", type="primary", use_container_width=True)

if selected_label == "— choose a fund —" or not run:
    st.markdown("---")
    st.markdown(
        "👆  Select a fund above and click **View Results** to see 16 years of "
        "overlay vs buy-and-hold performance."
    )
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# LOAD FUND DATA
# ─────────────────────────────────────────────────────────────────────────────
scheme_code = fund_options[selected_label]
fund_row    = master_df[master_df["scheme_code"] == scheme_code].iloc[0]
fund_curves = curves_df[curves_df["scheme_code"] == scheme_code].sort_values("date").reset_index(drop=True)
fund_crash  = crash_df[crash_df["scheme_code"] == scheme_code]
fund_crash_main = fund_crash[~fund_crash["period_name"].str.contains("Sideways", na=False)]
fund_sideways   = fund_crash[fund_crash["period_name"].str.contains("Sideways", na=False)]

scaled = scale_curves(fund_curves, amount)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# FUND HEADER
# ─────────────────────────────────────────────────────────────────────────────
h_col1, h_col2 = st.columns([6, 2])
with h_col1:
    st.markdown(f"### {fund_row['scheme_name']}")
    cat   = fund_row.get("scheme_category", "")
    role  = fund_row.get("final_role", "")
    conf  = fund_row.get("classification_confidence", "")
    st.markdown(
        f'<span style="color:#6b7280;font-size:0.88rem">{cat}</span>&nbsp;&nbsp;'
        f'<span class="role-chip">{role}</span>&nbsp;'
        f'<span style="color:#9ca3af;font-size:0.78rem">({conf} confidence)</span>',
        unsafe_allow_html=True,
    )
with h_col2:
    st.markdown(
        validation_badge(fund_row.to_dict()),
        unsafe_allow_html=True,
    )
    sim_start = fund_row.get("sim_start_date", "2010-01-04")
    sim_end   = fund_row.get("sim_end_date", "2026-04-08")
    st.markdown(
        f'<span style="color:#9ca3af;font-size:0.78rem">'
        f'Sim: {sim_start} → {sim_end}&nbsp;'
        f'({fund_row.get("years", 0):.1f} yrs)</span>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# PANEL A — KEY METRICS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Performance Summary</div>', unsafe_allow_html=True)

bnh_cagr   = fund_row["bnh_cagr"]
v2a_cagr   = fund_row["v2a_cagr"]
bnh_dd     = fund_row["bnh_max_dd"]
v2a_dd     = fund_row["v2a_max_dd"]
bnh_score  = bnh_cagr - abs(bnh_dd) / 2
v2a_score  = fund_row["v2a_score"]
edge_cagr  = fund_row["v2a_edge_cagr"]
edge_dd    = fund_row["v2a_edge_dd"]
edge_score = v2a_score - bnh_score
regime_pct = fund_row.get("v2a_regime_pct", 0)
num_sells  = fund_row.get("v2a_num_sells", 0)

# Final portfolio values
final_bnh = scaled["bnh_scaled"].iloc[-1] if len(scaled) > 0 else amount
final_v2a = scaled["v2a_scaled"].iloc[-1] if len(scaled) > 0 else amount

m1, m2, m3, m4, m5 = st.columns(5)

def metric_card(label, bnh_val, v2a_val, delta, fmt_fn, higher_is_better=True):
    good   = higher_is_better and delta > 0 or (not higher_is_better and delta < 0)
    bad    = higher_is_better and delta < 0 or (not higher_is_better and delta > 0)
    d_cls  = "delta-pos" if good else ("delta-neg" if bad else "delta-neu")
    sign   = "+" if delta > 0 else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div style="display:flex;justify-content:center;gap:18px;align-items:baseline;margin:6px 0 4px">
            <div>
                <div style="font-size:0.72rem;color:#9ca3af">BnH</div>
                <div class="metric-val" style="font-size:1.2rem">{fmt_fn(bnh_val)}</div>
            </div>
            <div>
                <div style="font-size:0.72rem;color:#0d6e6e;font-weight:600">Overlay</div>
                <div class="metric-val" style="font-size:1.2rem;color:#0d6e6e">{fmt_fn(v2a_val)}</div>
            </div>
        </div>
        <div class="metric-delta {d_cls}">{sign}{fmt_fn(delta)} vs BnH</div>
    </div>"""

with m1:
    st.markdown(metric_card("CAGR", bnh_cagr, v2a_cagr, edge_cagr,
                             lambda v: fmt_pct(v, 2), higher_is_better=True),
                unsafe_allow_html=True)
with m2:
    st.markdown(metric_card("Max Drawdown", bnh_dd, v2a_dd, edge_dd,
                             lambda v: fmt_pct(v, 1), higher_is_better=False),
                unsafe_allow_html=True)
with m3:
    st.markdown(metric_card("Score (CAGR − DD/2)", bnh_score, v2a_score, edge_score,
                             lambda v: f"{v:+.3f}" if v is not None else "—",
                             higher_is_better=True),
                unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Final Portfolio Value</div>
        <div style="display:flex;justify-content:center;gap:18px;align-items:baseline;margin:6px 0 4px">
            <div>
                <div style="font-size:0.72rem;color:#9ca3af">BnH</div>
                <div class="metric-val" style="font-size:1.2rem">{fmt_inr(final_bnh)}</div>
            </div>
            <div>
                <div style="font-size:0.72rem;color:#0d6e6e;font-weight:600">Overlay</div>
                <div class="metric-val" style="font-size:1.2rem;color:#0d6e6e">{fmt_inr(final_v2a)}</div>
            </div>
        </div>
        <div class="metric-delta" style="color:#6b7280">on ₹{amount:,.0f} invested</div>
    </div>""", unsafe_allow_html=True)
with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Overlay Activity</div>
        <div class="metric-val" style="margin:10px 0 4px">{regime_pct*100:.0f}%</div>
        <div style="color:#6b7280;font-size:0.82rem">of days overlay was active</div>
        <div style="color:#9ca3af;font-size:0.78rem;margin-top:4px">{int(num_sells)} total trims over {fund_row.get('years',16):.0f} years</div>
    </div>""", unsafe_allow_html=True)

# 2024-26 callout
if len(fund_sideways) > 0:
    sw = fund_sideways.iloc[0]
    if pd.notna(sw["v2a_beats_bnh"]):
        if sw["v2a_beats_bnh"]:
            st.markdown(
                f'<div class="callout-box">📈 <strong>2024–26 sideways market:</strong> '
                f'Overlay outperformed BnH — drawdown {fmt_pct_plain(sw["v2a_max_dd"],1)} '
                f'vs {fmt_pct_plain(sw["bnh_max_dd"],1)} for BnH. '
                f'Across all 173 funds, overlay beat BnH in <strong>152/173 funds (88%)</strong> '
                f'during this period.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="callout-box-warn">📉 <strong>2024–26 sideways market:</strong> '
                f'Overlay underperformed BnH for this fund in this period. '
                f'Across all 173 funds, overlay still beat BnH in '
                f'<strong>152/173 funds (88%)</strong> during this period.</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# PANEL B — EQUITY CURVE + REGIME ACTIVATION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Equity Curve: BnH vs Overlay</div>', unsafe_allow_html=True)

if len(scaled) == 0:
    st.warning("No curve data available for this fund.")
else:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.82, 0.18],
        vertical_spacing=0.03,
    )

    # ── Crash period shading ────────────────────────────────
    for name, start, end in CRASH_PERIODS:
        for row_idx in [1, 2]:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=CRASH_SHADE, opacity=1, line_width=0,
                row=row_idx, col=1,
            )

    # ── BnH line ────────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=scaled["date"], y=scaled["bnh_scaled"].round(0),
            mode="lines", name="Buy & Hold",
            line=dict(color=BNH_COLOR, width=1.8),
            hovertemplate="<b>Buy & Hold</b><br>%{x|%d %b %Y}<br>₹%{y:,.0f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # ── Overlay line ─────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=scaled["date"], y=scaled["v2a_scaled"].round(0),
            mode="lines", name="LARF Overlay",
            line=dict(color=OVERLAY_COLOR, width=2.2),
            hovertemplate="<b>LARF Overlay</b><br>%{x|%d %b %Y}<br>₹%{y:,.0f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # ── Regime activation bar chart ─────────────────────────
    # Merge regime timeline with fund date range
    fund_dates = scaled["date"]
    regime_fund = regime_tl[
        (regime_tl["date"] >= fund_dates.min()) &
        (regime_tl["date"] <= fund_dates.max())
    ].copy()

    fig.add_trace(
        go.Bar(
            x=regime_fund["date"],
            y=regime_fund["macro_active"].astype(int),
            marker_color=[ACTIVE_BAR if v else IDLE_BAR
                          for v in regime_fund["macro_active"]],
            name="Macro Regime Active",
            showlegend=True,
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Overlay watching: %{y}<extra></extra>",
        ),
        row=2, col=1,
    )

    # ── Layout ──────────────────────────────────────────────
    fig.update_layout(
        height=540,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
            font=dict(size=12),
        ),
        hovermode="x unified",
    )
    fig.update_yaxes(
        title_text="Portfolio Value (₹)", tickprefix="₹", tickformat=",.0f",
        row=1, col=1, gridcolor="#f3f4f6",
    )
    fig.update_yaxes(
        title_text="Active", tickvals=[0, 1], ticktext=["Idle", "On"],
        row=2, col=1, gridcolor="#f3f4f6",
    )
    fig.update_xaxes(gridcolor="#f3f4f6", row=1, col=1)
    fig.update_xaxes(
        gridcolor="#f3f4f6", row=2, col=1,
        title_text="Date",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<span style="font-size:0.78rem;color:#9ca3af">'
        f'🔴 Red shaded bands = crash periods. '
        f'Bottom panel: macro regime (overlay "watching" when Nifty 50 TRI is below its 200-day MA). '
        f'Overlay was active on <strong>{regime_pct*100:.0f}%</strong> of trading days for this fund.'
        f'</span>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PANEL D — CRASH PERIOD TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Performance in Major Market Crashes</div>',
            unsafe_allow_html=True)

crash_display = []
for _, row in fund_crash_main.iterrows():
    if pd.isna(row["bnh_max_dd"]):
        crash_display.append({
            "Period":             row["period_name"],
            "BnH Max Drawdown":   "N/A (fund not active)",
            "Overlay Max Drawdown": "N/A",
            "Drawdown Saved":     "—",
            "Result":             "—",
        })
    else:
        saved = row["drawdown_saved"]  # negative = overlay shallower = good
        beats = bool(row["v2a_beats_bnh"])
        crash_display.append({
            "Period":               row["period_name"],
            "BnH Max Drawdown":     fmt_pct_plain(row["bnh_max_dd"], 1),
            "Overlay Max Drawdown": fmt_pct_plain(row["v2a_max_dd"], 1),
            "Drawdown Saved":       f"{abs(saved)*100:.1f}pp {'✅ shallower' if beats else '❌ deeper'}",
            "Result":               "✅ Overlay better" if beats else "❌ BnH better",
        })

crash_table_df = pd.DataFrame(crash_display)

st.dataframe(
    crash_table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Period":                 st.column_config.TextColumn("Period", width=180),
        "BnH Max Drawdown":       st.column_config.TextColumn("BnH Max DD", width=130),
        "Overlay Max Drawdown":   st.column_config.TextColumn("Overlay Max DD", width=140),
        "Drawdown Saved":         st.column_config.TextColumn("Drawdown Saved", width=200),
        "Result":                 st.column_config.TextColumn("Result", width=150),
    },
)

st.markdown(
    '<span style="font-size:0.78rem;color:#9ca3af">'
    'Max drawdown = worst peak-to-trough decline during the period. '
    '"Drawdown saved" = how much shallower the overlay drawdown was vs BnH. '
    '"pp" = percentage points. N/A = fund had insufficient history during this period.'
    '</span>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# PANEL E — VALIDATION (expandable)
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📋  Validation Scorecard — click to expand", expanded=False):
    st.markdown(
        "These four independent tests confirm whether the overlay's historical edge "
        "is real or a backtest artefact. All pass/fail thresholds were set "
        "**before** running the tests."
    )

    val_rows = []

    # Walk-forward
    wf_pass = fund_row.get("wf_pass", False)
    wf_rate = fund_row.get("wf_pass_rate", None)
    wf_win_total = fund_row.get("wf_windows_total", None)
    wf_win_pass  = fund_row.get("wf_windows_pass", None)
    if pd.isna(wf_rate) if isinstance(wf_rate, float) else wf_rate is None:
        wf_detail = "Insufficient history for walk-forward windows"
        wf_icon   = "❌"
    else:
        wf_detail = (f"Overlay beat BnH in {int(wf_win_pass or 0)} of "
                     f"{int(wf_win_total or 0)} rolling windows "
                     f"({wf_rate*100:.0f}% · threshold: 50%)")
        wf_icon = "✅" if wf_pass else "❌"
    val_rows.append({"Test": "Walk-forward", "Result": wf_icon, "Detail": wf_detail})

    # OOS
    oos_elig = fund_row.get("oos_eligible", True)
    oos_pass = fund_row.get("oos_pass", False)
    if not oos_elig:
        val_rows.append({"Test": "Out-of-Sample (2023–26)",
                         "Result": "—",
                         "Detail": "Not eligible (insufficient training history)"})
    else:
        val_rows.append({
            "Test":   "Out-of-Sample (2023–26)",
            "Result": "✅" if oos_pass else "❌",
            "Detail": ("Overlay beat BnH CAGR in unseen 2023–2026 period (threshold: >0% edge)"
                       if oos_pass else
                       "Overlay did not beat BnH CAGR in unseen 2023–2026 period"),
        })

    # Monte Carlo
    mc_pass = fund_row.get("mc_pass", False)
    mc_pct  = fund_row.get("real_percentile", None)
    mc_pct_str = f"{mc_pct:.1f}th" if pd.notna(mc_pct) else "—"
    val_rows.append({
        "Test":   "Monte Carlo (1,000 shuffles)",
        "Result": "✅" if mc_pass else "❌",
        "Detail": (f"Real edge in {mc_pct_str} percentile of random simulations "
                   f"(threshold: ≥95th percentile)"),
    })

    # Parameter stability
    stab_pass  = fund_row.get("stability_pass", False)
    stab_rate  = fund_row.get("stability_pass_rate", None)
    cliff      = fund_row.get("cliff_detected", False)
    stab_str   = f"{stab_rate*100:.0f}%" if pd.notna(stab_rate) else "—"
    cliff_note = " ⚠️ Cliff detected — results are threshold-sensitive." if cliff else ""
    val_rows.append({
        "Test":   "Parameter Stability",
        "Result": "✅" if stab_pass else "❌",
        "Detail": (f"{stab_str} of threshold perturbations within ±15% of baseline score "
                   f"(threshold: ≥80%){cliff_note}"),
    })

    val_df = pd.DataFrame(val_rows)
    st.dataframe(
        val_df, use_container_width=True, hide_index=True,
        column_config={
            "Test":   st.column_config.TextColumn("Test", width=210),
            "Result": st.column_config.TextColumn("Result", width=70),
            "Detail": st.column_config.TextColumn("Detail", width=600),
        },
    )

    val_score = int(fund_row.get("validation_score", 0))
    oos_elig  = fund_row.get("oos_eligible", True)
    max_tests = 4 if oos_elig else 3
    st.markdown(
        f"**Overall:** {val_score}/{max_tests} tests passed. "
        + (
            "This fund's results are **fully validated** — the overlay edge is statistically "
            "robust across all tests."
            if val_score >= max_tests else
            f"This fund passed {val_score} of {max_tests} applicable tests. "
            "Interpret results with appropriate caution."
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# PANEL F — BEHAVIOUR PROFILE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Fund Behaviour Profile</div>', unsafe_allow_html=True)

b1, b2, b3, b4 = st.columns(4)

sharpe = fund_row.get("v2a_score", None)   # not sharpe — we'll show what we have
bnh_cagr_fmt  = fmt_pct_plain(fund_row.get("bnh_cagr"), 2)
v2a_cagr_fmt  = fmt_pct_plain(fund_row.get("v2a_cagr"), 2)
years_fmt     = f"{fund_row.get('years', 0):.1f} yrs"

with b1:
    st.metric("Behaviour Role", fund_row.get("final_role", "—"))
with b2:
    st.metric("Classification Confidence", fund_row.get("classification_confidence", "—"))
with b3:
    st.metric("Simulation Length", years_fmt)
with b4:
    st.metric("Total Overlay Trims", f"{int(fund_row.get('v2a_num_sells', 0))} sells")

summary = str(fund_row.get("summary_text", ""))
if summary.strip():
    st.markdown(
        f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;'
        f'padding:14px 18px;font-size:0.88rem;color:#374151;margin-top:8px">'
        f'<strong>Behaviour summary:</strong> {summary}</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#9ca3af;font-size:0.75rem">'
    'NivesAI · LARF Research Engine v2a · '
    'Data: AMFI NAV history · '
    'Universe: 173 Indian mutual funds · '
    'Period: Jan 2010 – May 2026 · '
    'Not investment advice'
    '</div>',
    unsafe_allow_html=True,
)
