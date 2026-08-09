import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("muted")

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
data_path = os.path.join(project_root, "data", "customer_churn.csv")
outputs_dir = os.path.join(project_root, "outputs")
charts_dir = os.path.join(outputs_dir, "charts")

os.makedirs(outputs_dir, exist_ok=True)
os.makedirs(charts_dir, exist_ok=True)

print("========== 1. Loading Data ==========")
df = pd.read_csv(data_path)
print(f"Dataset Shape: {df.shape}")

target_col = "Churn" if "Churn" in df.columns else "churned"
df[target_col] = df[target_col].map({"No": 0, "Yes": 1, 0: 0, 1: 1})

print("\n========== 2. Data Cleaning & Preprocessing ==========")
initial_rows = len(df)
df = df.drop_duplicates()
print(f"Removed duplicates: {initial_rows - len(df)}")

if "TotalCharges" in df.columns:
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")

id_col = "customerID" if "customerID" in df.columns else ("customer_id" if "customer_id" in df.columns else None)
customer_ids = df[id_col] if id_col else pd.Series([f"CUST_{i}" for i in range(len(df))])

drop_cols = [id_col, target_col] if id_col else [target_col]
X = df.drop(columns=[col for col in drop_cols if col in df.columns])
y = df[target_col]

numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

print(f"\n========== 3. Generating Required Charts in 'charts/' ==========")

# 01. Churn Distribution
plt.figure(figsize=(6, 4))
sns.countplot(x=y.map({0: "Stayed (0)", 1: "Churned (1)"}))
plt.title("Customer Churn Distribution")
plt.xlabel("Customer Status")
plt.ylabel("Count")
plt.savefig(os.path.join(charts_dir, "01_churn_distribution.png"), bbox_inches='tight')
plt.close()

# 02. Churn by Contract
if "Contract" in df.columns:
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x="Contract", hue=target_col)
    plt.title("Churn by Contract Type")
    plt.xlabel("Contract Type")
    plt.ylabel("Customer Count")
    plt.legend(title="Churn", labels=["Stayed", "Churned"])
    plt.savefig(os.path.join(charts_dir, "02_churn_by_contract.png"), bbox_inches='tight')
    plt.close()

# 03. Churn by Internet Service
if "InternetService" in df.columns:
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x="InternetService", hue=target_col)
    plt.title("Churn by Internet Service")
    plt.xlabel("Internet Service")
    plt.ylabel("Customer Count")
    plt.legend(title="Churn", labels=["Stayed", "Churned"])
    plt.savefig(os.path.join(charts_dir, "03_churn_by_internet_service.png"), bbox_inches='tight')
    plt.close()

# 04. Churn by Tenure
if "tenure" in df.columns:
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x="tenure", hue=target_col, multiple="stack", bins=30)
    plt.title("Churn by Tenure (Months)")
    plt.xlabel("Tenure")
    plt.ylabel("Customer Count")
    plt.savefig(os.path.join(charts_dir, "04_churn_by_tenure.png"), bbox_inches='tight')
    plt.close()

# 05. Churn by Payment Method
if "PaymentMethod" in df.columns:
    plt.figure(figsize=(10, 5))
    sns.countplot(data=df, x="PaymentMethod", hue=target_col)
    plt.title("Churn by Payment Method")
    plt.xlabel("Payment Method")
    plt.ylabel("Customer Count")
    plt.xticks(rotation=15)
    plt.legend(title="Churn", labels=["Stayed", "Churned"])
    plt.savefig(os.path.join(charts_dir, "05_churn_by_payment_method.png"), bbox_inches='tight')
    plt.close()

# 06. Churn by Tech Support
if "TechSupport" in df.columns:
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x="TechSupport", hue=target_col)
    plt.title("Churn by Tech Support")
    plt.xlabel("Tech Support")
    plt.ylabel("Customer Count")
    plt.legend(title="Churn", labels=["Stayed", "Churned"])
    plt.savefig(os.path.join(charts_dir, "06_churn_by_tech_support.png"), bbox_inches='tight')
    plt.close()

print("All 6 charts generated successfully!")

print("\n========== 4. Train/Test Split ==========")
X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X, y, customer_ids, test_size=0.2, random_state=42, stratify=y
)

