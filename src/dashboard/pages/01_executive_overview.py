from __future__ import annotations

from typing import Iterable

import streamlit as st

from src.dashboard.components.charts import (
    render_order_signals,
    render_product_mix_geo,
    render_row_sample,
    render_trend_chart,
)
from src.dashboard.components.diagnostics import render_diagnostics_panel
from src.dashboard.components.kpis import render_kpi_deck, summarize_changes
from src.dashboard.context import (
    get_dashboard_state,
    get_filtered_dataset,
    get_persisted_filters,
)


def _render_filter_summary(filters: dict[str, Iterable]) -> None:
    if not filters:
        return
    with st.expander("Filter overview", expanded=False):
        st.write(f"- Dates: {filters['date_range'][0]} to {filters['date_range'][1]}")
        st.write(f"- Product lines: {', '.join(filters['product_lines'])}")
        st.write(f"- Product keys: {len(filters['product_keys'])} selected")
        st.write(f"- Countries: {', '.join(filters['countries'])}")
        st.write(f"- Genders: {', '.join(filters['genders'])}")
        st.write(f"- Marital statuses: {', '.join(filters['marital_status'])}")


def main() -> None:
    state = get_dashboard_state()
    if not state or not state.selected_run:
        st.warning("No Silver runs detected. Please run the ELT pipeline first.")
        return
    if state.enriched is None:
        st.warning("Silver-Daten können nicht geladen werden.")
        st.caption(state.guidance)
        return

    filtered = get_filtered_dataset()
    filters = get_persisted_filters()

    st.metric("Active run", state.selected_run.run_id)
    st.caption(f"Artifacts served from {state.selected_run.artifact_label}")

    if filtered is None:
        st.warning("Filterwerte werden initialisiert. Bitte wählen Sie einen Bereich im Sidebar.")
        return

    render_kpi_deck(filtered, state.enriched)
    st.markdown("### What changed in this view")
    change_notes = summarize_changes(filtered, state.enriched)
    if change_notes:
        for note in change_notes:
            st.write(f"- {note}")
    else:
        st.write("No significant delta compared to the baseline run.")

    _render_filter_summary(filters or {})

    render_trend_chart(filtered)
    render_product_mix_geo(filtered)
    render_order_signals(filtered)
    render_row_sample(filtered)

    render_diagnostics_panel(state.metadata, state.selected_run, state.missing_info)


if __name__ == "__main__":
    main()
