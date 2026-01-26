from __future__ import annotations

from typing import Iterable

import pandas as pd
import streamlit as st

from src.dashboard.services.data_processing import parse_iso_timestamp
from src.dashboard.services.artifacts import RunLocation


def render_diagnostics_panel(
    metadata: dict,
    run_location: RunLocation,
    missing_info: dict[str, int],
) -> None:
    """Surface Silver run metadata, suggested transforms, and missing stats."""
    st.markdown("### Silver run diagnostics")
    run_info = metadata.get("run", {})
    summary = metadata.get("summary", {})
    tables = metadata.get("tables", {})

    started = parse_iso_timestamp(run_info.get("started_utc"))
    ended = parse_iso_timestamp(run_info.get("ended_utc"))
    duration = ended - started if started and ended else None

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Silver run", run_location.run_id)
    col2.metric(
        "Started (UTC)",
        started.strftime("%Y-%m-%d %H:%M:%S") if started else "n/a",
    )
    col3.metric("Duration", str(duration).split(".")[0] if duration else "n/a")
    col4.metric("Tables (+metadata)", f"{len(tables)}", delta=summary.get("files_total", 0))

    suggestion_count = sum(
        info.get("transformations_suggested", 0)
        for info in tables.values()
        if isinstance(info, dict)
    )

    with st.expander("Table overview & transformation suggestions", expanded=False):
        table_rows: list[dict[str, str]] = []
        for table_name, table_info in tables.items():
            table_rows.append(
                {
                    "table": table_name,
                    "rows_out": table_info.get("rows_out"),
                    "transform_hints": table_info.get("transformations_suggested", 0),
                }
            )
        if table_rows:
            st.table(pd.DataFrame(table_rows))
        else:
            st.write("No table-specific metadata found.")
        st.write(f"- Agent recommendations: {suggestion_count}")
        rows_total = summary.get("total_rows")
        rows_display = f"{rows_total:,}" if isinstance(rows_total, (int, float)) else rows_total
        st.write(f"- Rows processed (summary metadata): {rows_display}")

    st.caption(
        f"Data source: {run_location.artifact_label} · Missing sales: {missing_info['sales_missing']:,}, "
        f"Missing prices: {missing_info['price_missing']:,}"
    )


def display_missingness_summary(missing_info: dict[str, int]) -> None:
    """Inline missingness summary used across pages."""
    st.markdown("### Missingness overview")
    st.write(
        "- Missing `sls_sales`: "
        f"{missing_info['sales_missing']:,} rows\n"
        "- Missing `sls_price`: "
        f"{missing_info['price_missing']:,} rows\n"
        "- Missing `sls_quantity`: "
        f"{missing_info['quantity_missing']:,} rows"
    )
