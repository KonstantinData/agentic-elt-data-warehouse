from __future__ import annotations

from datetime import date
from typing import Sequence

import pandas as pd
import streamlit as st

from src.dashboard.services.data_processing import resolve_product_name


def session_multiselect(label: str, options: Sequence[str], key: str, default: Sequence[str], help_text: str | None = None) -> list[str]:
    """Keep multi-select widgets in session state so filters stay bookmarkable."""
    if not options:
        st.sidebar.warning(f"No options available for {label}.")
        return []
    select_all_label = f"Select all {label}"
    if st.sidebar.button(select_all_label, key=f"{key}_sel_all"):
        st.session_state[key] = list(options)
    existing = st.session_state.get(key, list(default))
    st.sidebar.multiselect(
        label,
        options,
        default=existing,
        key=key,
        help=help_text,
    )
    return st.session_state.get(key, list(options))


def session_range_slider(key: str, label: str, min_value: float, max_value: float, value: tuple[float, float] | None = None, step: float | None = None, format: str | None = None) -> tuple[float, float]:
    """Store slider range state so filtering feels deterministic."""
    default_value = st.session_state.get(key, value if value is not None else (min_value, max_value))
    step_value = step
    if step_value is not None:
        step_value = float(step_value)
    slider_value = st.sidebar.slider(label, min_value, max_value, default_value, step=step_value, format=format)
    st.session_state[key] = slider_value
    return slider_value


def configure_filters(
    enriched: pd.DataFrame,
    missing_info: dict[str, int],
    product_lookup: tuple[dict[str, str], dict[str, str]],
) -> dict[str, Sequence]:
    """Render the sidebar filters and capture selections."""
    st.sidebar.header("🧭 Dashboard filters")
    dates = enriched["order_dt"].dropna()
    today = date.today()
    start_date = dates.min().date() if not dates.empty else today
    end_date = dates.max().date() if not dates.empty else today

    st.sidebar.markdown("**Date selection**")
    col_start, col_end = st.sidebar.columns(2)
    start_date_value = col_start.date_input(
        "Start date",
        value=start_date,
        min_value=start_date,
        max_value=end_date,
        key="filter_start_date",
    )
    end_date_value = col_end.date_input(
        "End date",
        value=end_date,
        min_value=start_date_value,
        max_value=end_date,
        key="filter_end_date",
    )
    date_range = (start_date_value, end_date_value)

    available_lines = sorted(enriched["product_line"].dropna().unique())
    selected_lines = session_multiselect(
        "Product lines",
        available_lines,
        "filter_product_lines",
        default=available_lines,
        help_text="Selecting a line automatically trims the available product keys.",
    )

    available_keys = (
        enriched[enriched["product_line"].isin(selected_lines)]["sls_prd_key"]
        .dropna()
        .unique()
    )
    fallback_keys = enriched["sls_prd_key"].dropna().unique()
    key_set = sorted(available_keys) if available_keys.size else sorted(fallback_keys)
    label_options = []
    label_to_key: dict[str, str] = {}
    for key in key_set:
        name = resolve_product_name(key, product_lookup)
        label = f"{name} ({key})" if name else key
        label_options.append(label)
        label_to_key[label] = key
    selected_labels = session_multiselect(
        "Product names (hierarchical)",
        label_options,
        "filter_product_keys",
        default=label_options,
        help_text="Product-line trimming refreshes this list each time.",
    )
    selected_keys = [label_to_key[label] for label in selected_labels if label in label_to_key]

    country_options = sorted(enriched["country"].unique())
    selected_countries = session_multiselect(
        "Countries / regions",
        country_options,
        "filter_countries",
        default=country_options,
        help_text="Country selection also restricts gender and marital status pools.",
    )

    gender_options = sorted(enriched["customer_gender"].unique())
    selected_genders = session_multiselect(
        "Customer gender",
        gender_options,
        "filter_genders",
        default=gender_options,
    )

    marital_options = sorted(enriched["customer_marital_status"].unique())
    selected_marital = session_multiselect(
        "Customer marital status",
        marital_options,
        "filter_marital_status",
        default=marital_options,
    )

    def _range(series: pd.Series, fallback: float = 0.0) -> tuple[float, float]:
        valid = series.dropna()
        if valid.empty:
            return fallback, fallback
        return float(valid.min()), float(valid.max())

    sales_min, sales_max = _range(enriched["sls_sales"])
    price_min, price_max = _range(enriched["sls_price"])
    quantity_min, quantity_max = _range(enriched["sls_quantity"])

    sales_range = session_range_slider(
        "filter_sales_range",
        "Revenue per record",
        sales_min,
        sales_max,
        value=(sales_min, sales_max),
        format="%.0f",
        step=50,
    )
    price_range = session_range_slider(
        "filter_price_range",
        "Verkaufspreis",
        price_min,
        price_max,
        value=(price_min, price_max),
        format="%.0f",
        step=10,
    )
    quantity_range = session_range_slider(
        "filter_quantity_range",
        "Menge",
        quantity_min,
        quantity_max,
        value=(quantity_min, quantity_max),
        step=1,
    )

    with st.sidebar.expander("Data health & dependency hints", expanded=False):
        st.write(
            f"- Missing `sls_sales`: {missing_info['sales_missing']:,} rows\n"
            f"- Missing `sls_price`: {missing_info['price_missing']:,} rows\n"
            f"- Missing `sls_quantity`: {missing_info['quantity_missing']:,} rows"
        )
        st.caption(
            "Product-line selections cascade into the product-key list; country filters keep the gender and marital pools synchronized."
        )
    st.sidebar.caption("@st.cache_data caches file reads; session state keeps filter combos bookmarkable.")

    filters = {
        "date_range": date_range,
        "product_lines": selected_lines,
        "product_keys": selected_keys,
        "countries": selected_countries,
        "genders": selected_genders,
        "marital_status": selected_marital,
        "sales_range": sales_range,
        "price_range": price_range,
        "quantity_range": quantity_range,
    }
    st.session_state["dashboard_filters"] = filters
    return filters


def apply_filters(df: pd.DataFrame, filters: dict[str, Sequence]) -> pd.DataFrame:
    """Apply the sidebar filters to the enriched sales data."""
    mask = df["order_dt"].notna()
    start_date, end_date = filters["date_range"]
    mask &= df["order_dt"].dt.date >= start_date
    mask &= df["order_dt"].dt.date <= end_date
    mask &= df["product_line"].isin(filters["product_lines"])
    mask &= df["sls_prd_key"].isin(filters["product_keys"])
    mask &= df["country"].isin(filters["countries"])
    mask &= df["customer_gender"].isin(filters["genders"])
    mask &= df["customer_marital_status"].isin(filters["marital_status"])

    sales_low, sales_high = filters["sales_range"]
    mask &= df["sls_sales"].between(sales_low, sales_high).fillna(False)

    price_low, price_high = filters["price_range"]
    mask &= df["sls_price"].between(price_low, price_high).fillna(False)

    quantity_low, quantity_high = filters["quantity_range"]
    mask &= df["sls_quantity"].between(quantity_low, quantity_high).fillna(False)

    return df.loc[mask].copy()
