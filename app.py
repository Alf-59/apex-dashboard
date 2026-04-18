import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Apex Intelligence", layout="centered")

# ===== STYLE =====
st.markdown("""
<style>
body {
    background-color: #0b0f19;
    color: #e5e7eb;
}

.block-container {
    padding-top: 3rem;
    max-width: 800px;
}

/* Title */
.title {
    font-size: 34px;
    font-weight: 600;
    margin-bottom: 30px;
}

/* Cards */
.card {
    background: #111827;
    padding: 24px;
    border-radius: 14px;
    margin-bottom: 20px;
}

/* KPI */
.kpi-label {
    font-size: 12px;
    color: #9ca3af;
}

.kpi-value {
    font-size: 28px;
    font-weight: 600;
    margin-top: 4px;
}

/* Section titles */
.section {
    margin-top: 30px;
    margin-bottom: 10px;
    font-size: 16px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Divider */
.divider {
    height: 1px;
    background: #1f2937;
    margin: 30px 0;
}
</style>
""", unsafe_allow_html=True)

# ===== TITLE =====
st.markdown('<div class="title">Apex Fund — Investor Intelligence</div>', unsafe_allow_html=True)

# ===== DATA =====
np.random.seed(42)
dates = pd.date_range(start="2025-01-01", periods=180)
sites = [f"BESS_{i}" for i in range(1, 11)]

data = []
for site in sites:
    revenue = np.random.normal(50000, 15000, len(dates))
    revenue = np.maximum(revenue, 0)
    for i in range(len(dates)):
        data.append([dates[i], site, revenue[i]])

df = pd.DataFrame(data, columns=["Date", "Site", "Revenue"])

# KPI
total = int(df["Revenue"].sum())
today = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())
best_site = df.groupby("Site")["Revenue"].sum().idxmax()

# ===== KPI CARD =====
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<div class='kpi-label'>Total Revenue</div><div class='kpi-value'>{total:,.0f} DKK</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='kpi-label'>Revenue Today</div><div class='kpi-value'>{today:,.0f} DKK</div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='kpi-label'>Top Asset</div><div class='kpi-value'>{best_site}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===== INTELLIGENCE =====
st.markdown('<div class="section">Market Intelligence</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("""
**Current performance is stable across the portfolio.**

Revenue is primarily driven by ancillary service volatility:

- FCR dominates during stable grid conditions  
- aFRR / mFRR increase during imbalance periods  
- Asset performance is evenly distributed  

**No immediate risk signals detected.**
""")

st.markdown('</div>', unsafe_allow_html=True)

# ===== PORTFOLIO =====
st.markdown('<div class="section">Portfolio Ranking</div>', unsafe_allow_html=True)

site_table = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()

st.markdown('<div class="card">', unsafe_allow_html=True)
st.dataframe(site_table, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== TREND =====
st.markdown('<div class="section">Revenue Trend</div>', unsafe_allow_html=True)

daily = df.groupby("Date")["Revenue"].sum().reset_index()

st.markdown('<div class="card">', unsafe_allow_html=True)
st.line_chart(daily.set_index("Date"))
st.markdown('</div>', unsafe_allow_html=True)
