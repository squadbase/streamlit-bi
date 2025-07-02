import plotly.express as px
import streamlit as st

from lib.bigquery_client import bigquery_client
from lib.tailwind_colors import COLORS


@st.cache_data(ttl=86400)
def device_browser_distribution():
    # SQL to get session counts by device and browser
    query = """
    SELECT
      device.deviceCategory AS device_category,
      device.browser AS browser,
      COUNT(DISTINCT visitId) AS sessions
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE _TABLE_SUFFIX BETWEEN '20170701' AND '20170731'
    GROUP BY device_category, browser
    ORDER BY sessions DESC
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.fragment
def device_chart():
    # Load device/browser data
    device_browser_df = device_browser_distribution()

    # Aggregate sessions by device category only
    device_counts = (
        device_browser_df.groupby("device_category", as_index=False)["sessions"]
        .sum()
        .sort_values("sessions")  # Smallest→Largest
    )

    # Horizontal bar chart for device comparison
    device_bar_fig = px.bar(
        device_counts,
        x="sessions",
        y="device_category",
        orientation="h",
        title="Sessions by Device Category (July 2017)",
        labels={"device_category": "Device", "sessions": "Sessions"},
        color_discrete_sequence=[COLORS["blue"]["500"]],  # Indigo
    )

    st.plotly_chart(device_bar_fig, use_container_width=True)


@st.fragment
def browser_chart():
    device_browser_df = device_browser_distribution()
    devices = ["desktop", "mobile", "tablet"]
    tabs = st.tabs([d.capitalize() for d in devices])
    for tab, device in zip(tabs, devices):
        with tab:
            df_dev = device_browser_df[
                device_browser_df["device_category"] == device
            ].copy()
            # Calculate share percentages
            total_sessions = df_dev["sessions"].sum()
            df_dev["pct"] = df_dev["sessions"] / total_sessions * 100
            # Aggregate browsers with less than 1% into "Other"
            df_dev["browser"] = df_dev.apply(
                lambda row: "Other" if row["pct"] < 1 else row["browser"], axis=1
            )
            df_grouped = (
                df_dev.groupby("browser", as_index=False)["sessions"]
                .sum()
                .sort_values(
                    "sessions", ascending=False
                )  # sort descending for ordering
            )
            # Create donut chart with sorted order
            donut_fig = px.pie(
                df_grouped,
                names="browser",
                values="sessions",
                title=f"{device.capitalize()} Browser Share (July 2017)",
                hole=0.4,
                labels={"browser": "Browser", "sessions": "Sessions"},
                category_orders={
                    "browser": df_grouped["browser"].tolist()
                },  # enforce order
                color_discrete_sequence=[
                    COLORS["blue"]["400"],
                    COLORS["cyan"]["400"],
                    COLORS["emerald"]["400"],
                    COLORS["indigo"]["400"],
                    COLORS["sky"]["400"],
                ],
                # color_discrete_sequence=px.colors.sequential.Plotly3  # Use Plotly's qualitative color palette
            )
            st.plotly_chart(donut_fig, use_container_width=True)
