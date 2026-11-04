# YuvaIntern Week 3 — Data Integration and Transformation Report

**Project:** Apparel & Textiles Data Integration and Transformation  
**Prepared by:** Krishna Sahu  
**Role:** Junior Data Analyst — Apparel & Textiles  
**Tools:** Python, Pandas, NumPy, VS Code and GitHub

## 1. Executive Summary

This project demonstrates a reproducible workflow for preparing two apparel-related datasets for combined analysis. The first source contains retail purchase transactions, including customer references, purchased-item labels, sales amounts, dates, review ratings and payment methods. The second source is an H&M article catalogue containing product identifiers and descriptive attributes such as product names, product types, product groups and colours.

The workflow profiles both inputs, standardizes column names and data types, normalizes category labels, removes exact duplicate rows, preserves data-quality exceptions and joins transaction rows to a category-level product catalogue. It generates an integrated transaction table, a category catalogue, a product mapping file and data-quality reports.

A critical limitation is that the retail transaction source does not contain H&M article identifiers. A defensible exact SKU-to-article join is therefore not possible. This implementation uses transparent category-level reconciliation and does not claim that a retail item is the same physical H&M article. Unmatched transactions remain in the output.

## 2. Business Problem and Objectives

Retail businesses often store sales transactions and product catalogue information in separate systems. These systems may use different column names, category labels, identifiers and data types. Combining them without a clear integration process can lead to duplicated rows, incorrect totals and misleading analysis.

Objectives:
1. Select and document two public apparel-related datasets.
2. Explain differences in structure, format and data granularity.
3. Profile source data before transformation.
4. Standardize field names, text, dates and numeric data.
5. Create a common category taxonomy and mapping.
6. Integrate the sources while preserving transaction rows.
7. Detect and report duplicates, missing values and invalid records.
8. Validate the integrated output and document limitations.

## 3. Data Sources

### 3.1 Fashion Retail Sales

Source: https://www.kaggle.com/datasets/atharvasoundankar/fashion-retail-sales

This transaction-oriented CSV typically includes Customer Reference ID, Item Purchased, Purchase Amount (USD), Date Purchase, Review Rating and Payment Method. Its grain is a purchase record.

### 3.2 H&M Personalized Fashion Recommendations — Articles

Source: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations

The H&M `articles.csv` file is product-master data. Typical fields include article_id, prod_name, product_type_name, product_group_name and colour_group_name. Its grain is a product/article record rather than a purchase event.

### 3.3 Differences in source structures

| Aspect | Retail sales | H&M articles |
|---|---|---|
| Purpose | Record purchases | Describe products |
| Grain | Transaction | Article/product |
| Identifier | Customer reference; no H&M article ID | Article ID |
| Measures | Sales amount, rating | Product attributes |
| Date | Purchase date | No transaction date in article master |
| Product labels | Item Purchased | Product type/group |

The sources should not be appended row by row. A transaction table should be enriched through a documented product mapping or dimension.

## 4. Data Acquisition and Organization

Download the retail CSV as `Fashion_Retail_Sales.csv` and the H&M catalogue file as `articles.csv`. Place both in the project's `data/` folder. Kaggle account access and acceptance of competition rules may be required for H&M data.

Small synthetic sample CSVs are included to test the code. These are fictional demonstration records and must not be presented as real observations. Real source files take priority when present.

## 5. Data Profiling

The pipeline records source row and column counts. It also checks total missing cells and exact duplicate rows. Profiling helps identify schema differences and quality issues before transformation. It is important to distinguish missing values from labels that are merely written differently.

## 6. Cleaning and Transformation

### 6.1 Column-name standardization

Column labels are converted to lowercase snake_case. Spaces and punctuation are replaced with underscores, allowing consistent field references.

### 6.2 Numeric conversion

Sales amounts and ratings are converted to numeric values using safe conversion. Currency symbols and comma separators are removed from amount strings before conversion. Invalid values become missing and are reported.

### 6.3 Date conversion

Purchase dates are parsed into datetime values. Unparseable dates are flagged as missing/invalid. The pipeline does not guess unknown dates.

### 6.4 Text normalization

Text is trimmed to remove leading and trailing spaces. Payment method labels are converted to lowercase. Original item descriptions are retained so users can trace the standardized category back to the source label.

### 6.5 Category standardization

A controlled rule-based taxonomy maps related descriptions into categories such as tops, bottoms, one_piece, outerwear, footwear, accessories and innerwear. These rules can be extended after inspecting the full source vocabulary. Unknown labels are retained rather than forced into an unrelated category.

### 6.6 Duplicate handling

Only exact duplicate rows are removed. Two similar-looking purchase rows may represent two genuine transactions, so duplicates are not identified solely by customer, product or date. The number of exact duplicates removed is reported.

### 6.7 Missing values and unusual amounts

