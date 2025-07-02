import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from lib.bigquery_client import bigquery_client


@st.cache_data(ttl=86400)
def landing_page_performance():
    query = """
    SELECT
      hit.page.pagePath AS landing_page,
      COUNT(*) AS sessions,
      SUM(CASE WHEN totals.bounces = 1 THEN 1 ELSE 0 END) AS bounces,
      ROUND(SUM(CASE WHEN totals.bounces = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS bounce_rate
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS s,
    UNNEST(s.hits) AS hit
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
      AND hit.hitNumber = 1
    GROUP BY landing_page
    ORDER BY sessions DESC
    LIMIT 10
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.fragment
def landing_page_performance_chart():
    # Load data
    lp_df = landing_page_performance()

    # Create subplot with secondary y-axis
    lp_fig = make_subplots(specs=[[{"secondary_y": True}]])

    truncated_labels = lp_df["landing_page"].apply(
        lambda x: x if len(x) <= 25 else x[:25] + "..."
    )

    # Sessions on primary y-axis
    lp_fig.add_trace(
        go.Bar(
            x=lp_df["landing_page"],
            y=lp_df["sessions"],
            name="Sessions",
            marker_color="#3b82f6",
            offsetgroup="1",
        ),
        secondary_y=False,
    )

    # Bounce Rate (%) on secondary y-axis
    lp_fig.add_trace(
        go.Scatter(
            x=lp_df["landing_page"],
            y=lp_df["bounce_rate"],
            name="Bounce Rate (%)",
            mode="lines+markers",
            marker=dict(color="#EF553B"),
        ),
        secondary_y=True,
    )

    lp_fig.update_layout(
        title_text="Top 10 Landing Pages: Sessions and Bounce Rate",
        barmode="group",
        bargap=0.2,
        height=600,
    )

    lp_fig.update_xaxes(
        tickmode="array",
        tickvals=lp_df["landing_page"].tolist(),
        ticktext=truncated_labels.tolist(),
        tickangle=-45,
        title_text="Landing Page",
    )

    # Primary Y-axis
    lp_fig.update_yaxes(title_text="Sessions", secondary_y=False)

    # Secondary Y-axis fixed 0–100%
    lp_fig.update_yaxes(title_text="Bounce Rate (%)", secondary_y=True, range=[0, 100])

    st.plotly_chart(lp_fig, use_container_width=True)
