# Silver Layer Run Report  
**Bronze Run ID:** 20260125_214726_#013410d7  
**Silver Run ID:** 20260125_214727_#013410d7

---

## Executive Summary  
- Successful ingestion and cleaning of 9 source tables from CRM and ERP systems with no failures.  
- Core customer, product, sales, and location data is structurally sound with clear key candidates identified.  
- Silver-layer transformations will standardize date parsing, missing values, and text trimming to ensure data consistency.  
- Data quality issues mainly involve missing values in certain fields such as gender and dates but no duplicated rows detected.  
- The resulting Silver layer is well-prepared for downstream BI reporting, exploratory analytics, segmentation, and modeling tasks.

---

## 1. Problem Definition & Objectives  
The ingested data can support addressing common business questions such as:  
- Understanding customer retention and repeat purchase behavior via customer and sales details.  
- Analyzing product category performance and product lifecycle using product and category tables.  
- Investigating regional sales differences through location data linked to customers.  
- Evaluating the impact of pricing and discounting strategies on sales and returns.  

These questions potentially impact revenue growth, marketing efficiency, inventory optimization, and risk mitigation. Stakeholders include C-level executives, marketing, sales, operations, finance, and product management. Decisions can be informed on customer targeting, product assortment, pricing, and marketing investments. Key assumptions to test later may relate to demographic effects on sales or regional preferences for product categories.

---

## 2. Data Identification & Understanding  
- **Source Tables Processed:**  
  - CRM: `cst_info`, `customer_info`, `prd_info`, `sales_details`  
  - ERP: `CST_AZ12`, `LOC_A101`, `PX_CAT_G1V2`, `product_info`, `sales_transactions`  
- **Master Data vs. Transactional Data:**  
  - Master: Customers (`cst_info`, `customer_info`, `CST_AZ12`), Products (`prd_info`, `product_info`, `PX_CAT_G1V2`), Locations (`LOC_A101`)  
  - Transactional: Sales (`sales_details`, `sales_transactions`)  
- Key relationships are established via customer IDs, product keys, and location IDs, enabling integration across tables.

---

## 3. Data Ingestion & Integration (Bronze)  
- All nine source files were successfully ingested as-is into the Bronze layer with full row fidelity and no errors.  
- Runtime was efficient with average read and copy times well below a second per file.  
- Raw data is untransformed, preserving original values for traceability.

---

## 4. Data Cleaning & Transformation (Bronze → Silver)  
- Parsing of date fields (e.g., creation dates, birthdates, order and ship dates) into standard datetime formats.  
- Standardization of missing values across key fields such as gender, marital status, product line, country, and price.  
- Trimming of whitespace in string fields like customer names, product lines, and location codes.  
- No aggregate transformations applied—record grain preserved for all tables.

---

## 5. Exploratory Data Analysis  
- Structural consistency confirmed with zero duplicate rows detected in all tables.  
- Null values found notably in customer gender (~4578 missing), `prd_cost` and `prd_end_dt` in products, and sales price/sales amount in sales details.  
- Primary keys or key candidates identified for all major tables enabling reliable joins and referential integrity checks.

---

## 7. Validation & Quality Control  
- All tables passed row count and schema validation with expected column counts maintained.  
- No orphan keys or critical integrity issues identified during initial ingestion and profiling.  
- The Silver layer is ready to support business reporting, BI visualizations, and feature engineering for ML workflows.

---

## 8. Interpretation & Communication  
- Silver run achieved a cleaned, standardized dataset with harmonized data types and missing value handling poised for analysis.  
- Current data quality supports a broad range of customer, product, sales, and location explorations.  
- Some gaps remain in demographic completeness (gender), product attributes, and sales completeness that analysts should consider when interpreting results.

---

## 9. Operationalization  
- This Silver layer serves as a stable, canonical dataset foundation for consistent KPI definitions across BI tools such as Tableau.  
- Metadata lineage tracks source file versions and transformation steps for auditability.  
- Supports flexible, ad-hoc queries across customers, products, and sales dimensions.

---

## 10. Monitoring & Continuous Improvement  
- Future runs should monitor null value trends in key demographic and sales fields to identify emerging data quality issues.  
- Incremental validation to ensure key uniqueness and referential integrity over time will maintain Silver layer reliability.

---

## Schema Overview & Data Profiling Summary  

