import streamlit as st
import pandas as pd
import plotly.express as px

# تحميل البيانات
df = pd.read_csv("Payment(1).csv")

# تحويل التواريخ
df['time_purchased'] = pd.to_datetime(df['time_purchased'])

# 🎨 اختيار باليت ألوان موحدة
color_theme = px.colors.qualitative.Bold  

st.set_page_config(layout="wide")
st.title("💳 Payment Analysis Dashboard")

# =========================
# 🖌️ Custom CSS for Metrics
# =========================
st.markdown("""
    <style>
    /* Style the metric container */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        text-align: center;
    }
    /* Style the metric label */
    div[data-testid="metric-container"] > div > div:first-child {
        font-size: 1.2em;
        font-weight: bold;
        color: #2c3e50;
    }
    /* Style the metric value */
    div[data-testid="metric-container"] > div > div:last-child {
        font-size: 1.5em;
        color: #1e88e5;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# 🔍 الفلاتر
# =========================
st.sidebar.header("🔎 Filters")

# معالجة القيم الفارغة NaN
df['status'] = df['status'].fillna("Unknown")
df['payment_type'] = df['payment_type'].fillna("Unknown")
df['payment_installments'] = df['payment_installments'].fillna(0)

status_filter = st.sidebar.multiselect(
    "Filter by Status",
    options=df['status'].unique().tolist(),
    default=df['status'].unique().tolist()
)

payment_type_filter = st.sidebar.multiselect(
    "Filter by Payment Type",
    options=df['payment_type'].unique().tolist(),
    default=df['payment_type'].unique().tolist()
)

installments_filter = st.sidebar.multiselect(
    "Filter by Installments",
    options=df['payment_installments'].unique().tolist(),
    default=df['payment_installments'].unique().tolist()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['time_purchased'].min(), df['time_purchased'].max()]
)

# تطبيق الفلاتر على البيانات
filtered_df = df[
    (df['status'].isin(status_filter)) &
    (df['payment_type'].isin(payment_type_filter)) &
    (df['payment_installments'].isin(installments_filter)) &
    (df['time_purchased'].dt.date >= pd.to_datetime(date_range[0]).date()) &
    (df['time_purchased'].dt.date <= pd.to_datetime(date_range[1]).date())
]

# =========================
# KPIs
# =========================
total_payments = filtered_df['payment_value'].sum()
avg_payment = filtered_df['payment_value'].mean()
num_payments = filtered_df['Payment_id'].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Payments", f"${total_payments:,.2f}",border= True)
col2.metric("📊 Average Payment", f"${avg_payment:,.2f}",border= True)
col3.metric("🧾 Number of Payments", f"{num_payments:,}",border= True)

# =========================
# الرسوم
# =========================

# 1️⃣ نسبة الفشل حسب وسيلة الدفع
total_methods = filtered_df.groupby("payment_type")['status'].count().reset_index(name="total_count")
failed_methods = filtered_df[filtered_df['status'].str.lower().isin(["fail", "failed", "canceled", "refused"])] \
                    .groupby("payment_type")['status'].count().reset_index(name="failed_count")
merged = pd.merge(total_methods, failed_methods, on="payment_type", how="left").fillna(0)
merged["failed_ratio"] = (merged["failed_count"] / merged["total_count"]) * 100

fig2 = px.bar(
    merged, x="payment_type", y="failed_ratio",
    title="Failure Ratio by Payment Method (%)",
    text=merged["failed_ratio"].round(2),
    color="payment_type", color_discrete_sequence=color_theme
)
fig2.update_traces(textposition="outside")

# 2️⃣ توزيع طرق الدفع
payment_counts = filtered_df['payment_type'].value_counts().reset_index(name="count")
payment_counts.columns = ['payment_type', 'count']

fig4 = px.bar(
    payment_counts, x='payment_type', y='count',
    title="Payment Methods Usage",
    labels={'payment_type': 'Payment Method', 'count': 'Count'},
    color='payment_type', color_discrete_sequence=color_theme
)

# ✅ عرض أول صف: Payment Methods Focus
col1, col2 = st.columns(2)
col1.plotly_chart(fig2, use_container_width=True)
col2.plotly_chart(fig4, use_container_width=True)

# 3️⃣ المدفوعات الفاشلة
fig3 = px.bar(
    failed_methods, x="payment_type", y="failed_count",
    title="Failed Payments by Payment Method",
    color="payment_type", color_discrete_sequence=color_theme
)

# 4️⃣ إجمالي المبالغ حسب الحالة
status_df = filtered_df.groupby("status")['payment_value'].sum().reset_index()
fig5 = px.pie(
    status_df, names="status", values="payment_value",
    title="Payments by Status", hole=0,
    color_discrete_sequence=color_theme
)

# ✅ عرض ثاني صف: Failure and Status Analysis
col3, col4 = st.columns(2)
col3.plotly_chart(fig3, use_container_width=True)
col4.plotly_chart(fig5, use_container_width=True)

# 5️⃣ إجمالي المدفوعات عبر الزمن
monthly = filtered_df.groupby(filtered_df['time_purchased'].dt.to_period("M"))['payment_value'].sum().reset_index()
monthly['time_purchased'] = monthly['time_purchased'].astype(str)

fig1 = px.line(
    monthly, x="time_purchased", y="payment_value",
    markers=True, title="Total Payments Over Time",
    color_discrete_sequence=color_theme
)

# 6️⃣ الأجهزة الأكثر استخدامًا
device_counts = filtered_df['device'].value_counts().reset_index(name="count")
device_counts.columns = ['device', 'count']

fig6 = px.bar(
    device_counts, x='device', y='count',
    title="Payments by Device",
    labels={'device': 'Device', 'count': 'Count'},
    color='device', color_discrete_sequence=color_theme
)

# ✅ عرض ثالث صف: Device and Time Trends
col5, col6 = st.columns(2)
col5.plotly_chart(fig1, use_container_width=True)
col6.plotly_chart(fig6, use_container_width=True)

# 7️⃣ توزيع قيم المدفوعات
fig7 = px.histogram(
    filtered_df, x="payment_value", nbins=30,
    title="Distribution of Payment Values",
    color_discrete_sequence=color_theme
)

# ✅ عرض رابع صف: Payment Value Distribution
st.plotly_chart(fig7, use_container_width=True)