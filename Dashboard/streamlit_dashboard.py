"""
============================================================
  Zomato End-to-End Data Analytics
  Interactive Streamlit Dashboard
  Run: streamlit run Dashboard/streamlit_dashboard.py
============================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── PAGE CONFIG ──────────────────────────────────────────
st.set_page_config(
    page_title="Zomato Analytics Dashboard",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

  * { font-family: 'Inter', sans-serif !important; }

  /* ── APP BACKGROUND ── */
  [data-testid="stAppViewContainer"] { background: #0a0a0a; }
  [data-testid="stHeader"]           { background: transparent !important; }
  [data-testid="stMain"]             { background: #0a0a0a; }

  /* ── SIDEBAR ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f0f 0%, #141414 50%, #0f0f0f 100%) !important;
    border-right: 1px solid rgba(226,55,68,0.15) !important;
    box-shadow: 4px 0 30px rgba(0,0,0,0.6);
  }
  [data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

  /* ── SIDEBAR WIDGETS ── */
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
    background: #1a1a1a !important;
    border: 1px solid rgba(226,55,68,0.2) !important;
    border-radius: 10px !important;
    transition: border-color .2s;
  }
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div:hover {
    border-color: rgba(226,55,68,0.5) !important;
  }
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: rgba(226,55,68,0.2) !important;
    border: 1px solid rgba(226,55,68,0.4) !important;
    border-radius: 6px !important;
    color: #ff8a94 !important;
  }
  [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
    background: #1a1a1a !important;
    border: 1px solid rgba(226,55,68,0.2) !important;
    border-radius: 10px !important;
  }
  [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
    color: #888 !important; font-size: .75rem !important;
  }
  [data-testid="stSidebar"] .stRadio label {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 6px 12px;
    margin: 2px 0;
    width: 100%;
    transition: all .2s;
  }
  [data-testid="stSidebar"] .stRadio label:has(input:checked) {
    border-color: rgba(226,55,68,0.5) !important;
    background: rgba(226,55,68,0.1) !important;
    color: #E23744 !important;
  }
  [data-testid="stSidebar"] .stDateInput input {
    background: #1a1a1a !important;
    border: 1px solid rgba(226,55,68,0.2) !important;
    border-radius: 10px !important;
    color: #f0f0f0 !important;
  }
  [data-testid="stSidebar"] label {
    color: #aaa !important;
    font-size: .8rem !important;
    font-weight: 600 !important;
    letter-spacing: .02em !important;
  }

  /* ── SIDEBAR SCROLLBAR ── */
  [data-testid="stSidebar"]::-webkit-scrollbar { width: 4px; }
  [data-testid="stSidebar"]::-webkit-scrollbar-track { background: transparent; }
  [data-testid="stSidebar"]::-webkit-scrollbar-thumb { background: rgba(226,55,68,0.3); border-radius: 4px; }

  /* ══ GLOBAL — hide ALL stIconMaterial text everywhere ══ */
  [data-testid="stIconMaterial"] {
    display: none !important;
    visibility: hidden !important;
    font-size: 0 !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
  }

  /* ══ HEADER BAR — hide text + style the sidebar toggle button ══ */
  [data-testid="stHeader"] {
    background: transparent !important;
  }
  [data-testid="stHeader"] button,
  [data-testid="stHeader"] [data-testid="stBaseButton-headerNoPadding"] {
    background: #1a1a1a !important;
    border: 1px solid rgba(226,55,68,0.3) !important;
    border-radius: 10px !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    padding: 0 !important;
    position: relative !important;
    overflow: hidden !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  [data-testid="stHeader"] button span,
  [data-testid="stHeader"] button svg {
    display: none !important;
    visibility: hidden !important;
    font-size: 0 !important;
    width: 0 !important;
    height: 0 !important;
  }
  [data-testid="stHeader"] button::before {
    content: '☰';
    font-family: Arial, sans-serif !important;
    font-size: 1.1rem;
    color: #E23744;
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    display: block !important;
    visibility: visible !important;
  }

  /* ══ SIDEBAR TOGGLE — open state (stSidebarCollapseButton) ══ */
  [data-testid="stSidebarCollapseButton"] button {
    background: #1a1a1a !important;
    border: 1px solid rgba(226,55,68,0.3) !important;
    border-radius: 10px !important;
    width: 36px !important; height: 36px !important;
    min-width: 36px !important; min-height: 36px !important;
    padding: 0 !important;
    position: relative !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    transition: background .2s, border-color .2s !important;
    overflow: hidden !important;
  }
  /* ══ SIDEBAR TOGGLE — collapsed state (stBaseButton-headerNoPadding) ══ */
  [data-testid="stBaseButton-headerNoPadding"] {
    background: #1a1a1a !important;
    border: 1px solid rgba(226,55,68,0.3) !important;
    border-radius: 10px !important;
    width: 36px !important; height: 36px !important;
    min-width: 36px !important; min-height: 36px !important;
    padding: 0 !important;
    position: relative !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    transition: background .2s, border-color .2s !important;
    overflow: hidden !important;
  }
  [data-testid="stSidebarCollapseButton"] button:hover,
  [data-testid="stBaseButton-headerNoPadding"]:hover {
    background: rgba(226,55,68,0.15) !important;
    border-color: rgba(226,55,68,0.6) !important;
  }
  /* Hide SVG + stIconMaterial text in both states */
  [data-testid="stSidebarCollapseButton"] button svg,
  [data-testid="stBaseButton-headerNoPadding"] svg,
  [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
  [data-testid="stBaseButton-headerNoPadding"] [data-testid="stIconMaterial"],
  [data-testid="stSidebarCollapseButton"] span,
  [data-testid="stBaseButton-headerNoPadding"] span {
    display: none !important;
    visibility: hidden !important;
    font-size: 0 !important;
    width: 0 !important; height: 0 !important;
    overflow: hidden !important;
  }
  /* Static ☰ — always red, perfectly centered, both states */
  [data-testid="stSidebarCollapseButton"] button::before,
  [data-testid="stBaseButton-headerNoPadding"]::before {
    content: '☰';
    font-family: Arial, sans-serif !important;
    font-size: 1.1rem;
    color: #E23744;
    line-height: 1;
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    display: block !important;
    visibility: visible !important;
  }
  [data-testid="stSidebarCollapseButton"] button::after,
  [data-testid="stBaseButton-headerNoPadding"]::after { display: none !important; }

  /* ── TABS ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #141414 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid #2a2a2a !important;
    gap: 4px !important;
    display: flex !important;
    width: 100% !important;
  }
  .stTabs [data-baseweb="tab"] {
    flex: 1 !important;
    text-align: center !important;
    justify-content: center !important;
    color: #666 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    transition: all .2s !important;
    white-space: nowrap !important;
  }
  .stTabs [data-baseweb="tab"]:hover { color: #ccc !important; background: #1e1e1e !important; }
  .stTabs [aria-selected="true"] {
    color: #E23744 !important;
    background: rgba(226,55,68,0.12) !important;
    border-bottom: none !important;
  }
  .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
  .stTabs [data-baseweb="tab-border"]    { display: none !important; }

  /* ── MAIN CONTENT PADDING ── */
  [data-testid="stMain"] .block-container {
    padding-top: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
  }

  /* ── METRIC CARDS ── */
  .metric-card {
    background: linear-gradient(135deg, #1a1a1a 0%, #161616 100%);
    border: 1px solid #2a2a2a;
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
    transition: border-color .25s, transform .2s;
    position: relative;
    overflow: hidden;
    min-height: 90px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #E23744, #FF6B35);
    opacity: 0; transition: opacity .3s;
  }
  .metric-card:hover { border-color: rgba(226,55,68,0.35); transform: translateY(-2px); }
  .metric-card:hover::before { opacity: 1; }
  .metric-val {
    font-size: clamp(1rem, 1.8vw, 1.55rem);
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .metric-lbl {
    font-size: 0.65rem;
    color: #555;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: .07em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* ── PLOTLY CHARTS ── */
  .js-plotly-plot { border-radius: 12px !important; }

  /* ── SECTION DIVIDERS ── */
  hr { border-color: #1e1e1e !important; }

  /* ── GENERAL TEXT ── */
  h1,h2,h3,h4,h5 { color: #f0f0f0 !important; }
  p, li { color: #ccc; }
</style>
""", unsafe_allow_html=True)

