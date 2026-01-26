from __future__ import annotations

import streamlit as st

from src.dashboard.context import get_dashboard_state, get_filtered_dataset


def _render_top_n(filtered, column, top=5):
    summary = (
        filtered.groupby(column, as_index=False)["sls_sales"]
        .sum()
        .sort_values("sls_sales", ascending=False)
        .head(top)
    )
    st.table(summary.assign(sls_sales=lambda df: df["sls_sales"].map(lambda v: f"€{v:,.0f}")))


def main() -> None:
    state = get_dashboard_state()
    filtered = get_filtered_dataset()
    if not state or not state.selected_run:
        st.warning("No Silver runs detected yet.")
        return
    if filtered is None:
        st.warning("Filtering is still initializing. Choose a date window")
        return

    st.header("Exploration sandbox")
    st.markdown("Interactive data preview & top performers for the active filters.")

    st.subheader("Filtered data snapshot")
    st.dataframe(filtered.sort_values("order_dt", ascending=False).head(100), use_container_width=True)

    st.subheader("Top performers")
    cols = st.columns(3)
    with cols[0]:
        st.caption("Top products")
        _render_top_n(filtered, "product_name")
    with cols[1]:
        st.caption("Top countries")
        _render_top_n(filtered, "country")
    with cols[2]:
        st.caption("Top customers")
        _render_top_n(filtered, "sls_cust_id")
