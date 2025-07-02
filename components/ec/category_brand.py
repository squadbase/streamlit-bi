import plotly.express as px
import streamlit as st

from .data_queries import q_category_brand_sales
from .utils import get_date_inputs, get_date_range


def category_brand_analysis():
    start, end = get_date_inputs()
    start, end, *_ = get_date_range(start, end)
    st.title("🏷️ Product Category and Brand Analysis")

    df_cat_brand = q_category_brand_sales(start, end)

    if df_cat_brand.empty:
        st.warning("No category or brand data available for the selected date range.")
        return

    col_category_sales, col_brand_sales = st.columns(2)

    with col_category_sales:
        category_sales = (
            df_cat_brand.groupby("product_category")["total_sales"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        fig_category_sales = px.bar(
            category_sales,
            x="total_sales",
            y="product_category",
            orientation="h",
            title="Top 10 Categories by Sales",
            labels={
                "total_sales": "Total Sales ($)",
                "product_category": "Product Category",
            },
            template="plotly_white",
        )
        fig_category_sales.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_category_sales, use_container_width=True)

    with col_brand_sales:
        brand_sales = (
            df_cat_brand.groupby("product_brand")["total_sales"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        fig_brand_sales = px.bar(
            brand_sales,
            x="total_sales",
            y="product_brand",
            orientation="h",
            title="Top 10 Brands by Sales",
            labels={"total_sales": "Total Sales ($)", "product_brand": "Product Brand"},
            template="plotly_white",
        )
        fig_brand_sales.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_brand_sales, use_container_width=True)
