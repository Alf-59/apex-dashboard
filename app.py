import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Apex Intelligence", layout="wide")

# STYLE
st.markdown("""
<style>
body {
    background-color: #0b0f19;
    color: white;
}

.block-container {
    padding-top: 2rem;
    max-width: 900px;
}

.kpi {
    font-size: 26px;
    font-weight: 600;
}

.label {
    color: #9ca3af;
    font-size: 13px;
}

.card {
    background-color: #111827;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# TITLE
st.markdown("# Apex Fund – Investor Briefing")

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

services = ["FCR", "aFRR", "mFRR"]
df["Service"] = np.random.choice(services, len(df))

# KPI CALC
total = int(df["Revenue"].sum())
today = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())
best_site = df.groupby("Site")["Revenue"].sum().idxmax()

# ===== SUMMARY CARD =====
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<div class='label'>Total Revenue</div><div class='kpi'>{total:,.0f} DKK</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='label'>Today</div><div class='kpi'>{today:,.0f} DKK</div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='label'>Top Asset</div><div class='kpi'>{best_site}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===== AI / INSIGHT =====
st.markdown("### Market Intelligence")

st.markdown('<div class="card">', unsafe_allow_html=True)

st.write("""
Revenue performance is currently driven by volatility in ancillary services.

• FCR remains the dominant contributor in stable grid conditions  
• aFRR and mFRR provide upside during imbalance periods  
• Portfolio performance is stable across assets  

The current best performing asset is highlighted above.
""")

st.markdown('</div>', unsafe_allow_html=True)

# ===== SIMPLE TABLE =====
st.markdown("### Portfolio Overview")

site_table = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()

st.dataframe(site_table, use_container_width=True)

# ===== OPTIONAL SMALL CHART =====
st.markdown("### Trend")

daily = df.groupby("Date")["Revenue"].sum().reset_index()

st.line_chart(daily.set_index("Date"))
