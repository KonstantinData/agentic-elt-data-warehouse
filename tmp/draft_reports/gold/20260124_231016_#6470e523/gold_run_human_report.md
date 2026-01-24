# Phase-1 Gold Layer Design Report  
**Silver Run ID:** 20260124_231016_#6470e523

---

## 1. Executive Summary

- The Silver layer contains 9 clean, successfully processed tables covering sales, customers, products, locations, and categories with no errors.
- Data volumes vary widely: large sales details (~60k rows), customer and product master data in the low thousands or less.
- Key data quality issues identified include missing values in gender, country, product line, and sales price/sales amount fields, requiring standardization.
- The Gold layer will focus on building a robust BI foundation with conformed dimensions and fact tables to support sales and customer analytics.
- Emphasis on clear grain definition, surrogate keys, and handling missing values to ensure consistent, performant reporting.
- Early-stage Gold design excludes ML feature store or advanced analytics, focusing strictly on trusted, business-friendly data marts.

---

## 2. Available Silver Tables and Their Role

| Silver Table           | Role Description                                  |
|-----------------------|--------------------------------------------------|
| **sales_details.csv**  | Detailed transactional sales data (orders, quantities, prices, dates). Core fact table candidate. |
| **sales_transactions.csv** | Smaller transactional dataset with unit prices and quantities, possibly complementary or alternative sales data. |
| **cst_info.csv**       | Customer master data with demographics and status attributes. |
| **customer_info.csv**  | Small customer reference table, possibly a lookup or legacy source. |
| **CST_AZ12.csv**       | Customer demographic attributes (birthdate, gender). |
| **LOC_A101.csv**       | Customer location data (country). |
| **prd_info.csv**       | Product master data with cost, line, and lifecycle dates. |
| **product_info.csv**   | Product reference with category and pricing info. |
| **PX_CAT_G1V2.csv**    | Product category hierarchy and maintenance info. |

---

## 3. Proposed Gold-Layer Objectives

- Deliver a **conformed dimensional model** enabling consistent sales and customer analytics across the enterprise.
- Provide **cleaned, standardized master data** for customers, products, and locations with surrogate keys.
- Build **fact tables at transaction/order grain** to support detailed and aggregated sales reporting.
- Enable **time-aware analysis** by incorporating date dimensions and product lifecycle attributes.
- Ensure **data quality and completeness** by addressing missing values and standardizing key attributes.
- Facilitate **scalable and performant BI queries** through appropriate indexing and aggregation layers.

---

## 4. Recommended Gold Data Marts

### 4.1 Customer Dimension  
- **Business Purpose:** Centralized, clean customer master for analytics and reporting.  
- **Grain:** One row per customer (surrogate key).  
- **Primary Keys:** Surrogate Customer Key (SK_Customer).  
- **Attributes:** Customer ID, first/last name, gender (standardized), birthdate, marital status, create date, country (from LOC_A101), demographic flags.  
- **Notes:** Merge cst_info, CST_AZ12, LOC_A101, and customer_info to create a single, enriched customer dimension.

### 4.2 Product Dimension  
- **Business Purpose:** Product master with detailed attributes for sales analysis.  
- **Grain:** One row per product (surrogate key).  
- **Primary Keys:** Surrogate Product Key (SK_Product).  
- **Attributes:** Product ID, product name, category, subcategory, price, cost, product line, start/end dates, maintenance flags.  
- **Notes:** Combine prd_info, product_info, PX_CAT_G1V2 for a comprehensive product dimension.

### 4.3 Date Dimension  
- **Business Purpose:** Support time-based slicing of sales and customer activity.  
- **Grain:** One row per calendar date.  
- **Primary Keys:** Date Key (YYYYMMDD).  
- **Attributes:** Year, quarter, month, day, weekday, holiday flags, etc.  
- **Notes:** Populate from sales order, ship, due, and transaction dates.

### 4.4 Sales Fact Table  
- **Business Purpose:** Capture detailed sales transactions for revenue and volume analysis.  
- **Grain:** One row per sales order line (sls_ord_num + product + customer + date).  
- **Primary Keys:** Surrogate Fact Key or natural composite key (order number + product key).  
- **Measures:** Sales amount, quantity, price, discounts (if any), ship/due dates.  
- **Dimensions:** Customer, Product, Date (order, ship, due), Location (via customer).  
- **Notes:** Use sales_details.csv as primary source; consider sales_transactions.csv for validation or enrichment.

