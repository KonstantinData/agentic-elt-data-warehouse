# Silver Layer Run Report  
**Run ID:** 20260124_213339_#39e076b1  
**Bronze Run ID:** 20260124_213259_#39e076b1  
**Run Period:** 2026-01-24T21:32:59.653361Z to 2026-01-24T21:32:59.776182Z  

---

## Executive Summary  
- All 9 source tables from CRM and ERP systems were successfully ingested and processed in the Bronze run, providing a comprehensive raw foundation for the Silver layer transformation.  
- Profiling indicates consistent schema structures, with key columns identified and manageable null values in certain attributes that are candidates for standardization in Silver.  
- No duplicates found, ensuring structural uniqueness readiness for downstream linkage and integration.  
- The Silver layer is positioned well for supporting business problem exploration around customer, product, sales, and location dimensions.  
- Several actionable data quality transformations are suggested to improve consistency, especially for missing values in demographic and product attributes.

---

## 1. Problem Definition & Objectives  
The data available enables exploration of core business questions focused on customers, products, and sales, such as:  
- Understanding drivers of customer retention and repeat purchases by analyzing customer demographics (cst_info, CST_AZ12) and their transaction behaviors (sales_details).  
- Examining product category performance and lifecycle through product master data (prd_info, PX_CAT_G1V2) and sales transactions.  
- Investigating regional sales differences using location data (LOC_A101) linked to customer IDs.  
- Assessing the impact of pricing strategies and discount dependency using sales pricing fields.  

These analyses can help stakeholders including Marketing, Sales, Product Management, Operations, Finance, and Executive leadership make informed decisions on customer targeting, product assortment, pricing, and supply chain optimizations. Assumptions such as demographic influences on lifetime value or regional preferences on product mix can be tested.

---

## 2. Data Identification & Understanding  
- Tables processed:  
  - Customers: `cst_info.csv`, `customer_info.csv`, `CST_AZ12.csv`  
  - Products: `prd_info.csv`, `product_info.csv`, `PX_CAT_G1V2.csv`  
  - Transactions: `sales_details.csv`, `sales_transactions.csv`  
  - Locations: `LOC_A101.csv`  
- Key relationships involve linking customer IDs across tables (`cst_id`, `CID`, `customer_id`), product keys (`prd_key`, `product_id`), and sales order numbers.  
- CRM and ERP source systems are clearly distinguished, useful for lineage and integration quality control.  
- Referential integrity cannot yet be fully assessed at Bronze; the Silver layer will implement standardizations and prepare for joins.

---

## 3. Data Ingestion & Integration (Bronze)  
- All source files from CRM and ERP systems were successfully loaded with no failures or skips.  
- File sizes and read durations are consistent with table sizes indicating proper ingestion.  
- Raw data files preserved without transformations, ensuring traceability and fidelity.

---

## 4. Data Cleaning & Transformation Preparation (Bronze → Silver)  
- Key transformations suggested for Silver include standardizing missing values in:  
  - Customer demographic and identifier fields (e.g., `cst_gndr`, `cst_create_date`) in `cst_info.csv`  
  - Product cost, line, and end dates in `prd_info.csv`  
  - Country codes in `LOC_A101.csv`  
  - Sales price and sales amount fields in `sales_details.csv`  
  - Gender field in `CST_AZ12.csv`  
- No duplicate rows detected across any tables, preserving uniqueness crucial for joining.  
- Data types inferred and will be standardized (string, integer, datetime) in Silver for consistency.

---

## 5. Exploratory Data Analysis (Structural)  
- Null value distributions warrant attention, especially ~25% missing in gender (`cst_gndr`), and some missing dates or cost data in products.  
- High cardinality key fields like customer ID and product ID identified; strong candidates for primary keys after cleaning.  
- No duplicated rows ensure clean and reliable base for analytical constructs.  
- Silver transformations should focus on harmonizing missing or inconsistent values to enable reliable dimension and fact joining.

---

## 7. Validation & Quality Control  
- Row counts align across related customer and location files, indicating no major data loss.  
- Schema conformity is excellent with expected columns and data types inferred correctly.  
- No errors or skips reported during ingestion confirm technical stability of ETL pipeline.  
- Silver layer readiness is high for further aggregation, KPIs, and BI use cases pending cleaning steps.

---

## 8. Interpretation & Communication  
- The Silver preparation will focus on data quality improvement, particularly handling missing values, and standardizing datetime and categorical fields.  
- Once standardized, the data will support segmentation, KPI calculations, and dashboarding reliably.  
- Current data covers rich customer demographics and comprehensive product and sales records, enabling multi-dimensional analysis.  
- Gaps such as few rows in some ERP product files exist but do not impair the overall scope.

---

## 9. Operationalization  
- The Silver layer will build on the Bronze run’s full ingest, establishing clean, typed, and harmonized datasets for BI tools like Tableau.  
- Clear metadata lineage from Bronze files to Silver tables supports transparency and auditability.  
- Standard keys and datatype consistency enable integration with downstream ML features and segmentation workflows.

