import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Business Dashboard")
st.markdown("Marketing Analytics Overview")

# ----------------------------
# LOAD DATA
# ----------------------------

df = pd.read_csv("results/marketsphere_predictions.csv")

# ----------------------------
# KPI SECTION
# ----------------------------

st.markdown("## 📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Customers",
        len(df)
    )

with col2:
    st.metric(
        "Average Income",
        f"${df['Income'].mean():,.0f}"
    )

with col3:
    st.metric(
        "Average Spending",
        f"${df['Total_Spending'].mean():,.0f}"
    )

with col4:
    st.metric(
        "Average Opportunity Score",
        f"{df['Opportunity_Score'].mean():.1f}"
    )

st.markdown("---")

# ----------------------------
# CHARTS
# ----------------------------

left, right = st.columns(2)

# Cluster Distribution

with left:

    st.subheader("👥 Customer Segments")

    cluster_counts = (
        df["Cluster"]
        .value_counts()
        .sort_index()
    )

    fig = px.bar(
        x=cluster_counts.index.astype(str),
        y=cluster_counts.values,
        labels={
            "x":"Cluster",
            "y":"Customers"
        },
        title="Customers per Cluster"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# Spending Distribution

with right:

    st.subheader("💰 Spending Distribution")

    fig2 = px.histogram(
        df,
        x="Total_Spending",
        nbins=30,
        title="Customer Spending"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.markdown("---")

# ----------------------------
# INCOME VS SPENDING
# ----------------------------

st.subheader("📈 Income vs Spending")

fig3 = px.scatter(
    df,
    x="Income",
    y="Total_Spending",
    color=df["Cluster"].astype(str),
    hover_data=["ID"],
    title="Customer Segments"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown("---")

# ----------------------------
# TOP OPPORTUNITIES
# ----------------------------

st.subheader("⭐ Top Marketing Opportunities")

top = df.sort_values(
    "Opportunity_Score",
    ascending=False
)[[
    "ID",
    "Customer_Segment",
    "Opportunity_Score",
    "Expected_Revenue",
    "Priority"
]].head(10)

st.dataframe(
    top,
    use_container_width=True
)