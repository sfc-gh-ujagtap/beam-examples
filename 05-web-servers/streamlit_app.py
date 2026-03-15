import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="TPC-H Sales Dashboard", page_icon="❄️", layout="wide")
st.title("❄️ TPC-H Sales Dashboard")
st.markdown("Sales analytics powered by Snowflake TPC-H sample data")

@st.cache_resource
def get_snowflake_connection():
    import snowflake.connector
    pat = os.environ.get("SNOWFLAKE_PAT")
    password = os.environ.get("SNOWFLAKE_PASSWORD")
    
    conn_params = {
        "account": os.environ.get("SNOWFLAKE_ACCOUNT"),
        "user": os.environ.get("SNOWFLAKE_USER"),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        "database": "SNOWFLAKE_SAMPLE_DATA",
        "schema": "TPCH_SF1",
    }
    
    if pat:
        conn_params["token"] = pat
        conn_params["authenticator"] = "programmatic_access_token"
    elif password:
        conn_params["password"] = password
    
    return snowflake.connector.connect(**conn_params)

@st.cache_data(ttl=600)
def get_orders_summary():
    conn = get_snowflake_connection()
    query = """
    SELECT DATE_TRUNC('month', O_ORDERDATE) as ORDER_MONTH, COUNT(*) as ORDER_COUNT,
           SUM(O_TOTALPRICE) as TOTAL_REVENUE, COUNT(DISTINCT O_CUSTKEY) as UNIQUE_CUSTOMERS
    FROM ORDERS WHERE O_ORDERDATE >= '1995-01-01'
    GROUP BY DATE_TRUNC('month', O_ORDERDATE) ORDER BY ORDER_MONTH
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_top_nations():
    conn = get_snowflake_connection()
    query = """
    SELECT N.N_NAME as NATION, SUM(O.O_TOTALPRICE) as TOTAL_REVENUE, COUNT(DISTINCT C.C_CUSTKEY) as CUSTOMER_COUNT
    FROM ORDERS O JOIN CUSTOMER C ON O.O_CUSTKEY = C.C_CUSTKEY JOIN NATION N ON C.C_NATIONKEY = N.N_NATIONKEY
    GROUP BY N.N_NAME ORDER BY TOTAL_REVENUE DESC LIMIT 10
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_order_priorities():
    conn = get_snowflake_connection()
    query = """SELECT O_ORDERPRIORITY as PRIORITY, COUNT(*) as ORDER_COUNT, SUM(O_TOTALPRICE) as TOTAL_REVENUE
    FROM ORDERS GROUP BY O_ORDERPRIORITY ORDER BY ORDER_COUNT DESC"""
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_top_parts():
    conn = get_snowflake_connection()
    query = """SELECT P.P_NAME as PART_NAME, P.P_TYPE as PART_TYPE, SUM(L.L_QUANTITY) as TOTAL_QUANTITY, SUM(L.L_EXTENDEDPRICE) as TOTAL_REVENUE
    FROM LINEITEM L JOIN PART P ON L.L_PARTKEY = P.P_PARTKEY GROUP BY P.P_NAME, P.P_TYPE ORDER BY TOTAL_REVENUE DESC LIMIT 10"""
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_recent_orders():
    conn = get_snowflake_connection()
    query = """SELECT O.O_ORDERKEY, O.O_ORDERDATE, C.C_NAME as CUSTOMER_NAME, O.O_TOTALPRICE, O.O_ORDERSTATUS, O.O_ORDERPRIORITY
    FROM ORDERS O JOIN CUSTOMER C ON O.O_CUSTKEY = C.C_CUSTKEY ORDER BY O.O_ORDERDATE DESC LIMIT 100"""
    return pd.read_sql(query, conn)

if not all([os.environ.get("SNOWFLAKE_ACCOUNT"), os.environ.get("SNOWFLAKE_USER")]) or not (os.environ.get("SNOWFLAKE_PASSWORD") or os.environ.get("SNOWFLAKE_PAT")):
    st.error("⚠️ Snowflake credentials not configured!")
    st.markdown("Set: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and either SNOWFLAKE_PASSWORD or SNOWFLAKE_PAT")
    st.stop()

try:
    with st.spinner("Loading data from Snowflake..."):
        orders_df = get_orders_summary()
        nations_df = get_top_nations()
        priorities_df = get_order_priorities()
        parts_df = get_top_parts()
        recent_orders_df = get_recent_orders()
except Exception as e:
    st.error(f"❌ Error connecting to Snowflake: {e}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"${orders_df['TOTAL_REVENUE'].sum():,.0f}")
with col2:
    st.metric("Total Orders", f"{orders_df['ORDER_COUNT'].sum():,}")
with col3:
    st.metric("Total Customers", f"{nations_df['CUSTOMER_COUNT'].sum():,}")
with col4:
    st.metric("Avg Order Value", f"${orders_df['TOTAL_REVENUE'].sum() / orders_df['ORDER_COUNT'].sum():,.2f}")

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Monthly Revenue Trend")
    fig1 = px.line(orders_df, x='ORDER_MONTH', y='TOTAL_REVENUE', markers=True)
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.subheader("🌍 Revenue by Nation")
    fig2 = px.bar(nations_df, x='NATION', y='TOTAL_REVENUE', color='TOTAL_REVENUE')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Orders by Priority")
    fig3 = px.pie(priorities_df, values='ORDER_COUNT', names='PRIORITY')
    st.plotly_chart(fig3, use_container_width=True)
with col2:
    st.subheader("🏆 Top Parts")
    fig4 = px.bar(parts_df, x='TOTAL_REVENUE', y='PART_NAME', orientation='h')
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader("📋 Recent Orders")
st.dataframe(recent_orders_df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("🔍 Interactive Analysis")
orders_df['ORDER_MONTH'] = pd.to_datetime(orders_df['ORDER_MONTH'])
years = orders_df['ORDER_MONTH'].dt.year.unique()
selected_year = st.selectbox("Select Year", sorted(years, reverse=True))
filtered_data = orders_df[orders_df['ORDER_MONTH'].dt.year == selected_year]
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Summary for {selected_year}:** Revenue: ${filtered_data['TOTAL_REVENUE'].sum():,.0f}, Orders: {filtered_data['ORDER_COUNT'].sum():,}")
with col2:
    fig5 = px.area(filtered_data, x='ORDER_MONTH', y='TOTAL_REVENUE')
    st.plotly_chart(fig5, use_container_width=True)
st.success("✅ Dashboard loaded!")
