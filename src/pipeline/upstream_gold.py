"""
File: src/pipeline/upstream_gold.py
Purpose:
  This module provides a local copy of the Gold layer runner from the
  upstream repository.  It is used by ``gold_layer.py`` to build the
  star‑schema marts (dimensions, fact tables, and aggregates) from a
  Silver run.  The code here is copied from the upstream
  ``load_3_gold_layer.py`` with minimal modifications.  It defines
  helper functions for building each mart and a ``main()`` entrypoint
  that orchestrates the build.  By keeping this module local we avoid
  network dependencies and allow our wrapper to override output paths
  via environment variables.

Inputs:
  - artifacts/silver/<silver_run_id>/data/*.csv

Outputs:
  - artifacts/gold/marts/<gold_run_id>/data/*.csv
  - artifacts/gold/marts/<gold_run_id>/metadata.yaml
  - artifacts/gold/marts/<gold_run_id>/reports/gold_report.html

Step:
  Gold (marts builder)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import pandas as pd
import yaml


# ----------------------------------------------------------------------
# Constants and run id helpers
# ----------------------------------------------------------------------
RUN_ID_RE = re.compile(r"^(?P<ts>\d{8}_\d{6})_#(?P<suffix>[0-9a-fA-F]{6,32})$")
PIPELINE_VERSION = "1.1.0"
MAX_IO_ATTEMPTS = 3
IO_BACKOFF_S = 0.5

# Required schemas for input tables (subset of upstream)
REQUIRED_SCHEMAS: Dict[str, Tuple[str, ...]] = {
    "sales_details.csv": (
        "sls_ord_num",
        "sls_prd_key",
        "sls_cust_id",
        "sls_sales",
        "sls_quantity",
        "sls_price",
        "sls_order_dt",
        "sls_ship_dt",
        "sls_due_dt",
    ),
    "prd_info.csv": (
        "prd_key",
        "prd_nm",
        "prd_cost",
        "prd_line",
        "prd_start_dt",
        "prd_end_dt",
    ),
    "PX_CAT_G1V2.csv": ("ID", "CAT", "SUBCAT", "MAINTENANCE"),
    "cst_info.csv": (
        "cst_id",
        "cst_key",
        "cst_firstname",
        "cst_lastname",
        "cst_marital_status",
        "cst_gndr",
        "cst_create_date",
    ),
    "CST_AZ12.csv": ("CID", "BDATE", "GEN"),
    "LOC_A101.csv": ("CID", "CNTRY"),
}


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def find_repo_root(start: Path) -> Path:
    cur = start
    while cur != cur.parent:
        if (cur / "artifacts").exists() and (cur / "src").exists():
            return cur
        cur = cur.parent
    return start.resolve().parents[2]


REPO_ROOT = find_repo_root(Path(__file__).resolve())


def resolve_silver_root(repo_root: Path) -> Path:
    override = os.environ.get("SILVER_ROOT_OVERRIDE")
    if override:
        candidate = Path(override).expanduser()
        if candidate.exists() and candidate.is_dir():
            return candidate
        raise FileNotFoundError(
            f"SILVER_ROOT_OVERRIDE does not exist or is not a directory: {candidate}"
        )
    candidates = [
        repo_root / "artifacts" / "silver",
        repo_root / "artifacts" / "silver" / "elt",
        repo_root / "artifacts" / "silver" / "runs",
        repo_root / "artifacts" / "sylver" / "runs",
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    raise FileNotFoundError(
        "Could not find Silver root. Tried:\n" + "\n".join(str(c) for c in candidates)
    )


SILVER_ROOT = resolve_silver_root(REPO_ROOT)
GOLD_ROOT = Path(os.environ.get("GOLD_ROOT_OVERRIDE", str(REPO_ROOT / "artifacts" / "gold" / "marts"))).expanduser()


def should_emit_stdout() -> bool:
    return os.environ.get("PYTEST_CURRENT_TEST") is None


# IO helpers
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": iso_utc(utc_now()),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        event = getattr(record, "event", None)
        context = getattr(record, "context", None)
        if event:
            payload["event"] = event
        if context:
            payload["context"] = context
        if record.exc_info:
            exc_type = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            payload["exception"] = {
                "type": exc_type,
                "message": str(record.exc_info[1]),
            }
        return json.dumps(payload, ensure_ascii=False)


def build_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger(f"gold_runner_{log_path}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, event: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
    logger.info(message, extra={"event": event, "context": context or {}})
    if should_emit_stdout():
        print(f"{iso_utc(utc_now())} | {event} | {message}")


def with_retry(action: Callable[[], Any], *, attempts: int = MAX_IO_ATTEMPTS, backoff_s: float = IO_BACKOFF_S) -> Any:
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except (OSError, IOError) as exc:
            if attempt == attempts:
                raise
            time.sleep(backoff_s * attempt)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    def _read() -> None:
        with open(path, "rb") as f:
            while True:
                b = f.read(chunk_size)
                if not b:
                    break
                h.update(b)
    with_retry(_read)
    return h.hexdigest()


def write_yaml(obj: Dict[str, Any], path: Path) -> None:
    data = yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
    with_retry(lambda: path.write_text(data, encoding="utf-8"))


def write_html(report_ctx: Dict[str, Any], path: Path) -> None:
    from jinja2 import Template  # noqa: WPS433
    rendered = Template(HTML_REPORT_TEMPLATE).render(**report_ctx)
    with_retry(lambda: path.write_text(rendered, encoding="utf-8"))


def find_latest_run_id(root: Path) -> str:
    if not root.exists():
        raise FileNotFoundError(f"Root does not exist: {root}")
    run_ids: List[str] = []
    for name in root.iterdir():
        if not name.is_dir():
            continue
        if RUN_ID_RE.match(name.name):
            run_ids.append(name.name)
    if not run_ids:
        raise FileNotFoundError(f"No runs found in: {root}")
    return sorted(run_ids)[-1]


def resolve_silver_data_dir(silver_run_id: str) -> Path:
    d = SILVER_ROOT / silver_run_id / "data"
    if d.exists():
        return d
    for c in [
        REPO_ROOT / "artifacts" / "silver" / silver_run_id / "data",
        REPO_ROOT / "artifacts" / "silver" / "elt" / silver_run_id / "data",
        REPO_ROOT / "artifacts" / "silver" / "runs" / silver_run_id / "data",
        REPO_ROOT / "artifacts" / "sylver" / "runs" / silver_run_id / "data",
    ]:
        if c.exists():
            return c
    raise FileNotFoundError(f"Silver data dir not found for run_id={silver_run_id}")


def make_gold_run_id_from_silver(silver_run_id: str, now: Optional[datetime] = None) -> str:
    m = RUN_ID_RE.match(silver_run_id)
    if not m:
        raise ValueError(f"Invalid silver run_id format: {silver_run_id}")
    suffix = m.group("suffix")
    now_dt = now or utc_now()
    return f"{now_dt.strftime('%Y%m%d_%H%M%S')}_#{suffix}"


def load_csv(folder: Path, filename: str) -> Optional[pd.DataFrame]:
    p = folder / filename
    if not p.exists():
        return None
    return with_retry(lambda: pd.read_csv(p))


def write_csv(df: pd.DataFrame, path: Path) -> None:
    with_retry(lambda: df.to_csv(path, index=False))


def format_output_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def validate_required_columns(
    df: pd.DataFrame,
    required: Sequence[str],
    table_name: str,
) -> List[str]:
    missing = [col for col in required if col not in df.columns]
    return [f"{table_name} missing columns: {missing}"] if missing else []


# ----------------------------------------------------------------------
# Mart builder helper functions (copied from upstream)
# ----------------------------------------------------------------------
def int_to_date(val: Any) -> Optional[str]:
    try:
        v = int(val)
        if v <= 0:
            return None
        return f"{v // 10000:04d}-{(v // 100) % 100:02d}-{v % 100:02d}"
    except Exception:
        return None


def add_period_month(df: pd.DataFrame, date_col: str, out_col: str = "period") -> pd.DataFrame:
    df = df.copy()
    df[out_col] = df[date_col].apply(lambda x: int_to_date(x)[:7] if pd.notnull(x) and int_to_date(x) else None)
    return df


def build_gold_dim_customer(
    cst_info: pd.DataFrame,
    cst_az12: Optional[pd.DataFrame],
    loc: Optional[pd.DataFrame],
) -> pd.DataFrame:
    cst = cst_info.copy()
    cst["cst_id"] = pd.to_numeric(cst["cst_id"], errors="coerce")
    cst["cst_key"] = cst["cst_key"].astype(str)
    # merge az
    if cst_az12 is not None:
        az = cst_az12.copy()
        az["CID"] = az["CID"].astype(str)
        az["BDATE"] = pd.to_numeric(az["BDATE"], errors="coerce")
        az["GEN"] = az["GEN"].astype(str)
        cst["CID"] = cst["cst_key"].str.replace("-", "", regex=False)
        az["CID_norm"] = az["CID"].str.replace("-", "", regex=False)
        cst = cst.merge(
            az[["CID_norm", "BDATE", "GEN"]],
            left_on="CID",
            right_on="CID_norm",
            how="left",
        ).drop(columns=["CID_norm"])
    else:
        cst["BDATE"] = None
        cst["GEN"] = None
    # merge loc
    if loc is not None:
        loc_df = loc.copy()
        loc_df["CID"] = loc_df["CID"].astype(str)
        loc_df["CID_norm"] = loc_df["CID"].str.replace("-", "", regex=False)
        cst = cst.merge(
            loc_df[["CID_norm", "CNTRY"]],
            left_on="CID",
            right_on="CID_norm",
            how="left",
        ).drop(columns=["CID_norm"])
    else:
        cst["CNTRY"] = None
    out_cols = [
        "cst_id",
        "cst_key",
        "cst_firstname",
        "cst_lastname",
        "cst_marital_status",
        "cst_gndr",
        "cst_create_date",
        "CID",
        "BDATE",
        "GEN",
        "CNTRY",
    ]
    for col in out_cols:
        if col not in cst.columns:
            cst[col] = None
    cst = cst.drop_duplicates(subset=["cst_id"])
    return cst[out_cols]


def build_gold_dim_product(
    prd_info: pd.DataFrame,
    px_cat: Optional[pd.DataFrame],
) -> pd.DataFrame:
    prd = prd_info.copy()
    prd["prd_key"] = prd["prd_key"].astype(str)
    prd["prd_id"] = prd["prd_key"]
    if px_cat is not None:
        px = px_cat.copy()
        px["ID"] = px["ID"].astype(str)
        prd = prd.merge(
            px[["ID", "CAT", "SUBCAT", "MAINTENANCE"]],
            left_on="prd_key",
            right_on="ID",
            how="left",
        )
    else:
        prd["ID"] = prd["prd_key"]
        prd["CAT"] = None
        prd["SUBCAT"] = None
        prd["MAINTENANCE"] = None
    out_cols = [
        "prd_id",
        "prd_key",
        "prd_nm",
        "prd_cost",
        "prd_line",
        "prd_start_dt",
        "prd_end_dt",
        "ID",
        "CAT",
        "SUBCAT",
        "MAINTENANCE",
    ]
    for col in out_cols:
        if col not in prd.columns:
            prd[col] = None
    prd = prd.drop_duplicates(subset=["prd_id"])
    return prd[out_cols]


def build_gold_dim_location(loc: pd.DataFrame) -> pd.DataFrame:
    l = loc.copy()
    l["CID"] = l["CID"].astype(str)
    l = l.drop_duplicates(subset=["CID"])
    out_cols = ["CID", "CNTRY"]
    for col in out_cols:
        if col not in l.columns:
            l[col] = None
    return l[out_cols]


def build_gold_fact_sales(sales: pd.DataFrame) -> pd.DataFrame:
    f = sales.copy()
    for col in [
        "sls_ord_num",
        "sls_prd_key",
        "sls_cust_id",
        "sls_sales",
        "sls_quantity",
        "sls_price",
        "sls_order_dt",
        "sls_ship_dt",
        "sls_due_dt",
    ]:
        if col not in f.columns:
            f[col] = None
    f = f.drop_duplicates(subset=["sls_ord_num", "sls_prd_key"])
    out_cols = [
        "sls_ord_num",
        "sls_prd_key",
        "sls_cust_id",
        "sls_sales",
        "sls_quantity",
        "sls_price",
        "sls_order_dt",
        "sls_ship_dt",
        "sls_due_dt",
    ]
    return f[out_cols]


def build_gold_agg_exec_kpis(
    fact_sales: pd.DataFrame,
    dim_customer: pd.DataFrame,
) -> pd.DataFrame:
    sales = fact_sales.copy()
    sales = add_period_month(sales, "sls_order_dt", "period")
    cust = dim_customer.copy()
    cust["cst_id"] = pd.to_numeric(cust["cst_id"], errors="coerce")
    if "cst_marital_status" in cust.columns:
        cust["customer_segment"] = cust["cst_marital_status"].fillna("Unknown")
    else:
        cust["customer_segment"] = "All"
    sales["sls_cust_id"] = pd.to_numeric(sales["sls_cust_id"], errors="coerce")
    sales = sales.merge(
        cust[["cst_id", "customer_segment"]],
        left_on="sls_cust_id",
        right_on="cst_id",
        how="left",
    )
    def safe_div(a, b):
        return float(a) / float(b) if b else None
    agg = (
        sales.groupby(["period", "customer_segment"], dropna=False)
        .agg(
            total_sales=("sls_sales", "sum"),
            order_count=("sls_ord_num", "nunique"),
            customer_count=("sls_cust_id", "nunique"),
        )
        .reset_index()
    )
    agg["Conversion Rate"] = None
    agg["Customer Lifetime Value"] = agg.apply(lambda r: safe_div(r["total_sales"], r["customer_count"]), axis=1)
    agg["Return Rate"] = None
    agg["Average Order Value"] = agg.apply(lambda r: safe_div(r["total_sales"], r["order_count"]), axis=1)
    agg["Customer Retention Rate"] = None
    out_cols = [
        "period",
        "customer_segment",
        "Conversion Rate",
        "Customer Lifetime Value",
        "Return Rate",
        "Average Order Value",
        "Customer Retention Rate",
    ]
    return agg[out_cols]


def build_gold_agg_product_performance(
    fact_sales: pd.DataFrame,
    dim_product: pd.DataFrame,
) -> pd.DataFrame:
    sales = fact_sales.copy()
    sales = add_period_month(sales, "sls_order_dt", "period")
    prod = dim_product.copy()
    sales = sales.merge(
        prod[["prd_id", "prd_key", "prd_line", "CAT", "SUBCAT"]],
        left_on="sls_prd_key",
        right_on="prd_key",
        how="left",
    )
    agg = (
        sales.groupby(["prd_id", "period", "prd_line", "CAT", "SUBCAT"], dropna=False)
        .agg(
            Total_Sales=("sls_sales", "sum"),
            Total_Quantity_Sold=("sls_quantity", "sum"),
        )
        .reset_index()
    )
    agg["Return Rate"] = None
    out_cols = [
        "prd_id",
        "period",
        "prd_line",
        "CAT",
        "SUBCAT",
        "Total_Sales",
        "Total_Quantity_Sold",
        "Return Rate",
    ]
    return agg[out_cols]


def build_gold_agg_geo_performance(
    fact_sales: pd.DataFrame,
    dim_location: pd.DataFrame,
    dim_product: pd.DataFrame,
) -> pd.DataFrame:
    sales = fact_sales.copy()
    sales = add_period_month(sales, "sls_order_dt", "period")
    if "CID" not in sales.columns and "sls_cust_id" in sales.columns:
        sales["CID"] = sales["sls_cust_id"].astype(str)
    loc = dim_location.copy()
    loc["CID"] = loc["CID"].astype(str)
    sales = sales.merge(
        loc[["CID", "CNTRY"]],
        on="CID",
        how="left",
    )
    prod = dim_product.copy()
    prod["prd_key"] = prod["prd_key"].astype(str)
    sales = sales.merge(
        prod[["prd_key", "CAT"]],
        left_on="sls_prd_key",
        right_on="prd_key",
        how="left",
    )
    agg = (
        sales.groupby(["CNTRY", "CAT", "period"], dropna=False)
        .agg(
            Total_Sales=("sls_sales", "sum"),
            Total_Quantity_Sold=("sls_quantity", "sum"),
        )
        .reset_index()
    )
    out_cols = [
        "CNTRY",
        "CAT",
        "period",
        "Total_Sales",
        "Total_Quantity_Sold",
    ]
    return agg[out_cols]


def build_gold_wide_sales_enriched(
    fact_sales: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_location: pd.DataFrame,
) -> pd.DataFrame:
    sales = fact_sales.copy()
    cust = dim_customer.copy()
    cust["cst_id"] = pd.to_numeric(cust["cst_id"], errors="coerce")
    sales["sls_cust_id"] = pd.to_numeric(sales["sls_cust_id"], errors="coerce")
    sales = sales.merge(
        cust[
            [
                "cst_id",
                "cst_key",
                "cst_marital_status",
                "cst_gndr",
                "BDATE",
                "GEN",
                "CNTRY",
            ]
        ],
        left_on="sls_cust_id",
        right_on="cst_id",
        how="left",
    )
    prod = dim_product.copy()
    prod["prd_key"] = prod["prd_key"].astype(str)
    sales = sales.merge(
        prod[
            [
                "prd_id",
                "prd_key",
                "prd_nm",
                "prd_line",
                "CAT",
                "SUBCAT",
            ]
        ],
        left_on="sls_prd_key",
        right_on="prd_key",
        how="left",
    )
    if "CID" not in sales.columns and "cst_key" in sales.columns:
        sales["CID"] = sales["cst_key"].str.replace("-", "", regex=False)
    loc = dim_location.copy()
    loc["CID"] = loc["CID"].astype(str)
    sales = sales.merge(
        loc[["CID", "CNTRY"]],
        on="CID",
        how="left",
        suffixes=("", "_loc"),
    )
    out_cols = [
        "sls_ord_num",
        "sls_prd_key",
        "sls_cust_id",
        "sls_sales",
        "sls_quantity",
        "sls_price",
        "cst_id",
        "cst_key",
        "cst_marital_status",
        "cst_gndr",
        "BDATE",
        "GEN",
        "CNTRY",
        "prd_id",
        "prd_key",
        "prd_nm",
        "prd_line",
        "CAT",
        "SUBCAT",
    ]
    for col in out_cols:
        if col not in sales.columns:
            sales[col] = None
    return sales[out_cols]


# ----------------------------------------------------------------------
# HTML report template
# ----------------------------------------------------------------------
HTML_REPORT_TEMPLATE = """
<html>
<head><title>Gold Run Report</title></head>
<body>
<h1>Gold Run Report: {{ run_id }}</h1>
<p>Run start (UTC): {{ start_dt }}</p>
<p>Run end (UTC): {{ end_dt }}</p>
<p>Source silver_run_id: {{ silver_run_id }}</p>

