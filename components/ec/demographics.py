import pandas as pd
import plotly.express as px
import streamlit as st

from .data_queries import q_customer_demographics
from .utils import get_date_inputs, get_date_range


def customer_demographics():
    start, end = get_date_inputs()
    start, end, *_ = get_date_range(start, end)
    st.title("👥 Customer Demographics and Order Status")

    df_demographics = q_customer_demographics(start, end)

    if df_demographics.empty:
        st.warning("No demographic data available for the selected date range.")
        return

    col_order_status, col_gender_age = st.columns(2)

    with col_order_status:
        order_status_counts = (
            df_demographics.groupby("order_status")["order_count"].sum().reset_index()
        )
        order_status_counts.columns = ["Status", "Count"]
        fig_order_status = px.pie(
            order_status_counts,
            values="Count",
            names="Status",
            title="Order Status Distribution",
            hole=0.3,
            template="plotly_white",
        )
        st.plotly_chart(fig_order_status, use_container_width=True)

    with col_gender_age:
        # Ensure age is numeric and handle potential errors
        df_demographics["age"] = pd.to_numeric(df_demographics["age"], errors="coerce")
        df_demographics.dropna(subset=["age"], inplace=True)

        df_customers_by_gender_age = (
            df_demographics.groupby(["user_gender", "age"])["unique_customers"]
            .sum()
            .reset_index()
        )
        df_customers_by_gender_age.columns = ["Gender", "Age", "Unique Customers"]
        df_customers_by_gender_age = df_customers_by_gender_age.sort_values(by="Age")

        fig_gender_age = px.bar(
            df_customers_by_gender_age,
            x="Age",
            y="Unique Customers",
            color="Gender",
            title="Unique Customers by Gender and Age Group",
            labels={"Age": "Age", "Unique Customers": "Unique Customers"},
            template="plotly_white",
            barmode="group",
        )
        st.plotly_chart(fig_gender_age, use_container_width=True)
