from __future__ import annotations

import pandas as pd
import streamlit as st
from typing import Iterable, Sequence

from src.dashboard.state import DashboardState, build_dashboard_state


def hydrate_dashboard_state(
    selected_run_id: str | None = None,
    available_runs: Iterable | None = None,
) -> DashboardState:
    """Build or refresh the dashboard state and keep it in session state."""
    state = build_dashboard_state(selected_run_id, available_runs=available_runs)
    st.session_state["dashboard_state"] = state
    return state


def get_dashboard_state() -> DashboardState | None:
    return st.session_state.get("dashboard_state")


def persist_filters(filters: dict[str, Sequence]) -> dict[str, Sequence]:
    st.session_state["dashboard_filters"] = filters
    return filters


def get_persisted_filters() -> dict[str, Sequence] | None:
    return st.session_state.get("dashboard_filters")


def persist_filtered_dataset(filtered: pd.DataFrame) -> pd.DataFrame:
    st.session_state["dashboard_filtered"] = filtered
    return filtered


def get_filtered_dataset() -> pd.DataFrame | None:
    return st.session_state.get("dashboard_filtered")
