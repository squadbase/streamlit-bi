import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from lib.bigquery_client import bigquery_client
from lib.tailwind_colors import COLORS


@st.cache_data(ttl=86400)
def ave_session_time_and_page_views():
    # Define SQL to get average session time and pages per day
    query = """
    SELECT
      date AS session_date,
      AVG(totals.timeOnSite) AS avg_duration_seconds,
      SUM(totals.pageviews) AS total_pageviews
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    GROUP BY session_date
    ORDER BY session_date
    """
    df = bigquery_client.query(query).to_dataframe()
    df["session_date"] = pd.to_datetime(df["session_date"], format="%Y%m%d")
    return df


@st.fragment
def session_and_pv_by_date_chart():
    # Load session time and pageviews data
    session_pageview_df = ave_session_time_and_page_views()

    # Combined chart with secondary y-axis
    session_pageview_fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Bar trace for pageviews
    session_pageview_fig.add_trace(
        go.Bar(
            x=session_pageview_df["session_date"],
            y=session_pageview_df["total_pageviews"],
            name="Total Pageviews",
            marker_color=COLORS["blue"]["500"],
        ),
        secondary_y=False,
    )
    # Line trace for session duration
    session_pageview_fig.add_trace(
        go.Scatter(
            x=session_pageview_df["session_date"],
            y=session_pageview_df["avg_duration_seconds"],
            name="Avg Session Duration (s)",
            mode="lines+markers",
            marker_color=COLORS["amber"]["500"],
            line=dict(color=COLORS["amber"]["500"]),
        ),
        secondary_y=True,
    )
    # Axis titles
    session_pageview_fig.update_xaxes(title_text="Date")
    session_pageview_fig.update_yaxes(title_text="Total Pageviews", secondary_y=False)
    session_pageview_fig.update_yaxes(
        title_text="Avg Session Duration (s)", secondary_y=True
    )
    # Layout adjustments
    session_pageview_fig.update_layout(
        title_text="Daily Pageviews and Average Session Duration (July 2017)",
        legend=dict(x=0.01, y=0.99, bordercolor="LightGray", borderwidth=1),
    )

    st.plotly_chart(session_pageview_fig, use_container_width=True)
