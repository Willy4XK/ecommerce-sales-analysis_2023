"""
E-Commerce Sales Dashboard — Streamlit App
Run with:  streamlit run src/dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from analysis import generate_sample_data, clean_data, generate_insights

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
    padding: 1rem 1.2rem;
    border-radius: 12px;
    color: white;
    text-align: center;
}
.metric-value { font-size: 1.8rem; font-weight: 700; margin: 0; }
.metric-label { font-size: 0.8rem; opacity: 0.85; margin: 0; text-transform: uppercase; }
.insight-box {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    padding: 0.6rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ── Data ───────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = generate_sample_data(2000)
    return clean_data(df)


df = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filters")
categories = st.sidebar.multiselect(
    "Category", df["category"].unique(), default=list(df["category"].unique())
)
regions = st.sidebar.multiselect(
    "Region", df["region"].unique(), default=list(df["region"].unique())
)
channels = st.sidebar.multiselect(
    "Channel", df["channel"].unique(), default=list(df["channel"].unique())
)
quarters = st.sidebar.multiselect(
    "Quarter", ["Q1", "Q2", "Q3", "Q4"], default=["Q1", "Q2", "Q3", "Q4"]
)

mask = (
    df["category"].isin(categories) &
    df["region"].isin(regions) &
    df["channel"].isin(channels) &
    df["quarter"].isin(quarters)
)
fdf = df[mask]

# ── Header ─────────────────────────────────────────────────────────────────
st.title("🛒 E-Commerce Sales Dashboard")
st.caption("Interactive analysis of 2023 sales data — use sidebar filters to explore")
st.divider()

# ── KPI cards ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (c1, "Total Revenue",     f"${fdf['revenue'].sum():,.0f}",            "💰"),
    (c2, "Total Orders",      f"{len(fdf):,}",                            "📦"),
    (c3, "Avg Order Value",   f"${fdf['revenue'].mean():,.2f}",           "🧾"),
    (c4, "Unique Customers",  f"{fdf['customer_id'].nunique():,}",        "👥"),
    (c5, "Return Rate",       f"{fdf['is_returned'].mean()*100:.1f}%",   "🔄"),
]
for col, label, value, icon in kpis:
    col.markdown(f"""
    <div class="metric-card">
      <p class="metric-label">{icon} {label}</p>
      <p class="metric-value">{value}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Monthly Revenue + Category ─────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    monthly = fdf.groupby("month_num")["revenue"].sum().reset_index()
    monthly["Month"] = pd.to_datetime(monthly["month_num"], format="%m").dt.strftime("%b")
    fig = go.Figure()
    fig.add_bar(x=monthly["Month"], y=monthly["revenue"],
                marker_color="#2563EB", opacity=0.85, name="Revenue")
    fig.add_scatter(x=monthly["Month"], y=monthly["revenue"],
                    mode="lines+markers", line_color="#7c3aed",
                    marker_size=7, name="Trend")
    fig.update_layout(title="Monthly Revenue (2023)", height=350,
                      yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                      legend=dict(orientation="h", y=1.1),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    cat_rev = fdf.groupby("category")["revenue"].sum().reset_index()
    fig2 = px.pie(cat_rev, names="category", values="revenue",
                  hole=0.45, title="Revenue by Category",
                  color_discrete_sequence=px.colors.qualitative.Bold)
    fig2.update_layout(height=350,
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Heatmap + Discount Analysis ─────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    pivot = fdf.pivot_table(values="revenue", index="region",
                            columns="channel", aggfunc="sum")
    fig3 = px.imshow(pivot, text_auto=",.0f", color_continuous_scale="Blues",
                     title="Revenue Heatmap: Region × Channel", aspect="auto")
    fig3.update_layout(height=350,
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    disc = (fdf.groupby("discount_pct")
               .agg(avg_rev=("revenue", "mean"), orders=("order_id", "count"))
               .reset_index())
    fig4 = go.Figure()
    fig4.add_bar(x=disc["discount_pct"].astype(str) + "%",
                 y=disc["avg_rev"], name="Avg Revenue", marker_color="#059669")
    fig4.add_scatter(x=disc["discount_pct"].astype(str) + "%",
                     y=disc["orders"], name="Order Count",
                     mode="lines+markers", yaxis="y2", line_color="#DB2777")
    fig4.update_layout(
        title="Discount Impact on Revenue & Volume", height=350,
        yaxis=dict(title="Avg Revenue ($)", tickprefix="$"),
        yaxis2=dict(title="Order Count", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Insights ────────────────────────────────────────────────────────
st.subheader("💡 Auto-Generated Insights")
metrics = {
    "total_revenue":    fdf["revenue"].sum(),
    "total_orders":     len(fdf),
    "avg_order_value":  fdf["revenue"].mean(),
    "unique_customers": fdf["customer_id"].nunique(),
    "return_rate":      fdf["is_returned"].mean() * 100,
    "top_category":     fdf.groupby("category")["revenue"].sum().idxmax() if len(fdf) else "N/A",
    "top_region":       fdf.groupby("region")["revenue"].sum().idxmax() if len(fdf) else "N/A",
    "top_channel":      fdf.groupby("channel")["revenue"].sum().idxmax() if len(fdf) else "N/A",
}
if len(fdf) > 0:
    insights = generate_insights(fdf, metrics)
    cols = st.columns(2)
    for i, ins in enumerate(insights):
        cols[i % 2].markdown(f'<div class="insight-box">💡 {ins}</div>', unsafe_allow_html=True)
else:
    st.warning("No data matches the current filters.")

# ── Raw data table ─────────────────────────────────────────────────────────
with st.expander("🗃️ View Raw Data"):
    st.dataframe(fdf.head(200), use_container_width=True)
    st.caption(f"Showing 200 of {len(fdf):,} rows")
