import streamlit as st

from .data_queries import q_bottlenecks, q_inventory_demand
from .utils import get_date_inputs, get_date_range


def inventory_supply_chain():
    start, end = get_date_inputs()
    start, end, _, _, _ = get_date_range(start, end)
    st.title("🚚 Inventory & Supply Chain")

    df = q_inventory_demand(start, end)
    st.subheader("Days of Stock by Category")
    safe = 7
    df["Alert"] = df["days_of_stock"] <= safe
    st.dataframe(
        df.style.applymap(
            lambda v: "background-color: red" if v is True else "", subset=["Alert"]
        )
    )

    st.subheader("Bottleneck Trends")
    bot = q_bottlenecks(start, end)
    bot = bot.set_index("day")
    st.line_chart(bot[["proc_days", "ship_days"]])
