import pydeck as pdk
import streamlit as st

from .data_queries import q_distribution_centers, q_order_geo
from .utils import get_date_inputs, get_date_range


def geo_logistics():
    start, end = get_date_inputs()
    start, end, *_ = get_date_range(start, end)

    st.title("🌎 Geo & Logistics")
    st.caption("Customer distribution, DC overlay, shipping lead‑time analytics")

    dc_df = q_distribution_centers()
    geo_df = q_order_geo(start, end)

    if geo_df.empty:
        st.info("No geo‑tagged orders in selected period.")
        return

    # KPI – logistics
    avg_lead = geo_df.lead_time_days.mean()
    late_pct = (geo_df.lead_time_days > 7).mean() * 100
    served_states = geo_df.shape[0]

    k1, k2, k3 = st.columns(3)
    k1.metric("Avg Lead Time", f"{avg_lead:.1f} days")
    k2.metric("Late (>7 d)", f"{late_pct:.1f}%")
    k3.metric("Shipped Orders", f"{served_states:,}")

    # Map – heatmap of orders + DC dots
    st.subheader("Customer Heatmap & Distribution Centers")
    view = pdk.ViewState(
        latitude=geo_df.cust_lat.mean(),
        longitude=geo_df.cust_lon.mean(),
        zoom=3,
        pitch=0,
    )

    orders_layer = pdk.Layer(
        "HeatmapLayer",
        data=geo_df,
        get_position="[cust_lon, cust_lat]",
        radius_pixels=60,
        opacity=0.9,
    )
    dc_layer = pdk.Layer(
        "ScatterplotLayer",
        data=dc_df,
        get_position="[dc_lon, dc_lat]",
        get_radius=50000,
        get_fill_color=[255, 0, 0, 140],
        pickable=True,
    )

    deck = pdk.Deck(
        layers=[orders_layer, dc_layer],
        initial_view_state=view,
        map_provider="mapbox",
        map_style=pdk.map_styles.MAPBOX_LIGHT,
        tooltip={"text": "Lon: {cust_lon}\nLat: {cust_lat}"},
    )

    st.pydeck_chart(deck)

    # Lead‑time histogram
    st.subheader("Shipping Lead‑Time Distribution (days)")
    hist_vals = geo_df.lead_time_days.clip(lower=0, upper=30)
    st.bar_chart(hist_vals.value_counts().sort_index())
