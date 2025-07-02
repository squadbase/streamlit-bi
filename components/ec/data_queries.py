from datetime import date
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st

from lib.bigquery_client import bigquery_client

from .utils import iso_format


@st.cache_data(show_spinner="Querying daily revenue & orders …")
def q_daily_sales(start: date, end: date) -> pd.DataFrame:
    q = f"""
        WITH daily AS (
            SELECT DATE(o.created_at) AS day,
                   COUNT(DISTINCT o.order_id)      AS orders,
                   SUM(oi.sale_price)             AS revenue
            FROM `bigquery-public-data.thelook_ecommerce.order_items`  oi
            JOIN `bigquery-public-data.thelook_ecommerce.orders`      o
              ON oi.order_id = o.order_id
            WHERE o.created_at BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
            GROUP BY day
        )
        SELECT * FROM daily ORDER BY day;
    """
    return bigquery_client.query(q).to_dataframe()


@st.cache_data(show_spinner="Querying customer stats …")
def q_customer_stats(start: date, end: date) -> Tuple[int, int]:
    q = f"""
        WITH first_orders AS (
            SELECT user_id, MIN(created_at) AS first_order_date
            FROM `bigquery-public-data.thelook_ecommerce.orders`
            GROUP BY user_id
        ),
        new_customers_cte AS (
            SELECT COUNT(*) AS cnt FROM first_orders
            WHERE first_order_date BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
        ),
        tot AS (
            SELECT COUNT(DISTINCT user_id) AS cnt
            FROM `bigquery-public-data.thelook_ecommerce.orders`
            WHERE created_at BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
        )
        SELECT (SELECT cnt FROM new_customers_cte) AS new_customers,
               (SELECT cnt FROM tot) AS total_customers;
    """
    r = bigquery_client.query(q).to_dataframe().iloc[0]
    return int(r.new_customers), int(r.total_customers)


@st.cache_data(show_spinner="Fetching distribution centers …")
def q_distribution_centers() -> pd.DataFrame:
    q = """
        SELECT id, name, latitude  AS dc_lat, longitude AS dc_lon
        FROM `bigquery-public-data.thelook_ecommerce.distribution_centers`;
    """
    return bigquery_client.query(q).to_dataframe()


@st.cache_data(show_spinner="Querying order geo data …")
def q_order_geo(start: date, end: date) -> pd.DataFrame:
    """Return orders with customer lat/lon & shipping lead‑time."""
    q = f"""
        SELECT
            o.order_id,
            TIMESTAMP(o.created_at)                      AS order_date,
            TIMESTAMP_DIFF(o.delivered_at, o.shipped_at, DAY) AS lead_time_days,
            u.latitude  AS cust_lat,
            u.longitude AS cust_lon
        FROM `bigquery-public-data.thelook_ecommerce.orders` o
        JOIN `bigquery-public-data.thelook_ecommerce.users`  u
          ON o.user_id = u.id
        WHERE o.created_at BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
          AND o.shipped_at IS NOT NULL AND o.delivered_at IS NOT NULL
          AND u.latitude IS NOT NULL AND u.longitude IS NOT NULL;
    """
    result = bigquery_client.query(q).to_dataframe()
    result["lead_time_days"] = (
        pd.to_numeric(result["lead_time_days"], errors="coerce")
        .fillna(0)
        .astype(np.int64)
    )
    result["cust_lat"] = (
        pd.to_numeric(result["cust_lat"], errors="coerce").fillna(0).astype(np.float64)
    )
    result["cust_lon"] = (
        pd.to_numeric(result["cust_lon"], errors="coerce").fillna(0).astype(np.float64)
    )
    return result


@st.cache_data(show_spinner="Querying product sales …")
def q_product_sales(start: date, end: date) -> pd.DataFrame:
    q = f"""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            SUM(oi.sale_price) AS revenue,
            AVG(oi.sale_price) AS avg_price,
            SUM(oi.sale_price - ii.cost) AS profit
        FROM `bigquery-public-data.thelook_ecommerce.products` p
        JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON p.id = oi.product_id
        JOIN `bigquery-public-data.thelook_ecommerce.inventory_items` ii ON oi.inventory_item_id = ii.id
        WHERE DATE(oi.created_at) BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
          AND oi.status IN ('Complete', 'Shipped', 'Returned')
        GROUP BY p.id, p.name
        ORDER BY revenue DESC;
    """
    df = bigquery_client.query(q).to_dataframe()
    return df


