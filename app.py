import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Apex Intelligence", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body { background-color: #05070d; }

.big-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 20px;
}

.kpi-card {
    background: linear-gradient(135deg, #0f172a, #020617);
    padding: 20px;
    border-radius: 12px;
}

.kpi-label { color: #94a3b8; font-size: 13px; }
.kpi-value { font-size: 28px; font-weight: 700; }

.green { color: #22c55e; }
.red { color: #ef4444; }
.blue { color: #38bdf8; }

.section-title {
    font-size: 16px;
    color: #64748b;
    margin-top: 30px;
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

# ---------- SIDEBAR ----------
st.sidebar.title("Control Panel")

mode = st.sidebar.radio("Mode", ["Portfolio", "Single Asset"])

selected_site = None
if mode == "Single Asset":
    selected_site = st.sidebar.selectbox("Select BESS", sites)

# ---------- FILTER ----------
if mode == "Portfolio":
    df_filtered = df.copy()
else:
    df_filtered = df[df["Site"] == selected_site]

# ---------- TITLE ----------
st.markdown('<div class="big-title">Apex Fund — Investor Intelligence</div>', unsafe_allow_html=True)

# ---------- KPI ----------
total = int(df_filtered["Revenue"].sum())
today = int(df_filtered[df_filtered["Date"] == df_filtered["Date"].max()]["Revenue"].sum())

site_perf = df.groupby("Site")["Revenue"].sum()
avg_perf = site_perf.mean()

if mode == "Single Asset":
    current_perf = site_perf[selected_site]
    diff = current_perf - avg_perf
else:
    diff = 0

trend = "green" if diff >= 0 else "red"
symbol = "▲" if diff >= 0 else "▼"

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">Total Revenue</div>
<div class="kpi-value">{total:,.0f} DKK</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">Revenue Today</div>
<div class="kpi-value">{today:,.0f} DKK</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">Performance vs Avg</div>
<div class="kpi-value {trend}">
{symbol} {diff:,.0f} DKK
</div>
</div>
""", unsafe_allow_html=True)

# ---------- ALERT ----------
if mode == "Single Asset" and diff < 0:
    st.error(f"⚠️ {selected_site} is underperforming vs portfolio average")

# ---------- CHART ----------
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="section-title">Revenue Trend</div>', unsafe_allow_html=True)

    daily = df_filtered.groupby("Date")["Revenue"].sum().reset_index()
    fig = px.line(daily, x="Date", y="Revenue")
    fig.update_traces(line=dict(width=3))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Service Mix</div>', unsafe_allow_html=True)

    service_rev = df_filtered.groupby("Service")["Revenue"].sum().reset_index()
    fig2 = px.pie(service_rev, names="Service", values="Revenue", hole=0.5)
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- RANKING ----------
st.markdown('<div class="section-title">Portfolio Ranking</div>', unsafe_allow_html=True)

ranking = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()
st.dataframe(ranking, use_container_width=True)

# ---------- AI COPILOT ----------
st.markdown('<div class="section-title">Investor Copilot</div>', unsafe_allow_html=True)

question = st.text_input("Ask something about the portfolio...")

if question:
    if "best" in question.lower():
        best_site = ranking.iloc[0]["Site"]
        st.success(f"Top performing asset is {best_site}")
    elif "worst" in question.lower():
        worst_site = ranking.iloc[-1]["Site"]
        st.warning(f"Worst performing asset is {worst_site}")
    else:
        st.info("Portfolio is stable with no major anomalies")

# ---------- INSIGHT ----------
st.markdown('<div class="section-title">AI Market Insight</div>', unsafe_allow_html=True)

if mode == "Single Asset":
    if diff > 0:
        insight = f"{selected_site} is outperforming portfolio average."
    else:
        insight = f"{selected_site} is underperforming vs portfolio."
else:
    insight = "Portfolio performance is stable across assets."

st.markdown(f"""
<div class="insight-box">
<b>Insight:</b><br><br>
{insight}<br><br>
• Revenue driven by ancillary services<br>
• No critical risks detected<br>
</div>
""", unsafe_allow_html=True)
