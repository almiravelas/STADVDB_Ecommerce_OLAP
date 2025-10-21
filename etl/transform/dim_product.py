import pandas as pd
import numpy as np
from .utils import parse_date_formats

def transform_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans, standardizes, and re-aligns product data for the dimension table."""
    if df is None or df.empty:
        print("No data to transform for dim_product.")
        return None

    # --- Rename columns ---
    df = df.rename(columns={
        "ID": "product_key",
        "Name": "product_name",
        "Category": "category",
        "ProductCode": "product_code",
        "Price": "price",
        "CreatedAt": "created_at",
        "UpdatedAt": "updated_at"
    })

    # --- Clean whitespace ---
    text_cols = ["product_name", "category", "product_code"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # --- Handle duplicates ---
    df["non_null_count"] = df.notna().sum(axis=1)
    df = (
        df.sort_values(by=["product_code", "non_null_count", "updated_at"], ascending=[True, False, False])
        .drop_duplicates(subset=["product_code"], keep="first")
        .drop(columns=["non_null_count"])
    )

    # --- Normalize category names ---
    df["category"] = df["category"].astype(str).str.strip().str.title()
    category_mapping = {
        "Gadgets": "Electronics",
        "Laptops": "Electronics",
        "Appliances": "Electronics",
        "Toy": "Toys",
        "Bag": "Bags",
        "Make Up": "Makeup",
        "Makeup": "Makeup",
        "Men'S Apparel": "Clothing",
        "Clothes": "Clothing"
    }
    df["category"] = df["category"].replace(category_mapping)
    df["category"] = df["category"].replace("", np.nan)

    # --- Infer correct category based on product name ---
    def infer_category(name: str) -> str:
        if not isinstance(name, str):
            return "Uncategorized"

        name_lower = name.lower()

        if any(x in name_lower for x in ["shoe", "shirt", "pants", "dress", "clothes", "apparel", "jacket", "jeans", "sneaker", "sneakers", "skirt", "gloves", "hat", "coat", "suit", "t-shirt", "shorts", "socks", "scarf"]):
            return "Clothing"
        elif any(x in name_lower for x in ["phone", "laptop", "tablet", "charger", "earphone", "headphone", "tv", "camera", "microwave", "fridge", "television", "computer", "console", "smartwatch", "speaker", "monitor", "keyboard", "mouse"]):
            return "Electronics"
        elif any(x in name_lower for x in ["toy", "lego", "doll", "figure", "puzzle", "game", "board game", "action figure", "plush", "stuffed animal", "bike", "car", "ball", "chair", "soap", "table"]):
            return "Toys"
        elif any(x in name_lower for x in ["watch", "ring", "bracelet", "necklace", "earring", "jewelry", "towels"]):
            return "Clothing"  # Accessories → Clothing
        elif any(x in name_lower for x in ["bacon", "cheese", "sausage", "fish", "chicken", "bread", "beef", "egg", "chips", "soda", "snack", "candy", "cookie", "cake", "dessert", "salad", "pizza", "fish", "tuna"]):
            return "Toys"  # Food → Toys
        else:
            return "Uncategorized"

    # --- Apply category inference for all rows ---
    df["inferred_category"] = df["product_name"].apply(infer_category)

    # Always prioritize inferred category if it’s meaningful
    df["category"] = np.where(
        df["inferred_category"] != "Uncategorized",
        df["inferred_category"],
        df["category"]
    )

    df = df.drop(columns=["inferred_category"])

    # --- Final normalization to allowed categories ---
    allowed_categories = ["Electronics", "Toys", "Bags", "Makeup", "Clothing"]
    df["category"] = df["category"].apply(
        lambda c: c if c in allowed_categories else "Uncategorized"
    )

    # --- Convert numeric and datetime fields ---
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

    # --- Final clean-up ---
    df = df.drop_duplicates(subset=["product_code"], keep="first")
    df = df[df["product_name"].notna() & (df["product_name"].str.len() > 1)]
    df["category"] = df["category"].fillna("Uncategorized")
    df = df.sort_values(by="product_key").reset_index(drop=True)

    return df
