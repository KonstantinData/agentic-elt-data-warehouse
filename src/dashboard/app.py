from __future__ import annotations

from typing import Iterable

import streamlit as st

from src.dashboard.components.filters import apply_filters, configure_filters
from src.dashboard.components.kpis import render_kpi_deck, summarize_changes
from src.dashboard.components.charts import (
    render_trend_chart,
    render_product_mix_geo,
    render_order_signals,
    render_row_sample,
)
from src.dashboard.components.diagnostics import render_diagnostics_panel
from src.dashboard.context import (
    get_dashboard_state,
    hydrate_dashboard_state,
    persist_filters,
    persist_filtered_dataset,
)
from src.dashboard.services.artifacts import explain_missing_artifacts, list_available_runs


def _select_run_id(run_ids: list[str]) -> str:
    saved = st.session_state.get("dashboard_selected_run")
    candidate = saved if saved in run_ids else run_ids[0]
    index = run_ids.index(candidate)
    return st.sidebar.selectbox(
        "Select Silver run",
        run_ids,
        index=index,
        key="dashboard_selected_run",
        help="Latest run is chosen by default; selection is session-persistent.",
    )


def _prepare_state() -> None:
    runs = list_available_runs()
    if runs:
        run_id = _select_run_id([run.run_id for run in runs])
        hydrate_dashboard_state(run_id, available_runs=runs)
    else:
        hydrate_dashboard_state(selected_run_id=None, available_runs=[])


def _setup_sidebar(state) -> dict | None:
    filters = None
    if state.enriched is not None and state.product_lookup is not None:
        filters = configure_filters(state.enriched, state.missing_info, state.product_lookup)
        persist_filters(filters)
        filtered = apply_filters(state.enriched, filters)
        persist_filtered_dataset(filtered)
    else:
        st.sidebar.warning("Waiting for Silver artifacts to populate filters.")
    return filters


def _register_pages() -> st.StreamlitPage:
    pages = [
        st.Page("pages/01_executive_overview.py", title="Executive Overview", icon=":bar_chart:", default=True),
        st.Page("pages/02_explore.py", title="Exploration", icon=":mag:", default=False),
        st.Page("pages/03_run_diagnostics.py", title="Diagnostics / Run Health", icon=":clipboard:", default=False),
        st.Page("pages/04_export.py", title="Export", icon=":package:", default=False),
    ]
    return st.navigation(pages, position="top", expanded=True)


def main() -> None:
    st.set_page_config(
        page_title="2026 Enterprise Business Dashboard",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("2026 Enterprise Business Dashboard")
    st.markdown(
        "Evidence-first insights, canonical artifact discovery, and audit-ready exports for the Agentic ELT stack."
    )

    _prepare_state()
    state = get_dashboard_state()
    if not state:
        st.error("Unable to build dashboard state.")
        return

    if not state.selected_run:
        st.error("No Silver runs found.")
        st.markdown(explain_missing_artifacts())
    elif state.tables is None:
        st.warning("Silver tables could not be loaded for the selected run.")
        st.markdown(state.guidance)

    _setup_sidebar(state)
    page = _register_pages()
    page.run()


if __name__ == "__main__":
    main()