RED    = "#E23744"
ORANGE = "#FF6B35"
GOLD   = "#FFD700"
GREEN  = "#4CAF50"
BLUE   = "#2196F3"
BG     = "#1e1e1e"
GRID   = "#2a2a2a"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#111111", plot_bgcolor="#111111",
    font=dict(color="#cccccc", family="Inter, sans-serif", size=12),
    xaxis=dict(gridcolor="#1e1e1e", linecolor="#2a2a2a", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#1e1e1e", linecolor="#2a2a2a", tickfont=dict(size=11)),
    margin=dict(l=10, r=10, t=52, b=10),
    legend=dict(bgcolor="#111111", bordercolor="#2a2a2a", borderwidth=1),
)

def CL(title_text="", **extra):
    """chart_layout: merges PLOTLY_LAYOUT with a styled title + any extras."""
    return {
        **PLOTLY_LAYOUT,
        "title": dict(
            text=title_text,
            font=dict(size=14, color="#e0e0e0"),
            x=0, xanchor="left",
            pad=dict(l=4)
        ),
        **extra
    }

# ── LOAD DATA ────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "Data")

@st.cache_data(show_spinner="Loading and preparing datasets…")
def load_data():
    orders   = pd.read_csv(f"{DATA}/orders.csv",   parse_dates=["order_date"])
    users    = pd.read_csv(f"{DATA}/users.csv")
    rests    = pd.read_csv(f"{DATA}/restaurants.csv")
    delivery = pd.read_csv(f"{DATA}/delivery.csv", parse_dates=["order_date"])
    reviews  = pd.read_csv(f"{DATA}/reviews.csv",  parse_dates=["review_date"])

    orders_rich = (
        orders
        .merge(users[["user_id","city","gender","is_gold_member","age","occupation"]], on="user_id", how="left")
        .merge(rests[["restaurant_id","name","cuisine","restaurant_type","rating"]], on="restaurant_id", how="left", suffixes=("","_rest"))
    )
    orders_rich["order_hour"] = pd.to_datetime(orders_rich["order_time"], format="%H:%M:%S", errors="coerce").dt.hour
    orders_rich["month"]      = orders_rich["order_date"].dt.to_period("M").astype(str)

    del_full = delivery.merge(
        orders_rich[["order_id", "city", "cuisine", "order_time", "order_hour", "order_date"]], 
        on="order_id", how="left", suffixes=("", "_order")
    )
    
    rev_full = reviews.merge(
        orders_rich[["order_id", "city", "cuisine", "is_gold_member"]],
        on="order_id", how="left"
    )
    
    return orders_rich, del_full, rev_full, rests

