import os
import joblib
import pandas as pd

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

data_path = os.path.join(project_root, "data", "customer_retention_dataset.csv")
model_path = os.path.join(project_root, "outputs", "selected_model.joblib")
output_path = os.path.join(project_root, "outputs", "customer_with_churn_probability.csv")

# Load data
data = pd.read_csv(data_path)
if "TotalCharges" in data.columns:
    data["TotalCharges"] = pd.to_numeric(
        data["TotalCharges"].astype(str).str.strip(),
        errors="coerce"
    )
# Load churn model
churn_model = joblib.load(model_path)

# Prepare features
X = data.drop(
    columns=[
        "customerID",
        "Churn",
        "future_12_month_revenue_if_retained"
    ]
)

# Generate churn probabilities
churn_probabilities = churn_model.predict_proba(X)[:, 1]

# Add new column
data["churn_probability"] = churn_probabilities

# Save results
data.to_csv(output_path, index=False)

print("Churn probabilities generated successfully!")