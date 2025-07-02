import plotly.express as px
import streamlit as st

from .data_queries import q_daily_sales_trend
from .utils import get_date_inputs, get_date_range


def daily_sales_trend():
    start, end = get_date_inputs()
    start, end, *_ = get_date_range(start, end)
    st.title("📈 Daily Sales and Profit Trend")

    trend_df = q_daily_sales_trend(start, end)

    if trend_df.empty:
        st.warning("No data available for the selected date range.")
        return

    # Display Sales and Profit Trend using Plotly Express
    fig_sales_profit_trend = px.line(
        trend_df,
        x="day",
        y=["total_sales", "total_profit"],
        title="Daily Sales and Profit Trend",
        labels={"value": "Amount ($)", "day": "Date"},
        template="plotly_white",
        line_shape="linear",
    )
    fig_sales_profit_trend.update_layout(hovermode="x unified")
    st.plotly_chart(fig_sales_profit_trend, use_container_width=True)