<h2>Outputs</h2>
<ul>
{% for o in outputs %}
  <li>{{ o }}</li>
{% endfor %}
</ul>

<h2>Status</h2>
<p>{{ status }}</p>

{% if errors and errors|length > 0 %}
<h2>Errors</h2>
<ul>
{% for e in errors %}
  <li>{{ e }}</li>
{% endfor %}
</ul>
{% endif %}

{% if notes %}
<h2>Notes</h2>
<p>{{ notes }}</p>
{% endif %}

</body>
</html>
"""


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main() -> int:
    # Determine Silver run_id to read from.  Accept CLI arg or fall back to latest.
    silver_run_id = sys.argv[1] if len(sys.argv) > 1 else find_latest_run_id(SILVER_ROOT)
    silver_data_dir = resolve_silver_data_dir(silver_run_id)
    start_dt = utc_now()
    requested_run_id: Optional[str] = None
    if len(sys.argv) > 2:
        requested_run_id = sys.argv[2]
    else:
        requested_run_id = os.environ.get("RUN_ID") or os.environ.get("ORCHESTRATOR_RUN_ID")
    if requested_run_id and RUN_ID_RE.match(requested_run_id):
        gold_run_id = requested_run_id
        run_id_source = "provided"
    else:
        gold_run_id = make_gold_run_id_from_silver(silver_run_id, now=start_dt)
        run_id_source = "generated"
    m = RUN_ID_RE.match(silver_run_id)
    suffix = m.group("suffix") if m else None
    gold_dir = GOLD_ROOT / gold_run_id
    data_dir = gold_dir / "data"
    reports_dir = gold_dir / "reports"
    ensure_dir(data_dir)
    ensure_dir(reports_dir)
    run_log_path = gold_dir / "run_log.txt"
    logger = build_logger(run_log_path)
    # GOLD_MART_PLAN is not injected here; treat as None (build all marts)
    mart_plan: Optional[Dict[str, Any]] = None
    outputs: List[Dict[str, Any]] = []
    errors: List[str] = []
    notes: List[str] = []
    if requested_run_id and not RUN_ID_RE.match(requested_run_id):
        notes.append(
            f"Requested run_id '{requested_run_id}' did not match expected format; generated run_id used instead."
        )
    log_event(logger, "RUN_START", "Gold run started", {"silver_run_id": silver_run_id})
    log_event(
        logger,
        "RUN_METADATA",
        "Gold run identifiers resolved",
        {"gold_run_id": gold_run_id, "run_id_source": run_id_source},
    )
    log_event(
        logger,
        "RUN_PATHS",
        "Resolved IO paths",
        {"repo_root": str(REPO_ROOT), "silver_data_dir": str(silver_data_dir), "gold_dir": str(gold_dir)},
    )
    try:
        # Load all required silver tables
        sales = load_csv(silver_data_dir, "sales_details.csv")
        prd_info = load_csv(silver_data_dir, "prd_info.csv")
        px_cat = load_csv(silver_data_dir, "PX_CAT_G1V2.csv")
        cst_info = load_csv(silver_data_dir, "cst_info.csv")
        cst_az12 = load_csv(silver_data_dir, "CST_AZ12.csv")
        loc = load_csv(silver_data_dir, "LOC_A101.csv")
        # Validate required columns
        for name, df in [
            ("sales_details.csv", sales),
            ("prd_info.csv", prd_info),
            ("PX_CAT_G1V2.csv", px_cat),
            ("cst_info.csv", cst_info),
            ("CST_AZ12.csv", cst_az12),
            ("LOC_A101.csv", loc),
        ]:
            if df is None:
                continue
            required = REQUIRED_SCHEMAS.get(name)
            if required:
                schema_errors = validate_required_columns(df, required, name)
                if schema_errors:
                    raise ValueError("; ".join(schema_errors))
        # Build marts
        # 1) gold_dim_customer
        if cst_info is not None:
            dim_customer = build_gold_dim_customer(cst_info, cst_az12, loc)
            out = data_dir / "gold_dim_customer.csv"
            mart_start = time.perf_counter()
            write_csv(dim_customer, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_dim_customer",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(dim_customer)),
                    "schema": list(dim_customer.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_dim_customer",
                {"rows": len(dim_customer), "duration_s": duration},
            )
        else:
            errors.append("cst_info.csv is required for gold_dim_customer")
        # 2) gold_dim_product
        if prd_info is not None:
            dim_product = build_gold_dim_product(prd_info, px_cat)
            out = data_dir / "gold_dim_product.csv"
            mart_start = time.perf_counter()
            write_csv(dim_product, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_dim_product",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(dim_product)),
                    "schema": list(dim_product.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_dim_product",
                {"rows": len(dim_product), "duration_s": duration},
            )
        else:
            errors.append("prd_info.csv is required for gold_dim_product")
        # 3) gold_dim_location
        if loc is not None:
            dim_location = build_gold_dim_location(loc)
            out = data_dir / "gold_dim_location.csv"
            mart_start = time.perf_counter()
            write_csv(dim_location, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_dim_location",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(dim_location)),
                    "schema": list(dim_location.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_dim_location",
                {"rows": len(dim_location), "duration_s": duration},
            )
        else:
            errors.append("LOC_A101.csv is required for gold_dim_location")
        # 4) gold_fact_sales
        if sales is not None:
            fact_sales = build_gold_fact_sales(sales)
            out = data_dir / "gold_fact_sales.csv"
            mart_start = time.perf_counter()
            write_csv(fact_sales, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_fact_sales",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(fact_sales)),
                    "schema": list(fact_sales.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_fact_sales",
                {"rows": len(fact_sales), "duration_s": duration},
            )
        else:
            errors.append("sales_details.csv is required for gold_fact_sales")
        # 5) gold_agg_exec_kpis
        if sales is not None and cst_info is not None:
            dim_customer_local = dim_customer if 'dim_customer' in locals() else build_gold_dim_customer(cst_info, cst_az12, loc)
            agg_exec_kpis = build_gold_agg_exec_kpis(fact_sales, dim_customer_local)
            out = data_dir / "gold_agg_exec_kpis.csv"
            mart_start = time.perf_counter()
            write_csv(agg_exec_kpis, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_agg_exec_kpis",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(agg_exec_kpis)),
                    "schema": list(agg_exec_kpis.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_agg_exec_kpis",
                {"rows": len(agg_exec_kpis), "duration_s": duration},
            )
        # 6) gold_agg_product_performance
        if sales is not None and prd_info is not None:
            dim_product_local = dim_product if 'dim_product' in locals() else build_gold_dim_product(prd_info, px_cat)
            agg_prod_perf = build_gold_agg_product_performance(fact_sales, dim_product_local)
            out = data_dir / "gold_agg_product_performance.csv"
            mart_start = time.perf_counter()
            write_csv(agg_prod_perf, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_agg_product_performance",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(agg_prod_perf)),
                    "schema": list(agg_prod_perf.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_agg_product_performance",
                {"rows": len(agg_prod_perf), "duration_s": duration},
            )
        # 7) gold_agg_geo_performance
        if sales is not None and loc is not None and prd_info is not None:
            dim_location_local = dim_location if 'dim_location' in locals() else build_gold_dim_location(loc)
            dim_product_local = dim_product if 'dim_product' in locals() else build_gold_dim_product(prd_info, px_cat)
            agg_geo_perf = build_gold_agg_geo_performance(fact_sales, dim_location_local, dim_product_local)
            out = data_dir / "gold_agg_geo_performance.csv"
            mart_start = time.perf_counter()
            write_csv(agg_geo_perf, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_agg_geo_performance",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(agg_geo_perf)),
                    "schema": list(agg_geo_perf.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_agg_geo_performance",
                {"rows": len(agg_geo_perf), "duration_s": duration},
            )
        # 8) gold_wide_sales_enriched
        if sales is not None and cst_info is not None and prd_info is not None and loc is not None:
            dim_customer_local = dim_customer if 'dim_customer' in locals() else build_gold_dim_customer(cst_info, cst_az12, loc)
            dim_product_local = dim_product if 'dim_product' in locals() else build_gold_dim_product(prd_info, px_cat)
            dim_location_local = dim_location if 'dim_location' in locals() else build_gold_dim_location(loc)
            wide_sales = build_gold_wide_sales_enriched(fact_sales, dim_customer_local, dim_product_local, dim_location_local)
            out = data_dir / "gold_wide_sales_enriched.csv"
            mart_start = time.perf_counter()
            write_csv(wide_sales, out)
            duration = time.perf_counter() - mart_start
            outputs.append(
                {
                    "name": "gold_wide_sales_enriched",
                    "path": format_output_path(out, REPO_ROOT),
                    "rows": int(len(wide_sales)),
                    "schema": list(wide_sales.columns),
                    "sha256": sha256_file(out),
                    "duration_s": duration,
                }
            )
            log_event(
                logger,
                "MART_BUILT",
                "Built gold_wide_sales_enriched",
                {"rows": len(wide_sales), "duration_s": duration},
            )
        notes.append(
            "Gold marts built based on Silver sales, product, customer, demographic, and location data, "
            "where available. Return Rate KPIs set to None due to lack of returns data."
        )
    except Exception as e:
        errors.append(f"UNHANDLED gold build failure: {type(e).__name__}: {e}")
        logger.exception(
            "UNHANDLED_EXCEPTION",
            extra={"event": "UNHANDLED_EXCEPTION", "context": {"error_type": type(e).__name__}},
        )
    end_dt = utc_now()
    total_duration = time.perf_counter() - (start_dt.timestamp())
    status = "success" if not errors else "partial"
    meta: Dict[str, Any] = {
        "run": {
            "layer": "gold",
            "pipeline": "load_3_gold_layer",
            "pipeline_version": PIPELINE_VERSION,
            "run_id": gold_run_id,
            "started_utc": iso_utc(start_dt),
            "ended_utc": iso_utc(end_dt),
            "duration_s": (end_dt - start_dt).total_seconds(),
            "status": status,
        },
        "env": {
            "python": sys.version.replace("\n", " "),
            "pandas": getattr(pd, "__version__", "unknown"),
            "platform": platform.platform(),
        },
        "source": {
            "silver_run_id": silver_run_id,
            "silver_data_dir": str(silver_data_dir),
            "suffix": suffix,
        },
        "metrics": {
            "outputs_count": len(outputs),
            "errors_count": len(errors),
            "duration_s": (end_dt - start_dt).total_seconds(),
        },
        "outputs": outputs,
        "errors": errors,
        "notes": notes,
    }
    write_yaml(meta, gold_dir / "metadata.yaml")
    write_html(
        {
            "run_id": gold_run_id,
            "start_dt": iso_utc(start_dt),
            "end_dt": iso_utc(end_dt),
            "silver_run_id": silver_run_id,
            "outputs": [o["path"] for o in outputs],
            "status": status,
            "errors": errors,
            "notes": " ".join(notes),
        },
        reports_dir / "gold_report.html",
    )
    log_event(
        logger,
        "RUN_END",
        "Gold run completed",
        {"duration_s": (end_dt - start_dt).total_seconds(), "status": status, "output_dir": str(gold_dir)},
    )
    return 0 if status == "success" else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())