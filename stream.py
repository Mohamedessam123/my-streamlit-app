import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    df = pd.read_csv("customers_sessions.csv")
    df["session_start"] = pd.to_datetime(df["session_start"])
    return df

df = load_data()

# ===============================
# Sidebar Filters
# ===============================
with st.sidebar:
    st.header("🔎 Filter Options")
    
    selected_states = st.multiselect("Select States", df["customer_state"].unique())
    
    min_date = df["session_start"].dt.date.min()
    max_date = df["session_start"].dt.date.max()
    start_date, end_date = st.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    selected_devices = st.multiselect("Select Devices", df["device"].unique())
    selected_categories = st.multiselect("Select Categories", df["category_en"].unique())

# ===============================
# Apply filters
# ===============================
filtered_df = df.copy()

if selected_states:
    filtered_df = filtered_df[filtered_df["customer_state"].isin(selected_states)]

if isinstance(start_date, pd.Timestamp):
    start_date = start_date.date()
if isinstance(end_date, pd.Timestamp):
    end_date = end_date.date()

filtered_df = filtered_df[
    (filtered_df["session_start"].dt.date >= start_date) &
    (filtered_df["session_start"].dt.date <= end_date)
]

if selected_devices:
    filtered_df = filtered_df[filtered_df["device"].isin(selected_devices)]

if selected_categories:
    filtered_df = filtered_df[filtered_df["category_en"].isin(selected_categories)]


# ===============================
# Main Dashboard
# ===============================
st.title("📊 Customers & Sessions Analysis Dashboard")

if not filtered_df.empty:
    total_sessions = filtered_df["session_id"].nunique()
    total_products = filtered_df["product_id"].nunique()
    top_city = filtered_df['customer_city'].value_counts().idxmax()
    total_events = filtered_df["event_type"].count()
else:
    total_sessions, total_products, top_city, total_events = 0, 0, "N/A", 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("🖥️ Total Sessions", f"{total_sessions:,}")
col2.metric("📦 Unique Products", f"{total_products:,}")
col3.metric("🌆 Top City", f"{top_city}")
col4.metric("📈 Total Events", f"{total_events:,}")

st.markdown("---")

# ===============================
# Row 1 → Event Types + Device Usage
# ===============================
row1_col1, row1_col2 = st.columns(2, gap="large")

with row1_col1:
    st.subheader("1️⃣ Distribution of Event Types")
    if not filtered_df.empty:
        event_counts = filtered_df["event_type"].value_counts()
        event_df = event_counts.reset_index()
        event_df.columns = ["event_type", "count"]
        st.bar_chart(event_df.set_index("event_type"))
    else:
        st.warning("No data available for the selected filters.")

with row1_col2:
    st.subheader("2️⃣ Device Usage by Customers")
    if not filtered_df.empty:
        device_counts = filtered_df["device"].value_counts()
        fig, ax = plt.subplots(figsize=(8,5))
        ax.pie(device_counts.values, labels=device_counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title("Devices Used")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")

st.markdown("<br>", unsafe_allow_html=True)

# ===============================
# Row 2 → Sessions Over Time + Top Categories
# ===============================
row2_col1, row2_col2 = st.columns(2, gap="large")

with row2_col1:
    st.subheader("3️⃣ Sessions Over Time")
    if not filtered_df.empty:
        filtered_df["date"] = filtered_df["session_start"].dt.date
        sessions_per_day = filtered_df.groupby("date")["session_id"].nunique()

        fig, ax = plt.subplots(figsize=(10,5))
        sessions_per_day.plot(kind="line", marker="o", ax=ax)
        ax.set_ylabel("Number of Sessions")
        ax.set_xlabel("Date")
        ax.set_title("Sessions Trend Over Time")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")

with row2_col2:
    st.subheader("4️⃣ Top Product Categories")
    if not filtered_df.empty:
        category_counts = filtered_df["category_en"].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(10,5))
        sns.barplot(x=category_counts.values, y=category_counts.index, ax=ax)
        ax.set_xlabel("Count")
        ax.set_ylabel("Category")
        ax.set_title("Top 10 Product Categories")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")

st.markdown("<br>", unsafe_allow_html=True)

# ===============================
# Row 3 → Customer States
# ===============================
st.subheader("5️⃣ Customer Distribution by State")
if not filtered_df.empty:
    state_counts = filtered_df["customer_state"].value_counts()
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(x=state_counts.index, y=state_counts.values, ax=ax)
    ax.set_xlabel("State")
    ax.set_ylabel("Number of Customers")
    ax.set_title("Customer Distribution by State")
    st.pyplot(fig)
else:
    st.warning("No data available for the selected filters.")


st.write("### Raw Data Sample", filtered_df.head(10))