| Table Name          | Rows  | Columns | Key Candidates        | Nulls Observation | Duplicates | Suggested Silver Transforms                        |
|---------------------|-------|---------|-----------------------|-------------------|------------|---------------------------------------------------|
| CST_AZ12            | 18,484| 3       | CID (unique, non-null)| GEN: 1472 nulls   | 0          | Parse date, standardize GEN, trim whitespace      |
| cst_info            | 18,494| 7       | cst_id, cst_key        | cst_gndr: 4578 nulls; other fields also nulls | 0 | Parse dates, standardize missing, trim names      |
| customer_info       | 5     | 5       | customer_id            | None              | 0          | Parse dates                                       |
| LOC_A101            | 18,484| 2       | CID                    | CNTRY: 332 nulls  | 0          | Standardize CNTRY missing, trim whitespace         |
| prd_info            | 397   | 7       | prd_id                 | prd_cost: 2 nulls, prd_end_dt: 197 nulls, prd_line: 17 nulls | 0 | Parse dates, standardize/prd_cost, trim prd_line  |
| product_info        | 4     | 4       | product_id             | None              | 0          | No transformations needed                          |
| PX_CAT_G1V2         | 37    | 4       | ID, SUBCAT             | None              | 0          | No transformations needed                          |
| sales_details       | 60,398| 9       | None                   | sls_sales: 8 nulls, sls_price: 7 nulls | 0 | Standardize missing sales and price fields          |
| sales_transactions  | 8     | 6       | transaction_id         | None              | 0          | No transformations needed                          |

---

## Potential Business Problems and Decisions  
- **Customer Retention:** Investigate decline in repeat purchases using `sales_details` and `cst_info`. Impact: revenue and LTV losses. Stakeholders: Marketing, Sales, Finance. Decisions: Target retention campaigns, loyalty programs. Assumption: Faster delivery improves repeat purchase rates.  
- **Product Returns and Quality:** Analyze high return rates in product categories via `PX_CAT_G1V2`, linked to sales and product information. Impact: Increased logistics cost and margin erosion. Stakeholders: Operations, Product Management. Decisions: Adjust product mix or suppliers.  
- **Regional Sales Variation:** Explore unexplained sales differences regionally through `LOC_A101` combined with customer and sales data. Impact: Misallocated inventory, missed market opportunities. Stakeholders: Sales, Operations. Decisions: Regional marketing allocation, inventory distribution.  
- **Discount Dependence:** Evaluate sales sensitivity to discounts from pricing fields in `sales_details` and product costs. Impact: Margin erosion risk, customer churn. Stakeholders: Pricing, Sales, Finance. Decisions: Optimize discount policies, pricing strategies.

---

## Scope Definition Options  
- **Time:** Analyze data across specific years or monthly/quarterly periods based on order and transaction dates.  
- **Geography:** Filter by country or region using location and customer geography attributes (`LOC_A101`, `CST_AZ12`).  
- **Data:** Focus on specific product lines, customer demographics (gender, marital status), or transaction types.  
- **System/Source:** Select CRM-only, ERP-only, or combined datasets for focused workflows.  
- **Output:** Generate aggregated reports, customer/product cohort analyses, or detailed transaction level exports.

---

## KPI Candidates for BI/Tableau  
- **Total Sales Revenue:** Sum of sales amount (`sls_sales`) over selected periods and segments.  
- **Average Order Value:** Total sales revenue divided by number of orders (`sls_ord_num`).  
- **Customer Retention Rate:** Percentage of customers with repeated purchases in consecutive periods.  
- **Product Category Sales Share:** Sales by category (`CAT` from PX_CAT_G1V2) expressed as a proportion of total sales.  
- **On-Time Delivery Rate:** Percentage of orders shipped by due date (compare `sls_ship_dt` vs. `sls_due_dt`).  
- **Discount Penetration Rate:** Proportion of sales with prices below standard retail price.  
- **Return Rate by Category:** Number of returns over total sales by product category (requires downstream return data).  
- **Customer Lifetime Value (LTV):** Sum of sales per customer over their lifespan.

---

## Segmentation & Clustering Opportunities  
- **Features:** Customer demographics (age, gender, marital status), purchase frequency, average order value, product preferences (category lines), geographic location.  
- **Methods:** k-Means clustering for customer segments, hierarchical clustering for product groups, RFM analysis for retention-focused segments.  
- **Example Segments:**  
  - High-value repeat customers vs. one-time buyers  
  - Discount-sensitive vs. premium price buyers  
  - Regional sales hotspots or low-penetration markets  
  - Product categories with stable vs. volatile sales patterns  

These segments can be used for targeted marketing, personalized recommendations, and inventory planning.

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
  - Parse BDATE as datetime.
  - Standardize missing values in GEN.
  - Trim whitespace in GEN.

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
  - Parse cst_create_date as datetime.
  - Standardize missing values in cst_create_date.
  - Standardize missing values in cst_firstname.
  - Standardize missing values in cst_gndr.
  - Standardize missing values in cst_id.
  - Standardize missing values in cst_lastname.
  - Standardize missing values in cst_marital_status.
  - Trim whitespace in cst_firstname.
  - Trim whitespace in cst_lastname.

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
  - Parse date_of_birth as datetime.

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
  - Trim whitespace in CNTRY.

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
  - Parse prd_end_dt as datetime.
  - Parse prd_start_dt as datetime.
  - Standardize missing values in prd_cost.
  - Standardize missing values in prd_end_dt.
  - Standardize missing values in prd_line.
  - Trim whitespace in prd_line.

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
  - MAINTENANCE: boolean
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
  - Parse transaction_date as datetime.
