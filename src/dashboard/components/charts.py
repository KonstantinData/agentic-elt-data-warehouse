from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_trend_chart(filtered: pd.DataFrame) -> None:
    st.subheader("Revenue trajectory (daily)")
    time_series = (
        filtered.dropna(subset=["order_dt", "sls_sales"])
        .assign(order_date=lambda df: df["order_dt"].dt.date)
        .groupby("order_date", as_index=False)["sls_sales"]
        .sum()
    )
    if time_series.empty:
        st.info("No revenue data available for the selected window.")
        return

    fig = px.line(
        time_series,
        x="order_date",
        y="sls_sales",
        markers=True,
        title="Daily revenue",
        labels={"order_date": "Order date", "sls_sales": "Revenue (€)"},
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(hovermode="x unified", yaxis_title="Revenue (€)")
    st.plotly_chart(fig, use_container_width=True)


def render_product_mix_geo(filtered: pd.DataFrame) -> None:
    st.subheader("Product-line mix & geopolitical heatmap")
    col1, col2 = st.columns(2)
    with col1:
        product_summary = (
            filtered[["product_line", "sls_sales"]]
            .dropna()
            .groupby("product_line", as_index=False)["sls_sales"]
            .sum()
        )
        if product_summary.empty:
            st.info("No product lines match the current selection.")
        else:
            total_sales = product_summary["sls_sales"].sum()
            top_lines = (
                product_summary.sort_values("sls_sales", ascending=False).head(5).copy()
            )
            others_sales = total_sales - top_lines["sls_sales"].sum()
            waterfall_names = top_lines["product_line"].tolist()
            waterfall_values = top_lines["sls_sales"].tolist()
            if others_sales > 0:
                waterfall_names.append("Other")
                waterfall_values.append(others_sales)
            waterfall_names.append("Total")
            waterfall_values.append(total_sales)

            measures = ["relative"] * (len(waterfall_values) - 1) + ["total"]
            fig_waterfall = go.Figure(
                go.Waterfall(
                    name="Revenue bridge",
                    orientation="v",
                    measure=measures,
                    x=waterfall_names,
                    y=waterfall_values,
                    text=[f"€{int(v):,}" for v in waterfall_values],
                    textposition="outside",
                    connector={"line": {"color": "#444"}},
                    increasing={"marker": {"color": "#00CC96"}},
                    decreasing={"marker": {"color": "#EF553B"}},
                    totals={"marker": {"color": "#636EFA"}},
                )
            )
            fig_waterfall.update_layout(
                title="Product-line revenue bridge",
                yaxis_title="Revenue (€)",
                xaxis_title="Product line",
                uniformtext_mode="hide",
                margin=dict(l=0, r=0, t=40, b=40),
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)

    with col2:
        heatmap_source = (
            filtered.dropna(subset=["order_day", "country", "sls_sales"])
            .groupby(["order_day", "country"], as_index=False)["sls_sales"]
            .sum()
        )
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_source["order_day"] = pd.Categorical(
            heatmap_source["order_day"], categories=weekdays, ordered=True
        )
        pivot = heatmap_source.pivot(index="order_day", columns="country", values="sls_sales").fillna(0)
        if pivot.empty:
            st.info("Heatmap requires data with country, weekday, and revenue.")
        else:
            fig_heat = px.imshow(
                pivot,
                labels={"x": "Country", "y": "Weekday", "color": "Revenue (€)"},
                title="Revenue heatmap by weekday & country",
                aspect="auto",
                text_auto=".2s",
                color_continuous_scale="Teal",
            )
            st.plotly_chart(fig_heat, use_container_width=True)


def render_order_signals(filtered: pd.DataFrame) -> None:
    st.subheader("Order Signals")
    agg = (
        filtered.dropna(subset=["sls_price", "sls_quantity"])
        .assign(
            price_bucket=lambda df: pd.cut(
                df["sls_price"],
                bins=10,
                include_lowest=True,
                labels=False,
            )
        )
    )
    if agg.empty:
        st.info("No price/quantity information available with the active filters.")
        return

    bucket_summary = (
        agg.groupby("price_bucket", as_index=False).agg(
            price_mean=("sls_price", "mean"),
            quantity_median=("sls_quantity", "median"),
            transactions=("sls_ord_num", "nunique"),
        )
    )
    bucket_summary["price_bucket_label"] = bucket_summary["price_mean"].round(0).map(
        lambda v: f"€{int(v):,}"
    )
    fig_bucket = px.bar(
        bucket_summary,
        x="price_bucket_label",
        y="quantity_median",
        color="transactions",
        color_continuous_scale="Viridis",
        labels={"quantity_median": "Median quantity", "price_bucket_label": "Price bucket"},
        title="Median quantity per price bucket & transaction count",
        text="quantity_median",
    )
    fig_bucket.update_layout(xaxis_title="Price bucket", yaxis_title="Median quantity")
    st.plotly_chart(fig_bucket, use_container_width=True)


def render_row_sample(filtered: pd.DataFrame) -> None:
    st.subheader("Filtered sample")
    if filtered.empty:
        st.warning("No rows after the current filter—adjust the sidebar controls.")
        return

    st.dataframe(
        filtered.sort_values("order_dt", ascending=False)[
            [
                "sls_ord_num",
                "order_dt",
                "product_line",
                "country",
                "sls_sales",
                "sls_quantity",
                "sls_price",
            ]
        ].head(10),
        use_container_width=True,
    )
