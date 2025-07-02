import pandas as pd
import streamlit as st

from lib.bigquery_client import bigquery_client


@st.cache_data
def query_public_bq():
    query = """
            SELECT *
            FROM `bigquery-public-data.google_analytics_sample.ga_sessions_20170801`
            LIMIT 10
            """
    result = bigquery_client.query(query)
    return result.to_dataframe()


@st.fragment
def data_catalog():
    # Display the DataFrame
    df = query_public_bq()
    st.dataframe(df, use_container_width=True)  # Display full width

    st.markdown("---")
    st.header("Data Column Descriptions")
    st.write("Below are the main columns in this dataset and their descriptions.")

    # Table of main top-level columns
    st.subheader("Main Top-Level Columns")
    st.table(
        pd.DataFrame(
            {
                "Column Name": [
                    "fullVisitorId",
                    "visitId",
                    "visitNumber",
                    "visitStartTime",
                    "date",
                    "channelGrouping",
                ],
                "Description": [
                    "Anonymous ID that uniquely identifies a user visiting the site.",
                    "ID that uniquely identifies a specific session.",
                    "Number indicating which session this is for the user.",
                    "Unix timestamp (UTC seconds) when the session started.",
                    "Date of the session (string in YYYYMMDD format).",
                    "Default channel grouping for the session (e.g., 'Organic Search', 'Direct').",
                ],
                "Example": [
                    "1234567890",
                    "987654321",
                    "1",
                    "1501603200",
                    "20170801",
                    "Organic Search",
                ],
            }
        )
    )

    st.subheader("Details of Nested Fields")

    # totals info in an expander
    with st.expander("📊 totals (Session Aggregation Info)"):
        st.write("Contains aggregate information for each session.")
        st.table(
            pd.DataFrame(
                {
                    "Column Name": [
                        "totals.visits",
                        "totals.hits",
                        "totals.pageviews",
                        "totals.timeOnSite",
                        "totals.bounces",
                        "totals.newVisits",
                        "totals.transactions",
                        "totals.totalTransactionRevenue",
                    ],
                    "Description": [
                        "Number of visits in the session (usually 1).",
                        "Total interactions in the session (pageviews, events, transactions, etc.).",
                        "Total pageviews in the session.",
                        "Total session duration in seconds.",
                        "`1` if the session bounced (only one pageview), otherwise NULL.",
                        "`1` if the session is a new user’s first session, otherwise NULL.",
                        "Number of transactions in the session.",
                        "Total revenue from transactions in the session (in micros).",
                    ],
                    "Example": [
                        "1",
                        "15",
                        "10",
                        "300",
                        "NULL",
                        "1",
                        "1",
                        "1234500000",
                    ],
                }
            )
        )

    # trafficSource info in an expander
    with st.expander("🔗 trafficSource (Referral Information)"):
        st.write(
            "Contains information about the referrer that brought the session to the site."
        )
        st.table(
            pd.DataFrame(
                {
                    "Column Name": [
                        "trafficSource.campaign",
                        "trafficSource.source",
                        "trafficSource.medium",
                        "trafficSource.keyword",
                        "trafficSource.adContent",
                    ],
                    "Description": [
                        "Campaign name associated with the session.",
                        "Source of the session (e.g., 'google', 'direct', 'bing').",
                        "Medium of the session (e.g., 'organic', 'cpc', 'referral').",
                        "Organic or paid search keyword.",
                        "Ad content.",
                    ],
                    "Example": [
                        "Default Campaign",
                        "google",
                        "organic",
                        "search keyword",
                        "Ad Content A",
                    ],
                }
            )
        )

    # device info in an expander
    with st.expander("📱 device (Device Information)"):
        st.write(
            "Contains information about the device used by the user to access the site."
        )
        st.table(
            pd.DataFrame(
                {
                    "Column Name": [
                        "device.browser",
                        "device.operatingSystem",
                        "device.isMobile",
                        "device.deviceCategory",
                    ],
                    "Description": [
                        "Browser name (e.g., 'Chrome', 'Safari').",
                        "Operating system (e.g., 'Windows', 'iOS').",
                        "TRUE if accessed from a mobile device, otherwise FALSE.",
                        "Device category (e.g., 'desktop', 'mobile', 'tablet').",
                    ],
                    "Example": [
                        "Chrome",
                        "Macintosh",
                        "FALSE",
                        "desktop",
                    ],
                }
            )
        )

    # geoNetwork info in an expander
    with st.expander("🌍 geoNetwork (Geographic Information)"):
        st.write("Contains geographic information of the user.")
        st.table(
            pd.DataFrame(
                {
                    "Column Name": [
                        "geoNetwork.continent",
                        "geoNetwork.subContinent",
                        "geoNetwork.country",
                        "geoNetwork.region",
                        "geoNetwork.city",
                    ],
                    "Description": [
                        "Continent.",
                        "Sub-continent.",
                        "Country.",
                        "Region (e.g., state or province).",
                        "City.",
                    ],
                    "Example": [
                        "Americas",
                        "Northern America",
                        "United States",
                        "California",
                        "Mountain View",
                    ],
                }
            )
        )

    # hits info in an expander
    with st.expander("⚡ hits (Individual Interaction Info)"):
        st.write(
            "A **repeated record** containing detailed information on each interaction "
            "(pageview, event, transaction, etc.) within a session. To analyze this field "
            "in detail, you need to expand it using the `UNNEST` clause in BigQuery SQL."
        )
        st.table(
            pd.DataFrame(
                {
                    "Column Name": [
                        "hits.hitNumber",
                        "hits.type",
                        "hits.page.pagePath",
                        "hits.page.pageTitle",
                        "hits.eventInfo.eventCategory",
                        "hits.eventInfo.eventAction",
                        "hits.transaction.transactionId",
                    ],
                    "Description": [
                        "Sequential number of the hit within the session.",
                        "Type of hit (e.g., 'PAGE', 'EVENT', 'TRANSACTION').",
                        "URL path of the hit page.",
                        "Title of the hit page.",
                        "Event category.",
                        "Event action.",
                        "Transaction ID (if a purchase occurred).",
                    ],
                    "Example": [
                        "1",
                        "PAGE",
                        "/home",
                        "Homepage",
                        "Video",
                        "Play",
                        "T12345",
                    ],
                }
            )
        )

    # customDimensions info in an expander
    with st.expander("📏 customDimensions (Custom Dimension Information)"):
        st.write(
            "A **repeated record** containing custom dimensions set in Google Analytics. "
            "Each custom dimension has an `index` and a `value`."
        )
        st.table(
            pd.DataFrame(
                {
                    "Column Name": [
                        "customDimensions.index",
                        "customDimensions.value",
                    ],
                    "Description": [
                        "Index number of the custom dimension.",
                        "Value of the custom dimension.",
                    ],
                    "Example": [
                        "1",
                        "Premium User",
                    ],
                }
            )
        )

    st.info(
        "💡 **Note**: When using `SELECT *`, some columns are provided as nested records "
        "(e.g., `totals`, `device`, `geoNetwork`, `trafficSource`, `hits`, `customDimensions`). "
        "You can access them in a DataFrame using dot notation, but to retrieve and expand all "
        "details of **repeated records** such as `hits` or `customDimensions`, you need to use "
        "the `UNNEST` clause in BigQuery SQL."
    )

    st.markdown("---")

    st.header("🗄️ Expanding Repeated Records with UNNEST")
    st.write(
        "BigQuery datasets include **repeated records** in fields like `hits` or `customDimensions`, "
        "where a single row can contain multiple values. These records appear as nested lists or "
        "dictionaries when accessed directly in a DataFrame, making it difficult to analyze individual "
        "elements."
    )
    st.write(
        "This is where the BigQuery SQL `UNNEST` operator comes in handy. Using `UNNEST` expands each "
        "element in a repeated record into its own row, transforming it into a flat table structure. "
        "This makes filtering, aggregating, and analyzing the data much easier."
    )

    st.subheader("Basic Usage of UNNEST")
    st.write(
        "`UNNEST` is often used with a `CROSS JOIN` or `LEFT JOIN` against a table."
    )

    st.markdown("""
    * **`CROSS JOIN UNNEST(array_expression)`**:
        Duplicates the original table row for each element in the repeated field. If the repeated field is empty, the original row is not included in the result.

    * **`LEFT JOIN UNNEST(array_expression) AS alias`**:
        Similar to `CROSS JOIN UNNEST`, but retains the original row even if the repeated field is empty. In this case, the expanded field values will be `NULL`. `LEFT JOIN` is generally recommended when you want to avoid losing data.
    """)

    st.subheader("Example: Expanding `hits` Records")
    st.write(
        "The following SQL query shows how to fetch session information and expand each hit within the session from the `ga_sessions_20170801` table."
    )
    st.code("""
    SELECT
        t1.fullVisitorId,
        t1.visitStartTime,
        hits.hitNumber,
        hits.type,
        hits.page.pagePath,
        hits.page.pageTitle
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_20170801` AS t1,
        UNNEST(t1.hits) AS hits -- expand the 'hits' array here
    LIMIT 100
    """)
    st.write("**Explanation:**")
    st.markdown("""
    * `FROM ... AS t1, UNNEST(t1.hits) AS hits`:
        * Aliases the original table `ga_sessions_20170801` as `t1`.
        * Uses `UNNEST(t1.hits) AS hits` to expand the `hits` array for each row of `t1`, treating the result as a new table with the alias `hits`.
        * This duplicates each session row for each hit in the session, assigning different hit information to each row.
    * `hits.hitNumber`, `hits.type`, `hits.page.pagePath`, `hits.page.pageTitle`:
        Allows direct access to fields within the expanded `hits` record.
    """)

    st.subheader("Example: Expanding `customDimensions` Records")
    st.write(
        "Similarly, to expand custom dimensions, use `UNNEST` on the `customDimensions` field."
    )
    st.code("""
    SELECT
        t1.fullVisitorId,
        t1.visitStartTime,
        cd.index AS customDimensionIndex,
        cd.value AS customDimensionValue
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_20170801` AS t1,
        UNNEST(t1.customDimensions) AS cd
    WHERE
        cd.index = 1 -- filter for a specific custom dimension
    LIMIT 100
    """)
    st.write("**Explanation:**")
    st.markdown("""
    * `UNNEST(t1.customDimensions) AS cd`: Expands the `customDimensions` array and treats each index/value pair as the alias `cd`.
    * `cd.index` and `cd.value`: Access the `index` and `value` fields from the expanded `cd` record.
    """)

    st.write(
        "`UNNEST` is a powerful tool for handling complex nested repeated data in BigQuery. Use this knowledge to tackle deeper analyses!"
    )
