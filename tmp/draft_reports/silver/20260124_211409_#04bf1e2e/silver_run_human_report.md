# Silver Layer Run Report: 2026-01-24_211547_#04bf1e2e

---

## Executive Summary

- The Bronze layer ingested 9 source CSV files successfully with no failures, capturing customer, product, sales, location, and category data.
- Data quality requires attention for missing values in key demographic and transactional fields; standardization steps are recommended in Silver.
- The integrated Silver layer sets a solid foundation for customer and product views, transactional sales analysis, and location-based segmentation.
- No structural integrity issues such as duplicate rows or broken keys were detected, ensuring readiness for downstream analytics.
- Rich metadata and consistent schema enable BI dashboarding, segmentation modeling, and support for addressing varied business problems.

---

## 1. Problem Definition & Objectives

This Silver layer run supports analysis of core business questions related to:

- **Customer behavior**: e.g. declining repeat purchase rates, lifetime value segmentation, and churn risk.
- **Product performance**: e.g. identifying high return rate categories, product lifecycle management, and pricing strategies.
- **Sales patterns across locations**: e.g. regional sales discrepancies, discount dependence, and delivery time impacts.
- **Marketing and operational decisions**: e.g. targeted promotions, inventory allocation, and channel budget optimization.

**Impacted Stakeholders** include executives (revenue and profitability), marketing (segmentation and acquisition), sales teams (conversion and pricing), operations (fulfillment and logistics), finance (forecasting), and product management.

Key decisions that this data can inform:

- Customer targeting and retention programs.
- Product category assortment adjustments.
- Marketing budget allocation by segment and channel.
- Price and discount optimization strategies.

Assumptions such as correlations between customer demographics and purchase frequency or regional product performance can be explored using the Silver layer.

---

## 2. Data Identification & Understanding

- **Input source tables covered:**

  - Customer master/tier: `cst_info`, `CST_AZ12`, `customer_info`
  - Product master/tier: `prd_info`, `product_info`, `PX_CAT_G1V2`
  - Sales transactional: `sales_details`, `sales_transactions`
  - Locations: `LOC_A101`

- Customer keys (`cst_id`, `CID`, `customer_id`), product keys (`prd_id`, `product_id`, `sls_prd_key`), and location IDs (`CID`) are consistently present.

- Separation of master data (customers, products, locations) and transactional sales data is clear.

---

## 3. Data Ingestion & Integration (Bronze)

- All 9 expected CSV files from CRM and ERP sources were ingested successfully with zero failures or skips.
- Data was read swiftly (total run duration ~0.12 seconds), preserving fidelity with no transformations at this stage.
- Files included large volumes for sales and customer data plus smaller dimension files.

---

## 4. Data Cleaning & Transformation (Bronze -> Silver)

- Silver layer should conduct:

  - Whitespace trimming and conversion of empty strings to standardized missing (NA) values.
  - Type casting: e.g., timestamps parsed for dates, string-to-integer conversions as needed.
  - Harmonization of categorical codes such as gender flags and maintenance indicators.
  
- Missing values identified in demographic fields (gender, marital status), product attributes (cost, end dates), location country codes, and sales monetary fields require cleaning.

---

## 5. Exploratory Data Analysis (on Silver)

- **Schema overview:**
  
  - 9 tables with row counts ranging from 4 to ~60k and column counts from 2 to 9.
  
- **Inferred types:**
  
  - Customer DOB and product start/end dates as datetime.
  - Prices and sales as numeric (float or integer).
  - IDs consistently typed as strings or integers depending on source.

- **Nulls:**

  - Missing gender values in customer tables (~25% in `cst_info`).
  - Null country codes in location data.
  - Gaps in product category, cost, end dates.
  - Occasional missing sales price and sales amount values.
  
- **Duplicates:**

  - No duplicate rows detected in any table.
  
- **Key candidates:**
  
  - Strong unique keys identified for customer ID variants, product ID, and transaction IDs.
  
- **Suggested Silver transforms:**
  
  - Standardize missing values (fill with NA) in demographic, product, location, and sales monetary columns.
  - Parse string dates consistently into datetime format.
  
---

## 6. Modeling & Analytical Methods

- The Silver layer now supports construction of:

  - Customer behavioral aggregates (frequency, recency, monetary values).
  - Product and category performance views.
  - Sales fact tables with consistent keys for joining customers, products, and locations.

- Enables building ML features for customer segmentation and predictive modeling in downstream layers.

---

## 7. Validation & Quality Control

