app.py
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

# Title
st.title("Apex Fund Performance")

# Generate fake data
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

# KPIs
total_revenue = int(df["Revenue"].sum())
today_revenue = int(df[df["Date"] == df["Date"].max()]["Revenue"].sum())
avg_per_site = int(df.groupby("Site")["Revenue"].mean().mean())

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"{total_revenue:,.0f} DKK")
col2.metric("Revenue Today", f"{today_revenue:,.0f} DKK")
col3.metric("Avg Revenue per Site", f"{avg_per_site:,.0f} DKK")

# Daily revenue chart
daily = df.groupby("Date")["Revenue"].sum().reset_index()
fig = px.line(daily, x="Date", y="Revenue", title="Daily Revenue")
st.plotly_chart(fig, use_container_width=True)

# Revenue per site
site_rev = df.groupby("Site")["Revenue"].sum().reset_index()
fig2 = px.bar(site_rev, x="Site", y="Revenue", title="Revenue per BESS Site")
st.plotly_chart(fig2, use_container_width=True)

# Explanation
st.subheader("Performance Insight")
st.write("Revenue variations are driven by market volatility in ancillary services and site availability.")
