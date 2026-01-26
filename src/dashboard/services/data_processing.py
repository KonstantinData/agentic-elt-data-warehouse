from __future__ import annotations

from datetime import datetime
from typing import Tuple

import pandas as pd


def parse_iso_timestamp(value: str | None) -> datetime | None:
    """Convert ISO timestamps (possibly with Z suffix) into aware datetimes."""
    if not value:
        return None
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def build_product_lookup(product_df: pd.DataFrame) -> tuple[dict[str, str], dict[str, str]]:
    """Build direct/suffix lookups for product keys."""
    direct: dict[str, str] = {}
    suffix: dict[str, str] = {}
    for _, row in product_df.iterrows():
        key = str(row.get("prd_key") or "")
        name = row.get("prd_nm") or ""
        if not key:
            continue
        label = name if name else key
        direct[key] = label
        parts = key.split("-")
        for idx in range(len(parts)):
            suffix_key = "-".join(parts[idx:])
            suffix.setdefault(suffix_key, label)
    return direct, suffix


def resolve_product_name(
    key: str, lookup: tuple[dict[str, str], dict[str, str]]
) -> str | None:
    """Try to resolve a product key to the best available label."""
    direct_map, suffix_map = lookup
    if key in direct_map:
        return direct_map[key]
    if key in suffix_map:
        return suffix_map[key]
    return None


def prepare_sales_data(tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, tuple[dict[str, str], dict[str, str]]]:
    """Enrich raw Silver tables with calendar, geography, and product context."""
    sales = tables["sales"].copy()
    product = tables["product"].copy()
    customer = tables["customer"].copy()
    location = tables["location"].copy()

    date_columns = ["sls_order_dt", "sls_ship_dt", "sls_due_dt"]
    for column in date_columns:
        sales[column] = pd.to_datetime(sales[column], errors="coerce")

    numeric_columns = ["sls_sales", "sls_price", "sls_quantity"]
    for column in numeric_columns:
        sales[column] = pd.to_numeric(sales[column], errors="coerce")

    customer = customer.assign(
        location_key=customer["cst_key"]
        .astype(str)
        .str.replace("-", "", regex=False)
        .str.upper()
    )
    location = location.assign(
        location_key=location["CID"]
        .astype(str)
        .str.replace("-", "", regex=False)
        .str.upper()
    )
    loc_map = dict(zip(location["location_key"], location["CNTRY"]))
    customer["country"] = customer["location_key"].map(loc_map)
    customer = customer.rename(
        columns={
            "cst_gndr": "customer_gender",
            "cst_marital_status": "customer_marital_status",
        }
    )

    enriched = (
        sales.merge(
            product[["prd_key", "prd_line", "prd_nm", "prd_cost"]],
            left_on="sls_prd_key",
            right_on="prd_key",
            how="left",
        )
        .merge(
            customer[
                [
                    "cst_id",
                    "customer_gender",
                    "customer_marital_status",
                    "country",
                ]
            ],
            left_on="sls_cust_id",
            right_on="cst_id",
            how="left",
        )
    )

    enriched["product_line"] = enriched["prd_line"].fillna("Other").astype(str)
    enriched["product_name"] = enriched["prd_nm"].fillna("Unknown product")
    enriched["customer_gender"] = enriched["customer_gender"].fillna("Unspecified")
    enriched["customer_marital_status"] = enriched["customer_marital_status"].fillna("Unspecified")
    enriched["country"] = enriched["country"].fillna("Unknown")

    enriched["order_dt"] = enriched["sls_order_dt"]
    enriched["order_date"] = enriched["order_dt"].dt.date
    enriched["order_day"] = enriched["order_dt"].dt.day_name()
    enriched["order_week"] = enriched["order_dt"].dt.to_period("W").dt.start_time
    return enriched, build_product_lookup(product)
