import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from .data_queries import q_product_sales, q_rfm
from .utils import get_date_inputs, get_date_range


def product_merchandising():
    start, end = get_date_inputs()
    start, end, _, _, _ = get_date_range(start, end)
    st.title("🛍️ Product & Merchandising")

    df = q_product_sales(start, end)
    total_rev = df["revenue"].sum()
    df = df.sort_values("revenue", ascending=False)
    df["cum_rev"] = df["revenue"].cumsum()
    df["cum_pct"] = df["cum_rev"] / total_rev
    top20 = df.head(int(len(df) * 0.2))["revenue"].sum() / total_rev * 100
    st.metric("Top 20% Products Revenue", f"{top20:.1f}% of total")

    # Pareto chart
    st.subheader("Pareto Chart")
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    ax.bar(df["product_id"], df["revenue"])
    ax2.plot(df["product_id"], df["cum_pct"], color="green")
    st.pyplot(fig)

    # RFM segmentation
    rfm = q_rfm(start, end)
    q1 = rfm.quantile(0.33)
    q2 = rfm.quantile(0.66)

    def r_score(x):
        return 3 if x <= q1.recency else 2 if x <= q2.recency else 1

    def fm_score(x, col):
        return 1 if x <= q1[col] else 2 if x <= q2[col] else 3

    rfm["R"] = rfm["recency"].apply(r_score)
    rfm["F"] = rfm["frequency"].apply(lambda x: fm_score(x, "frequency"))
    rfm["M"] = rfm["monetary"].apply(lambda x: fm_score(x, "monetary"))
    rfm["Segment"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    seg_counts = rfm["Segment"].value_counts().sort_index()
    st.subheader("RFM Segment Counts")
    st.bar_chart(seg_counts)

    # Price vs Profit
    st.subheader("Price vs Profit")
    fig, ax = plt.subplots()
    ax.scatter(df["avg_price"], df["profit"])
    m, b = np.polyfit(df["avg_price"], df["profit"], 1)
    ax.plot(df["avg_price"], m * df["avg_price"] + b)
    ax.set_xlabel("Avg Price")
    ax.set_ylabel("Profit")
    st.pyplot(fig)
