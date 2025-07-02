import polars as pl
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer

from lib.bigquery_client import bigquery_client


@st.cache_data
def query_public_bq():
    query = """
            SELECT
              fullVisitorId                                   AS visitorId,
              CAST(visitId       AS STRING)                   AS visitId,
              CAST(visitStartTime AS STRING)                  AS visitStartTime,
              date,

              CAST(totals.hits                     AS STRING) AS totals_hits,
              CAST(totals.pageviews                AS STRING) AS totals_pageviews,
              CAST(totals.timeOnSite               AS STRING) AS totals_timeOnSite,

              trafficSource.source           AS trafficSource_source,
              trafficSource.medium           AS trafficSource_medium,
              trafficSource.campaign         AS trafficSource_campaign,
              trafficSource.keyword          AS trafficSource_keyword,
              trafficSource.referralPath     AS trafficSource_referralPath,

              device.browser,
              device.operatingSystem,
              device.deviceCategory        AS device_category,

              geoNetwork.continent,
              geoNetwork.country           AS geo_country,

              channelGrouping,

            FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
            WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
            """
    result = bigquery_client.query(query)
    df = pl.from_arrow(result.to_arrow())
    return df


def eda_pygwalker():
    # Load data
    df = query_public_bq()
    walker = StreamlitRenderer(df, kernel_computation=True)
    walker.explorer()
