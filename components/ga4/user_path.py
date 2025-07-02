import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib.bigquery_client import bigquery_client


@st.cache_data(ttl=86400)
def page_path_transitions(limit=50):
    # English comments only inside code blocks
    query = f"""
    WITH hits AS (
      SELECT
        CONCAT(fullVisitorId, '-', CAST(visitId AS STRING)) AS session_id,
        hits.hitNumber AS hit_num,
        hits.page.pagePath AS page
      FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`,
           UNNEST(hits) AS hits
      WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    ),
    transitions AS (
      SELECT
        a.page AS source,
        b.page AS target,
        COUNT(*) AS value
      FROM hits a
      JOIN hits b
        ON a.session_id = b.session_id
       AND b.hit_num = a.hit_num + 1
      GROUP BY source, target
      ORDER BY value DESC
      LIMIT {limit}
    )
    SELECT * FROM transitions;
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.fragment
def user_path_chart():
    # Load transition data (top 50 transitions by default)
    trans_df = page_path_transitions(limit=50)

    # Build node list and index map
    all_nodes = list(pd.unique(trans_df[["source", "target"]].values.ravel()))
    node_indices = {page: idx for idx, page in enumerate(all_nodes)}

    # Prepare Sankey inputs
    sources = trans_df["source"].map(node_indices)
    targets = trans_df["target"].map(node_indices)
    values = trans_df["value"]

    # Create Sankey diagram
    sankey_fig = go.Figure(
        go.Sankey(
            node=dict(
                label=all_nodes,
                pad=15,
                thickness=15,
                line=dict(color="black", width=0.5),
            ),
            link=dict(source=sources, target=targets, value=values),
        )
    )
    sankey_fig.update_layout(
        title_text="Top Page-to-Page Transitions (Sankey Diagram)",
        height=800,
        font=dict(
            size=12,
            color="black",  # English comment: ensure all text uses black
        ),
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
    )

    # Display in Streamlit
    st.plotly_chart(sankey_fig, use_container_width=True)
