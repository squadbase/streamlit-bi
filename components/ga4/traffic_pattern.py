import plotly.express as px
import streamlit as st

from lib.bigquery_client import bigquery_client


@st.cache_data(ttl=86400)
def traffic_by_weekday_and_hour():
    # SQL to get session counts by weekday and hour
    query = """
    SELECT
      FORMAT_TIMESTAMP('%A', TIMESTAMP_SECONDS(visitStartTime)) AS weekday,
      EXTRACT(HOUR FROM TIMESTAMP_SECONDS(visitStartTime)) AS hour,
      COUNT(*) AS sessions
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    GROUP BY weekday, hour
    ORDER BY weekday, hour
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.fragment
def traffic_pattern_chart():
    # Load traffic data
    traffic_df = traffic_by_weekday_and_hour()

    # Pivot DataFrame to have weekdays as rows and hours as columns
    traffic_pivot = traffic_df.pivot(index="weekday", columns="hour", values="sessions")

    # Ensure weekdays are ordered Monday→Sunday (adjust as needed)
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    traffic_pivot = traffic_pivot.reindex(weekday_order)

    # Create heatmap
    heatmap_fig = px.imshow(
        traffic_pivot,
        labels=dict(x="Hour of Day", y="Weekday", color="Sessions"),
        x=traffic_pivot.columns,
        y=traffic_pivot.index,
        aspect="auto",
        title="Sessions by Weekday and Hour (July 2017)",
    )
    # Increase figure height if needed
    heatmap_fig.update_layout(height=600, margin=dict(l=50, r=50, t=80, b=50))

    # Display in Streamlit
    st.plotly_chart(heatmap_fig, use_container_width=True)