### 4.5 Aggregated Sales Mart (Optional Phase-1)  
- **Business Purpose:** Pre-aggregated sales summaries by product, customer segment, time period for faster BI queries.  
- **Grain:** Aggregated at chosen levels (e.g., product-month, customer-region-month).  
- **Measures:** Total sales, total quantity, average price.  
- **Dimensions:** Product, Customer, Date, Location.  
- **Notes:** Build after core dimensions and fact are stable.

---

## 5. Join and Data-Quality Considerations

- **Keys and Cardinalities:**  
  - Customer dimension keys: cst_id (high uniqueness but some nulls), CID from CST_AZ12 (string, unique). Need to resolve key conflicts and missing values.  
  - Product keys: prd_id and product_id both unique; reconcile and choose consistent surrogate key strategy.  
  - Sales fact keys: sls_ord_num unique per order line; join to customer and product via keys.  
- **Null and Missing Values:**  
  - Gender missing in ~25% of customers (cst_gndr). Standardize with "Unknown" or similar.  
  - Country missing in ~2% of LOC_A101 records. Impute or flag as unknown.  
  - Product line and end dates missing in prd_info; handle as open-ended or unknown.  
  - Sales price and sales amount missing in a few rows; exclude or impute carefully.  
- **Date Handling:**  
  - Sales dates in integer format (likely YYYYMMDD); convert to date dimension keys.  
  - Multiple date fields per sales record (order, ship, due) require careful modeling.  
- **Duplicates:** No duplicates detected, simplifying key management.  
- **Potential Pitfalls:**  
  - Small customer_info.csv (5 rows) may be legacy or incomplete; avoid mixing with main customer dimension without validation.  
  - Disparate keys across tables require robust key mapping and surrogate key generation.

---

## 6. Risks & Assumptions

- **Data Completeness:** Some tables have missing or sparse data (e.g., product_info only 4 rows vs. prd_info 397 rows). Assumed prd_info is primary product master.  
- **Key Consistency:** Assumed keys like cst_id and prd_id are stable and can be used for joins after cleaning.  
- **Data Quality:** Missing values and inconsistent attribute naming require standardization before Gold layer ingestion.  
- **Small Tables:** Very small tables (customer_info, sales_transactions) may not be representative or may require special handling.  
- **Temporal Validity:** Product start/end dates and customer create dates may require slowly changing dimension logic in future phases.  
- **No ML Features:** This phase excludes feature engineering or advanced analytics, focusing on BI-ready data only.

---

## 7. Recommended Next Steps for Implementation and Testing

1. **Silver-to-Gold Transformation Development:**  
   - Implement data cleaning and standardization for missing values as per Silver suggestions.  
   - Develop ETL pipelines to create surrogate keys and conformed dimensions.  
   - Build date dimension from all relevant date fields.

2. **Dimension Integration and Validation:**  
   - Merge customer-related tables into a single dimension; validate key uniqueness and completeness.  
   - Consolidate product-related tables similarly.

3. **Fact Table Construction:**  
   - Load sales_details as primary fact table; validate joins to dimensions.  
   - Investigate sales_transactions for potential enrichment or reconciliation.

4. **Data Quality and Consistency Checks:**  
   - Implement automated checks for nulls, duplicates, and referential integrity.  
   - Validate date conversions and time zone consistency.

5. **Performance Testing:**  
   - Test query performance on Gold data marts with representative BI queries.  
   - Optimize indexing and partitioning strategies as needed.

6. **Documentation and Business Validation:**  
   - Document Gold layer schema, grain, and business logic.  
   - Engage business users for validation of dimension attributes and fact measures.

7. **Plan for Phase-2 Enhancements:**  
   - Prepare for slowly changing dimensions, additional aggregates, and eventual ML feature store integration.

---

This design provides a pragmatic, business-friendly foundation for trusted sales and customer analytics, enabling scalable BI reporting and decision support.