print("\n========== 5. Preprocessing Pipeline ==========")
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

print("\n========== 6. Business Rule Baseline ==========")
def baseline_rule(row):
    tenure_low = row.get("tenure", 30) < 12
    monthly_high = row.get("MonthlyCharges", 50) > 70
    contract_monthly = row.get("Contract", "") == "Month-to-month"
    if tenure_low and (monthly_high or contract_monthly):
        return 1
    return 0

baseline_preds = X_test.apply(baseline_rule, axis=1)

base_acc = accuracy_score(y_test, baseline_preds)
base_prec = precision_score(y_test, baseline_preds, zero_division=0)
base_rec = recall_score(y_test, baseline_preds, zero_division=0)
base_f1 = f1_score(y_test, baseline_preds, zero_division=0)

print(f"Baseline - Accuracy: {base_acc:.4f}, Precision: {base_prec:.4f}, Recall: {base_rec:.4f}, F1: {base_f1:.4f}")

print("\n========== 7. Training Machine Learning Models ==========")
models = {
    "Logistic Regression": Pipeline(steps=[('preprocessor', preprocessor), ('classifier', LogisticRegression(random_state=42, max_iter=1000))]),
    "Decision Tree": Pipeline(steps=[('preprocessor', preprocessor), ('classifier', DecisionTreeClassifier(random_state=42, max_depth=5))]),
    "Random Forest": Pipeline(steps=[('preprocessor', preprocessor), ('classifier', RandomForestClassifier(random_state=42, n_estimators=100))])
}

comparison_data = [{
    "Model": "Business rule",
    "Accuracy": round(base_acc, 4),
    "Precision": round(base_prec, 4),
    "Recall": round(base_rec, 4),
    "F1-score": round(base_f1, 4)
}]

best_f1_score = -1
best_model_name = ""
best_model_obj = None 
best_preds = None
best_probs = None

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    
    comparison_data.append({
        "Model": name,
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1-score": round(f1, 4)
    })
    
    # حفظ مصفوفة الارتباك كصورة لكل نموذج
    cm = confusion_matrix(y_test, preds)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title(f"CM - {name}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    file_name = f"cm_{name.lower().replace(' ', '_')}.png"
    plt.savefig(os.path.join(charts_dir, file_name), bbox_inches='tight')
    plt.close()
    
    if f1 > best_f1_score:
        best_f1_score = f1
        best_model_name = name
        best_model_obj = model
        best_preds = preds
        best_probs = probs

print("\nModel Comparison Table:")
df_comparison = pd.DataFrame(comparison_data)
print(df_comparison)

df_comparison.to_csv(os.path.join(outputs_dir, "model_comparison.csv"), index=False)
print(f"\nSelected Best Model based on F1-score: {best_model_name}")

print("\n========== 8. Saving Outputs ==========")
test_results_df = pd.DataFrame({
    "customer_id": id_test.values,
    "actual_churn": y_test.values,
    "predicted_churn": best_preds,
    "churn_probability": best_probs
})
test_results_df.to_csv(os.path.join(outputs_dir, "test_predictions.csv"), index=False)

cm_best = confusion_matrix(y_test, best_preds)
tn, fp, fn, tp = cm_best.ravel()

eval_summary = {
    "selected_model": best_model_name,
    "accuracy": round(float(accuracy_score(y_test, best_preds)), 4),
    "precision": round(float(precision_score(y_test, best_preds, zero_division=0)), 4),
    "recall": round(float(recall_score(y_test, best_preds, zero_division=0)), 4),
    "F1-score": round(float(f1_score(y_test, best_preds, zero_division=0)), 4),
    "false_positives": int(fp),
    "false_negatives": int(fn),
    "important_business_conclusion": "The model helps customer success proactively identify high-risk churners, minimizing revenue loss while balancing retention campaign costs."
}

with open(os.path.join(outputs_dir, "evaluation_summary.json"), "w") as f:
    json.dump(eval_summary, f, indent=4)

joblib.dump(best_model_obj, os.path.join(outputs_dir, "selected_model.joblib"))

print("All scripts, models, and charts successfully generated in 'outputs/charts/'!")