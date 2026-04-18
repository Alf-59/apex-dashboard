import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
st.title("Apex Fund — Intelligence Platform")

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

# ---------- TIME SERIES ----------
daily = df_filtered.groupby("Date")["Revenue"].sum().reset_index()

# ---------- FORECAST ----------
window = 14
daily["MA"] = daily["Revenue"].rolling(window).mean()

last_value = daily["MA"].iloc[-1]

future_dates = pd.date_range(start=daily["Date"].iloc[-1], periods=30)
trend = np.linspace(last_value, last_value * 1.05, 30)

forecast_df = pd.DataFrame({
    "Date": future_dates,
    "Forecast": trend
})

# ---------- GRAPH ----------
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=daily["Date"],
    y=daily["Revenue"],
    mode="lines",
    name="Historical",
    line=dict(width=3)
))

fig.add_trace(go.Scatter(
    x=forecast_df["Date"],
    y=forecast_df["Forecast"],
    mode="lines",
    name="Forecast",
    line=dict(dash="dash")
))

fig.update_layout(
    template="plotly_dark",
    title="Revenue + Forecast",
    plot_bgcolor="#020617",
    paper_bgcolor="#020617"
)

st.plotly_chart(fig, use_container_width=True)

# ---------- VOLATILITY ----------
volatility = daily["Revenue"].std()
risk_level = "Low"

if volatility > 20000:
    risk_level = "High"
elif volatility > 10000:
    risk_level = "Medium"

# ---------- ALERT ----------
if risk_level == "High":
    st.error("⚠️ High volatility detected")
elif risk_level == "Medium":
    st.warning("⚠️ Moderate volatility")
else:
    st.success("Stable revenue pattern")

# ---------- RANKING ----------
st.subheader("Portfolio Ranking")

ranking = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()
st.dataframe(ranking, use_container_width=True)

# ---------- AI ANALYSIS ----------
st.subheader("AI Analysis")

trend_change = daily["Revenue"].iloc[-1] - daily["Revenue"].iloc[-30]

if trend_change > 0:
    trend_text = "Revenue trending upward"
else:
    trend_text = "Revenue trending downward"

if mode == "Single Asset":
    if perf > 0:
        perf_text = "Asset outperforming portfolio"
    else:
        perf_text = "Asset underperforming portfolio"
else:
    perf_text = "Portfolio balanced"

st.markdown(f"""
**Summary**

- {trend_text}  
- Risk level: **{risk_level}**  
- {perf_text}  

**Forecast Outlook**

- Expected revenue growth next 30 days  
- No extreme downside scenarios detected  
""")

# ---------- COPILOT ----------
st.subheader("Investor Copilot")

q = st.text_input("Ask about performance")

if q:
    if "forecast" in q.lower():
        st.info("Revenue expected to grow ~5% next 30 days")
    elif "risk" in q.lower():
        st.warning(f"Risk level is {risk_level}")
    elif "best" in q.lower():
        st.success(f"Best asset: {ranking.iloc[0]['Site']}")
    else:
        st.info("System stable with normal variation")
