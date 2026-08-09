import os
import pandas as pd

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

data_path = os.path.join(
    project_root,
    "outputs",
    "customer_priority_list.csv"
)

output_path = os.path.join(
    project_root,
    "outputs",
    "campaign_strategy_results.csv"
)
data = pd.read_csv(data_path)

print(data.head())

campaign_size = 500
random_strategy = data.sample(
    n=campaign_size,
    random_state=42
)
random_saved = random_strategy["revenue_at_risk"].sum()
print("Random Strategy Revenue Saved:")
print(random_saved)

highest_churn_strategy = data.sort_values(
    by="churn_probability",
    ascending=False
)
highest_churn_strategy = highest_churn_strategy.head(campaign_size)
highest_churn_saved = highest_churn_strategy["revenue_at_risk"].sum()
print("Highest Churn Strategy Revenue Saved:")
print(highest_churn_saved)

highest_revenue_strategy = data.sort_values(
    by="revenue_at_risk",
    ascending=False
)
highest_revenue_strategy = highest_revenue_strategy.head(campaign_size)
highest_revenue_saved = highest_revenue_strategy["revenue_at_risk"].sum()
print("Highest Revenue at Risk Strategy Revenue Saved:")
print(highest_revenue_saved)

highest_value_strategy = data.sort_values(
    by="predicted_future_12_month_revenue",
    ascending=False
)
highest_value_strategy = highest_value_strategy.head(campaign_size)

results = pd.DataFrame({
    "Strategy": [
        "Random",
        "Highest Churn Probability",
        "Highest Predicted Future Value",
        "Highest Revenue at Risk"
    ],

    "Customers Contacted": [
        campaign_size,
        campaign_size,
        campaign_size,
        campaign_size
    ],

    "Total Predicted Customer Value": [
        random_strategy["predicted_future_12_month_revenue"].sum(),
        highest_churn_strategy["predicted_future_12_month_revenue"].sum(),
        highest_value_strategy["predicted_future_12_month_revenue"].sum(),
        highest_revenue_strategy["predicted_future_12_month_revenue"].sum()
    ],

    "Total Revenue at Risk": [
        random_strategy["revenue_at_risk"].sum(),
        highest_churn_strategy["revenue_at_risk"].sum(),
        highest_value_strategy["revenue_at_risk"].sum(),
        highest_revenue_strategy["revenue_at_risk"].sum()
    ],

    "Average Churn Probability": [
        random_strategy["churn_probability"].mean(),
        highest_churn_strategy["churn_probability"].mean(),
        highest_value_strategy["churn_probability"].mean(),
        highest_revenue_strategy["churn_probability"].mean()
    ]
})
output_path = os.path.join(
    project_root,
    "outputs",
    "campaign_strategy_results.csv"
)

results.to_csv(output_path, index=False)

print("Campaign strategy comparison saved successfully!")


