"""
File: src/pipeline/bronze_layer.py
Purpose:
  Implements the Bronze layer of the ELT pipeline by copying raw CRM/ERP CSV files
  into a run‑scoped directory under the unified run root.  The bronze layer
  performs no transformations; it merely ingests raw files, computes checksums
  and records ingestion metadata.  This module wraps the original bronze loader
  from the upstream repository and exposes a function `run_bronze` that accepts
  a target run root and a run identifier.

Inputs:
  - raw/source_crm/*.csv – raw CRM source files
  - raw/source_erp/*.csv – raw ERP source files
Outputs:
  - artifacts/runs/<run_id>/bronze/data/*.csv – copies of all source files
  - artifacts/runs/<run_id>/bronze/data/metadata.yaml – bronze run metadata
  - artifacts/runs/<run_id>/bronze/reports/elt_report.html – human report
  - run details returned as a dictionary

Step:
  Bronze (ELT ingest)

This file is largely derived from the upstream `load_1_bronze_layer.py`.  See
that file for full implementation details.  We re‑export the `BronzeRunConfig`
and `run_bronze_load` functions to avoid breaking references.
"""

# NOTE: Re‑export classes and functions from the upstream bronze loader.  This
# NOTE: allows the golden path to call a stable API while keeping the
# NOTE: implementation in one place.  The original code lives below.

from __future__ import annotations

from typing import Any, Dict, Optional

import os

from . import upstream_bronze as _upstream


def run_bronze(run_id: str, run_root: str, raw_crm: str = "raw/source_crm", raw_erp: str = "raw/source_erp") -> Dict[str, Any]:
    """
    Execute a bronze layer load into the unified run root.

    Parameters
    ----------
    run_id : str
        The run identifier.  Must match the pattern ``YYYYMMDD_HHMMSS_#<hex>``.
    run_root : str
        The root directory for this run (e.g. ``artifacts/runs/<run_id>``).
    raw_crm : str
        Path to the CRM raw source directory.
    raw_erp : str
        Path to the ERP raw source directory.

    Returns
    -------
    Dict[str, Any]
        A JSON‑serialisable summary of the bronze load (see upstream loader for
        keys).

    Notes
    -----
    This function sets the environment variables ``BRONZE_ROOT`` and
    ``BRONZE_RUN_ID`` so that the upstream bronze loader writes into
    ``<run_root>/bronze`` and uses the provided ``run_id`` without modifying it.
    """

    bronze_root = os.path.join(run_root, "bronze")
    # Ensure the directory exists
    os.makedirs(bronze_root, exist_ok=True)
    # Override environment for upstream loader
    os.environ["BRONZE_ROOT"] = bronze_root
    os.environ["BRONZE_RUN_ID"] = run_id
    config = _upstream.BronzeRunConfig(
        raw_crm=raw_crm,
        raw_erp=raw_erp,
        bronze_root=bronze_root,
        crm_file_glob="*.csv",
        crm_file_exclude=None,
        erp_file_glob="*.csv",
        erp_file_exclude=None,
        run_id=run_id,
    )
    return _upstream.run_bronze_load(config)


# NOTE: The remainder of this file contains the upstream bronze loader under
# NOTE: the name ``upstream_bronze``.  It is imported in this module to
# NOTE: preserve the original functionality.  Do not edit the upstream code
# NOTE: directly; any modifications should be done in our wrapper functions.
