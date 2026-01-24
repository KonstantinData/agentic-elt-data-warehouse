# Data Policy

This document outlines how personal data is handled throughout the ELT/analytics pipeline in compliance with the GDPR.

## Raw Inputs

The pipeline ingests raw CSV files from the CRM and ERP systems.  These files may contain personally identifying information (PII) such as:

- `cst_firstname`, `cst_lastname` – customer names
- `cst_key`, `CID` – business identifiers that uniquely identify individuals
- `GEN`, `cst_gndr` – gender codes
- `BDATE` – birth dates

The raw CSV files are copied byte‑for‑byte into `artifacts/runs/<run_id>/bronze/data/` for auditability.  Access to the bronze layer should be restricted to authorised personnel only.

## Pseudonymisation and Removal

During the Silver and Gold stages the data is cleaned and normalised but still contains direct identifiers.  Later stages (feature engineering, segmentation and reporting) must not leak PII.  To achieve this:

1. **Removal** – direct name columns (`cst_firstname`, `cst_lastname`) are dropped entirely when computing customer features and segmentation.
2. **Pseudonymisation** – business keys (`cst_key`, `CID`) are transformed into stable hashes using a secret salt stored in a local `.env` file.  The same salt is applied consistently across runs to preserve joinability without revealing the original identifiers.
3. **Sensitive attributes** – gender and marital status are treated as quasi‑identifiers.  They are retained in aggregated form for segmentation (e.g. counts per segment) but never exposed alongside an individual identifier.

## `data_policy.json`

Each run produces `artifacts/runs/<run_id>/_meta/data_policy.json` summarising how personal fields were handled.  The JSON contains:

- `personal_fields` – list of column names detected as personal or sensitive.
- `pseudonymised` – fields that were hashed with a salt.
- `removed` – fields that were dropped entirely from downstream outputs.
- `salt_hash` – SHA‑256 hash of the secret salt used for pseudonymisation (the salt value itself is not stored).

Operators should review the `data_policy.json` to ensure compliance and audit readiness.
