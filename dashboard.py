
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Superstore Sales Analysis Dashboard")
st.markdown(
    "Interactive dashboard for analyzing sales, "
    "profit, products, customers, and regional performance."
)

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    data = pd.read_csv("output/cleaned_superstore_data.csv")
    data["Order Date"] = pd.to_datetime(data["Order Date"])
    data["Ship Date"] = pd.to_datetime(data["Ship Date"])
    return data

df = load_data()

# --------------------------------------------------
# 3. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

regions = sorted(df["Region"].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=regions
)

categories = sorted(df["Category"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Select Category",
    categories,
    default=categories
)

segments = sorted(df["Segment"].dropna().unique())
selected_segments = st.sidebar.multiselect(
    "Select Customer Segment",
    segments,
    default=segments
)

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# --------------------------------------------------
# 4. APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    (df["Region"].isin(selected_regions)) &
    (df["Category"].isin(selected_categories)) &
    (df["Segment"].isin(selected_segments))
].copy()

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_date) &
        (filtered_df["Order Date"].dt.date <= end_date)
    ]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --------------------------------------------------
# 5. KPI METRICS
# --------------------------------------------------

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()
total_customers = filtered_df["Customer ID"].nunique()
profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

st.subheader("Business Performance Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Customers", f"{total_customers:,}")
col5.metric("Profit Margin", f"{profit_margin:.2f}%")

st.divider()

# --------------------------------------------------
# 6. SALES TREND
# --------------------------------------------------

st.subheader("Monthly Sales Trend")

monthly_sales = (
    filtered_df.set_index("Order Date")
    .resample("MS")["Sales"]
    .sum()
    .reset_index()
)

fig1 = px.line(
    monthly_sales,
    x="Order Date",
    y="Sales",
    markers=True,
    title="Monthly Sales Trend"
)

st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------
# 7. CATEGORY PERFORMANCE
# --------------------------------------------------

col1, col2 = st.columns(2)

category_summary = (
    filtered_df.groupby("Category")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
)

with col1:
    fig2 = px.bar(
        category_summary,
        x="Category",
        y="Sales",
        color="Category",
        title="Sales by Category"
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    fig3 = px.bar(
        category_summary,
        x="Category",
        y="Profit",
        color="Category",
        title="Profit by Category"
    )
    st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------
# 8. REGIONAL PERFORMANCE
# --------------------------------------------------

st.subheader("Regional Sales Distribution")

region_summary = (
    filtered_df.groupby("Region")["Sales"]
    .sum()
    .reset_index()
)

fig4 = px.pie(
    region_summary,
    names="Region",
    values="Sales",
    hole=0.4,
    title="Sales by Region"
)

st.plotly_chart(fig4, use_container_width=True)

# --------------------------------------------------
# 9. TOP 10 PRODUCTS
# --------------------------------------------------

st.subheader("Top 10 Products by Sales")

top_products = (
    filtered_df.groupby("Product Name")["Sales"]
    .sum()
    .reset_index()
    .nlargest(10, "Sales")
    .sort_values("Sales")
)

fig5 = px.bar(
    top_products,
    x="Sales",
    y="Product Name",
    orientation="h",
    title="Top 10 Products"
)

st.plotly_chart(fig5, use_container_width=True)

# --------------------------------------------------
# 10. PROFIT VS DISCOUNT
# --------------------------------------------------

st.subheader("Profitability Analysis")

fig6 = px.scatter(
    filtered_df,
    x="Discount",
    y="Profit",
    color="Category",
    size="Quantity",
    hover_data=["Product Name", "Region"],
    title="Discount vs Profit"
)

fig6.add_hline(y=0, line_dash="dash")

st.plotly_chart(fig6, use_container_width=True)

# --------------------------------------------------
# 11. DATA TABLE
# --------------------------------------------------

st.subheader("Filtered Sales Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# 12. DOWNLOAD FILTERED DATA
# --------------------------------------------------

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Sales Data",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully!")