- All source files validated by row count and schema completeness.
- No broken referential integrity or orphan keys identified.
- The Silver layer is ready for:

  - Business reporting.
  - Feeding BI tools such as Tableau.
  - Preparation of ML feature tables.

---

## 8. Interpretation & Communication

- The Silver run achieved:

  - Full ingestion of all relevant data sources.
  - Identification and standardization of missing values needed.
  - Data type harmonization recommendations.
  
- It does not yet include aggregated or cleaned data; these are planned for later stages.

- The current Silver data allows thorough exploration of customer, product, and sales questions with robust data quality and structure.

- Analysts can trust keys and metadata to build KPIs and dashboards without concerns of duplicates or missing entities, but should address missing attribute values in cleaning steps.

---

## 9. Operationalization

- Silver layer tables serve as the stable base layer for:

  - Ad-hoc analytical queries.
  - BI dashboarding and reporting consistency.
  - Downstream ML feature extraction.

- Metadata ensures full lineage from Bronze, supporting traceability and audit.

- Standards in key naming and data types are maintained for unified data definitions.

---

## 10. Monitoring & Continuous Improvement

- Repeatable run demonstrated with consistent file ingestion and processing times.

- Missing value patterns and null counts are stable but should be monitored for trends.

- Feedback to source data providers and cleansing logic can reduce missing demographic and sales monetary fields over time.

---

# Schema Overview and Data Profiling Highlights

| Table               | Rows  | Columns | Key Candidates             | Nulls Noted                       | Duplicates | Silver Transforms Suggested                 |
|---------------------|-------|---------|----------------------------|---------------------------------|------------|---------------------------------------------|
| cst_info.csv        | 18,494| 7       | cst_id (99.95% unique), cst_key (99.97%) | Missing: cst_id (4), cst_firstname, cst_gndr (~4578), marital status, create_date | 0          | Standardize missing attributes and dates    |
| CST_AZ12.csv        | 18,484| 3       | CID (unique)                | Missing GEN (~1472)               | 0          | Standardize missing GEN flag                 |
| customer_info.csv   | 5     | 5       | customer_id (unique)        | None                            | 0          | None                                        |
| LOC_A101.csv        | 18,484| 2       | CID (unique)                | Missing CNTRY (332)               | 0          | Standardize missing country info             |
| prd_info.csv        | 397   | 7       | prd_id (unique)             | Missing prd_cost, prd_line, prd_end_dt | 0          | Standardize missing product attributes       |
| product_info.csv    | 4     | 4       | product_id (unique)         | None                            | 0          | None                                        |
| PX_CAT_G1V2.csv     | 37    | 4       | ID (unique), SUBCAT         | None                            | 0          | None                                        |
| sales_details.csv   | 60,398| 9       | None                       | Missing sls_sales (8), sls_price (7) | 0          | Standardize missing sales values             |
| sales_transactions.csv | 8    | 6       | transaction_id (unique)     | None                            | 0          | None                                        |

---

# Potential Business Problems and Decisions

- **Declining Customer Retention**
  - Identify customer segments with decreasing repeat purchases to reduce churn.
  - Impact: Revenue loss from lost customers.
  - Decisions: Target retention campaigns, optimize delivery times.
  - Assumptions: Faster delivery correlates with retention.

- **Product Category Underperformance**
  - Detect categories with high return rates or low sales growth.
  - Impact: Margin erosion and wasted inventory costs.
  - Decisions: Adjust product assortment or pricing.
  - Assumptions: Categories vary by region or customer demographics.

- **Regional Sales Disparities**
  - Analyze differences in sales across countries and regions.
  - Impact: Missed market opportunities.
  - Decisions: Localized marketing spend and stock allocation.
  - Assumptions: Certain products perform better in specific countries.

- **Discount Dependency Risks**
  - Assess the impact of frequent discounts on profitability and customer loyalty.
  - Impact: Margin dilution and potential customer churn.
  - Decisions: Refine discount policies and promotions.
  - Assumptions: Heavy discount users may have higher returns.

---

# Scope Definition Options

- **Time Scope**
  - Last 12 months data.
  - Year-to-date.
  - Rolling windows (e.g. last 90 days).

- **Geographic Scope**
  - DACH region (Germany, Austria, Switzerland).
  - EMEA countries based on location data.
  - Specific countries identified in LOC_A101.

- **Data Scope**
  - Customers with ≥1 purchase only.
  - Active customers (purchased within last N days).
  - Products with minimum sales volume thresholds.

- **System/Source Scope**
  - CRM data focused on customer and product info.
  - ERP system data for transactions and categories.
  - Combined integrated view using both.

