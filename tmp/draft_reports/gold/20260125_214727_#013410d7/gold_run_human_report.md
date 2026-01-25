# Phase-1 Gold Layer Design Report  
Silver Run ID: 20260125_214727_#013410d7

---

## 1. Executive Summary

- The Silver layer contains 9 clean and successfully processed tables covering sales, customers, products, locations, and categories.
- Data volumes vary significantly, with sales_details as the largest fact-like table (~60k rows) and several small reference tables.
- The Gold layer will focus on delivering a robust BI and analytics foundation, emphasizing conformed dimensions and a sales fact.
- Proposed Gold Data Marts include Customer, Product, Location, Category dimensions, and a Sales Fact table at the transaction/order line grain.
- Key challenges include aligning multiple customer and product identifiers, handling missing values, and ensuring consistent date/time formats.
- Next steps involve defining transformation rules, key mappings, and validation tests to ensure data quality and usability.

---

## 2. Available Silver Tables and Their Role

| Table Name           | Role / Domain                         | Notes on Content & Volume                      |
|----------------------|-------------------------------------|-----------------------------------------------|
| **sales_details.csv** | Sales fact (order line details)     | 60,398 rows; detailed sales transactions with quantities, prices, and dates. |
| **sales_transactions.csv** | Sales fact (transaction header) | 8 rows; possibly high-level transactions, less detailed than sales_details. |
| **cst_info.csv**      | Customer master data                 | ~18,494 rows; detailed customer attributes including demographics and status. |
| **CST_AZ12.csv**      | Customer demographic info            | ~18,484 rows; includes birthdate and gender, linked by customer ID. |
| **customer_info.csv** | Small customer reference table       | 5 rows; limited scope, possibly a lookup or test data. |
| **prd_info.csv**      | Product master data                  | 397 rows; product attributes including cost, line, and lifecycle dates. |
| **product_info.csv**  | Product reference info               | 4 rows; likely high-level product categories or sample data. |
| **LOC_A101.csv**      | Customer location data               | 18,484 rows; country-level location info linked by customer ID. |
| **PX_CAT_G1V2.csv**   | Product category hierarchy           | 37 rows; category and subcategory with maintenance flag. |

---

## 3. Proposed Gold-Layer Objectives

- **Deliver conformed, clean, and integrated dimensions** for Customers, Products, Locations, and Categories to enable consistent reporting.
- **Create a comprehensive Sales Fact table** at the order line grain combining sales details with customer and product dimensions.
- **Support key BI use cases** such as sales performance analysis, customer segmentation, product profitability, and geographic sales distribution.
- **Ensure data quality and consistency** by resolving identifier mismatches, standardizing date/time fields, and handling missing values.
- **Provide a scalable foundation** for future phases, including advanced analytics and potential ML feature stores.

---

## 4. Recommended Gold Data Marts

### 4.1 Customer Dimension  
- **Business Purpose:** Provide a unified view of customer attributes for segmentation and demographic analysis.  
- **Grain:** One row per unique customer (using a stable customer key).  
- **Primary Keys:** `cst_id` (from cst_info), reconciled with `CID` (from CST_AZ12 and LOC_A101).  
- **Main Attributes:** First and last names, gender, birthdate, marital status, create date, country.  
- **Notes:** Merge demographic and location info; handle missing gender and country values carefully.

### 4.2 Product Dimension  
- **Business Purpose:** Describe products for sales and profitability analysis.  
- **Grain:** One row per unique product.  
- **Primary Keys:** `prd_id` (from prd_info), linked to `product_id` (from product_info).  
- **Main Attributes:** Product name, category, cost, price, product line, lifecycle dates.  
- **Notes:** Integrate category info from PX_CAT_G1V2; standardize missing cost and line data.

### 4.3 Location Dimension  
- **Business Purpose:** Enable geographic analysis of customers and sales.  
- **Grain:** One row per unique location (country-level).  
- **Primary Keys:** Country code or name (`CNTRY` from LOC_A101).  
- **Main Attributes:** Country name, region (if derivable), other geographic attributes if available.  
- **Notes:** Address missing country values; consider enriching with external geo data later.

