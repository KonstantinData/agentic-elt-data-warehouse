"""
File: src/pipeline/gold_layer.py

Purpose:
  Implements the Gold layer (Step 2) of the data pipeline.  The Gold
  layer builds a simple star schema from the cleaned data produced by
  the Silver layer.  It creates dimension tables for customers and
  products, a fact table for sales transactions, and aggregate KPI
  tables.  Additionally it produces a wide sales table joining
  customers and products for ease of analysis and modelling.

Why it exists:
  The Gold layer organises data into business‑friendly structures that
  support analytics and ML.  A star schema with separate dimension and
  fact tables provides a clear separation between descriptive
  attributes (dimensions) and quantitative events (facts).

Inputs:
  - Cleaned CSV files from the Silver layer located at
    `artifacts/runs/<run_id>/silver/data`.

Outputs:
  - Dimension tables: `gold_dim_customer.csv`, `gold_dim_product.csv`.
  - Fact table: `gold_fact_sales.csv`.
  - Aggregate tables: `gold_agg_sales_per_customer.csv`,
    `gold_agg_sales_per_product.csv`.
  - Wide table: `gold_wide_sales_enriched.csv`.
  - Metadata YAML file `gold_metadata.yaml` capturing table schemas.
  - Markdown report `gold_marts_report.md` summarising row counts.

Step:
  This module belongs to the Gold layer and is part of the reporting
  stage before EDA and modelling.
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib
import yaml


# NOTE: Read a CSV file into header and rows
def _read_csv(path: Path) -> Tuple[List[str], List[List[str]]]:
    """
    Read a CSV file into header and rows.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]
    return header, rows