orders_rich, del_full, rev_full, rests = load_data()

# ── SIDEBAR ──────────────────────────────────────────────
all_cities   = sorted(orders_rich["city"].dropna().unique().tolist())
all_cuisines = sorted(orders_rich["cuisine"].dropna().unique().tolist())
date_min = orders_rich["order_date"].min().date()
date_max = orders_rich["order_date"].max().date()

# ── Brand header
st.sidebar.markdown("""
<div style='
  background: linear-gradient(135deg, rgba(226,55,68,0.15) 0%, rgba(255,107,53,0.08) 100%);
  border: 1px solid rgba(226,55,68,0.25);
  border-radius: 16px;
  padding: 20px 16px;
  margin-bottom: 8px;
  text-align: center;
'>
  <div style='font-size:2rem; margin-bottom:6px;'>🍕</div>
  <div style='font-size:1.15rem; font-weight:900; color:#ffffff; letter-spacing:-.01em;'>
    Zomato <span style='color:#E23744;'>Analytics</span>
  </div>
  <div style='font-size:.72rem; color:#666; margin-top:4px; text-transform:uppercase; letter-spacing:.1em;'>
    Data Intelligence Platform
  </div>
</div>
""", unsafe_allow_html=True)

# ── Filter section header
st.sidebar.markdown("""
<div style='display:flex;align-items:center;gap:8px;margin:16px 0 12px;'>
  <div style='height:1px;flex:1;background:linear-gradient(90deg,rgba(226,55,68,0.4),transparent);'></div>
  <span style='color:#E23744;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;'>⚙ Filters</span>
  <div style='height:1px;flex:1;background:linear-gradient(90deg,transparent,rgba(226,55,68,0.4));'></div>
</div>
""", unsafe_allow_html=True)

# ── City
st.sidebar.markdown("<p style='color:#888;font-size:.75rem;font-weight:600;margin:0 0 4px;text-transform:uppercase;letter-spacing:.08em;'>🏙️ City</p>", unsafe_allow_html=True)
sel_cities = st.sidebar.multiselect(
    "", all_cities, default=all_cities, label_visibility="collapsed"
)

