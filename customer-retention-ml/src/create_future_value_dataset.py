import pandas as pd

# Read original customer churn dataset
data_path = "data/Customer_Churn.csv"

df = pd.read_csv(data_path)

# Check data
print(df.head())
print(df.columns)

# Create future revenue column
df["future_12_month_revenue_if_retained"] = df["MonthlyCharges"] * 12

# Create the future value dataset
future_value_df = df[
    ["customerID", "future_12_month_revenue_if_retained"]
]

# Check result
print(future_value_df.head())

# Save new dataset
future_value_df.to_csv(
    "data/customer_future_value.csv",
    index=False
)

print("Future customer value dataset created successfully!")