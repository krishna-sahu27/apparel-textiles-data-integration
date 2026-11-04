"""
YuvaIntern Week 3: Apparel & Textiles Data Integration.
Author: Krishna Sahu

Integrates retail transactions with H&M article metadata using a transparent
category-level mapping. The source datasets do not share a product/SKU key,
so this script does NOT claim exact product-level matches.
"""
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

RETAIL_FILES = ["Fashion_Retail_Sales.csv", "sample_fashion_retail_sales.csv"]
ARTICLE_FILES = ["articles.csv", "HnM_Articles.csv", "sample_hm_articles.csv"]

def locate_file(names, label):
    for name in names:
        path = DATA / name
        if path.exists():
            print(f"[LOAD] {label}: {path}")
            return path
    raise FileNotFoundError(
        f"{label} file not found in {DATA}. Expected one of: {', '.join(names)}"
    )

def read_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1", low_memory=False)

def clean_columns(df):
    df = df.copy()
    df.columns = [
        re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_")
        for c in df.columns
    ]
    return df

def find_column(df, candidates, required=True):
    for col in candidates:
        if col in df.columns:
            return col
    if required:
        raise ValueError(
            f"Missing required column. Expected one of {candidates}; "
            f"available columns: {list(df.columns)}"
        )
    return None

def category(value):
    if pd.isna(value):
        return "unknown"
    value = re.sub(r"[^a-z0-9 ]", " ", str(value).lower())
    value = re.sub(r"\s+", " ", value).strip()
    rules = [
        (r"t.?shirt|tee shirt|blouse|shirt|top|hoodie|sweatshirt|sweater|cardigan", "tops"),
        (r"jean|trouser|pant|legging|short|skirt", "bottoms"),
        (r"dress|gown|jumpsuit|playsuit", "one_piece"),
        (r"coat|jacket|blazer|parka", "outerwear"),
        (r"shoe|boot|sandal|sneaker|trainer", "footwear"),
        (r"bag|backpack|purse|hat|cap|scarf|belt|glove|sock", "accessories"),
        (r"underwear|bra|brief|lingerie|swimwear|bikini", "innerwear"),
    ]
    for pattern, label in rules:
        if re.search(pattern, value):
            return label
    return value.replace(" ", "_") if value else "unknown"

def prepare_retail(raw):
    df = clean_columns(raw)
    customer = find_column(df, ["customer_reference_id", "customer_id"], False)
    item = find_column(df, ["item_purchased", "product_name", "product"])
    amount = find_column(df, ["purchase_amount_usd", "sales_amount_usd",
                              "purchase_amount", "amount"])
    date = find_column(df, ["date_purchase", "transaction_date", "date"], False)
    rating = find_column(df, ["review_rating", "rating"], False)
    payment = find_column(df, ["payment_method", "payment_type"], False)

    out = pd.DataFrame(index=df.index)
    out["source_customer_id"] = (
        df[customer].astype("string").str.strip() if customer else pd.NA
    )
    out["source_product_name"] = df[item].astype("string").str.strip()
    out["sales_amount_usd"] = pd.to_numeric(
        df[amount].astype("string").str.replace(r"[$,]", "", regex=True),
        errors="coerce"
    )
    out["transaction_date"] = (
        pd.to_datetime(df[date], errors="coerce") if date else pd.NaT
    )
    out["review_rating"] = (
        pd.to_numeric(df[rating], errors="coerce") if rating else pd.NA
    )
    out["payment_method"] = (
        df[payment].astype("string").str.strip().str.lower()
        if payment else "not_provided"
    )
    out["canonical_category"] = out["source_product_name"].map(category)
    out["source_row_number"] = range(2, len(out) + 2)
    return out

def prepare_articles(raw):
    df = clean_columns(raw)
    article_id = find_column(df, ["article_id", "product_id", "sku"], False)
    product_type = find_column(df, ["product_type_name", "product_type"], False)
    product_group = find_column(df, ["product_group_name", "product_group"], False)
    name = find_column(df, ["prod_name", "product_name", "product"], False)
    if not any([product_type, product_group, name]):
        raise ValueError("Article file needs a product type, group, or name column.")

    out = pd.DataFrame(index=df.index)
    out["source_article_id"] = (
        df[article_id].astype("string") if article_id else pd.NA
    )
    out["article_name"] = (
        df[name].astype("string").str.strip() if name else pd.NA
    )
    out["product_type"] = (
        df[product_type].astype("string").str.strip() if product_type else pd.NA
    )
    out["product_group"] = (
        df[product_group].astype("string").str.strip() if product_group else pd.NA
    )
    basis = out["product_type"].fillna(out["article_name"]).fillna(out["product_group"])
    out["canonical_category"] = basis.map(category)
    return out

