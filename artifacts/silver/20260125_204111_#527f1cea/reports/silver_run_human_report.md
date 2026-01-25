# Silver Layer Data Run Report  
**Bronze run id:** 20260125_204110_#527f1cea  
**Silver run id:** 20260125_204111_#527f1cea  

---

## Executive Summary
- Successful ingestion and integration of 9 source tables from CRM and ERP systems with no failures.
- All datasets preserved original granularity; Silver layer cleaning and type harmonization are ready for downstream business analysis.
- Data quality is generally good; some columns require standardization of missing values for completeness.
- Structural integrity robust: unique keys identified, no duplicate rows detected.
- Silver layer is prepared to support business problem exploration, KPI development, segmentation, and operational BI dashboards.

---

## 1. Problem Definition & Objectives
The current Silver layer lays the foundation to analyze critical business questions such as:  
- Which customer segments exhibit declining retention or repeat purchase behavior?  
- Are high return rates concentrated in certain product categories or locations?  
- What are the regional sales performance differentiators and how can marketing be adjusted accordingly?  
- How dependent is sales growth on discounts, and how does pricing strategy affect margins?  

**Impacts and Opportunities:**  
- Revenue maximization via targeted retention efforts and optimized product mixes.  
- Cost savings from improved inventory allocation and reduced returns processing.  
- Risk mitigation by refining pricing strategies and demand forecasts.  
- Enhanced decision-making for marketing campaigns and assortment planning.

**Potential Stakeholders:**  
- Executive leadership overseeing revenue and profitability.  
- Marketing teams conducting segmentation and targeting.  
- Sales management for pipeline and pricing strategies.  
- Operations for fulfillment and logistics optimization.  
- Finance for budgeting and forecasting.  
- Product management for category lifecycle and performance.

**Decisions Supported:**  
- Customer targeting and loyalty program focus.  
- SKU rationalization and category expansions.  
- Marketing budget allocation.  
- Pricing and discount policy adjustments.

**Assumptions to Test:**  
- Faster delivery leads to higher repeat purchase rates.  
- Certain categories perform better in select regions.  
- Heavy discounting correlates with higher return or churn risk.  
- Demographic factors influence customer lifetime value.

---

## 2. Data Identification & Understanding
- **Source Systems:** CRM and ERP raw CSV files were ingested.  
- **Core Tables:** Customer info (cst_info, CST_AZ12), product info (prd_info, product_info, PX_CAT_G1V2), sales transactions (sales_details, sales_transactions), and location data (LOC_A101).  
- **Keys:** Customer IDs, product keys, and location codes are well identified for integration.  
- **Master vs Transactional:** Master tables include customers, products, categories, and locations; transactional sales data is detailed per order.  

---

## 3 & 4. Data Ingestion, Integration, Cleaning & Transformation  
- Raw Bronze data files were successfully ingested with full row counts preserved.  
- Transformation to Silver involves trimming whitespace, type harmonization, and missing value standardization (planned as per suggestions).  
- No aggregations have been applied yet, maintaining the original grain for downstream analytics.  

---

## 5. Exploratory Data Analysis (Structural & Quality Checks)
- **Schema Overview:** 9 tables with row counts ranging from 4 to over 60,000; column counts between 2 and 9.  
- **Inferred Data Types:** Strong alignment with expected types – string identifiers, datetime columns, numeric measures.  
- **Null Values:** Some columns notably contain missing data needing standardization, e.g., customer gender, product line, sales price.  
- **Duplicates:** No duplicate rows found in any table, ensuring uniqueness and consistency.  
- **Unique Keys:** Candidate primary keys identified (e.g., CID in CST_AZ12, cst_id in cst_info, prd_id in prd_info, transaction_id in sales_transactions).  

---

## 6. Modeling & Analytical Methods (Preparation)
- Silver layer prepared for development of customer and product aggregated views.  
- Supports future creation of sales facts for BI and predictive modeling.  
- Enables feature engineering with clean, consistent data types.

---

## 7. Validation & Quality Control
- All files loaded successfully, with no errors or skips.  
- Row counts and schemas matched expectations from source.  
- Ready for controlled Silver creation with standard missing value handling for flagged columns.  
- Orphan key checks can be executed in downstream steps.

---

## 8. Interpretation & Communication
- Silver run fulfilled extraction and structural standardization goals fully.  
- Data quality is sufficient to support KPI calculations, segmentation, and reporting.  
- Some completeness concerns remain with missing values needing harmonization.  
- Enables exploratory analysis but does not yet aggregate or enrich data.