# ── Cuisine
st.sidebar.markdown("<p style='color:#888;font-size:.75rem;font-weight:600;margin:8px 0 4px;text-transform:uppercase;letter-spacing:.08em;'>🍽️ Cuisine</p>", unsafe_allow_html=True)
sel_cuisines = st.sidebar.multiselect(
    "", all_cuisines, default=all_cuisines, label_visibility="collapsed"
)

# ── Date Range
st.sidebar.markdown("<p style='color:#888;font-size:.75rem;font-weight:600;margin:8px 0 4px;text-transform:uppercase;letter-spacing:.08em;'>📅 Date Range</p>", unsafe_allow_html=True)
sel_dates = st.sidebar.date_input(
    "",
    value=(date_min, date_max),
    min_value=date_min, max_value=date_max,
    label_visibility="collapsed"
)

# ── Order Status
st.sidebar.markdown("<p style='color:#888;font-size:.75rem;font-weight:600;margin:8px 0 4px;text-transform:uppercase;letter-spacing:.08em;'>📦 Order Status</p>", unsafe_allow_html=True)
sel_status = st.sidebar.selectbox(
    "", ["All", "Delivered", "Cancelled", "Pending"],
    label_visibility="collapsed"
)

# ── Member Type
st.sidebar.markdown("<p style='color:#888;font-size:.75rem;font-weight:600;margin:8px 0 4px;text-transform:uppercase;letter-spacing:.08em;'>💛 Member Type</p>", unsafe_allow_html=True)
sel_member = st.sidebar.radio(
    "", ["All", "Gold Members", "Regular Members"],
    label_visibility="collapsed"
)

