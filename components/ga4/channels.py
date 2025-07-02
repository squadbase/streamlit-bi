import plotly.express as px  # Import Plotly Express
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
def channel_metrics_comparison_chart():
    # Fetch the data
    data = get_user_behavior_data()

    # Aggregate core metrics by channel
    metrics_df = (
        data.groupby("channelGrouping")
        .agg(
            avg_pageviews=("pageviews", "mean"),
            avg_session_duration=("timeOnSite", "mean"),
            bounce_rate=("bounces", "mean"),
            total_sessions=("visits", "sum"),  # for reference or filtering
        )
        .reset_index()
    )

    # Convert session duration from seconds to minutes
    metrics_df["avg_session_duration_min"] = metrics_df["avg_session_duration"] / 60

    # (Optional) Filter to top 5 channels by session count
    top_channels = metrics_df.nlargest(5, "total_sessions")["channelGrouping"]
    metrics_df = metrics_df[metrics_df["channelGrouping"].isin(top_channels)]

    # Melt for plotting
    plot_df = metrics_df.melt(
        id_vars="channelGrouping",
        value_vars=["avg_pageviews", "avg_session_duration_min"],
        var_name="Metric",
        value_name="Value",
    )

    # Map to readable labels
    plot_df["Metric"] = plot_df["Metric"].map(
        {
            "avg_pageviews": "Avg Pageviews",
            "avg_session_duration_min": "Avg Session Duration (min)",
        }
    )

    # Create grouped bar chart
    fig = px.bar(
        plot_df,
        x="Metric",
        y="Value",
        color="channelGrouping",
        barmode="group",
        title="Average Metrics by Channel",
    )

    # Update axis and legend labels
    fig.update_layout(xaxis_title="Metric", yaxis_title="Value", legend_title="Channel")

    # Render the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
