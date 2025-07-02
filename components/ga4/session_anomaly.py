import plotly.graph_objects as go
import streamlit as st

from lib.bigquery_client import bigquery_client
from lib.tailwind_colors import COLORS


@st.cache_data(ttl=86400)
def detect_session_anomalies():
    query = """
    WITH daily AS (
    SELECT
        PARSE_DATE('%Y%m%d', date) AS session_date,
        COUNT(*) AS sessions
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    GROUP BY session_date
    ),
    calculated_metrics AS (
    SELECT
        session_date,
        sessions,
        AVG(sessions) OVER (
        ORDER BY session_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_avg,
        STDDEV_POP(sessions) OVER (
        ORDER BY session_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_std
    FROM daily
    )
    SELECT
    session_date,
    sessions,
    moving_avg,
    moving_std,
    CASE
        WHEN sessions > moving_avg + 1 * moving_std
        THEN TRUE
        ELSE FALSE
    END AS is_positive_anomaly,
    CASE
        WHEN sessions < moving_avg - 1 * moving_std
        THEN TRUE
        ELSE FALSE
    END AS is_negative_anomaly
    FROM calculated_metrics
    ORDER BY session_date
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.fragment
def session_anomaly_chart():
    # Load anomaly data
    anomaly_df = detect_session_anomalies()
    # Map colors: red for anomalies, blue otherwise
    colors = anomaly_df.apply(
        lambda row: COLORS["pink"]["500"]
        if row["is_positive_anomaly"]  # sessions > moving_avg + σ
        else COLORS["yellow"]["500"]
        if row["is_negative_anomaly"]  # sessions < moving_avg - σ
        else COLORS["blue"]["500"],  # normal range
        axis=1,
    )

    # Create bar chart with anomaly highlights
    anomaly_fig = go.Figure()
    anomaly_fig.add_trace(
        go.Bar(
            x=anomaly_df["session_date"],
            y=anomaly_df["sessions"],
            name="Sessions",
            marker_color=colors,
        )
    )

    # Add moving average line
    anomaly_fig.add_trace(
        go.Scatter(
            x=anomaly_df["session_date"],
            y=anomaly_df["moving_avg"],
            name="7-day Moving Avg",
            mode="lines",
            marker=dict(color=COLORS["amber"]["500"]),
            line=dict(color=COLORS["amber"]["500"], dash="dash"),
        )
    )

    anomaly_fig.update_layout(
        title_text="Daily Sessions with Anomaly Detection",
        xaxis_title="Date",
        yaxis_title="Sessions",
        legend=dict(x=0.01, y=0.99, bordercolor="LightGray", borderwidth=1),
        height=600,
    )

    st.plotly_chart(anomaly_fig, use_container_width=True)