@st.cache_data(show_spinner="Querying RFM …")
def q_rfm(start: date, end: date) -> pd.DataFrame:
    q = f"""
        WITH order_data AS (
            SELECT
                user_id,
                order_id,
                created_at,
                sale_price
            FROM `bigquery-public-data.thelook_ecommerce.order_items`
            WHERE DATE(created_at) BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
              AND status IN ('Complete', 'Shipped', 'Returned')
        ),
        user_rfm AS (
            SELECT
                user_id,
                DATE_DIFF(PARSE_DATE('%Y-%m-%d', '{iso_format(end)}'), MAX(DATE(created_at)), DAY) AS recency,
                COUNT(DISTINCT order_id) AS frequency,
                SUM(sale_price) AS monetary
            FROM order_data
            GROUP BY user_id
        )
        SELECT * FROM user_rfm;
    """
    df = bigquery_client.query(q).to_dataframe()
    return df


@st.cache_data(show_spinner="Querying inventory & demand …")
def q_inventory_demand(start: date, end: date) -> pd.DataFrame:
    q = f"""
        SELECT
            ii.product_category,
            AVG(ii.cost) AS avg_cost,
            SUM(CASE WHEN oi.status = 'Shipped' THEN 1 ELSE 0 END) AS units_sold,
            0 AS days_of_stock
        FROM `bigquery-public-data.thelook_ecommerce.inventory_items` ii
        LEFT JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
          ON ii.id = oi.inventory_item_id
         AND DATE(oi.created_at) BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
        GROUP BY ii.product_category;
    """
    df = bigquery_client.query(q).to_dataframe()
    return df


@st.cache_data(show_spinner="Querying bottlenecks …")
def q_bottlenecks(start: date, end: date) -> pd.DataFrame:
    q = f"""
        SELECT
            DATE(o.created_at) AS day,
            AVG(TIMESTAMP_DIFF(o.shipped_at, o.created_at, HOUR)) AS proc_days,
            AVG(TIMESTAMP_DIFF(o.delivered_at, o.shipped_at, HOUR)) AS ship_days
        FROM `bigquery-public-data.thelook_ecommerce.orders` o
        WHERE o.shipped_at IS NOT NULL AND o.delivered_at IS NOT NULL
          AND DATE(o.created_at) BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
        GROUP BY day
        ORDER BY day;
    """
    df = bigquery_client.query(q).to_dataframe()
    return df


@st.cache_data(show_spinner="Querying daily sales trend …")
def q_daily_sales_trend(start: date, end: date) -> pd.DataFrame:
    q = f"""
        SELECT
            DATE(oi.created_at) AS day,
            SUM(oi.sale_price) AS total_sales,
            SUM(oi.sale_price - ii.cost) AS total_profit
        FROM
            `bigquery-public-data.thelook_ecommerce.order_items` AS oi
        JOIN
            `bigquery-public-data.thelook_ecommerce.inventory_items` AS ii
        ON
            oi.inventory_item_id = ii.id
        WHERE
            DATE(oi.created_at) BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
        GROUP BY
            day
        ORDER BY
            day
    """
    df = bigquery_client.query(q).to_dataframe()
    if not df.empty:
        df["day"] = pd.to_datetime(df["day"])
    return df


@st.cache_data(show_spinner="Querying customer demographics...")
def q_customer_demographics(start: date, end: date) -> pd.DataFrame:
    query = f"""
    SELECT
        u.gender AS user_gender,
        u.age AS age,
        o.status AS order_status,
        COUNT(DISTINCT o.order_id) AS order_count,
        COUNT(DISTINCT u.id) AS unique_customers
    FROM
        `bigquery-public-data.thelook_ecommerce.orders` AS o
    JOIN
        `bigquery-public-data.thelook_ecommerce.users` AS u ON o.user_id = u.id
    WHERE
        DATE(o.created_at) BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
    GROUP BY
        u.gender, u.age, o.status
    """
    df = bigquery_client.query(query).to_dataframe()
    return df


@st.cache_data(show_spinner="Querying category and brand sales...")
def q_category_brand_sales(start: date, end: date) -> pd.DataFrame:
    query = f"""
    SELECT
        ii.product_category,
        ii.product_brand,
        SUM(oi.sale_price) AS total_sales
    FROM
        `bigquery-public-data.thelook_ecommerce.order_items` AS oi
    JOIN
        `bigquery-public-data.thelook_ecommerce.inventory_items` AS ii ON oi.inventory_item_id = ii.id
    WHERE
        DATE(oi.created_at) BETWEEN '{iso_format(start)}' AND '{iso_format(end)}'
        AND oi.status IN ('Complete', 'Shipped', 'Returned')
    GROUP BY
        ii.product_category, ii.product_brand
    """
    df = bigquery_client.query(query).to_dataframe()
    return df
