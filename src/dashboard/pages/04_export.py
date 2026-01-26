from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from src.dashboard.context import get_dashboard_state, get_filtered_dataset, get_persisted_filters


def _serialize_filters(filters: dict[str, object]) -> dict[str, object]:
    serialized: dict[str, object] = {}
    for key, value in filters.items():
        if isinstance(value, tuple):
            serialized[key] = [str(v) for v in value]
        elif isinstance(value, list):
            serialized[key] = [str(v) for v in value]
        else:
            serialized[key] = str(value)
    return serialized


def main() -> None:
    state = get_dashboard_state()
    filtered = get_filtered_dataset()
    filters = get_persisted_filters()

    st.header("Exports & context")
    if not state or not state.selected_run:
        st.warning("No Silver run selected.")
        return
    if filtered is None:
        st.warning("Filtered data is not yet available.")
        return

    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered dataset (CSV)",
        data=csv_data,
        file_name=f"{state.selected_run.run_id}_filtered_data.csv",
        mime="text/csv",
    )

    context_payload = {
        "run_id": state.selected_run.run_id,
        "filters": _serialize_filters(filters or {}),
        "artifact_source": state.selected_run.artifact_label,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "row_count": len(filtered),
    }
    context_json = json.dumps(context_payload, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        label="Download dashboard context (JSON)",
        data=context_json,
        file_name=f"{state.selected_run.run_id}_dashboard_context.json",
        mime="application/json",
    )
