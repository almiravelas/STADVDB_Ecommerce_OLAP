import pandas as pd
from etl.transform import transform_dim_product  # ✅ correct import path

# 1️⃣ Create or load your raw product dataset
df_raw = pd.DataFrame({
    "productID": [1, 2, 3, 4, 5, 6],
    "Name": ["Phone", "Laptop", "Toy Car", "Makeup Kit", "Bagpack", "BAG"],
    "Category": ["Electronics", "GADGETS", "Toy", "make up", "Bags", "BAG"],
    "Description": [None, "Gaming laptop", "Small car", None, "Travel bag", "Handbag"],
    "ProductCode": ["P001", "P002", "P003", "P004", "P005", "P005"],  # duplicate on purpose
    "Price": [500.0, 1200.0, 15.0, 25.0, 60.0, 55.0],
    "CreatedAt": [
        "2024-01-01", "2024-02-01", "2024-03-01",
        "2024-03-02", "2024-03-03", "2024-03-03"
    ],
    "UpdatedAt": [
        "2024-02-01", "2024-03-01", "2024-04-01",
        "2024-04-02", "2024-04-03", "2024-04-03"
    ]
})

# 2️⃣ BEFORE TRANSFORMATION
print("🧩 BEFORE TRANSFORMATION:")
print(f"Number of rows: {len(df_raw)}")
print(df_raw)

# 3️⃣ Apply the transformation function
df_transformed = transform_dim_product(df_raw)

# 4️⃣ AFTER TRANSFORMATION
print("\n✅ AFTER TRANSFORMATION:")
print(f"Number of rows: {len(df_transformed)}")
print(df_transformed)

# 5️⃣ Optional: Save output for inspection
df_transformed.to_csv("Transformed_Products_Output.csv", index=False)
print("\n💾 Transformed data saved as 'Transformed_Products_Output.csv'")
