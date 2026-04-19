import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from openai import OpenAI

st.set_page_config(page_title="Apex Intelligence", layout="centered")

# -------------------------
# 🎨 DESIGN (PRO LEVEL)
# -------------------------
st.markdown("""
<style>
body {
    background-color: #050a16;
    color: white;
}

.block-container {
    max-width: 900px;
    margin: auto;
}

/* KPI cards */
.kpi {
    background: linear-gradient(145deg, #0b1c35, #071427);
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f3b73;
    box-shadow: 0 0 20px rgba(0,100,255,0.08);
    margin-bottom: 10px;
}

.kpi-title {
    color: #9bb3ff;
    font-size: 13px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
}

.kpi-positive {
    color: #00ffa3;
}

.kpi-negative {
    color: #ff4d6d;
}

/* Section titles */
.section {
    font-size: 14px;
    color: #6b85c5;
    margin-top: 40px;
    margin-bottom: 10px;
    letter-spacing: 1px;
}

/* Input styling */
.stTextInput input {
    background-color: #0b1c35;
    border: 1px solid #1f3b73;
    color: white;
}

/* Button */
.stButton button {
    background: linear-gradient(90deg, #3b82f6, #6366f1);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# DATA
# -------------------------
np.random.seed(42)
dates = pd.date_range(start="2025-01-01", periods=180)
sites = [f"BESS_{i}" for i in range(1, 11)]

data = []
for site in sites:
    revenue = np.random.normal(500000, 50000, len(dates))
    revenue = np.maximum(revenue, 0)
    for i in range(len(dates)):
        data.append([dates[i], site, revenue[i]])

df = pd.DataFrame(data, columns=["Date", "Site", "Revenue"])

services = ["FCR", "aFRR", "mFRR"]
df["Service"] = np.random.choice(services, size=len(df))

# -------------------------
# FILTER
# -------------------------
view = st.radio("View", ["Portfolio", "Single Asset"])

if view == "Single Asset":
    selected = st.selectbox("Select BESS", sites)
    df = df[df["Site"] == selected]

# -------------------------
# KPI
# -------------------------
total = int(df["Revenue"].sum())
today = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())

delta = np.random.uniform(-5, 5)

col1, col2 = st.columns(2)

col1.markdown(f"""
<div class="kpi">
<div class="kpi-title">Total Revenue</div>
<div class="kpi-value">{total:,.0f} DKK</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi">
<div class="kpi-title">Revenue Today</div>
<div class="kpi-value">{today:,.0f} DKK</div>
<div class="{ 'kpi-positive' if delta>0 else 'kpi-negative'}">
{delta:.2f}%
</div>
</div>
""", unsafe_allow_html=True)

# -------------------------
# 📈 CHART (TRADING STYLE)
# -------------------------
daily = df.groupby("Date")["Revenue"].sum().reset_index()

future_dates = pd.date_range(daily["Date"].max(), periods=20)
forecast = np.linspace(daily["Revenue"].iloc[-1], daily["Revenue"].iloc[-1]*1.2, 20)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=daily["Date"],
    y=daily["Revenue"],
    mode="lines",
    name="Actual",
    line=dict(color="#4c6fff", width=3)
))

fig.add_trace(go.Scatter(
    x=future_dates,
    y=forecast,
    mode="lines",
    name="Forecast",
    line=dict(color="#ff4d6d", width=3, dash="dot")
))

fig.update_layout(
    plot_bgcolor="#050a16",
    paper_bgcolor="#050a16",
    font=dict(color="white"),
    margin=dict(l=0, r=0, t=10, b=0),
    height=300
)

st.markdown('<div class="section">REVENUE TREND</div>', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 🤖 AUTO AI INSIGHT
# -------------------------
st.markdown('<div class="section">AI INTELLIGENCE</div>', unsafe_allow_html=True)

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    summary = f"""
    Total revenue: {total}
    Today revenue: {today}
    Trend increasing slightly
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":f"Analyze this portfolio:\n{summary}"}]
    )

    st.markdown(response.choices[0].message.content)

except:
    st.info("AI requires API key")

# -------------------------
# 💬 CHAT
# -------------------------
st.markdown('<div class="section">INVESTOR COPILOT</div>', unsafe_allow_html=True)

q = st.text_input("Ask about your portfolio")

if q:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":q}]
        )
        st.write(response.choices[0].message.content)
    except:
        st.warning("Add API key")
