from __future__ import annotations

import pandas as pd
import streamlit as st


def render_kpi_deck(filtered: pd.DataFrame, full: pd.DataFrame) -> None:
    """Display executive KPIs with deltas compared to the full run."""
    st.markdown("### KPI deck & filter coverage")
    filtered_revenue = float(filtered["sls_sales"].sum())
    full_revenue = float(full["sls_sales"].sum())
    filtered_orders = filtered["sls_ord_num"].nunique()
    full_orders = full["sls_ord_num"].nunique()
    filtered_customers = filtered["sls_cust_id"].nunique()
    full_customers = full["sls_cust_id"].nunique()
    avg_order_value = filtered_revenue / filtered_orders if filtered_orders else 0.0
    baseline_avg = full_revenue / full_orders if full_orders else 0.0

    cols = st.columns(4)
    cols[0].metric(
        "Revenue (filtered)",
        f"€{filtered_revenue:,.0f}",
        delta=f"€{filtered_revenue - full_revenue:,.0f}",
    )
    cols[1].metric(
        "Average Order Value",
        f"€{avg_order_value:,.2f}",
        delta=f"€{avg_order_value - baseline_avg:,.2f}",
    )
    cols[2].metric(
        "Transactions in view",
        f"{filtered_orders:,}",
        delta=f"{filtered_orders - full_orders:,}",
    )
    cols[3].metric(
        "Customers in view",
        f"{filtered_customers:,}",
        delta=f"{filtered_customers - full_customers:,}",
    )


def summarize_changes(filtered: pd.DataFrame, baseline: pd.DataFrame) -> list[str]:
    """Create a short bullet trail describing what changed in this view."""
    bullets: list[str] = []
    filtered_revenue = filtered["sls_sales"].sum()
    baseline_revenue = baseline["sls_sales"].sum()
    if baseline_revenue:
        delta = filtered_revenue - baseline_revenue
        pct = (delta / baseline_revenue) * 100
        bullets.append(f"Revenue view is {delta:+,.0f}€ ({pct:+.1f}%) vs. the full run.")
    if not filtered.empty and not baseline.empty:
        top_line_filtered = (
            filtered.groupby("product_line", as_index=False)["sls_sales"]
            .sum()
            .sort_values("sls_sales", ascending=False)
        )
        top_line_baseline = (
            baseline.groupby("product_line", as_index=False)["sls_sales"]
            .sum()
            .sort_values("sls_sales", ascending=False)
        )
        if not top_line_filtered.empty:
            line = top_line_filtered.iloc[0]["product_line"]
            filtered_share = (
                top_line_filtered.iloc[0]["sls_sales"] / filtered_revenue * 100
                if filtered_revenue
                else 0.0
            )
            baseline_share = (
                top_line_baseline.iloc[0]["sls_sales"] / baseline_revenue * 100
                if baseline_revenue
                else 0.0
            )
            bullets.append(
                f"Top line '{line}' contributes {filtered_share:.1f}% of filtered revenue vs {baseline_share:.1f}% baseline."
            )
    return bullets
