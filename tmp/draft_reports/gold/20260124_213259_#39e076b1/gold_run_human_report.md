# Phase-1 Gold Layer Design Report  
**Silver Run ID:** 20260124_213259_#39e076b1  

---

## 1. Executive Summary  
- The Silver layer contains 9 clean, successfully processed tables covering sales, customer, product, location, and category data domains.  
- Data volumes vary widely: large transactional tables (60k+ rows) and small reference tables (4-37 rows).  
- Several Silver tables require standardization of missing values before Gold layer consumption.  
- The Gold layer will focus on delivering curated, integrated data marts optimized for BI and analytics, excluding ML feature store concerns at this stage.  
- Proposed Gold data marts include core dimensions (Customer, Product, Location, Category) and a Sales fact table at the transaction/order line grain.  
- Key challenges include reconciling multiple customer and product tables, handling missing values, and ensuring consistent keys for joins.  

---

## 2. Available Silver Tables and Their Role  

| Table Name           | Rows  | Role / Domain                 | Notes on Content & Quality                         |
|----------------------|-------|------------------------------|---------------------------------------------------|
| **sales_details.csv** | 60,398| Sales fact (order lines)      | Detailed sales info with order, product, customer keys; some missing sales/price values. |
| **sales_transactions.csv** | 8   | Sales fact (transactions)     | Sparse transactional data; possibly summary or sample data. |
| **cst_info.csv**      | 18,494| Customer master data          | Rich customer attributes; some missing values in key fields. |
| **CST_AZ12.csv**      | 18,484| Customer demographics         | Contains birthdate, gender; missing gender values present. |
| **customer_info.csv** | 5     | Customer reference            | Very small, possibly lookup or test data; fully populated. |
| **prd_info.csv**      | 397   | Product master data           | Product details with cost, lifecycle dates; some missing cost and line info. |
| **product_info.csv**  | 4     | Product reference             | Small, clean product data; possibly category or pricing reference. |
| **LOC_A101.csv**      | 18,484| Customer location             | Country info per customer; some missing country values. |
| **PX_CAT_G1V2.csv**   | 37    | Product category hierarchy    | Category and subcategory info; clean data. |

---

## 3. Proposed Gold-layer Objectives  
- **Integrate and harmonize** customer and product data from multiple Silver sources to create consistent, enriched dimension tables.  
- **Create a comprehensive Sales fact table** at the order line grain, combining sales details with customer, product, and location dimensions.  
- **Support key BI use cases** such as sales performance analysis, customer segmentation, product profitability, and geographic sales distribution.  
- **Ensure data quality and consistency** by addressing missing values and standardizing keys for reliable joins.  
- **Provide a foundation for incremental enhancements** in future phases, including aggregates and wider denormalized views.  

---

## 4. Recommended Gold Data Marts  

### 4.1 Customer Dimension  
- **Business Purpose:** Provide a unified, enriched view of customers for segmentation and analysis.  
- **Grain:** One row per customer.  
- **Primary Key:** Surrogate Customer_ID (mapped from cst_id / CID / customer_id).  
- **Main Attributes:** Name, gender, birthdate, marital status, create date, country (from LOC_A101), demographic attributes (from CST_AZ12).  
- **Notes:** Resolve duplicates and missing values; standardize gender and dates.  

### 4.2 Product Dimension  
- **Business Purpose:** Describe products with attributes for sales and profitability analysis.  
- **Grain:** One row per product.  
- **Primary Key:** Surrogate Product_ID (mapped from prd_id / product_id).  
- **Main Attributes:** Product name, category, subcategory (from PX_CAT_G1V2), cost, price, product line, lifecycle dates.  
- **Notes:** Harmonize product references; fill missing cost and line info; link categories.  

### 4.3 Location Dimension  
- **Business Purpose:** Capture customer geographic info for regional sales analysis.  
- **Grain:** One row per customer location.  
- **Primary Key:** Customer_ID (linked to Customer Dimension).  
- **Main Attributes:** Country, possibly extended with region or city in future phases.  
- **Notes:** Standardize missing country values; consider country code normalization.  

