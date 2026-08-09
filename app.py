import streamlit as st

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="MarketSphere",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# HOME PAGE
# ---------------------------------------------------

st.title("📊 MarketSphere")

st.markdown("### AI-Powered Marketing Decision Intelligence Platform")

st.markdown("---")

st.write("""
Welcome to **MarketSphere**, an AI-driven marketing analytics platform that helps businesses
understand customers, predict marketing outcomes, and make smarter decisions.

MarketSphere combines Machine Learning with Business Intelligence to transform raw customer
data into actionable marketing strategies.
""")

st.markdown("## 🚀 Core Modules")

col1, col2 = st.columns(2)

with col1:
        st.success("👥 Customer Intelligence")
        st.success("💰 Customer Lifetime Value Prediction")
        st.success("📣 Campaign Response Prediction")

        with col2:
          st.success("🧠 Decision Impact Engine")
          st.success("📊 Business Dashboard")
          st.success("📄 Export Reports")

        st.markdown("---")

        st.markdown("## 💡 Why MarketSphere?")

        st.info("""
Unlike traditional marketing dashboards that only visualize data,
MarketSphere **predicts future customer behavior** and recommends
which customers deserve marketing investment using the **Decision Impact Engine**.
""")

        st.markdown("---")

        st.markdown("## 🔄 MarketSphere Workflow")

        st.code("""
Customer Data
      │
      ▼
Customer Segmentation
      │
      ▼
CLV Prediction
      │
      ▼
Campaign Response Prediction
      │
      ▼
Decision Impact Engine
      │
      ▼
Business Recommendation
""")

        st.markdown("---")

        st.caption("© 2026 MarketSphere | AI-Powered Marketing Decision Platform")