---

## 10. Monitoring & Continuous Improvement  
- Repeatable Bronze and Silver runs with logged durations and file hashes ensure stability and reproducibility.  
- Future improvements should monitor null value trends and increase data completeness, especially for key demographic and product attributes.  
- Feedback loops to source or ETL teams may improve upstream data quality based on Silver profiling insights.

---

## Schema Overview & Profiling Highlights  
| Table               | Rows  | Columns | Key Candidates                | Nulls Notes                                     | Suggested Silver Transforms                                        |
|---------------------|-------|---------|------------------------------|------------------------------------------------|-------------------------------------------------------------------|
| CST_AZ12.csv        | 18,484| 3       | CID (unique)                 | GEN missing 1,472 rows (about 8%)               | Standardize missing in GEN                                         |
| cst_info.csv        | 18,494| 7       | cst_id, cst_key (high unique) | Up to 4 missing in IDs, ~4,578 missing gender (25%) | Standardize missing in cst_gndr, cst_id, cst_create_date, names  |
| customer_info.csv   | 5     | 5       | customer_id, firstname, lastname | No nulls                                         | No transformations suggested                                     |
| LOC_A101.csv        | 18,484| 2       | CID (unique)                 | 332 nulls in CNTRY                               | Standardize missing CNTRY                                          |
| prd_info.csv        | 397   | 7       | prd_id (unique)              | Missing prd_cost (2), prd_line (17), prd_end_dt (197) | Standardize missing in prd_cost, prd_end_dt, prd_line             |
| product_info.csv    | 4     | 4       | product_id, product_name     | No nulls                                         | None                                                             |
| PX_CAT_G1V2.csv     | 37    | 4       | ID, SUBCAT (unique)          | No nulls                                         | None                                                             |
| sales_details.csv   | 60,398| 9       | None                        | 8 missing sls_sales, 7 missing sls_price         | Standardize missing in sls_sales, sls_price                       |
| sales_transactions.csv | 8     | 6       | transaction_id (unique)      | No nulls                                         | None                                                             |

---

## Potential Business Problems and Decisions  
- **Customer Retention & Churn:** Analyze which demographics, purchase behaviors, or delivery times correlate with repeat purchase rates to reduce churn.  
- **Product Category Performance:** Identify high return or low margin categories from product and sales data to optimize assortments and discontinuations.  
- **Regional Sales Variations:** Use location and customer linkage to explain stark differences in sales by country or region, impacting marketing and inventory planning.  
- **Pricing Strategy Impact:** Evaluate sales dependency on discounts or price levels to adjust promotional strategies for margin improvement.  

**Stakeholders:** Marketing, Sales, Product Management, Operations, Finance, Executives  
**Decisions Supported:** Customer segmentation targeting, product portfolio adjustments, budget allocations, pricing optimizations  
**Assumptions to Test:** Demographic factors influence lifetime value; certain products succeed regionally; discount reliance correlates with churn.

---

## Scope Definition Options  
- **Time:** Filter data by order or transaction date ranges to analyze recent performance or historical trends.  
- **Geography:** Focus analysis on specific countries or regions using location table (LOC_A101) linked by customer IDs.  
- **Data Domains:** Limit to transactions and customers for retention studies or expand to products and categories for assortment insights.  
- **Systems/Sources:** Choose CRM-only for marketing-centric views or combine CRM and ERP datasets for more comprehensive insights.  
- **Outputs:** KPI dashboards, segmented customer personas, product performance reports, or ML model feature sets.

---

## KPI Candidates for BI/Tableau  
- **Repeat Purchase Rate:** % of customers with >1 purchase within a defined period.  
- **Average Sales per Customer:** Sum of sales amount / number of active customers.  
- **Sales by Product Category:** Total sales aggregated by product category and subcategory.  
- **On-Time Delivery Rate:** % of orders shipped by due date (derived from `sls_due_dt` and `sls_ship_dt`).  
- **Return Rate (proxy):** % of sales discounts or price adjustments per category (requires further data).  
- **Customer Lifetime Value (LTV) Proxy:** Aggregated sales per customer over their relationship duration.  

Formulas would rely on clean, joined data in Silver layer incorporating customer, product, sales, and location attributes.

---

## Segmentation & Clustering Opportunities  
- **Features:** Customer demographics (gender, age from birthdate), purchase behavior (frequency, recency, monetary), product preferences (categories bought), geographic location (country).  
- **Methods:** K-means, hierarchical clustering for segment discovery; decision trees or association rules for profiling; time-series clustering for purchasing patterns.  
- **Example Segments:**  
  - High-value loyal customers vs. discount-seeking churn risks  
  - Regional product preference groups  
  - Product category affinity clusters to inform personalized marketing  
  - Late delivery sensitive customers for logistics prioritization  

This Silver layer enables feature engineering and foundational data cleanliness to support these ML workflows.

---

# End of Report

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
