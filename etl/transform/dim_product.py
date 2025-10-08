import pandas as pd
from .utils import parse_date_formats

def transform_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans, standardizes, and re-aligns product data for the dimension table."""
    if df is None or df.empty:
        print("No data to transform for dim_product.")
        return None

    # Rename columns for consistency
    df = df.rename(columns={
        "ID": "product_key",
        "Name": "product_name",
        "Category": "category",
        "Description": "description",
        "ProductCode": "product_code",
        "Price": "price",
        "CreatedAt": "created_at",
        "UpdatedAt": "updated_at"
    })

    # --- 🔧 Fix misalignment: group by product_code to ensure consistent rows ---
    # If there are duplicated product codes with mismatched info, keep the most complete one
    df = (
        df.sort_values(by=["product_code", "updated_at"], ascending=[True, False])
        .groupby("product_code", as_index=False)
        .first()
    )

    # Handle capitalization inconsistencies
    df["category"] = df["category"].astype(str).str.strip().str.title()

    # Standardize categories with known duplicates
    category_mapping = {
        "Gadgets": "Electronics",
        "Toy": "Toys",
        "Toys": "Toys",
        "Bag": "Bags",
        "Make Up": "Makeup",
        "Makeup": "Makeup",
        "Men'S Apparel": "Men's Apparel",  # fix title() apostrophe issue
        "Clothes": "Clothing"
    }

    df["category"] = df["category"].replace(category_mapping)

    # Fill missing or blank categories
    df["category"] = df["category"].replace("", "Uncategorized").fillna("Uncategorized")

    # Handle missing descriptions
    df["description"] = df["description"].replace("", "No description available").fillna("No description available")

    # Ensure price is numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Convert timestamps to datetime
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

    # Remove any remaining duplicates
    df = df.drop_duplicates(subset=["product_code"], keep="last")

    # Optional: Sort for readability
    df = df.sort_values(by="product_key")

    return df