### 4.4 Category Dimension  
- **Business Purpose:** Provide product category hierarchy for drill-down and roll-up in reports.  
- **Grain:** One row per unique category/subcategory.  
- **Primary Keys:** `ID` from PX_CAT_G1V2.  
- **Main Attributes:** Category, subcategory, maintenance flag.  
- **Notes:** Ensure category keys align with product dimension.

### 4.5 Sales Fact Table  
- **Business Purpose:** Capture detailed sales transactions for revenue, quantity, and price analytics.  
- **Grain:** One row per sales order line (`sls_ord_num` + product + customer).  
- **Primary Keys:** Composite key of sales order number and product key.  
- **Measures:** Sales amount, quantity sold, price, shipping and due dates.  
- **Dimensions:** Customer, Product, Date (order, ship, due), Location (via customer).  
- **Notes:** Convert integer date fields to datetime; handle missing sales and price values.

---

## 5. Join and Data-Quality Considerations

- **Customer Keys:** Multiple customer IDs (`cst_id`, `CID`, `customer_id`) require reconciliation and mapping to a single conformed key.  
- **Product Keys:** Align `prd_id`, `prd_key`, and `product_id` across product tables; ensure category linkage is consistent.  
- **Date Fields:** Several date fields are integers (likely YYYYMMDD); must be parsed and standardized to datetime.  
- **Missing Values:** Address nulls in gender, country, product cost, sales price, and sales amount to avoid analytic bias.  
- **Cardinalities:**  
  - Customers to sales: one-to-many  
  - Products to sales: one-to-many  
  - Categories to products: one-to-many  
  - Locations to customers: one-to-one or one-to-many (depending on granularity)  
- **Potential Pitfalls:**  
  - Small `customer_info.csv` and `product_info.csv` tables may not be representative or complete; verify their role.  
  - Duplicate or inconsistent customer and product keys could cause join errors or data duplication.  
  - Sparse sales_transactions.csv (8 rows) suggests it may be a sample or summary table; clarify its role before integration.

---

## 6. Risks & Assumptions

- **Incomplete or inconsistent keys:** Assumes that customer and product keys can be reliably mapped across tables.  
- **Data freshness and completeness:** Silver layer shows no errors but some tables have very low row counts (e.g., customer_info.csv), which may limit coverage.  
- **Date parsing correctness:** Integer date fields must be correctly interpreted; errors here can propagate to all time-based analytics.  
- **Missing value handling:** Assumes missing values can be standardized or imputed without introducing bias.  
- **Limited location granularity:** Location data is at country level only; finer granularity may be needed for some analyses.  
- **Sales_transactions.csv role unclear:** Its small size and overlap with sales_details.csv require clarification to avoid redundancy.

---

## 7. Recommended Next Steps for Implementation and Testing

1. **Define and document key reconciliation logic** for customers and products to establish conformed dimension keys.  
2. **Implement Silver-to-Gold transformations:**  
   - Parse and standardize date fields.  
   - Clean and impute missing demographic and product attributes.  
   - Trim and standardize string fields.  
3. **Build dimension tables** with surrogate keys and conformed attributes.  
4. **Construct the Sales Fact table** at order line grain, linking to dimension keys and including measures.  
5. **Develop data quality tests:**  
   - Uniqueness and completeness of keys.  
   - Referential integrity between facts and dimensions.  
   - Validation of date conversions and missing value handling.  
6. **Engage business stakeholders** to validate dimension attributes and fact measures for BI relevance.  
7. **Prepare documentation and metadata** for Gold layer datasets to facilitate BI tool integration.  
8. **Plan incremental refresh and monitoring** for ongoing data quality and performance.

---

This design provides a clear, pragmatic foundation for Phase-1 Gold layer implementation, enabling reliable BI and analytics while setting the stage for future enhancements.