### 4.4 Category Dimension  
- **Business Purpose:** Support product categorization and hierarchical analysis.  
- **Grain:** One row per category/subcategory.  
- **Primary Key:** Category_ID (from PX_CAT_G1V2 ID).  
- **Main Attributes:** Category, subcategory, maintenance flags.  

### 4.5 Sales Fact Table  
- **Business Purpose:** Capture detailed sales transactions for revenue and volume analysis.  
- **Grain:** One row per sales order line (sls_ord_num + sls_prd_key).  
- **Primary Key:** Composite key of sales order number and product key.  
- **Measures:** Sales amount, quantity, price, shipping and due dates.  
- **Dimensions:** Customer_ID, Product_ID, Date (order, ship, due), Location (via customer).  
- **Notes:** Address missing sales and price values; convert integer dates to datetime.  

### 4.6 Optional Wide Sales View (Denormalized)  
- **Business Purpose:** Simplify BI queries by combining fact and dimension attributes.  
- **Grain:** Same as Sales Fact.  
- **Content:** Sales measures plus customer, product, category, and location attributes.  
- **Notes:** Useful for self-service BI tools; refresh frequency to be balanced with performance.  

---

## 5. Join and Data-Quality Considerations  

- **Keys & Cardinalities:**  
  - Customer keys vary: cst_id (integer), CID (string), customer_id (integer). Need mapping and deduplication.  
  - Product keys: prd_id, product_id, prd_key; must be reconciled.  
  - Sales details link to customers and products via sls_cust_id and sls_prd_key (string/integer mismatch to resolve).  
- **Potential Pitfalls:**  
  - Missing values in key dimension attributes (gender, country, product line) may impact join completeness and filtering.  
  - Date fields in sales_details are integers, likely encoded dates; conversion needed for analytics.  
  - Small tables like customer_info.csv and product_info.csv may be incomplete or test data; verify relevance.  
  - Duplicate or near-duplicate customer records require careful consolidation to avoid double counting.  
- **Data Quality Actions:**  
  - Standardize missing values as per Silver suggestions before Gold ingestion.  
  - Validate and enforce surrogate keys in dimensions to ensure referential integrity.  
  - Implement data profiling and monitoring for key columns post-Gold load.  

---

## 6. Risks & Assumptions  

- **Risks:**  
  - Incomplete or inconsistent customer and product keys may cause join failures or data duplication.  
  - Missing or null values in critical attributes could degrade BI insights or require imputation strategies.  
  - Small reference tables with very few rows may not represent full business entities, risking incomplete dimensions.  
  - Date fields stored as integers may have ambiguous formats, requiring clarification.  
- **Assumptions:**  
  - Silver layer transformations to standardize missing values will be completed prior to Gold layer processing.  
  - The Silver layer tables represent the latest and most accurate data snapshot.  
  - Business definitions of customers, products, and sales align with the Silver-layer schema and keys.  
  - Additional metadata or business rules will be provided for key reconciliation if needed.  

---

## 7. Recommended Next Steps for Implementation and Testing  

1. **Data Preparation:**  
   - Apply Silver-layer suggested transformations to standardize missing values and clean key columns.  
   - Validate and harmonize keys across customer and product tables; define surrogate key generation logic.  

2. **Dimension Development:**  
   - Build Customer, Product, Location, and Category dimensions with surrogate keys and enriched attributes.  
   - Implement data quality checks on dimension completeness and uniqueness.  

3. **Fact Table Construction:**  
   - Develop Sales fact table at order line grain, joining cleaned dimensions.  
   - Convert integer date fields to datetime format; handle missing sales and price values.  

4. **Testing & Validation:**  
   - Perform row counts, key uniqueness, and referential integrity tests.  
   - Validate BI queries against known business metrics for accuracy.  
   - Conduct performance testing for query responsiveness on Gold data marts.  

5. **Documentation & Handover:**  
   - Document data lineage from Silver to Gold layer.  
   - Provide clear data dictionary and usage guidelines for BI teams.  

6. **Plan for Phase-2:**  
   - Identify opportunities for aggregates, wide tables, and incremental refresh strategies.  
   - Prepare for integration of additional data sources or ML feature store in future phases.  

---

This design provides a pragmatic, business-focused foundation for the Gold layer, enabling reliable and insightful BI reporting while maintaining flexibility for future enhancements.