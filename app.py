import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Apex Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# CUSTOM CSS (Modern UI)
# -------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.metric-card {
    background: #1c1f26;
    padding: 20px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("⚙️ Apex Intelligence")
mode = st.sidebar.radio("Mode", ["Dashboard", "Forecast", "AI Insights"])

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# -------------------------
# DATA LOADING
# -------------------------
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower()
    return df

if uploaded_file:
    df = load_data(uploaded_file)
else:
    st.warning("Upload a dataset to begin")
    st.stop()

# -------------------------
# DASHBOARD
# -------------------------
if mode == "Dashboard":
    st.title("📊 Apex Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Missing Values", df.isna().sum().sum())

    st.subheader("Data Preview")
    st.dataframe(df.head())

    # Auto detect numeric
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if numeric_cols:
        selected_col = st.selectbox("Select Metric", numeric_cols)

        fig = px.line(df, y=selected_col, title=f"{selected_col} Trend")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.histogram(df, x=selected_col, nbins=30)
        st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# FORECAST (Prophet)
# -------------------------
elif mode == "Forecast":
    st.title("📈 Forecast Engine")

    date_col = st.selectbox("Select Date Column", df.columns)
    target_col = st.selectbox("Select Target Column", df.select_dtypes(include=np.number).columns)

    df_forecast = df[[date_col, target_col]].dropna()
    df_forecast.columns = ["ds", "y"]

    df_forecast["ds"] = pd.to_datetime(df_forecast["ds"])

    model = Prophet()
    model.fit(df_forecast)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    st.subheader("Forecast Plot")
    fig1 = px.line(forecast, x="ds", y="yhat")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Components")
    fig2 = model.plot_components(forecast)
    st.pyplot(fig2)

# -------------------------
# AI INSIGHTS
# -------------------------
elif mode == "AI Insights":
    st.title("🤖 AI Intelligence Engine")

    sample_data = df.head(50).to_csv(index=False)

    prompt = st.text_area(
        "Ask AI about your data",
        "Analyze trends, anomalies and business insights."
    )

    if st.button("Run AI Analysis"):
        with st.spinner("Thinking..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior data analyst AI. Provide insights, trends and anomalies."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Dataset sample:
                        {sample_data}

                        Question:
                        {prompt}
                        """
                    }
                ]
            )

            st.success("Analysis Complete")
            st.write(response.choices[0].message.content)

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.caption("Apex Intelligence © 2026")
