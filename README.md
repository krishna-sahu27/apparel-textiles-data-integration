# Apparel & Textiles Data Integration and Transformation

**Internship:** YuvaIntern — Junior Data Analyst (Apparel & Textiles)  
**Week:** 3  
**Prepared by:** Krishna Sahu  
**Tools:** Python, Pandas, NumPy, VS Code and GitHub

## Project objective

Integrate a fashion retail transaction dataset with a separate apparel product catalogue. The workflow demonstrates data profiling, cleaning, standardization, transformation, category mapping, joining, validation and quality reporting.

## Public data sources

1. **Fashion Retail Sales:** https://www.kaggle.com/datasets/atharvasoundankar/fashion-retail-sales  
   Typical fields: Customer Reference ID, Item Purchased, Purchase Amount (USD), Date Purchase, Review Rating and Payment Method.
2. **H&M Personalized Fashion Recommendations — Articles:** https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations  
   The `articles.csv` file contains article IDs and product attributes such as product type, product group, product name and colour.

Kaggle account access and acceptance of competition rules may be required for the H&M source.

## Important integration limitation

The retail transaction source does not contain H&M article IDs or a shared SKU. Therefore, this project performs **category-level reconciliation only**, not exact product/SKU matching. Category similarity does not prove that two records describe the same physical item. Unmatched transactions are preserved and labelled. Do not interpret category matches as verified H&M product sales.

## Folder structure

```
apparel-textiles-data-integration/
├── data/
│   ├── sample_fashion_retail_sales.csv
│   └── sample_hm_articles.csv
├── output/
├── data_integration.py
├── requirements.txt
├── README.md
└── REPORT.md
```

## Run in VS Code on Windows

Open this repository folder in VS Code. Open Terminal → New Terminal and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python data_integration.py
```

The script first looks for the real files `data/Fashion_Retail_Sales.csv` and `data/articles.csv`. If they are not present, it uses the included synthetic sample CSVs so you can test the workflow immediately. The sample data is fictional and is not the original public dataset.

## Outputs

After execution, the `output/` folder contains:

- `integrated_apparel_transactions.csv` — retail transactions enriched with category-level catalogue metadata.
- `category_catalog.csv` — one row per canonical category.
- `product_mapping.csv` — original retail item labels mapped to standardized categories.
- `data_quality_report.csv` and `data_quality_report.json` — validation results.

## Methods

- Standardize source column names to lowercase snake_case.
- Trim text and normalize payment-method case.
- Convert sales and ratings to numeric values; parse dates.
- Normalize product labels to a common category taxonomy.
- Remove exact duplicate rows only.
- Retain and flag missing/invalid amounts, negative amounts, invalid ratings and dates.
- Aggregate the article catalogue to one row per category before joining to prevent row multiplication.
- Use a left join and assert that the transaction row count is preserved.
- Report matched and unmatched categories.

## Data handling and limitations

Missing amounts and dates are not fabricated. Negative amounts may represent returns or adjustments and should be investigated. Exact product-level matching requires a shared article/SKU identifier or an approved crosswalk. Currency, tax, discount, returns and time-period definitions must be reconciled before comparing financial totals. Respect dataset licences and Kaggle terms; do not commit restricted raw datasets or personal data.

## Reference implementation for learning

https://github.com/its-Kunal-fr/Apparel-Textiles-Data-Integration

This project is independently implemented and explicitly documents the limits of category-level matching.