def main():
    retail_path = locate_file(RETAIL_FILES, "Retail sales")
    articles_path = locate_file(ARTICLE_FILES, "H&M articles")
    retail_raw, articles_raw = read_csv(retail_path), read_csv(articles_path)

    print("Retail source:", retail_raw.shape, "Articles source:", articles_raw.shape)
    retail = prepare_retail(retail_raw)
    articles = prepare_articles(articles_raw)

    retail_before = len(retail)
    retail = retail.drop_duplicates().copy()
    articles = articles.drop_duplicates().copy()

    retail["amount_status"] = retail["sales_amount_usd"].apply(
        lambda x: "missing_or_invalid" if pd.isna(x) else
        ("negative_review" if x < 0 else "valid")
    )
    retail["rating_status"] = retail["review_rating"].apply(
        lambda x: "not_available" if pd.isna(x) else
        ("valid" if 1 <= x <= 5 else "out_of_range")
    )
    retail["date_status"] = retail["transaction_date"].apply(
        lambda x: "missing_or_invalid" if pd.isna(x) else "valid"
    )

    # One catalogue row per category prevents a many-to-many join and row inflation.
    article_categories = articles[articles["canonical_category"] != "unknown"]
    catalogue = article_categories.groupby("canonical_category", as_index=False).agg(
        article_count=("canonical_category", "size"),
        example_article=("article_name", "first"),
        example_product_type=("product_type", "first"),
        example_product_group=("product_group", "first")
    )

    integrated = retail.merge(
        catalogue, on="canonical_category", how="left", validate="many_to_one"
    )
    integrated["catalog_match"] = integrated["article_count"].notna().map(
        {True: "matched_category", False: "unmatched_category"}
    )
    integrated.insert(
        0, "integration_record_id",
        [f"INT_{i:07d}" for i in range(1, len(integrated) + 1)]
    )

    mapping = retail[["source_product_name", "canonical_category"]].drop_duplicates()
    mapping = mapping.sort_values("source_product_name").reset_index(drop=True)
    mapping.insert(0, "master_category_id",
                   [f"CAT_{i:04d}" for i in range(1, len(mapping) + 1)])

    checks = {
        "retail_input_rows": int(len(retail_raw)),
        "retail_rows_after_exact_deduplication": int(len(retail)),
        "exact_duplicate_rows_removed": int(retail_before - len(retail)),
        "article_input_rows": int(len(articles_raw)),
        "article_rows_after_exact_deduplication": int(len(articles)),
        "integrated_rows": int(len(integrated)),
        "row_count_preserved": bool(len(integrated) == len(retail)),
        "duplicate_integration_ids": int(integrated["integration_record_id"].duplicated().sum()),
        "missing_or_invalid_amounts": int(integrated["sales_amount_usd"].isna().sum()),
        "negative_amounts": int((integrated["sales_amount_usd"] < 0).sum()),
        "invalid_ratings": int((integrated["rating_status"] == "out_of_range").sum()),
        "invalid_dates": int(integrated["transaction_date"].isna().sum()),
        "matched_category_rows": int((integrated["catalog_match"] == "matched_category").sum()),
        "unmatched_category_rows": int((integrated["catalog_match"] == "unmatched_category").sum()),
        "duplicate_catalogue_categories": int(catalogue["canonical_category"].duplicated().sum())
    }

    assert checks["row_count_preserved"], "Join changed transaction row count."
    assert checks["duplicate_integration_ids"] == 0, "Integration IDs are not unique."
    assert checks["duplicate_catalogue_categories"] == 0, "Catalogue keys are not unique."

    integrated.to_csv(OUTPUT / "integrated_apparel_transactions.csv", index=False)
    catalogue.to_csv(OUTPUT / "category_catalog.csv", index=False)
    mapping.to_csv(OUTPUT / "product_mapping.csv", index=False)
    pd.DataFrame([{"check": k, "result": v} for k, v in checks.items()]).to_csv(
        OUTPUT / "data_quality_report.csv", index=False
    )
    (OUTPUT / "data_quality_report.json").write_text(
        json.dumps(checks, indent=2), encoding="utf-8"
    )

    print("\nVALIDATION SUMMARY")
    for key, value in checks.items():
        print(f"{key}: {value}")
    print("\nPipeline completed. Output directory:", OUTPUT)
    print("Note: category-level mapping is not exact SKU/article matching.")

if __name__ == "__main__":
    main()
