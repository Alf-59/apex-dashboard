import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Apex Intelligence", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {
    background-color: #05070d;
}

.big-title {
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 10px;
}

.kpi-card {
    background: linear-gradient(135deg, #0f172a, #020617);
    padding: 20px;
    border-radius: 12px;
}

.kpi-label {
    color: #94a3b8;
    font-size: 13px;
}

.kpi-value {
    font-size: 26px;
    font-weight: 700;
}

.green { color: #22c55e; }
.red { color: #ef4444; }
.blue { color: #38bdf8; }

.section-title {
    font-size: 16px;
    color: #64748b;
    margin-top: 40px;
    margin-bottom: 10px;
}

.insight-box {
    background: #020617;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.markdown('<div class="big-title">Apex Fund — Investor Intelligence</div>', unsafe_allow_html=True)

# ---------- DATA ----------
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
df["Service"] = np.random.choice(services, size=len(df))

# ---------- KPI ----------
total = int(df["Revenue"].sum())
today = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())
best = df.groupby("Site")["Revenue"].sum().idxmax()

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">Total Revenue</div>
<div class="kpi-value">{total:,.0f} DKK</div>
<div class="green">▲ +4.2%</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">Revenue Today</div>
<div class="kpi-value">{today:,.0f} DKK</div>
<div class="green">▲ Strong day</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">Top Asset</div>
<div class="kpi-value">{best}</div>
<div class="blue">Stable</div>
</div>
""", unsafe_allow_html=True)

# ---------- LAYOUT SPLIT ----------
left, right = st.columns([2, 1])

# ---------- LEFT SIDE ----------
with left:
    st.markdown('<div class="section-title">Revenue Trend</div>', unsafe_allow_html=True)
    
    daily = df.groupby("Date")["Revenue"].sum().reset_index()
    fig = px.line(daily, x="Date", y="Revenue")
    fig.update_traces(line=dict(width=3))
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#020617",
        paper_bgcolor="#020617",
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- RIGHT SIDE ----------
with right:
    st.markdown('<div class="section-title">Service Mix</div>', unsafe_allow_html=True)

    service_rev = df.groupby("Service")["Revenue"].sum().reset_index()
    fig2 = px.pie(service_rev, names="Service", values="Revenue", hole=0.5)
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="#020617",
        paper_bgcolor="#020617"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------- TABLE ----------
st.markdown('<div class="section-title">Portfolio Ranking</div>', unsafe_allow_html=True)

ranking = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()
st.dataframe(ranking, use_container_width=True)

# ---------- INSIGHT ----------
st.markdown('<div class="section-title">Market Intelligence</div>', unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<b>Portfolio Status:</b> Stable<br><br>

• FCR dominates stable grid conditions<br>
• aFRR / mFRR spike during imbalance<br>
• No immediate risk signals detected<br>
</div>
""", unsafe_allow_html=True)
