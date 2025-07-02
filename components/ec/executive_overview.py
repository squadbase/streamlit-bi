import os
from datetime import date, timedelta

import streamlit as st

from lib.bigquery_client import bigquery_client

from .data_queries import q_customer_stats, q_daily_sales
from .utils import iso_format


def executive_overview():
    st.title("📊 Executive Overview")
    st.caption("thelook‑ecommerce public dataset → BigQuery → Streamlit 1.45.1")

    # Date Range Selection & Derived Periods
    TODAY = date.today()
    def_start = TODAY - timedelta(days=30)
    def_end = TODAY - timedelta(days=1)

    with st.sidebar:
        st.header("📅 Date Range")
        start_date: date = st.date_input("Start", def_start, max_value=TODAY)
        end_date: date = st.date_input("End", def_end, max_value=TODAY)

        if end_date < start_date:
            st.error("⚠️ End date must be on/after start date.")
            st.stop()

    # Previous period (same length immediately before)
    period_days = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)

    # Data Fetch
    current_df = q_daily_sales(start_date, end_date)
    prev_df = q_daily_sales(prev_start, prev_end)

    new_cust_cur, tot_cust_cur = q_customer_stats(start_date, end_date)
    new_cust_prev, tot_cust_prev = q_customer_stats(prev_start, prev_end)

    # KPI Calculations
    revenue_cur = current_df["revenue"].sum()
    revenue_prev = prev_df["revenue"].sum()
    orders_cur = current_df["orders"].sum()
    orders_prev = prev_df["orders"].sum()

    # Guard divisions
    aov_cur = revenue_cur / orders_cur if orders_cur else 0
    aov_prev = revenue_prev / orders_prev if orders_prev else 0

    new_rate_cur = (new_cust_cur / tot_cust_cur) * 100 if tot_cust_cur else 0
    new_rate_prev = (new_cust_prev / tot_cust_prev) * 100 if tot_cust_prev else 0

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Revenue",
        f"${revenue_cur:,.0f}",
        delta=f"{(revenue_cur - revenue_prev) / revenue_prev * 100:,.1f}%"
        if revenue_prev
        else "N/A",
    )
    col2.metric(
        "Orders",
        f"{orders_cur:,}",
        delta=f"{(orders_cur - orders_prev) / orders_prev * 100:,.1f}%"
        if orders_prev
        else "N/A",
    )
    col3.metric(
        "Avg. Order Value",
        f"${aov_cur:,.0f}",
        delta=f"{(aov_cur - aov_prev) / aov_prev * 100:,.1f}%" if aov_prev else "N/A",
    )
    col4.metric(
        "New‑Customer Rate",
        f"{new_rate_cur:.1f}%",
        delta=f"{(new_rate_cur - new_rate_prev):.1f} pt" if new_rate_prev else "N/A",
    )

    # Trend Charts
    st.subheader("Daily Revenue & Orders")
    trend_cols = st.columns(2)

    with trend_cols[0]:
        st.caption("💰 Revenue by Day")
        chart_df = current_df.set_index("day")[["revenue"]]
        st.line_chart(chart_df)

    with trend_cols[1]:
        st.caption("📦 Orders by Day")
        chart_df = current_df.set_index("day")[["orders"]]
        st.line_chart(chart_df)

    # New customers bar chart
    st.subheader("New Customers per Day")

    daily_new_query = f"""
        WITH first_orders AS (
            SELECT user_id, MIN(created_at) AS first_order_date
            FROM `bigquery-public-data.thelook_ecommerce.orders`
            GROUP BY user_id
        )
        SELECT DATE(first_order_date) AS order_date, COUNT(*) AS new_customers
        FROM first_orders
        WHERE first_order_date BETWEEN '{iso_format(start_date)}' AND '{iso_format(end_date)}'
        GROUP BY order_date
        ORDER BY order_date;
    """
    new_daily_df = bigquery_client.query(daily_new_query).to_dataframe()
    if not new_daily_df.empty:
        st.bar_chart(new_daily_df.set_index("order_date"))
    else:
        st.info("No new customers in the selected period.")

    # Optional AI Summary (if OpenAI key provided)
    if os.getenv("OPENAI_API_KEY"):
        st.subheader("📝 AI Summary")
        if st.button("Summarize with AI"):
            try:
                import openai

                openai.api_key = os.environ["OPENAI_API_KEY"]

                prompt = (
                    f"You are an e‑commerce BI analyst. Summarize the past {period_days} days "
                    "of performance in up to 80 words given these numbers:\n"
                    f"Revenue: ${revenue_cur:,.0f} ({(revenue_cur - revenue_prev) / revenue_prev * 100:,.1f}% vs prev).\n"
                    f"Orders: {orders_cur:,} ({(orders_cur - orders_prev) / orders_prev * 100:,.1f}% vs prev).\n"
                    f"AOV: ${aov_cur:,.0f}.\n"
                    f"New‑customer rate: {new_rate_cur:.1f}%."
                )
                with st.spinner("Generating summary …"):
                    resp = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=120,
                    )
                    st.write(resp.choices[0].message.content.strip())
            except Exception as e:
                st.warning(f"AI summary unavailable: {e}")
