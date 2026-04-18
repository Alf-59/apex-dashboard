import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page config
st.set_page_config(page_title="Apex Fund", layout="wide")

# ====== STYLING ======
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.metric-box {
    background: linear-gradient(135deg, #111827, #1f2937);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
}

.metric-title {
    font-size: 14px;
    color: #9ca3af;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ====== TITLE ======
st.markdown("## Apex Fund Performance")

# ====== FAKE DATA ======
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

# Services
services = ["FCR", "aFRR", "mFRR"]
df["Service"] = np.random.choice(services, size=len(df))

# ====== KPI ======
total_revenue = int(df["Revenue"].sum())
today_revenue = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())
avg_per_site = int(df.groupby("Site")["Revenue"].mean().mean())

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="metric-box">
<div class="metric-title">Total Revenue</div>
<div class="metric-value">{total_revenue:,.0f} DKK</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="metric-box">
<div class="metric-title">Revenue Today</div>
<div class="metric-value">{today_revenue:,.0f} DKK</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="metric-box">
<div class="metric-title">Avg per Site</div>
<div class="metric-value">{avg_per_site:,.0f} DKK</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ====== DAILY CHART ======
daily = df.groupby("Date")["Revenue"].sum().reset_index()
fig = px.line(daily, x="Date", y="Revenue")
fig.update_layout(
    template="plotly_dark",
    title="Daily Revenue",
    margin=dict(l=0, r=0, t=40, b=0)
)
st.plotly_chart(fig, use_container_width=True)

# ====== 2 COLUMN LAYOUT ======
colA, colB = st.columns(2)

with colA:
    site_rev = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()
    fig2 = px.bar(site_rev, x="Site", y="Revenue")
    fig2.update_layout(template="plotly_dark", title="Revenue per Site")
    st.plotly_chart(fig2, use_container_width=True)

with colB:
    service_rev = df.groupby("Service")["Revenue"].sum().reset_index()
    fig3 = px.pie(service_rev, names="Service", values="Revenue")
    fig3.update_layout(template="plotly_dark", title="Revenue by Service")
    st.plotly_chart(fig3, use_container_width=True)

# ====== BEST SITE ======
best_site = df.groupby("Site")["Revenue"].sum().idxmax()
st.markdown(f"### Best performing asset: **{best_site}**")

# ====== INSIGHT ======
st.markdown("### Performance Insight")
st.write("""
Revenue is primarily driven by volatility in ancillary services.

FCR dominates stable periods, while aFRR and mFRR increase during demand spikes.
""")