# ── Live Stats
st.sidebar.markdown("""
<div style='
  background: #111;
  border: 1px solid #222;
  border-radius: 12px;
  padding: 14px 16px;
  margin-top: 20px;
'>
  <div style='font-size:.68rem;color:#555;text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;'>📊 Dataset Info</div>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>
    <div style='text-align:center;'>
      <div style='font-size:1.1rem;font-weight:800;color:#E23744;'>567K+</div>
      <div style='font-size:.65rem;color:#555;margin-top:2px;'>Total Rows</div>
    </div>
    <div style='text-align:center;'>
      <div style='font-size:1.1rem;font-weight:800;color:#FF6B35;'>6</div>
      <div style='font-size:.65rem;color:#555;margin-top:2px;'>SQL Tables</div>
    </div>
    <div style='text-align:center;'>
      <div style='font-size:1.1rem;font-weight:800;color:#FFD700;'>40+</div>
      <div style='font-size:.65rem;color:#555;margin-top:2px;'>SQL Queries</div>
    </div>
    <div style='text-align:center;'>
      <div style='font-size:1.1rem;font-weight:800;color:#4CAF50;'>3</div>
      <div style='font-size:.65rem;color:#555;margin-top:2px;'>ML Models</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── APPLY FILTERS ────────────────────────────────────────
df = orders_rich.copy()

if sel_cities:
    df = df[df["city"].isin(sel_cities)]
if sel_cuisines:
    df = df[df["cuisine"].isin(sel_cuisines)]
if len(sel_dates) == 2:
    df = df[(df["order_date"].dt.date >= sel_dates[0]) &
            (df["order_date"].dt.date <= sel_dates[1])]
if sel_status != "All":
    df = df[df["order_status"] == sel_status]
if sel_member == "Gold Members":
    df = df[df["is_gold_member"] == 1]
elif sel_member == "Regular Members":
    df = df[df["is_gold_member"] == 0]

delivered = df[df["order_status"] == "Delivered"]

# Cascaded subsets for performance
valid_order_ids = set(df["order_id"])
del_filtered = del_full[del_full["order_id"].isin(valid_order_ids)].copy()
rev_filtered = rev_full[rev_full["order_id"].isin(valid_order_ids)].copy()

# ── HEADER ───────────────────────────────────────────────
date_range_str = f"{sel_dates[0]} &rarr; {sel_dates[1]}" if len(sel_dates) == 2 else "All dates"
st.markdown(f"""
<div style='margin-bottom:1.5rem;'>
  <h1 style='font-size:clamp(1.6rem,3vw,2.2rem);font-weight:900;margin:0 0 6px;line-height:1.1;'>
    🍕 Zomato <span style='color:{RED};'>Analytics</span> Dashboard
  </h1>
  <div style='display:flex;flex-wrap:wrap;gap:8px;align-items:center;'>
    <span style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:3px 12px;font-size:.78rem;color:#aaa;'>
      📦 <b style='color:white;'>{len(df):,}</b> orders
    </span>
    <span style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:3px 12px;font-size:.78rem;color:#aaa;'>
      🏙️ <b style='color:white;'>{len(sel_cities)}</b> cities
    </span>
    <span style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:3px 12px;font-size:.78rem;color:#aaa;'>
      📅 {date_range_str}
    </span>
    <span style='background:rgba(226,55,68,0.12);border:1px solid rgba(226,55,68,0.3);border-radius:20px;padding:3px 12px;font-size:.78rem;color:#E23744;font-weight:600;'>
      {sel_member}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI ROW ──────────────────────────────────────────────
total_rev  = delivered["final_amount"].sum()
total_ord  = len(df)
aov        = delivered["final_amount"].mean() if len(delivered) else 0
active_usr = df["user_id"].nunique()
delay_rt   = del_filtered["delay_flag"].mean() * 100 if len(del_filtered) else 0
cancel_rt  = (df["order_status"] == "Cancelled").mean() * 100 if len(df) else 0

# Abbreviate large numbers so they never overflow the card
def fmt_inr(v):
    if v >= 1_000_000: return f"₹{v/1_000_000:.1f}M"
    if v >= 1_000:     return f"₹{v/1_000:.1f}K"
    return f"₹{v:.0f}"

kpis = [
    (fmt_inr(total_rev), "Total Revenue"),
    (f"{total_ord:,}",   "Total Orders"),
    (fmt_inr(aov),       "Avg Order Value"),
    (f"{active_usr:,}",  "Active Users"),
    (f"{delay_rt:.1f}%", "Delay Rate"),
    (f"{cancel_rt:.1f}%","Cancel Rate"),
]

cols = st.columns(6)
for col, (val, lbl) in zip(cols, kpis):
    col.markdown(f"""
    <div class="metric-card">
      <div class="metric-val">{val}</div>
      <div class="metric-lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Revenue & Orders",
    "👥 Customer Insights",
    "🚴 Delivery Analytics",
    "⭐ Restaurant Performance"
])

# ════════════════════════════════════════════════════════
# TAB 1: REVENUE & ORDERS
# ════════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)

    # Monthly Revenue Trend
    with c1:
        monthly = delivered.groupby("month")["final_amount"].sum().reset_index()
        monthly.columns = ["month","revenue"]
        fig = px.area(monthly, x="month", y="revenue",
                      title="📈 Monthly Revenue Trend",
                      color_discrete_sequence=[RED])
        fig.update_layout(**CL(""))
        fig.update_traces(fillcolor=f"rgba(226,55,68,0.15)", line_color=RED)
        fig.update_yaxes(tickprefix="₹")
        st.plotly_chart(fig, use_container_width=True)

    # Revenue by City
    with c2:
        city_rev = delivered.groupby("city")["final_amount"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(city_rev, x="city", y="final_amount",
                     title="🏙️ Revenue by City",
                     color="final_amount",
                     color_continuous_scale=[[0,"#2a2a2a"],[1, RED]])
        fig.update_layout(**CL("", coloraxis_showscale=False))
        fig.update_yaxes(tickprefix="₹")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    # Peak Hour
    with c3:
        hourly = df.groupby("order_hour").size().reset_index(name="orders")
        hourly["color"] = hourly["order_hour"].apply(
            lambda h: RED if h in [12,13,19,20,21] else ORANGE if h in [11,14,18,22] else "#444"
        )
        fig = go.Figure(go.Bar(
            x=hourly["order_hour"], y=hourly["orders"],
            marker_color=hourly["color"], name="Orders"
        ))
        fig.update_layout(**CL("⏰ Order Volume by Hour"))
        fig.update_xaxes(title="Hour of Day", dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    # Revenue by Cuisine
    with c4:
        cuis_rev = delivered.groupby("cuisine")["final_amount"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(cuis_rev, x="final_amount", y="cuisine", orientation="h",
                     title="🍽️ Top 10 Cuisines by Revenue",
                     color="final_amount",
                     color_continuous_scale=[[0,"#2a2a2a"],[1, ORANGE]])
        fig.update_layout(**CL("", coloraxis_showscale=False))
        fig.update_xaxes(tickprefix="₹")
        st.plotly_chart(fig, use_container_width=True)

    # Payment Mode — in columns to avoid full-width stretch
    pay_dist = df["payment_mode"].value_counts().reset_index()
    pay_dist.columns = ["mode","count"]
    pc1, pc2 = st.columns([1, 1])
    with pc1:
        fig = px.pie(pay_dist, names="mode", values="count",
                     title="💳 Payment Mode Split",
                     hole=0.4,
                     color_discrete_sequence=[RED, ORANGE, GOLD, GREEN, BLUE])
        fig.update_layout(**CL(""))
        fig.update_traces(textfont_color="white", textposition="inside")
        st.plotly_chart(fig, use_container_width=True)
    with pc2:
        # Order status breakdown alongside
        status_dist = df["order_status"].value_counts().reset_index()
        status_dist.columns = ["status","count"]
        fig2 = px.pie(status_dist, names="status", values="count",
                      title="📦 Order Status Split",
                      hole=0.4,
                      color_discrete_sequence=[GREEN, RED, ORANGE, BLUE])
        fig2.update_layout(**CL(""))
        fig2.update_traces(textfont_color="white", textposition="inside")
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 2: CUSTOMER INSIGHTS
# ════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    # Gold vs Regular
    with c1:
        gold_agg = delivered.groupby("is_gold_member").agg(
            avg_order=("final_amount","mean"),
            avg_discount=("discount_amount","mean"),
            total_orders=("order_id","count")
        ).reset_index()
        gold_agg["type"] = gold_agg["is_gold_member"].map({0:"Regular",1:"💛 Gold"})

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Avg Order Value (₹)",
                             x=gold_agg["type"], y=gold_agg["avg_order"],
                             marker_color=[RED, GOLD]))
        fig.update_layout(**CL("💛 Gold vs Regular: Avg Order Value"))
        st.plotly_chart(fig, use_container_width=True)

    # Age Group
    with c2:
        age_df = delivered.copy()
        age_df["age_group"] = pd.cut(age_df["age"],
            bins=[0,21,35,50,100],
            labels=["Gen Z (<22)","Millennials (22-35)","Gen X (36-50)","Boomers (50+)"])
        age_rev = age_df.groupby("age_group", observed=True)["final_amount"].sum().reset_index()
        fig = px.pie(age_rev, names="age_group", values="final_amount",
                     title="👥 Revenue by Age Group",
                     color_discrete_sequence=[RED, ORANGE, GOLD, GREEN])
        fig.update_layout(**CL(""))
        fig.update_traces(textfont_color="white")
        st.plotly_chart(fig, use_container_width=True)

    # RFM Segmentation
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin:28px 0 16px;'>
      <div style='height:1px;flex:1;background:linear-gradient(90deg,rgba(226,55,68,0.4),transparent);'></div>
      <span style='color:#E23744;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;white-space:nowrap;'>🎯 RFM Customer Segmentation</span>
      <div style='height:1px;flex:1;background:linear-gradient(90deg,transparent,rgba(226,55,68,0.4));'></div>
    </div>
    """, unsafe_allow_html=True)

    if len(delivered) < 50:
        st.info("⚠️ Not enough data for RFM segmentation with current filters. Try expanding your selection.")
    else:
        ref_date = delivered["order_date"].max()
        rfm = delivered.groupby("user_id").agg(
            recency=("order_date", lambda x: (ref_date - x.max()).days),
            frequency=("order_id","count"),
            monetary=("final_amount","sum")
        ).reset_index().dropna()

        rfm["r"] = pd.qcut(rfm["recency"].rank(method="first"),  5, labels=[5,4,3,2,1], duplicates="drop").astype(int)
        rfm["f"] = pd.qcut(rfm["frequency"].rank(method="first"),5, labels=[1,2,3,4,5], duplicates="drop").astype(int)

        def seg(row):
            r, f = row["r"], row["f"]
            if r>=4 and f>=4: return "Champions"
            elif r>=3 and f>=3: return "Loyal"
            elif r>=4 and f<2:  return "New Customers"
            elif 2<=r<=3 and f>=3: return "Potential Loyalists"
            elif r<2 and f>=3: return "At Risk"
            elif r<2 and f<2:  return "Lost"
            return "Needs Attention"

        rfm["segment"] = rfm.apply(seg, axis=1)
        seg_cnt = rfm["segment"].value_counts().reset_index()
        seg_cnt.columns = ["segment","count"]

        col_map = {
            "Champions":"#FFD700","Loyal":"#E23744","New Customers":"#4CAF50",
            "Potential Loyalists":"#FF6B35","At Risk":"#FF5722",
            "Lost":"#607D8B","Needs Attention":"#9C27B0"
        }

        c3, c4 = st.columns([1,1])
        with c3:
            fig = px.pie(seg_cnt, names="segment", values="count", hole=0.45,
                         color="segment", color_discrete_map=col_map,
                         title="RFM Segment Distribution")
            fig.update_layout(**CL("RFM Segment Distribution"))
            fig.update_traces(textfont_color="white")
            st.plotly_chart(fig, use_container_width=True)

        with c4:
            seg_rev = rfm.merge(
                delivered.groupby("user_id")["final_amount"].sum().reset_index(),
                on="user_id", how="left"
            ).groupby("segment")["final_amount"].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(seg_rev, x="segment", y="final_amount",
                         title="Revenue by RFM Segment",
                         color="final_amount",
                         color_continuous_scale=[[0,"#2a2a2a"],[1, RED]])
            fig.update_layout(**CL("Revenue by RFM Segment", coloraxis_showscale=False))
            fig.update_yaxes(tickprefix="₹")
            st.plotly_chart(fig, use_container_width=True)

    # Occupation breakdown
    occ_rev = delivered.groupby("occupation")["final_amount"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(occ_rev, x="occupation", y="final_amount",
                 title="💼 Revenue by Occupation",
                 color="final_amount",
                 color_continuous_scale=[[0,"#2a2a2a"],[1, ORANGE]])
    fig.update_layout(**CL("", coloraxis_showscale=False))
    fig.update_yaxes(tickprefix="₹")
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 3: DELIVERY ANALYTICS
# ════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    # Delay rate by city
    with c1:
        city_delay = del_filtered.groupby("city")["delay_flag"].mean().mul(100).sort_values(ascending=False).reset_index()
        city_delay.columns = ["city","delay_rate"]
        city_delay["color"] = city_delay["delay_rate"].apply(
            lambda x: RED if x>30 else ORANGE if x>20 else GREEN
        )
        fig = go.Figure(go.Bar(
            x=city_delay["city"], y=city_delay["delay_rate"],
            marker_color=city_delay["color"],
            text=city_delay["delay_rate"].round(1).astype(str)+"%",
            textposition="outside"
        ))
        fig.update_layout(**CL("🚴 Delay Rate by City (%)"))
        st.plotly_chart(fig, use_container_width=True)

    # Avg delivery time by city
    with c2:
        city_time = del_filtered.groupby("city")["actual_time_min"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(city_time, x="actual_time_min", y="city", orientation="h",
                     title="⏱️ Avg Delivery Time by City (min)",
                     color="actual_time_min",
                     color_continuous_scale=[[0, GREEN],[0.5, ORANGE],[1, RED]])
        fig.update_layout(**CL("", coloraxis_showscale=False))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    # Peak vs Off-peak
    with c3:
        peak_grp = del_filtered.groupby("is_peak_hour").agg(
            deliveries=("delivery_id","count"),
            delay_rate=("delay_flag","mean"),
            avg_time=("actual_time_min","mean")
        ).reset_index()
        peak_grp["label"] = peak_grp["is_peak_hour"].map({0:"Off-Peak",1:"Peak Hour"})
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Delay Rate %",
            x=peak_grp["label"],
            y=(peak_grp["delay_rate"]*100).round(1),
            marker_color=[GREEN, RED], text=(peak_grp["delay_rate"]*100).round(1),
            textposition="outside"
        ))
        fig.update_layout(**CL("⚡ Peak vs Off-Peak Delay Rate"))
        st.plotly_chart(fig, use_container_width=True)

    # Distance tiers
    with c4:
        del_filtered["distance_tier"] = pd.cut(
            del_filtered["distance_km"],
            bins=[0,2,5,10,100],
            labels=["<2 km","2–5 km","5–10 km",">10 km"]
        )
        dist_grp = del_filtered.groupby("distance_tier", observed=True)["delay_flag"].mean().mul(100).reset_index()
        dist_grp.columns = ["distance_tier","delay_rate"]
        fig = px.bar(dist_grp, x="distance_tier", y="delay_rate",
                     title="📍 Delay Rate by Distance Tier",
                     color="delay_rate",
                     color_continuous_scale=[[0, GREEN],[0.5, ORANGE],[1, RED]],
                     text=dist_grp["delay_rate"].round(1))
        fig.update_layout(**CL("", coloraxis_showscale=False))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # Weekend vs Weekday
    wk_grp = del_filtered.groupby("is_weekend").agg(
        orders=("delivery_id","count"),
        delay_rate=("delay_flag","mean"),
        avg_time=("actual_time_min","mean")
    ).reset_index()
    wk_grp["label"] = wk_grp["is_weekend"].map({0:"Weekday",1:"Weekend"})

    c5, c6 = st.columns(2)
    with c5:
        fig = px.bar(wk_grp, x="label", y=wk_grp["delay_rate"]*100,
                     title="📅 Weekend vs Weekday Delay Rate",
                     color="label",
                     color_discrete_map={"Weekday":BLUE,"Weekend":RED})
        fig.update_layout(**CL("", showlegend=False))
        fig.update_yaxes(title="Delay Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    with c6:
        fig = px.bar(wk_grp, x="label", y="avg_time",
                     title="📅 Weekend vs Weekday Avg Delivery Time",
                     color="label",
                     color_discrete_map={"Weekday":BLUE,"Weekend":RED})
        fig.update_layout(**CL("", showlegend=False))
        fig.update_yaxes(title="Avg Time (min)")
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 4: RESTAURANT PERFORMANCE
# ════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)

    # Top 10 restaurants by revenue
    with c1:
        top_rest = (
            delivered.groupby("restaurant_id")["final_amount"].sum()
            .reset_index()
            .merge(rests[["restaurant_id","name","city"]], on="restaurant_id")
            .sort_values("final_amount", ascending=False)
            .head(10)
        )
        fig = px.bar(top_rest, x="final_amount", y="name", orientation="h",
                     title="🏆 Top 10 Restaurants by Revenue",
                     color="final_amount",
                     color_continuous_scale=[[0,"#2a2a2a"],[1, RED]],
                     hover_data=["city"])
        fig.update_layout(**CL("", coloraxis_showscale=False))
        fig.update_xaxes(tickprefix="₹")
        st.plotly_chart(fig, use_container_width=True)

    # Rating distribution
    with c2:
        rat_df = rests[rests["city"].isin(sel_cities)] if sel_cities else rests
        fig = px.histogram(rat_df, x="rating", nbins=20,
                           title="⭐ Restaurant Rating Distribution",
                           color_discrete_sequence=[ORANGE])
        fig.update_layout(**CL(""))
        st.plotly_chart(fig, use_container_width=True)

    # Sentiment by city
    sent_city = rev_filtered.groupby(["city", "sentiment"]).size().reset_index(name="count")
    sent_pct = sent_city.pivot(index="city", columns="sentiment", values="count").fillna(0).reset_index()

    fig = go.Figure()
    colors = {"Positive": GREEN, "Neutral": ORANGE, "Negative": RED}
    for sent in ["Positive","Neutral","Negative"]:
        if sent in sent_pct.columns:
            fig.add_trace(go.Bar(
                name=sent, x=sent_pct["city"], y=sent_pct[sent],
                marker_color=colors[sent]
            ))
    fig.update_layout(**CL("⭐ Review Sentiment by City (%)", barmode="stack"))
    fig.update_yaxes(title="Percentage (%)")
    st.plotly_chart(fig, use_container_width=True)

    # Revenue vs Rating scatter
    rest_data = (
        delivered.groupby("restaurant_id")["final_amount"].sum()
        .reset_index()
        .merge(rests[["restaurant_id","name","city","rating","cuisine"]], on="restaurant_id")
    )
    if sel_cities:
        rest_data = rest_data[rest_data["city"].isin(sel_cities)]
    fig = px.scatter(rest_data, x="rating", y="final_amount",
                     color="city", hover_name="name",
                     hover_data=["cuisine"],
                     title="📊 Revenue vs Rating (per Restaurant)",
                     opacity=0.6,
                     color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(**CL(""))
    fig.update_yaxes(tickprefix="₹", title="Revenue")
    fig.update_xaxes(title="Restaurant Rating")
    st.plotly_chart(fig, use_container_width=True)

# ── FOOTER ───────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#555;font-size:.82rem;'>"
    "🍕 Zomato End-to-End Data Analytics · 567K+ rows · 6 tables · "
    "Streamlit + Plotly Interactive Dashboard</p>",
    unsafe_allow_html=True
)
