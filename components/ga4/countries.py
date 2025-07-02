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
        totals.newVisits,
        totals.bounces,
        geoNetwork.country AS country
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.fragment
def country_analysis_fragment():
    # Fetch the data
    data = get_user_behavior_data()

    # Aggregate core metrics by country
    metrics_df = (
        data.groupby("country")
        .agg(
            total_sessions=("visits", "sum"),
            avg_pageviews=("pageviews", "mean"),
            avg_session_duration=("timeOnSite", "mean"),
            bounce_rate=("bounces", "mean"),
        )
        .reset_index()
    )

    # Convert session duration from seconds to minutes
    metrics_df["avg_session_duration_min"] = metrics_df["avg_session_duration"] / 60

    # --- 1) World map of total sessions by country ---
    fig_map = px.choropleth(
        metrics_df,
        locations="country",  # Country names
        locationmode="country names",  # Interpret as full names
        color="total_sessions",  # Color scale by sessions
        title="Total Sessions by Country",
        hover_data={
            "avg_pageviews": True,
            "avg_session_duration_min": ":.1f",
        },
        projection="natural earth",  # Natural Earth projection
        scope="world",  # Limit to world map
    )

    # Tidy up geographic features
    fig_map.update_geos(
        showframe=False,  # Remove frame
        showcountries=True,
        countrycolor="LightGrey",
        showland=False,
        showocean=False,
        lataxis_range=[-60, 90],
    )

    # Expand chart area, label the colorbar
    fig_map.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Sessions", ticks="outside", lenmode="fraction", len=0.5
        ),
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # --- 2) Top 10 countries by total sessions (bar chart) ---
    top_countries = metrics_df.nlargest(10, "total_sessions")
    fig_bar = px.bar(
        top_countries,
        x="country",
        y="total_sessions",
        title="Top 10 Countries by Sessions",
        labels={"country": "Country", "total_sessions": "Total Sessions"},
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- 3) Comparison of average metrics for top 5 countries ---
    compare_df = top_countries.nlargest(5, "total_sessions")[
        [
            "country",
            "avg_pageviews",
            "avg_session_duration_min",
        ]
    ].melt(id_vars="country", var_name="Metric", value_name="Value")
    compare_df["Metric"] = compare_df["Metric"].map(
        {
            "avg_pageviews": "Avg Pageviews",
            "avg_session_duration_min": "Avg Session Duration (min)",
        }
    )

    fig_compare = px.bar(
        compare_df,
        x="Metric",
        y="Value",
        color="country",
        barmode="group",
        title="Average Metrics by Country (Top 5)",
    )
    fig_compare.update_layout(
        xaxis_title="Metric", yaxis_title="Value", legend_title="Country"
    )
    st.plotly_chart(fig_compare, use_container_width=True)
