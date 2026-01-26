from __future__ import annotations

import streamlit as st

from src.dashboard.components.diagnostics import display_missingness_summary, render_diagnostics_panel
from src.dashboard.context import get_dashboard_state


def main() -> None:
    state = get_dashboard_state()
    if not state or not state.selected_run:
        st.warning("No Silver run detected yet.")
        return

    if state.enriched is None or state.tables is None:
        st.warning("Silver tables or metadata are missing for the selected run.")
        st.caption(state.guidance)
        return

    st.header("Run health & diagnostics")
    render_diagnostics_panel(state.metadata, state.selected_run, state.missing_info)
    display_missingness_summary(state.missing_info)


if __name__ == "__main__":
    main()