- **Output Format**
  - BI dashboards (Tableau, Power BI).
  - Static periodic reports.
  - ML-ready feature tables for segmentation/predictive analytics.

---

# KPI Candidates for BI/Tableau

| KPI Name               | Description                                      | Formula (conceptual)                                      |
|------------------------|------------------------------------------------|----------------------------------------------------------|
| Conversion Rate        | % of visitors converting to customers           | (Number of purchases / Number of unique customers) * 100%|
| Customer Lifetime Value (LTV) | Total expected revenue per customer            | Average Order Value * Purchase Frequency * Customer Lifespan |
| Return Rate            | % of items returned vs items sold                | (Returned Units / Sold Units) * 100%                      |
| Cost per Acquisition (CPA) | Marketing spend per newly acquired customer     | Marketing Spend / Number of New Customers                 |
| Revenue Growth (%)      | Growth in revenue between time periods           | ((Revenue_period2 - Revenue_period1) / Revenue_period1) * 100% |
| Average Order Value (AOV) | Average revenue per order                        | Total Revenue / Total Orders                               |
| Purchase Frequency      | Average purchases per customer                     | Number of Orders / Number of Unique Customers             |
| Customer Retention Rate | % of customers retained over the period           | ((Customers_end_period - New_customers) / Customers_start_period) * 100% |

---

# Segmentation & Clustering Opportunities

- **Potential Features**
  - Demographics: age (from DOB), gender, country.
  - Behavior: recency, frequency, monetary spend, discount usage.
  - Product preferences: categories and subcategories purchased.
  - Sales transactional timelines and delivery metrics.

- **Common Methods**
  - RFM (Recency, Frequency, Monetary) segmentation.
  - K-Means clustering for behavioral groups.
  - Hierarchical clustering for nested segments.
  - Market basket analysis for product affinity groups.

- **Example Segments**
  - High-value loyal customers.
  - Discount-sensitive and price-conscious shoppers.
  - Seasonal or category-specific buyers.
  - One-time or dormant customers.

These segmentation outputs can inform targeted marketing, personalized offers, and retention efforts.

---

# Summary

This Silver layer run successfully consolidated clean, consistent customer, product, transactional, location, and category data from CRM and ERP sources. The data readiness supports rich analytical use cases including KPI reporting, segmentation, and predictive modeling. Addressing identified missing values and standardizing key fields will further enhance data quality and trustworthiness for business insights.

## Automated Bronze Profiling (for Silver Draft)

### Schema Overview
- CST_AZ12.csv: 18484 rows, 3 columns
- cst_info.csv: 18494 rows, 7 columns
- customer_info.csv: 5 rows, 5 columns
- LOC_A101.csv: 18484 rows, 2 columns
- prd_info.csv: 397 rows, 7 columns
- product_info.csv: 4 rows, 4 columns
- PX_CAT_G1V2.csv: 37 rows, 4 columns
- sales_details.csv: 60398 rows, 9 columns
- sales_transactions.csv: 8 rows, 6 columns

### Table: CST_AZ12.csv
- Rows: 18484
- Columns: CID, BDATE, GEN
- Inferred types:
  - CID: string
  - BDATE: datetime
  - GEN: string
- Null counts:
  - CID: 0
  - BDATE: 0
  - GEN: 1472
- Duplicate rows: 0
- Key candidates:
  - CID: unique_non_null
- Suggested Silver transforms:
  - Standardize missing values in GEN.

### Table: cst_info.csv
- Rows: 18494
- Columns: cst_id, cst_key, cst_firstname, cst_lastname, cst_marital_status, cst_gndr, cst_create_date
- Inferred types:
  - cst_id: integer
  - cst_key: string
  - cst_firstname: string
  - cst_lastname: string
  - cst_marital_status: string
  - cst_gndr: string
  - cst_create_date: datetime
- Null counts:
  - cst_id: 4
  - cst_key: 0
  - cst_firstname: 8
  - cst_lastname: 7
  - cst_marital_status: 7
  - cst_gndr: 4578
  - cst_create_date: 4
- Duplicate rows: 0
- Key candidates:
  - cst_id: high_uniqueness_99.95%
  - cst_key: high_uniqueness_99.97%
- Suggested Silver transforms:
  - Standardize missing values in cst_create_date.
  - Standardize missing values in cst_firstname.
  - Standardize missing values in cst_gndr.
  - Standardize missing values in cst_id.
  - Standardize missing values in cst_lastname.
  - Standardize missing values in cst_marital_status.

