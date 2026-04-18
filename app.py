import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from openai import OpenAI

st.set_page_config(page_title="Apex Intelligence", layout="centered")

# ---------- OPENAI ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- LIVE DATA (SIMPEL VERSION) ----------
def load_live_data():
    try:
        # HER kan du senere indsætte Soft Control API
        # fx requests.get(...)
        
        # fallback demo
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

    except:
        st.error("Data load failed")
        return pd.DataFrame()

df = load_live_data()

# ---------- UI ----------
st.title("Apex Intelligence")

mode = st.radio("View", ["Portfolio", "Single Asset"])

if mode == "Single Asset":
    selected_site = st.selectbox("Choose BESS", df["Site"].unique())
    df_filtered = df[df["Site"] == selected_site]
else:
    df_filtered = df

# ---------- KPI ----------
total = int(df_filtered["Revenue"].sum())
today = int(df_filtered[df_filtered["Date"] == df_filtered["Date"].max()]["Revenue"].sum())

st.metric("Total Revenue", f"{total:,.0f} DKK")
st.metric("Revenue Today", f"{today:,.0f} DKK")

# ---------- TIME SERIES ----------
daily = df_filtered.groupby("Date")["Revenue"].sum().reset_index()

# ---------- FORECAST ----------
daily["t"] = np.arange(len(daily))
X = daily[["t"]].values
y = daily["Revenue"].values

coef = np.linalg.lstsq(X, y, rcond=None)[0]

future_days = 30
future_t = np.arange(len(daily), len(daily) + future_days)

future_dates = pd.date_range(start=daily["Date"].iloc[-1], periods=future_days)
forecast = future_t * coef[0]

forecast_df = pd.DataFrame({
    "Date": future_dates,
    "Forecast": forecast
})

# ---------- GRAPH ----------
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=daily["Date"],
    y=daily["Revenue"],
    mode="lines",
    name="Actual"
))

fig.add_trace(go.Scatter(
    x=forecast_df["Date"],
    y=forecast_df["Forecast"],
    mode="lines",
    name="Forecast",
    line=dict(dash="dash")
))

fig.update_layout(template="plotly_dark", height=400)

st.plotly_chart(fig, use_container_width=True)

# ---------- AI ANALYSIS ----------
st.subheader("AI Analysis")

data_summary = f"""
Total revenue: {total}
Today revenue: {today}
Last 30 day trend: {daily['Revenue'].iloc[-1] - daily['Revenue'].iloc[-30]}
"""

if st.button("Generate AI Analysis"):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an energy market analyst."},
            {"role": "user", "content": f"Analyze this BESS portfolio:\n{data_summary}"}
        ]
    )

    st.write(response.choices[0].message.content)

# ---------- COPILOT ----------
st.subheader("Investor Copilot")

q = st.text_input("Ask anything about the portfolio")

if q:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in BESS and energy markets."},
            {"role": "user", "content": q}
        ]
    )

    st.write(response.choices[0].message.content)
