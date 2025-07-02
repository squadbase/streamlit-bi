import pandas as pd
import streamlit as st

from lib.bigquery_client import bigquery_client


@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_user_behavior_data():
    query = """
    SELECT
        FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', date)) AS date,
        fullVisitorId,
        (SELECT MAX(IF(hit.type = 'PAGE', 1, 0)) FROM UNNEST(hits) AS hit) AS is_pageview,
        device.deviceCategory AS deviceCategory,
        channelGrouping,
        totals.visits,
        totals.pageviews,
        totals.timeOnSite,
        totals.bounces,
        totals.newVisits
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.fragment
def basic_metrics():
    data = get_user_behavior_data()

    if data.empty:
        st.warning("No data found. Please check the BigQuery query and date range.")
        st.stop()

    # --- Data preprocessing and metric calculations ---
    # Convert to datetime
    data["date"] = pd.to_datetime(data["date"])

    # Unique Users (UU): count of unique fullVisitorId
    # Sessions: sum of totals.visits (each row typically represents one session)
    # Pageviews: sum of totals.pageviews
    # Bounce rate: (number of sessions with bounces == 1) / total sessions
    # Average session duration: mean of totals.timeOnSite

    # Prepare time series summary data
    daily_summary = (
        data.groupby("date")
        .agg(
            unique_users=("fullVisitorId", "nunique"),
            sessions=("visits", "sum"),
            pageviews=("pageviews", "sum"),
            bounces=("bounces", lambda x: (x == 1).sum()),
        )
        .reset_index()
    )

    daily_summary["bounce_rate"] = (
        daily_summary["bounces"] / daily_summary["sessions"] * 100
    ).fillna(0)
    daily_summary["avg_session_duration"] = (
        data.groupby("date")["timeOnSite"]
        .mean()
        .fillna(0)
        .reset_index(name="avg_session_duration")["avg_session_duration"]
    )

    # --- KPI Cards ---
    st.subheader("Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Pageviews", f"{data['pageviews'].sum():,.0f}")
    with col2:
        st.metric("Total Unique Users", f"{data['fullVisitorId'].nunique():,.0f}")
    with col3:
        st.metric("Total Sessions", f"{data['visits'].sum():,.0f}")
    with col4:
        st.metric("Average Session Duration (s)", f"{data['timeOnSite'].mean():,.1f}")
    with col5:
        st.metric("Bounce Rate", f"{daily_summary['bounce_rate'].mean():,.1f}%")
