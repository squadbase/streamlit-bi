import streamlit as st

from components.ga4.basic_metrics import basic_metrics
from components.ga4.channels import channel_metrics_comparison_chart
from components.ga4.countries import country_analysis_fragment
from components.ga4.data_catalog import data_catalog
from components.ga4.device_and_browser import browser_chart, device_chart
from components.ga4.eda_pygwalker import eda_pygwalker
from components.ga4.landing_page_performance import landing_page_performance_chart
from components.ga4.new_vs_returning import (
    metrics_comparison_chart,
    new_vs_returning_chart,
)
from components.ga4.session_and_pv_by_date import session_and_pv_by_date_chart
from components.ga4.session_anomaly import session_anomaly_chart
from components.ga4.traffic_pattern import traffic_pattern_chart
from components.ga4.unique_visitors_by_date import unique_vistors_by_date_chart
from components.ga4.user_path import user_path_chart

# st.set_page_config(page_title="Google Analytics Dashboard", layout="wide")


# Data Catalog Page
def page_data_catalog():
    st.title("Google Analytics Sample Dataset Catalog")
    data_catalog()


# Basic Analysis Page
def page_basic_analysis():
    st.title("Basic Analysis")
    basic_metrics()
    st.write("---")
    cols1 = st.columns(2)
    with cols1[0]:
        st.subheader("Unique Visitors by Date")
        unique_vistors_by_date_chart()
    with cols1[1]:
        st.subheader("Session and Pageviews by Date")
        session_and_pv_by_date_chart()
    st.write("---")
    cols2 = st.columns(2)
    with cols2[0]:
        st.subheader("Device Distribution")
        device_chart()
    with cols2[1]:
        st.subheader("Browser Distribution")
        browser_chart()
    st.write("---")
    st.subheader("Daily sessions with 7-day avg")
    session_anomaly_chart()


# User Behavior Analysis Page
def page_user_behavior():
    st.title("User Behavior Analysis")
    cols1 = st.columns(2)
    with cols1[0]:
        st.subheader("New vs Returning Users")
        new_vs_returning_chart()
    with cols1[1]:
        st.subheader("Metrics Comparison: New vs Returning Users")
        metrics_comparison_chart()
    st.write("---")
    st.subheader("Channel Metrics Comparison")
    st.markdown(
        "This chart compares average metrics across different channels, including pageviews, session duration, and bounce rate."
    )
    channel_metrics_comparison_chart()
    st.write("---")
    st.subheader("Top Landing Pages: Sessions and Bounce Rate")
    landing_page_performance_chart()
    st.write("---")
    st.subheader("User Path Transitions")
    user_path_chart()
    st.write("---")
    st.subheader("Traffic Pattern by Weekday and Hour")
    traffic_pattern_chart()


# Country Analysis Page
def page_country_analysis():
    st.title("Country Analysis")
    st.markdown(
        "This section provides insights into user behavior by country, including total sessions, average pageviews, session duration, and bounce rate."
    )
    country_analysis_fragment()


# EDA PyGWalker
def page_eda_pygwalker():
    st.title("EDA with PyGWalker")
    st.markdown(
        "This section allows you to explore the dataset interactively using PyGWalker."
    )
    eda_pygwalker()


# Pages setup
PAGES = {
    "Basic Analysis": page_basic_analysis,
    "User Behavior Analysis": page_user_behavior,
    "Country Analysis": page_country_analysis,
    "EDA with PyGWalker": page_eda_pygwalker,
    "Data Catalog": page_data_catalog,
}

selection = st.sidebar.radio("Pages", list(PAGES.keys()))
st.sidebar.markdown("---")

# Render selected page
PAGES[selection]()
