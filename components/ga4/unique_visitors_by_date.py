import pandas as pd
import plotly.express as px
import streamlit as st

from lib.bigquery_client import bigquery_client
from lib.tailwind_colors import COLORS


# ----------
# Unique Visitors
# ----------
@st.cache_data(ttl=86400)
def unique_visitors_by_date():
    # Initialize the BigQuery client
    # Define SQL to get unique visits per day
    query = """
    SELECT
      date AS session_date,
      COUNT(DISTINCT visitId) AS unique_visitors
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    GROUP BY session_date
    ORDER BY session_date
    """
    df = bigquery_client.query(query).to_dataframe()
    df["session_date"] = pd.to_datetime(df["session_date"], format="%Y%m%d")
    return df


@st.fragment
def unique_vistors_by_date_chart():
    # Load unique visitors data
    unique_visitors_df = unique_visitors_by_date()

    # Area chart for unique visitors# Area chart for unique visitors
    unique_visitors_fig = px.area(
        unique_visitors_df,
        x="session_date",
        y="unique_visitors",
        title="Daily Unique Visitors in July 2017",
        labels={"session_date": "Date", "unique_visitors": "Unique Visitors"},
        color_discrete_sequence=[COLORS["blue"]["500"]],
    )
    unique_visitors_fig.update_yaxes(range=[0, None])
    unique_visitors_fig.update_layout(xaxis_title="Date", yaxis_title="Unique Visitors")

    st.plotly_chart(unique_visitors_fig, use_container_width=True)