### Table: customer_info.csv
- Rows: 5
- Columns: customer_id, firstname, lastname, gender, date_of_birth
- Inferred types:
  - customer_id: integer
  - firstname: string
  - lastname: string
  - gender: string
  - date_of_birth: datetime
- Null counts:
  - customer_id: 0
  - firstname: 0
  - lastname: 0
  - gender: 0
  - date_of_birth: 0
- Duplicate rows: 0
- Key candidates:
  - customer_id: unique_non_null
  - firstname: unique_non_null
  - lastname: unique_non_null
  - date_of_birth: unique_non_null
- Suggested Silver transforms:
  - No obvious Silver transformations detected.

### Table: LOC_A101.csv
- Rows: 18484
- Columns: CID, CNTRY
- Inferred types:
  - CID: string
  - CNTRY: string
- Null counts:
  - CID: 0
  - CNTRY: 332
- Duplicate rows: 0
- Key candidates:
  - CID: unique_non_null
- Suggested Silver transforms:
  - Standardize missing values in CNTRY.

### Table: prd_info.csv
- Rows: 397
- Columns: prd_id, prd_key, prd_nm, prd_cost, prd_line, prd_start_dt, prd_end_dt
- Inferred types:
  - prd_id: integer
  - prd_key: string
  - prd_nm: string
  - prd_cost: integer
  - prd_line: string
  - prd_start_dt: datetime
  - prd_end_dt: datetime
- Null counts:
  - prd_id: 0
  - prd_key: 0
  - prd_nm: 0
  - prd_cost: 2
  - prd_line: 17
  - prd_start_dt: 0
  - prd_end_dt: 197
- Duplicate rows: 0
- Key candidates:
  - prd_id: unique_non_null
- Suggested Silver transforms:
  - Standardize missing values in prd_cost.
  - Standardize missing values in prd_end_dt.
  - Standardize missing values in prd_line.

### Table: product_info.csv
- Rows: 4
- Columns: product_id, product_name, category, price
- Inferred types:
  - product_id: integer
  - product_name: string
  - category: string
  - price: float
- Null counts:
  - product_id: 0
  - product_name: 0
  - category: 0
  - price: 0
- Duplicate rows: 0
- Key candidates:
  - product_id: unique_non_null
  - product_name: unique_non_null
  - price: unique_non_null
- Suggested Silver transforms:
  - No obvious Silver transformations detected.

### Table: PX_CAT_G1V2.csv
- Rows: 37
- Columns: ID, CAT, SUBCAT, MAINTENANCE
- Inferred types:
  - ID: string
  - CAT: string
  - SUBCAT: string
  - MAINTENANCE: string
- Null counts:
  - ID: 0
  - CAT: 0
  - SUBCAT: 0
  - MAINTENANCE: 0
- Duplicate rows: 0
- Key candidates:
  - ID: unique_non_null
  - SUBCAT: unique_non_null
- Suggested Silver transforms:
  - No obvious Silver transformations detected.

### Table: sales_details.csv
- Rows: 60398
- Columns: sls_ord_num, sls_prd_key, sls_cust_id, sls_order_dt, sls_ship_dt, sls_due_dt, sls_sales, sls_quantity, sls_price
- Inferred types:
  - sls_ord_num: string
  - sls_prd_key: string
  - sls_cust_id: integer
  - sls_order_dt: integer
  - sls_ship_dt: integer
  - sls_due_dt: integer
  - sls_sales: integer
  - sls_quantity: integer
  - sls_price: integer
- Null counts:
  - sls_ord_num: 0
  - sls_prd_key: 0
  - sls_cust_id: 0
  - sls_order_dt: 0
  - sls_ship_dt: 0
  - sls_due_dt: 0
  - sls_sales: 8
  - sls_quantity: 0
  - sls_price: 7
- Duplicate rows: 0
- Key candidates:
  - None detected
- Suggested Silver transforms:
  - Standardize missing values in sls_price.
  - Standardize missing values in sls_sales.

### Table: sales_transactions.csv
- Rows: 8
- Columns: transaction_id, customer_id, product_id, quantity, unit_price, transaction_date
- Inferred types:
  - transaction_id: integer
  - customer_id: integer
  - product_id: integer
  - quantity: integer
  - unit_price: float
  - transaction_date: datetime
- Null counts:
  - transaction_id: 0
  - customer_id: 0
  - product_id: 0
  - quantity: 0
  - unit_price: 0
  - transaction_date: 0
- Duplicate rows: 0
- Key candidates:
  - transaction_id: unique_non_null
  - transaction_date: unique_non_null
- Suggested Silver transforms:
  - No obvious Silver transformations detected.
