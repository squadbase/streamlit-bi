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
def new_vs_returning_chart():
    # Fetch the data
    data = get_user_behavior_data()

    # Classify each session as New or Returning
    user_type_counts = (
        data["newVisits"]
        .fillna(0)
        .apply(lambda x: "New User" if x == 1 else "Returning User")
        .value_counts()
        .reset_index()
    )
    user_type_counts.columns = ["UserType", "Count"]

    # Create a pie chart with Plotly Express
    fig = px.pie(
        user_type_counts,
        names="UserType",  # Column for labels
        values="Count",  # Column for values
        title="New vs Returning Users",  # Chart title
        hole=0.4,  # Make it a donut chart; remove or set to 0 for a full pie
    )

    # Improve the label display inside slices
    fig.update_traces(textposition="inside", textinfo="percent+label")

    # Render the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


@st.fragment
def metrics_comparison_chart():
    # Fetch the data
    data = get_user_behavior_data()

    # Label sessions as New User or Returning User
    data["UserType"] = (
        data["newVisits"]
        .fillna(0)
        .apply(lambda x: "New User" if x == 1 else "Returning User")
    )

    # Calculate core metrics: average pageviews, average session duration, bounce rate
    metrics_df = (
        data.groupby("UserType")
        .agg(
            avg_pageviews=("pageviews", "mean"),
            avg_session_duration=("timeOnSite", "mean"),
            bounce_rate=("bounces", "mean"),
            # If you selected transactions, you could do:
            # avg_transactions=('transactions', 'mean'),
            # conversion_rate=('transactions', lambda s: (s > 0).mean())
        )
        .reset_index()
    )

    # Convert session duration from seconds to minutes
    metrics_df["avg_session_duration_min"] = metrics_df["avg_session_duration"] / 60

    # Prepare data for plotting
    plot_df = metrics_df.melt(
        id_vars="UserType",
        value_vars=["avg_pageviews", "avg_session_duration_min"],
        var_name="Metric",
        value_name="Value",
    )

    # Map technical metric names to readable labels
    plot_df["Metric"] = plot_df["Metric"].map(
        {
            "avg_pageviews": "Avg Pageviews",
            "avg_session_duration_min": "Avg Session Duration (min)",
            # 'avg_transactions': 'Avg Transactions',
            # 'conversion_rate': 'Conversion Rate (%)'
        }
    )

    # Create grouped bar chart
    fig = px.bar(
        plot_df,
        x="Metric",
        y="Value",
        color="UserType",
        barmode="group",
        title="Average Metrics by User Type",
    )

    # Update axis and legend labels
    fig.update_layout(
        xaxis_title="Metric", yaxis_title="Value", legend_title="User Type"
    )

    # Render the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
