import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Apex Intelligence", layout="wide")

# ---------- DATA ----------
@st.cache_data
def load_data():
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
    return df

df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("Control Panel")

mode = st.sidebar.radio("View Mode", ["Portfolio", "Single Asset"])

if mode == "Single Asset":
    selected_site = st.sidebar.selectbox("Select BESS", df["Site"].unique())
    df_filtered = df[df["Site"] == selected_site]
else:
    df_filtered = df

# ---------- HEADER ----------
st.title("Apex Fund — Investor Intelligence")

# ---------- KPI ----------
total = int(df_filtered["Revenue"].sum())
today = int(df_filtered[df_filtered["Date"] == df_filtered["Date"].max()]["Revenue"].sum())

site_perf = df.groupby("Site")["Revenue"].sum()
avg_perf = site_perf.mean()

if mode == "Single Asset":
    perf = site_perf[selected_site] - avg_perf
else:
    perf = 0

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"{total:,.0f} DKK")
col2.metric("Revenue Today", f"{today:,.0f} DKK")
col3.metric("Performance vs Avg", f"{perf:,.0f} DKK")

# ---------- ALERT ----------
if mode == "Single Asset" and perf < 0:
    st.warning(f"{selected_site} is underperforming vs portfolio")

# ---------- MAIN CHART ----------
st.subheader("Revenue Trend")

if mode == "Portfolio":
    # PORTFOLIO + individual lines
    daily = df.groupby(["Date", "Site"])["Revenue"].sum().reset_index()

    fig = px.line(
        daily,
        x="Date",
        y="Revenue",
        color="Site",
    )

else:
    # SINGLE + benchmark
    asset = df[df["Site"] == selected_site]
    portfolio = df.groupby("Date")["Revenue"].mean().reset_index()

    asset["Type"] = "Selected Asset"
    portfolio["Type"] = "Portfolio Avg"

    combined = pd.concat([
        asset[["Date", "Revenue"]].assign(Type="Selected Asset"),
        portfolio.rename(columns={"Revenue": "Revenue"})
    ])

    fig = px.line(
        combined,
        x="Date",
        y="Revenue",
        color="Type"
    )

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#020617",
    paper_bgcolor="#020617"
)

fig.update_traces(line=dict(width=3))

st.plotly_chart(fig, use_container_width=True)

# ---------- SPLIT ----------
colA, colB = st.columns(2)

with colA:
    st.subheader("Portfolio Ranking")
    ranking = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()
    st.dataframe(ranking, use_container_width=True)

with colB:
    st.subheader("Service Mix")
    service_rev = df_filtered.groupby("Service")["Revenue"].sum().reset_index()
    fig2 = px.pie(service_rev, names="Service", values="Revenue", hole=0.5)
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- COPILOT ----------
st.subheader("Investor Copilot")

q = st.text_input("Ask about performance (best, worst, risk)")

if q:
    if "best" in q.lower():
        st.success(f"Top asset: {ranking.iloc[0]['Site']}")
    elif "worst" in q.lower():
        st.warning(f"Worst asset: {ranking.iloc[-1]['Site']}")
    elif "risk" in q.lower():
        st.warning("No major risks detected")
    else:
        st.info("Portfolio stable")

# ---------- INSIGHT ----------
st.subheader("AI Market Insight")

if mode == "Single Asset":
    if perf > 0:
        st.info(f"{selected_site} outperforming portfolio average.")
    else:
        st.info(f"{selected_site} underperforming portfolio.")
else:
    st.info("Portfolio stable across assets.")
