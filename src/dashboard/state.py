from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from src.dashboard.services.artifacts import (
    RunLocation,
    explain_missing_artifacts,
    list_available_runs,
    load_required_tables,
    load_run_metadata,
)
from src.dashboard.services.data_processing import prepare_sales_data


@dataclass
class DashboardState:
    available_runs: list[RunLocation]
    selected_run: RunLocation | None
    metadata: dict
    tables: dict[str, pd.DataFrame] | None
    enriched: pd.DataFrame | None
    product_lookup: tuple[dict[str, str], dict[str, str]] | None
    missing_info: dict[str, int]
    guidance: str


def _calculate_missing_info(enriched: pd.DataFrame) -> dict[str, int]:
    if enriched is None:
        return {"sales_missing": 0, "price_missing": 0, "quantity_missing": 0}
    return {
        "sales_missing": int(enriched["sls_sales"].isna().sum()),
        "price_missing": int(enriched["sls_price"].isna().sum()),
        "quantity_missing": int(enriched["sls_quantity"].isna().sum()),
    }


def build_dashboard_state(
    selected_run_id: str | None = None,
    available_runs: Iterable[RunLocation] | None = None,
) -> DashboardState:
    runs = list(available_runs) if available_runs is not None else list_available_runs()
    guidance = explain_missing_artifacts()
    selected_run: RunLocation | None = None
    if runs:
        if selected_run_id:
            selected_run = next((run for run in runs if run.run_id == selected_run_id), runs[0])
        else:
            selected_run = runs[0]
        guidance = f"Artifacts served from {selected_run.artifact_label}"

    metadata: dict = {}
    tables: dict[str, pd.DataFrame] | None = None
    enriched: pd.DataFrame | None = None
    product_lookup = None

    if selected_run:
        metadata = load_run_metadata(selected_run)
        tables = load_required_tables(selected_run)
        if tables:
            enriched, product_lookup = prepare_sales_data(tables)

    missing_info = _calculate_missing_info(enriched) if enriched is not None else {
        "sales_missing": 0,
        "price_missing": 0,
        "quantity_missing": 0,
    }

    return DashboardState(
        available_runs=runs,
        selected_run=selected_run,
        metadata=metadata,
        tables=tables,
        enriched=enriched,
        product_lookup=product_lookup,
        missing_info=missing_info,
        guidance=guidance,
    )
