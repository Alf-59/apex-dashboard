import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page setup
st.set_page_config(page_title="Apex Fund", layout="wide")

# Simple styling
st.markdown("""
<style>
.big-font {font-size:28px !important; font-weight:600;}
.metric-card {
    background-color: #111;
    padding: 15px;
    border-radius: 10px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="big-font">Apex Fund Performance</p>', unsafe_allow_html=True)

# Fake data
np.random.seed(42)
dates = pd.date_range(start="2025-01-01", periods=180)
sites = [f"BESS_{i}" for i in range(1, 11)]

data = []
for site in sites:
    revenue = np.random.normal(loc=50000, scale=15000, size=len(dates))
    revenue = np.maximum(revenue, 0)
    for i in range(len(dates)):
        data.append([dates[i], site, revenue[i]])

df = pd.DataFrame(data, columns=["Date", "Site", "Revenue"])

# Add services
services = ["FCR", "aFRR", "mFRR"]
df["Service"] = np.random.choice(services, size=len(df))

# KPIs
total_revenue = int(df["Revenue"].sum())
today_revenue = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())
avg_per_site = int(df.groupby("Site")["Revenue"].mean().mean())

col1, col2, col3 = st.columns(3)

col1.markdown(f"<div class='metric-card'>Total Revenue<br><b>{total_revenue:,.0f} DKK</b></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'>Revenue Today<br><b>{today_revenue:,.0f} DKK</b></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'>Avg per Site<br><b>{avg_per_site:,.0f} DKK</b></div>", unsafe_allow_html=True)

# Daily chart
daily = df.groupby("Date")["Revenue"].sum().reset_index()
fig = px.line(daily, x="Date", y="Revenue", title="Daily Revenue")
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Two columns layout
colA, colB = st.columns(2)

with colA:
    site_rev = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()
    fig2 = px.bar(site_rev, x="Site", y="Revenue", title="Revenue per Site")
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

with colB:
    service_rev = df.groupby("Service")["Revenue"].sum().reset_index()
    fig3 = px.pie(service_rev, names="Service", values="Revenue", title="Revenue by Service")
    fig3.update_layout(template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

# Best site
best_site = df.groupby("Site")["Revenue"].sum().idxmax()

st.markdown(f"### Best performing site: {best_site}")

# Insight
st.markdown("### Performance Insight")
st.write("""
Revenue is driven by volatility in ancillary service markets.
FCR dominates stable periods, while aFRR/mFRR increase during demand spikes.
""")