# NOTE: Write a CSV file to the given path
def _write_csv(path: Path, header: List[str], rows: List[List[str]]) -> None:
    """
    Write a CSV file to the given path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# NOTE: Deterministically hash a string value with a salt using SHA256
def _pseudonymise(value: str, salt: str) -> str:
    """
    Deterministically hash a string value with a salt using SHA256.
    """
    if value == "":
        return ""
    return hashlib.sha256((salt + value).encode("utf-8")).hexdigest()[:16]


# NOTE: Execute the Gold layer for a given run ID
def run_gold(run_id: str, salt: str = "my_salt") -> None:
    """
    Entry point for the Gold layer.

    Args:
        run_id (str): Unique identifier for this pipeline run.
        salt (str): Salt value used for pseudonymising customer identifiers.
    """
    # NOTE: Define directories for inputs and outputs
    project_root = Path(__file__).resolve().parents[2]
    silver_data = project_root / "artifacts" / "runs" / run_id / "silver" / "data"
    gold_data = project_root / "artifacts" / "runs" / run_id / "gold" / "data"
    gold_meta = project_root / "artifacts" / "runs" / run_id / "gold" / "_meta"
    gold_reports = project_root / "artifacts" / "runs" / run_id / "gold" / "reports"
    gold_meta.mkdir(parents=True, exist_ok=True)
    gold_reports.mkdir(parents=True, exist_ok=True)
    # NOTE: Read source tables from the Silver layer
    cust_header, cust_rows = _read_csv(silver_data / "customer_info.csv")
    prod_header, prod_rows = _read_csv(silver_data / "product_info.csv")
    sales_header, sales_rows = _read_csv(silver_data / "sales_transactions.csv")
    # NOTE: Build the customer dimension table with pseudonymised hashes
    dim_customer_header = ["customer_id", "customer_hash", "gender", "date_of_birth"]
    dim_customer_rows: List[List[str]] = []
    for row in cust_rows:
        row_dict = dict(zip(cust_header, row))
        customer_id = row_dict["customer_id"]
        cust_hash = _pseudonymise(customer_id, salt)
        dim_customer_rows.append([
            customer_id,
            cust_hash,
            row_dict.get("gender", ""),
            row_dict.get("date_of_birth", ""),
        ])
    _write_csv(gold_data / "gold_dim_customer.csv", dim_customer_header, dim_customer_rows)
    # NOTE: Build the product dimension table
    dim_product_header = ["product_id", "product_name", "category", "price"]
    _write_csv(gold_data / "gold_dim_product.csv", dim_product_header, prod_rows)
    # NOTE: Build the fact_sales table and the wide enriched table
    fact_sales_header = [
        "transaction_id",
        "customer_hash",
        "product_id",
        "quantity",
        "unit_price",
        "transaction_date",
    ]
    fact_sales_rows: List[List[str]] = []
    # Build wide table simultaneously
    wide_header = [
        "transaction_id",
        "customer_hash",
        "gender",
        "date_of_birth",
        "product_id",
        "product_name",
        "category",
        "price",
        "quantity",
        "unit_price",
        "transaction_date",
    ]
    wide_rows: List[List[str]] = []
    # Map for product lookup
    prod_dict = {row[0]: row for row in prod_rows}
    cust_hash_map = {row[0]: row[1] for row in dim_customer_rows}
    cust_gender_map = {row[0]: row[2] for row in dim_customer_rows}
    cust_dob_map = {row[0]: row[3] for row in dim_customer_rows}
    for sale_row in sales_rows:
        sale = dict(zip(sales_header, sale_row))
        cust_id = sale["customer_id"]
        p_id = sale["product_id"]
        hashed = cust_hash_map.get(cust_id, "")
        fact_sales_rows.append([
            sale["transaction_id"],
            hashed,
            p_id,
            sale["quantity"],
            sale["unit_price"],
            sale["transaction_date"],
        ])
        prod = prod_dict.get(p_id, [p_id, "", "", ""])
        wide_rows.append([
            sale["transaction_id"],
            hashed,
            cust_gender_map.get(cust_id, ""),
            cust_dob_map.get(cust_id, ""),
            p_id,
            prod[1],
            prod[2],
            prod[3],
            sale["quantity"],
            sale["unit_price"],
            sale["transaction_date"],
        ])
    _write_csv(gold_data / "gold_fact_sales.csv", fact_sales_header, fact_sales_rows)
    _write_csv(gold_data / "gold_wide_sales_enriched.csv", wide_header, wide_rows)
    # NOTE: Compute aggregated KPI tables per customer and per product
    # Aggregate per customer
    agg_cust: Dict[str, Dict[str, float]] = {}
    for row in fact_sales_rows:
        cust_hash = row[1]
        qty = float(row[3]) if row[3] else 0.0
        price = float(row[4]) if row[4] else 0.0
        revenue = qty * price
        agg = agg_cust.setdefault(cust_hash, {"total_qty": 0.0, "total_revenue": 0.0})
        agg["total_qty"] += qty
        agg["total_revenue"] += revenue
    agg_cust_rows = [[cust_hash, f"{data['total_qty']}", f"{data['total_revenue']}"] for cust_hash, data in agg_cust.items()]
    _write_csv(gold_data / "gold_agg_sales_per_customer.csv", ["customer_hash", "total_qty", "total_revenue"], agg_cust_rows)
    # Aggregate per product
    agg_prod: Dict[str, Dict[str, float]] = {}
    for row in fact_sales_rows:
        p_id = row[2]
        qty = float(row[3]) if row[3] else 0.0
        price = float(row[4]) if row[4] else 0.0
        revenue = qty * price
        agg = agg_prod.setdefault(p_id, {"total_qty": 0.0, "total_revenue": 0.0})
        agg["total_qty"] += qty
        agg["total_revenue"] += revenue
    agg_prod_rows = [[p_id, f"{data['total_qty']}", f"{data['total_revenue']}"] for p_id, data in agg_prod.items()]
    _write_csv(gold_data / "gold_agg_sales_per_product.csv", ["product_id", "total_qty", "total_revenue"], agg_prod_rows)
    # NOTE: Write metadata YAML summarising row counts and generate report
    metadata = {
        "gold_dim_customer": len(dim_customer_rows),
        "gold_dim_product": len(prod_rows),
        "gold_fact_sales": len(fact_sales_rows),
        "gold_wide_sales_enriched": len(wide_rows),
        "gold_agg_sales_per_customer": len(agg_cust_rows),
        "gold_agg_sales_per_product": len(agg_prod_rows),
    }
    with open(gold_meta / "gold_metadata.yaml", "w") as f:
        yaml.dump(metadata, f)
    # Write report
    report_lines = ["# Gold Marts Report", "", f"Run ID: {run_id}", ""]
    for table_name, count in metadata.items():
        report_lines.append(f"- {table_name}.csv: {count} rows")
    (gold_reports / "gold_marts_report.md").write_text("\n".join(report_lines), encoding="utf-8")
