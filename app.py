import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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
# SIDEBAR
# =====================
st.sidebar.header("🔍 Điều khiển")

view_mode = st.sidebar.radio(
    "Chế độ xem",
    ["Tổng quan", "Chi tiết theo Cluster", "👑 VIP Customers"]
)

# =====================
# SUMMARY TABLE
# =====================
summary = df.groupby("cluster").agg(
    num_customers=("CustomerID", "nunique"),
    avg_recency=("Recency", "mean"),
    avg_frequency=("Frequency", "mean"),
    avg_monetary=("Monetary", "mean")
).reset_index()

# Xác định cluster VIP
vip_cluster = summary.sort_values(
    by="avg_monetary", ascending=False
).iloc[0]["cluster"]

# =====================
# PCA 2D VISUALIZATION
# =====================
st.subheader("🧭 Không gian phân cụm 2D (PCA)")

rfm = df[["Recency", "Frequency", "Monetary"]]

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm)

pca = PCA(n_components=2)
pca_components = pca.fit_transform(rfm_scaled)

df_pca = pd.DataFrame(
    pca_components,
    columns=["PC1", "PC2"]
)
df_pca["cluster"] = df["cluster"]

fig_pca = px.scatter(
    df_pca,
    x="PC1",
    y="PC2",
    color="cluster",
    title="Biểu đồ PCA 2D – Phân bố các Cluster",
    opacity=0.7
)

st.plotly_chart(fig_pca, use_container_width=True)

st.markdown("""
**Nhận xét:**  
- Các điểm dữ liệu được chiếu xuống không gian 2 chiều bằng PCA từ RFM.  
- Một số cluster có xu hướng tách tương đối rõ, trong khi một vài cluster có chồng lấn nhẹ → phản ánh hành vi mua có phần giao thoa.  
- Tuy PCA không giữ toàn bộ thông tin, nhưng đủ để quan sát cấu trúc tổng thể và tính hợp lý của việc phân cụm.
""")

# =====================
# VIEW: TỔNG QUAN
# =====================
if view_mode == "Tổng quan":
    st.subheader("📌 Tổng quan dữ liệu")

    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng khách hàng", df["CustomerID"].nunique())
    col2.metric("Số cluster", df["cluster"].nunique())
    col3.metric("Doanh thu TB", round(df["Monetary"].mean(), 2))

    st.subheader("📊 Thống kê theo Cluster")
    st.dataframe(summary, use_container_width=True)

    fig = px.bar(
        summary,
        x="cluster",
        y="avg_monetary",
        title="Giá trị chi tiêu trung bình theo Cluster",
        labels={"avg_monetary": "Avg Monetary"}
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================
# VIEW: CHI TIẾT CLUSTER
# =====================
elif view_mode == "Chi tiết theo Cluster":
    selected_cluster = st.sidebar.selectbox(
        "Chọn Cluster",
        sorted(df["cluster"].unique())
    )

    df_cluster = df[df["cluster"] == selected_cluster]

    st.subheader(f"🧠 Phân tích Cluster {selected_cluster}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Số khách hàng", df_cluster["CustomerID"].nunique())
    col2.metric("Frequency TB", round(df_cluster["Frequency"].mean(), 2))
    col3.metric("Monetary TB", round(df_cluster["Monetary"].mean(), 2))

    st.markdown("### 🎯 Persona & Chiến lược marketing")

    persona_map = {
        0: ("Frequent Buyers", "Bundle sản phẩm + tích điểm"),
        1: ("Premium Customers", "Upsell + chăm sóc VIP"),
        2: ("Occasional Shoppers", "Voucher kích hoạt mua lại"),
        3: ("Balanced Customers", "Cross-sell theo ngữ cảnh"),
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
# VIEW: VIP CUSTOMERS
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
