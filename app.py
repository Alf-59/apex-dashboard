import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Apex Intelligence", layout="wide")

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- LOGIN ----------
if not st.session_state.logged_in:
    st.title("🔐 Apex Intelligence Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong credentials")

    st.stop()

# ---------- STYLE ----------
st.markdown("""
<style>
body { background-color: #05070d; }
.kpi { background:#020617;padding:15px;border-radius:10px }
</style>
""", unsafe_allow_html=True)

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

mode = st.sidebar.radio("Mode", ["Portfolio", "Single Asset"])

if mode == "Single Asset":
    selected_site = st.sidebar.selectbox("Select Asset", df["Site"].unique())
    df_filtered = df[df["Site"] == selected_site]
else:
    df_filtered = df

# ---------- HEADER ----------
st.title("Apex Fund — Investor Intelligence")

# ---------- KPI ----------
total = int(df_filtered["Revenue"].sum())
today = int(df_filtered[df_filtered["Date"] == df_filtered["Date"].max()]["Revenue"].sum())

site_perf = df.groupby("Site")["Revenue"].sum()
avg = site_perf.mean()

if mode == "Single Asset":
    perf = site_perf[selected_site] - avg
else:
    perf = 0

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"{total:,.0f} DKK")
col2.metric("Revenue Today", f"{today:,.0f} DKK")
col3.metric("Performance vs Avg", f"{perf:,.0f} DKK")

# ---------- ALERT ----------
if mode == "Single Asset" and perf < 0:
    st.warning(f"{selected_site} underperforming")

# ---------- CHART ----------
daily = df_filtered.groupby("Date")["Revenue"].sum().reset_index()
fig = px.line(daily, x="Date", y="Revenue", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# ---------- RANK ----------
ranking = df.groupby("Site")["Revenue"].sum().sort_values(ascending=False).reset_index()
st.dataframe(ranking)

# ---------- AI COPILOT ----------
st.subheader("Investor Copilot")

q = st.text_input("Ask a question...")

if q:
    if "best" in q:
        st.success(f"Best asset: {ranking.iloc[0]['Site']}")
    elif "risk" in q:
        st.warning("No major risks detected")
    else:
        st.info("Portfolio stable")

# ---------- LOGOUT ----------
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
