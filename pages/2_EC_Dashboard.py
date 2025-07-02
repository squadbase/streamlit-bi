import streamlit as st

from components.ec.category_brand import category_brand_analysis
from components.ec.data_agent_chat import data_agent_chat
from components.ec.demographics import customer_demographics
from components.ec.executive_overview import executive_overview
from components.ec.geo_logistics import geo_logistics
from components.ec.inventory_supply import inventory_supply_chain
from components.ec.product_merchandising import product_merchandising
from components.ec.sales_trends import daily_sales_trend

PAGES = {
    "Executive Overview": executive_overview,
    "Geo & Logistics": geo_logistics,
    "Product & Merchandising": product_merchandising,
    "Inventory & Supply Chain": inventory_supply_chain,
    "Trends": daily_sales_trend,
    "Demographics": customer_demographics,
    "Category & Brand": category_brand_analysis,
    "AI Data Agent": data_agent_chat,
}

st.sidebar.title("🗺️ Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
st.sidebar.markdown("---")

# Render selected page
PAGES[selection]()
