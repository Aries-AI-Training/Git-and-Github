import pandas as pd


# Load original churn dataset
churn_data = pd.read_csv("data/Customer_Churn.csv")

# Load future value dataset
future_value_data = pd.read_csv("data/customer_future_value.csv")


print(churn_data.head())
print(future_value_data.head())
merged_data = pd.merge(
    churn_data,
    future_value_data,
    on="customerID",
    how="inner"
)
print(merged_data.head())

print(merged_data.shape)

# ==========================
# Data Validation
# ==========================

# 1. Check missing future revenue values
missing_revenue = merged_data[
    "future_12_month_revenue_if_retained"
].isna().sum()

print("Missing future revenue:", missing_revenue)


# 2. Check duplicate customer IDs
duplicate_ids = merged_data["customerID"].duplicated().sum()

print("Duplicate customer IDs:", duplicate_ids)


# 3. Check negative revenue values
negative_revenue = (
    merged_data["future_12_month_revenue_if_retained"] < 0
).sum()

print("Negative revenue values:", negative_revenue)

# 4. Compare number of customers before and after merge

print("Original customers:", len(churn_data))
print("Future value customers:", len(future_value_data))
print("Merged customers:", len(merged_data))

merged_data.to_csv(
    "data/customer_retention_dataset.csv",
    index=False
)

print("Merged dataset saved successfully!")