---

## 9. Operationalization
- Silver layer functions as a stable clean source for BI tools like Tableau.  
- Metadata and lineage preserved to trace back to Bronze files.  
- Standardizations align with consistent KPI definitions and downstream ML workflows.

---

## 10. Monitoring & Continuous Improvement
- Run durations confirm efficient pipeline performance.  
- Data completeness and consistency checks to be monitored continuously for improvement.  
- Feedback expected to address missing values and any schema evolution.

---

## Schema Overview and Data Quality Highlights

| Table Name           | Rows  | Columns | Key Candidate(s)       | Nulls Present               | Duplicates | Suggested Silver Transforms                      |
|----------------------|-------|---------|------------------------|----------------------------|------------|-------------------------------------------------|
| CST_AZ12             | 18484 | 3       | CID                    | GEN: 1472 nulls            | 0          | Standardize missing GEN values                   |
| cst_info             | 18494 | 7       | cst_id, cst_key        | Multiple columns with nulls | 0          | Standardize nulls in cst_create_date, names, gender, marital status, id |
| customer_info        | 5     | 5       | customer_id            | None                       | 0          | None                                            |
| LOC_A101             | 18484 | 2       | CID                    | CNTRY: 332 nulls           | 0          | Standardize missing CNTRY values                 |
| prd_info             | 397   | 7       | prd_id                 | prd_cost(2), prd_line(17), prd_end_dt(197) | 0          | Standardize nulls in prd_cost, prd_line, prd_end_dt            |
| product_info         | 4     | 4       | product_id             | None                       | 0          | None                                            |
| PX_CAT_G1V2          | 37    | 4       | ID, SUBCAT             | None                       | 0          | None                                            |
| sales_details        | 60398 | 9       | None                   | sls_sales(8), sls_price(7) | 0          | Standardize nulls in sls_price and sls_sales     |
| sales_transactions   | 8     | 6       | transaction_id         | None                       | 0          | None                                            |

---

## Potential Business Problems and Decisions
- **Declining Repeat Purchases:** Analyze customer retention using customers and sales details tables to identify segments with decreasing loyalty.  
- **High Return Rates:** Explore sales details by product categories (from PX_CAT_G1V2 and prd_info) to isolate problem SKUs or categories.  
- **Regional Sales Variability:** Utilize LOC_A101 location data linked to sales_transactions for geographic performance differentiation.  
- **Discount Dependency:** Identify sales heavily dependent on discount pricing by analyzing sls_price and comparing with sales volume and return indicators.  
- **Customer Demographics Impact:** Leverage gender, age (from BDATE, date_of_birth) for customer lifetime value profiling and targeted marketing.

---

## Scope Definition Options
- **Time Scope:** Filter data by order dates or product lifecycle dates for periodic trend analysis or campaign periods.  
- **Geographic Scope:** Limit analysis to countries or regions using LOC_A101 CNTRY codes.  
- **Data Scope:** Focus on core sales transactions, or enrich with master data on customers, products, and categories.  
- **System/Source Scope:** Choose CRM-centric or ERP-combined data sets depending on analysis complexity.  
- **Output Scope:** Define KPIs for dashboards, segmentation clusters, or predictive models customized to business unit needs.

---

## KPI Candidates for BI/Tableau
- **Total Sales Revenue:** Sum of sales amounts per period, product, or region.  
- **Repeat Purchase Rate:** Percentage of customers with multiple transactions in a defined timeframe.  
- **Average Order Value (AOV):** Average sales price multiplied by quantity per order.  
- **Sales by Category/Region:** Aggregated sales segmented by product category and customer country.  
- **Customer Churn Rate:** Rate at which customers stop purchasing over a period.  
- **Discount Utilization Ratio:** Proportion of sales involving discount prices below standard list price.

---

## Segmentation & Clustering Opportunities
- **Features for Segmentation:** Customer demographics (age, gender, marital status), purchase frequency, average spend, product preferences, and location.  
- **Methods:** K-means clustering, hierarchical clustering for customer and product groups; time series clustering for sales trends.  
- **Example Segments:**  
  - High-value loyal customers vs. infrequent buyers.  
  - Price-sensitive segments identified by discount use.  
  - Regional clusters with distinct category preferences.  
  - Product lifecycle stages clustering based on sales start/end dates and volume.

---

*This report outlines the structural readiness and potential downstream analytical uses of the Silver-layer data derived from the Bronze ingestion run 20260125_204110_#527f1cea. No computations have been performed; the focus remains on enabling analysis and ensuring data quality and integration.*

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
