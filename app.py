import streamlit as st
import pandas as pd
import plotly.express as px

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Customer Clustering Dashboard",
    layout="wide"
)

st.title("🛒 Customer Clustering & Marketing Insight")
st.caption("Phân khúc khách hàng dựa trên Association Rules + RFM")

# =====================
# LOAD DATA
# =====================
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/customer_clusters_from_rules.csv")

df = load_data()

# =====================
# SUMMARY + VIP
# =====================
summary = df.groupby("cluster").agg(
    num_customers=("CustomerID", "nunique"),
    avg_recency=("Recency", "mean"),
    avg_frequency=("Frequency", "mean"),
    avg_monetary=("Monetary", "mean")
).reset_index()

# Xác định cluster VIP (chi tiêu cao nhất)
vip_cluster = summary.sort_values(
    by="avg_monetary", ascending=False
).iloc[0]["cluster"]

# =====================
# SIDEBAR
# =====================
st.sidebar.header("🔍 Điều khiển")

view_mode = st.sidebar.radio(
    "Chế độ xem",
    ["Tổng quan", "Chi tiết theo Cluster", "👑 VIP Customers"]
)

# =====================
# VIEW 1: TỔNG QUAN
# =====================
if view_mode == "Tổng quan":
    st.subheader("📌 Tổng quan dữ liệu")

    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng khách hàng", df["CustomerID"].nunique())
    col2.metric("Số cluster", df["cluster"].nunique())
    col3.metric("Doanh thu TB", round(df["Monetary"].mean(), 2))

    st.subheader("📊 Thống kê theo Cluster")
    st.dataframe(summary, use_container_width=True)

    st.subheader("📈 So sánh các Cluster")
    fig = px.bar(
        summary,
        x="cluster",
        y="avg_monetary",
        title="Giá trị chi tiêu trung bình theo Cluster",
        labels={"avg_monetary": "Avg Monetary"}
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================
# VIEW 2: CHI TIẾT CLUSTER
# =====================
elif view_mode == "Chi tiết theo Cluster":
    clusters = sorted(df["cluster"].unique())
    selected_cluster = st.sidebar.selectbox(
        "Chọn Cluster",
        ["Tất cả"] + clusters
    )

    if selected_cluster == "Tất cả":
        st.subheader("📄 Toàn bộ khách hàng")
        st.dataframe(df.head(50), use_container_width=True)
    else:
        df_cluster = df[df["cluster"] == selected_cluster]

        st.subheader(f"🧠 Phân tích Cluster {selected_cluster}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Số khách hàng", df_cluster["CustomerID"].nunique())
        col2.metric("Frequency TB", round(df_cluster["Frequency"].mean(), 2))
        col3.metric("Monetary TB", round(df_cluster["Monetary"].mean(), 2))

        st.markdown("### 🎯 Persona & Chiến lược marketing")

        persona_map = {
            0: ("Frequent Buyers", "Mua thường xuyên – Bundle + Loyalty"),
            1: ("Premium Customers", "Chi tiêu cao – Upsell & VIP Care"),
            2: ("Occasional Shoppers", "Ít mua – Voucher kích hoạt"),
            3: ("Balanced Customers", "Cân bằng – Cross-sell theo ngữ cảnh"),
        }

        persona, strategy = persona_map.get(
            selected_cluster, ("Khác", "Chiến lược linh hoạt")
        )

        st.markdown(f"""
        **Persona:** {persona}  
        **Chiến lược đề xuất:** {strategy}
        """)

        st.subheader("📄 Một số khách hàng tiêu biểu")
        st.dataframe(df_cluster.head(20), use_container_width=True)

# =====================
# VIEW 3: VIP CUSTOMERS
# =====================
elif view_mode == "👑 VIP Customers":
    st.subheader(f"👑 Phân tích VIP – Cluster {vip_cluster}")

    df_vip = df[df["cluster"] == vip_cluster]

    col1, col2, col3 = st.columns(3)
    col1.metric("Số khách VIP", df_vip["CustomerID"].nunique())
    col2.metric("Frequency TB", round(df_vip["Frequency"].mean(), 2))
    col3.metric("Monetary TB", round(df_vip["Monetary"].mean(), 2))

    st.markdown("### 🎯 Chiến lược VIP đề xuất")
    st.markdown("""
    - Chăm sóc khách hàng thân thiết (VIP care)
    - Ưu đãi độc quyền / early access
    - Upsell bundle giá trị cao
    - Giữ chân khách hàng dài hạn
    """)

    st.subheader("📄 Một số khách VIP tiêu biểu")
    st.dataframe(df_vip.head(30), use_container_width=True)
