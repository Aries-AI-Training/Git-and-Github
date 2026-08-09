import os
import joblib
import pandas as pd
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

data_path = os.path.join(
    project_root,
    "outputs",
    "customer_with_churn_probability.csv"
)

model_path = os.path.join(
    project_root,
    "outputs",
    "selected_value_model.joblib"
)

output_path = os.path.join(
    project_root,
    "outputs",
    "customer_priority_list.csv"
)

data = pd.read_csv(data_path)

revenue_model = joblib.load(model_path)

X = data.drop(
    columns=[
        "customerID",
        "Churn",
        "future_12_month_revenue_if_retained",
        "churn_probability"
    ],
    errors="ignore"
)
predicted_revenue = revenue_model.predict(X)
data["predicted_future_12_month_revenue"] = predicted_revenue

#Revenue At Risk
data["revenue_at_risk"] = (
    data["churn_probability"] *
    data["predicted_future_12_month_revenue"]
)
data = data.sort_values(
    by="revenue_at_risk",
    ascending=False
)
data["priority_rank"] = range(1, len(data)+1)

# Customer Segmentation
revenue_threshold = data["predicted_future_12_month_revenue"].median()


def assign_segment(row):

    if row["churn_probability"] >= 0.7 and row["predicted_future_12_month_revenue"] >= revenue_threshold:
        return "Critical Priority"

    elif row["churn_probability"] >= 0.7 and row["predicted_future_12_month_revenue"] < revenue_threshold:
        return "High Risk - Lower Value"

    elif row["churn_probability"] < 0.7 and row["predicted_future_12_month_revenue"] >= revenue_threshold:
        return "Valuable but Stable"

    else:
        return "Low Priority"


data["retention_segment"] = data.apply(assign_segment, axis=1)

def assign_action(segment):

    actions = {
        "Critical Priority": "Immediate personal call",
        "High Risk - Lower Value": "Automated retention campaign",
        "Valuable but Stable": "Maintain relationship",
        "Low Priority": "No immediate intervention"
    }

    return actions[segment]


data["recommended_action"] = data["retention_segment"].apply(assign_action)

business_output = data[
    [
        "customerID",
        "churn_probability",
        "predicted_future_12_month_revenue",
        "revenue_at_risk",
        "priority_rank",
        "retention_segment",
        "recommended_action"
    ]
]


business_output.to_csv(
    "outputs/customer_priority_list.csv",
    index=False
)