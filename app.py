import streamlit as st
import pandas as pd

st.set_page_config(page_title="Customer Clustering Demo", layout="wide")

st.title("🛒 Customer Clustering based on Association Rules")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/customer_clusters_from_rules.csv")

df = load_data()

# Sidebar
st.sidebar.header("Chọn Cluster")
clusters = sorted(df["cluster"].unique())
selected_cluster = st.sidebar.selectbox("Cluster", clusters)

# Filter data
df_cluster = df[df["cluster"] == selected_cluster]

# Main info
st.subheader(f"📊 Thông tin Cluster {selected_cluster}")

col1, col2, col3 = st.columns(3)
col1.metric("Số khách hàng", df_cluster["CustomerID"].nunique())
col2.metric("Frequency TB", round(df_cluster["Frequency"].mean(), 2))
col3.metric("Monetary TB", round(df_cluster["Monetary"].mean(), 2))

# Persona + strategy (viết tay – đúng mini project)
st.subheader("🧠 Persona & Chiến lược")

persona_map = {
    0: ("Frequent Buyers", "Combo thiết yếu, tích điểm"),
    1: ("Premium Bundlers", "Bundle cao cấp, Upsell"),
    2: ("Occasional Shoppers", "Kích hoạt lại, Voucher"),
    3: ("Balanced Customers", "Cross-sell theo ngữ cảnh"),
}

persona, strategy = persona_map.get(
    selected_cluster, ("Khác", "Chưa xác định")
)

st.markdown(f"""
**Persona:** {persona}  
**Chiến lược marketing:** {strategy}
""")

# Show sample customers
st.subheader("📄 Một số khách hàng trong cluster")
st.dataframe(df_cluster.head(20))
