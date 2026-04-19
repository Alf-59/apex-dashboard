```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from openai import OpenAI

st.set_page_config(page_title="Apex Intelligence", layout="centered")

# -------------------------
# 🎨 DESIGN
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

.section {
    font-size: 14px;
    color: #6b85c5;
    margin-top: 40px;
    margin-bottom: 10px;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# DATA (cached)
# -------------------------
@st.cache_data
def load_data():
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

    return df

df = load_data()

# -------------------------
# FILTER
# -------------------------
view = st.radio("View", ["Portfolio", "Single Asset"])

if view == "Single Asset":
    selected = st.selectbox("Select BESS", df["Site"].unique())
    df = df[df["Site"] == selected]

# -------------------------
# KPI
# -------------------------
total = int(df["Revenue"].sum())
today = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())

yesterday = df[df["Date"] == df["Date"].max() - pd.Timedelta(days=1)]["Revenue"].sum()
delta = ((today - yesterday) / yesterday * 100) if yesterday else 0

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
# 📈 REVENUE TREND
# -------------------------
st.markdown('<div class="section">REVENUE TREND</div>', unsafe_allow_html=True)

daily = df.groupby("Date")["Revenue"].sum().reset_index()
daily["MA7"] = daily["Revenue"].rolling(7).mean()

future_x = np.arange(len(daily), len(daily)+20)
trend = np.polyfit(range(len(daily)), daily["Revenue"], 1)
forecast = trend[0]*future_x + trend[1]

future_dates = pd.date_range(daily["Date"].max(), periods=20)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=daily["Date"],
    y=daily["Revenue"],
    mode="lines",
    name="Actual",
    line=dict(color="#4c6fff", width=3)
))

fig.add_trace(go.Scatter(
    x=daily["Date"],
    y=daily["MA7"],
    mode="lines",
    name="7D Avg",
    line=dict(color="#00ffa3", width=2)
))

fig.add_trace(go.Scatter(
    x=future_dates,
    y=forecast,
    mode="lines",
    name="Forecast",
    line=dict(color="#ff4d6d", dash="dot")
))

fig.update_layout(
    plot_bgcolor="#050a16",
    paper_bgcolor="#050a16",
    font=dict(color="white"),
    height=300
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 📊 ASSET + SERVICE
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section">ASSET PERFORMANCE</div>', unsafe_allow_html=True)
    asset_perf = df.groupby("Site")["Revenue"].sum().reset_index()

    fig_bar = go.Figure(go.Bar(
        x=asset_perf["Site"],
        y=asset_perf["Revenue"],
        marker=dict(color="#4c6fff")
    ))

    fig_bar.update_layout(
        plot_bgcolor="#050a16",
        paper_bgcolor="#050a16",
        font=dict(color="white"),
        height=300
    )

    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown('<div class="section">SERVICE MIX</div>', unsafe_allow_html=True)
    service_mix = df.groupby("Service")["Revenue"].sum().reset_index()

    fig_donut = go.Figure(go.Pie(
        labels=service_mix["Service"],
        values=service_mix["Revenue"],
        hole=0.6
    ))

    fig_donut.update_layout(
        plot_bgcolor="#050a16",
        paper_bgcolor="#050a16",
        font=dict(color="white"),
        height=300
    )

    st.plotly_chart(fig_donut, use_container_width=True)

# -------------------------
# 🔥 HEATMAP
# -------------------------
st.markdown('<div class="section">REVENUE HEATMAP</div>', unsafe_allow_html=True)

heat = df.copy()
heat["Day"] = heat["Date"].dt.day
heat["Month"] = heat["Date"].dt.month

pivot = heat.pivot_table(values="Revenue", index="Month", columns="Day", aggfunc="sum")

fig_heat = go.Figure(go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale="Blues"
))

fig_heat.update_layout(
    plot_bgcolor="#050a16",
    paper_bgcolor="#050a16",
    font=dict(color="white"),
    height=300
)

st.plotly_chart(fig_heat, use_container_width=True)

# -------------------------
# 🤖 AI
# -------------------------
st.markdown('<div class="section">AI INTELLIGENCE</div>', unsafe_allow_html=True)

client = None
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    with st.spinner("Analyzing..."):
        prompt = f"""
        You are an energy trading analyst.

        Total revenue: {total}
        Today revenue: {today}

        Give insights, risks, and optimization ideas.
        """

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )

        st.markdown(res.choices[0].message.content)

except Exception as e:
    st.info("Add API key")

# -------------------------
# 💬 CHAT
# -------------------------
st.markdown('<div class="section">INVESTOR COPILOT</div>', unsafe_allow_html=True)

q = st.text_input("Ask about your portfolio")

if q and client:
    with st.spinner("Thinking..."):
        messages = [
            {"role": "system", "content": "You are an expert energy portfolio analyst."},
            {"role": "user", "content": f"Portfolio total: {total}, today: {today}. Question: {q}"}
        ]

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        st.write(res.choices[0].message.content)
```

---

## ✅ Hvad du får nu

* 📈 Trend + forecast + moving average
* 📊 Asset performance (bar chart)
* 🧠 Service mix (donut)
* 🔥 Heatmap (visuel wow-effekt)
* 🤖 Bedre AI insight + chat med kontekst
* ⚡ Hurtigere (cache) + mere robust

---

Hvis du vil tage næste skridt, kan jeg bygge:

* live data (Nord Pool / API)
* ægte ML forecast (ikke trendline)
* login + database (rigtig SaaS)

Sig til hvad du vil optimere næste.