Missing or invalid amounts are retained and flagged. Negative amounts are flagged because they may represent returns, refunds or corrections. Ratings outside the expected 1–5 range are flagged. No arbitrary median imputation is applied to sales values because doing so would fabricate financial data.

## 7. Integration Workflow

1. Load the retail transaction CSV and H&M article CSV.
2. Profile row counts, columns, missing values and exact duplicates.
3. Standardize source column names.
4. Convert dates and numeric fields.
5. Normalize retail product labels and H&M product descriptions.
6. Remove exact duplicate rows and record the count.
7. Build a product catalogue with one row per normalized category.
8. Aggregate article metadata by category.
9. Perform a left join from retail transactions to the category catalogue.
10. Assign unique integration record IDs and match statuses.
11. Validate row counts, keys and data-quality indicators.
12. Export CSV and JSON outputs.

### Why aggregate the article catalogue first?

A category may contain many article records. Joining raw articles directly to transactions by category can multiply each transaction into multiple rows and inflate totals. The catalogue is therefore aggregated to one row per canonical category before joining. The article_count field indicates how many catalogue records contribute to each category.

## 8. Reconciliation Conflicts and Solutions

| Conflict | Solution |
|---|---|
| Different column names | Standardize to a common schema |
| Upper/lowercase differences | Normalize text case |
| Extra spaces and punctuation | Trim and clean labels |
| Different product category terms | Apply a controlled mapping taxonomy |
| Many articles per category | Aggregate to one category record before joining |
| No shared product ID | Use category-level mapping and disclose limitation |
| Unmatched categories | Retain transaction and flag it |
| Missing amount/date | Retain and report; do not fabricate |
| Negative amount | Flag for returns/adjustment review |
| Exact duplicate rows | Remove and report count |

## 9. Validation and Quality Assurance

The pipeline performs structural and field-level validation.

### Structural checks
- Integrated row count equals the cleaned retail row count.
- Integration record IDs are unique.
- Canonical category keys in the catalogue are unique.
- A many-to-one merge validation detects accidental row multiplication.

### Field-level checks
- Missing or invalid sales amounts.
- Negative sales amounts.
- Ratings outside the 1–5 range.
- Missing or invalid dates.
- Matched and unmatched category counts.

### Reconciliation checks
A left join preserves every cleaned retail transaction. An assertion catches unexpected row loss or multiplication. A category match indicates broad category compatibility only; it does not verify exact product identity.

### Audit outputs
Validation results are saved in both CSV and JSON formats. The mapping file records original item names and normalized categories, supporting traceability and review.

## 10. Generated Deliverables

- `integrated_apparel_transactions.csv` — integrated transaction-level table.
- `category_catalog.csv` — one record per normalized category.
- `product_mapping.csv` — original retail labels and canonical category.
- `data_quality_report.csv` — validation checks in tabular form.
- `data_quality_report.json` — machine-readable validation summary.

These files are generated after running the Python script. They are not pre-filled with invented analysis results.

## 11. Business Applications

The integrated data can support category-level sales summaries, product assortment coverage checks, customer purchase pattern analysis, identification of categories with weak catalogue coverage and preparation of a Power BI dashboard. Sales amount is not equivalent to profit. Margin, inventory, discounts, returns and taxes are needed for profitability analysis.

## 12. Challenges, Limitations and Future Improvements

The main challenge is the absence of a shared product identifier. Category mapping is approximate and depends on the quality of the rule set. A production solution should use a shared SKU/article ID, barcode or an approved crosswalk. The mapping should be reviewed by a domain expert and version-controlled.

The two sources may differ in currency, market, time period and field definitions. Financial comparisons should not be made until currency, taxes, discounts, returns and date semantics are harmonized. Future improvements include automated tests, schema contracts, logging, source checksums and a quarantine process for invalid records.

## 13. Conclusion

This project demonstrates a structured and reproducible data integration workflow for apparel retail. It combines transaction information with product catalogue metadata through transparent category-level reconciliation. It standardizes fields, handles duplicates, preserves exceptions, validates row counts and reports unmatched categories. The implementation avoids claiming exact product matches when the sources do not provide a common identifier.

## 14. References

1. Fashion Retail Sales dataset: https://www.kaggle.com/datasets/atharvasoundankar/fashion-retail-sales
2. H&M Personalized Fashion Recommendations: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
3. Reference learning repository: https://github.com/its-Kunal-fr/Apparel-Textiles-Data-Integration
4. Pandas documentation: https://pandas.pydata.org/docs/

## Appendix A — Run Instructions (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python data_integration.py
```

## Appendix B — Reproducibility

Run the included synthetic samples first to verify the workflow. For the internship analysis, download the actual source files, place them in `data/`, rerun the script and record the real source filenames, row counts, run date and validation results. Do not report sample-data outputs as results from the public datasets.
