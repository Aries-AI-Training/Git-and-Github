import os
import json
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def setup_directories():
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('outputs/charts', exist_ok=True)
    os.makedirs('reports', exist_ok=True)

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    return pd.read_csv(filepath)

def generate_eda_charts(df):
    print("Generating exploratory data analysis charts...")
    setup_directories()
    
    # Custom color palette (Slate for Stayed, Red for Churn)
    churn_colors = {"No": "#475569", "Yes": "#b91c1c"}
    sns.set_theme(style="whitegrid")
    
    # Chart 1: Churn Distribution
    plt.figure(figsize=(6, 5))
    ax = sns.countplot(x='Churn', data=df, hue='Churn', palette=churn_colors, legend=False)
    plt.title('Overall Customer Churn Distribution', fontsize=14, pad=15)
    plt.xlabel('Customer Status (No = Retained, Yes = Churned)', fontsize=11)
    plt.ylabel('Number of Customers', fontsize=11)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontsize=10)
    plt.tight_layout()
    plt.savefig('outputs/charts/01_churn_distribution.png', dpi=150)
    plt.close()

    # Chart 2: Churn by Contract Type
    plt.figure(figsize=(8, 5))
    ax = sns.countplot(x='Contract', hue='Churn', data=df, palette=churn_colors)
    plt.title('Churn Count by Contract Type', fontsize=14, pad=15)
    plt.xlabel('Contract Type', fontsize=11)
    plt.ylabel('Customer Count', fontsize=11)
    plt.legend(title='Status', labels=['Retained', 'Churned'])
    plt.tight_layout()
    plt.savefig('outputs/charts/02_churn_by_contract.png', dpi=150)
    plt.close()

    # Chart 3: Churn by Internet Service Type
    plt.figure(figsize=(8, 5))
    sns.countplot(x='InternetService', hue='Churn', data=df, palette=churn_colors)
    plt.title('Churn by Internet Service Type', fontsize=14, pad=15)
    plt.xlabel('Internet Service Type', fontsize=11)
    plt.ylabel('Customer Count', fontsize=11)
    plt.legend(title='Status', labels=['Retained', 'Churned'])
    plt.tight_layout()
    plt.savefig('outputs/charts/03_churn_by_internet_service.png', dpi=150)
    plt.close()

    # Chart 4: Churn by Tenure Months (Box Plot)
    plt.figure(figsize=(8, 5))
    sns.boxplot(x='Churn', y='tenure', data=df, hue='Churn', palette=churn_colors, legend=False)
    plt.title('Tenure Months: Retained vs Churned Customers', fontsize=14, pad=15)
    plt.xlabel('Customer Status (No = Retained, Yes = Churned)', fontsize=11)
    plt.ylabel('Tenure (Months)', fontsize=11)
    plt.tight_layout()
    plt.savefig('outputs/charts/04_churn_by_tenure.png', dpi=150)
    plt.close()

    # Chart 5: Churn by Payment Method
    plt.figure(figsize=(10, 5))
    sns.countplot(x='PaymentMethod', hue='Churn', data=df, palette=churn_colors)
    plt.title('Churn Distribution by Payment Method', fontsize=14, pad=15)
    plt.xlabel('Payment Method', fontsize=11)
    plt.ylabel('Customer Count', fontsize=11)
    plt.xticks(rotation=15)
    plt.legend(title='Status', labels=['Retained', 'Churned'])
    plt.tight_layout()
    plt.savefig('outputs/charts/05_churn_by_payment_method.png', dpi=150)
    plt.close()

    # Chart 6: Churn by Tech Support service adoption
    plt.figure(figsize=(8, 5))
    sns.countplot(x='TechSupport', hue='Churn', data=df, palette=churn_colors)
    plt.title('Churn Rate by Tech Support Service Adoption', fontsize=14, pad=15)
    plt.xlabel('Tech Support Status', fontsize=11)
    plt.ylabel('Customer Count', fontsize=11)
    plt.legend(title='Status', labels=['Retained', 'Churned'])
    plt.tight_layout()
    plt.savefig('outputs/charts/06_churn_by_tech_support.png', dpi=150)
    plt.close()
    
    print("EDA charts saved successfully to outputs/charts/")

def clean_data(df):
    print("Cleaning dataset...")
    initial_shape = df.shape
    print(f"Initial dataset shape: {initial_shape}")
    
    # 1. Duplicates
    df_clean = df.drop_duplicates(subset=['customerID'], keep='first')
    num_duplicates = initial_shape[0] - df_clean.shape[0]
    print(f"Removed {num_duplicates} duplicate records.")
    
    # 2. Correct Data Types & Missing Values
    # TotalCharges contains empty spaces " " for customers with tenure = 0
    # Convert spaces to NaN
    df_clean['TotalCharges'] = df_clean['TotalCharges'].replace(r'^\s*$', np.nan, regex=True)
    num_missing_total = df_clean['TotalCharges'].isna().sum()
    
    # Cast to float and fill NaNs with 0.0 (since tenure = 0 means no charge accrued yet)
    df_clean['TotalCharges'] = pd.to_numeric(df_clean['TotalCharges'], errors='coerce')
    df_clean['TotalCharges'] = df_clean['TotalCharges'].fillna(0.0)
    print(f"Corrected {num_missing_total} missing TotalCharges values (set to 0.0 for new customers).")
    
    # Map Churn target column to binary integers: Yes -> 1, No -> 0
    df_clean['Churn'] = df_clean['Churn'].map({'Yes': 1, 'No': 0})
    
    print(f"Cleaned dataset shape: {df_clean.shape}")
    return df_clean

def evaluate_baseline_rule(test_df):
    print("Evaluating simple business-rule baseline...")
    # Business logic baseline rule for Telco dataset:
    # Predict Churn if:
    # Contract is Month-to-month
    # AND OnlineSecurity is No
    # AND TechSupport is No
    # (This represents month-to-month customers with no security and no support)
    
    predictions = (
        (test_df['Contract'] == 'Month-to-month') & 
        (test_df['OnlineSecurity'] == 'No') & 
        (test_df['TechSupport'] == 'No')
    ).astype(int)
    
    y_true = test_df['Churn'].values
    y_pred = predictions.values
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    
    print(f"Baseline Rule - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
    return accuracy, precision, recall, f1, cm, y_pred

def train_and_evaluate_ml(X_train, X_test, y_train, y_test):
    setup_directories()
    
    # Define features
    numeric_features = ['tenure', 'MonthlyCharges', 'TotalCharges']
    categorical_features = [
        'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 
        'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
        'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 
        'Contract', 'PaperlessBilling', 'PaymentMethod'
    ]
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    
    # Models dict
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
        'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=4, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(random_state=42, max_depth=5, n_estimators=100, class_weight='balanced')
    }
    
    results = {}
    pipelines = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        # Train
        pipeline.fit(X_train, y_train)
        pipelines[name] = pipeline
        
        # Predict
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else [None] * len(y_pred)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        
        results[name] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'cm': cm,
            'preds': y_pred,
            'probs': y_prob
        }
        
        print(f"{name} - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        # Save confusion matrix plot
        plt.figure(figsize=(5.5, 4.5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                    xticklabels=['Retained', 'Churned'], yticklabels=['Retained', 'Churned'])
        plt.title(f'Confusion Matrix: {name}', fontsize=12, pad=10)
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.tight_layout()
        cm_filename = f"outputs/charts/cm_{name.lower().replace(' ', '_')}.png"
        plt.savefig(cm_filename, dpi=150)
        plt.close()
        
    return results, pipelines

def main():
    setup_directories()
    
    # 1. Load Data
    data_path = 'data/customer_churn.csv'
    if not os.path.exists(data_path):
        print(f"Error: {data_path} does not exist.")
        return
        
    df = load_data(data_path)
    
    # 2. EDA Visualizations
    generate_eda_charts(df)
    
    # 3. Clean Data
    df_clean = clean_data(df)
    
    # 4. Features & Target
    X = df_clean.drop(columns=['Churn', 'customerID'])
    y = df_clean['Churn']
    
    # 5. Split Data (Stratified split 80/20, random_state=42)
    X_train_df, X_test_df, y_train, y_test = train_test_split(
        df_clean, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train = X_train_df.drop(columns=['Churn', 'customerID'])
    X_test = X_test_df.drop(columns=['Churn', 'customerID'])
    test_customer_ids = X_test_df['customerID'].values
    
    print(f"Train set size: {len(X_train)} customers.")
    print(f"Test set size: {len(X_test)} customers.")
    
    # 6. Simple Heuristic Baseline
    base_acc, base_prec, base_rec, base_f1, base_cm, base_preds = evaluate_baseline_rule(X_test_df)
    
    # 7. Train ML Models
    ml_results, ml_pipelines = train_and_evaluate_ml(X_train, X_test, y_train, y_test)
    
    # 8. Compare Models
    comparison_data = [
        {
            "Model": "Business rule",
            "Accuracy": base_acc,
            "Precision": base_prec,
            "Recall": base_rec,
            "F1-score": base_f1
        }
    ]
    
    for name, metrics in ml_results.items():
        comparison_data.append({
            "Model": name,
            "Accuracy": metrics['accuracy'],
            "Precision": metrics['precision'],
            "Recall": metrics['recall'],
            "F1-score": metrics['f1']
        })
        
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df.to_csv('outputs/model_comparison.csv', index=False)
    print("\nModel Comparison Table:")
    print(comparison_df.to_string(index=False))
    
    # 9. Model Selection
    # Choose Decision Tree for interpretability and high recall
    selected_model_name = "Decision Tree"
    selected_pipeline = ml_pipelines[selected_model_name]
    selected_metrics = ml_results[selected_model_name]
    
    print(f"\nSelected Model: {selected_model_name}")
    
    # Save Selected Model
    joblib.dump(selected_pipeline, 'outputs/selected_model.joblib')
    print("Selected model saved to outputs/selected_model.joblib")
    
    # 10. Save Test Predictions CSV
    test_preds_df = pd.DataFrame({
        'customerID': test_customer_ids,
        'actual_churn': y_test.values,
        'predicted_churn': selected_metrics['preds'],
        'churn_probability': selected_metrics['probs']
    })
    test_preds_df.to_csv('outputs/test_predictions.csv', index=False)
    print("Test predictions saved to outputs/test_predictions.csv")
    
    # 11. Save Evaluation Summary JSON
    cm = selected_metrics['cm']
    false_positives = int(cm[0, 1])
    false_negatives = int(cm[1, 0])
    
    conclusion = (
        f"The {selected_model_name} model was chosen because it achieves a strong balance "
        f"between identifying at-risk customers (Recall: {selected_metrics['recall']:.2%}) and maintaining "
        f"reasonable targeting efficiency (Precision: {selected_metrics['precision']:.2%}). "
        f"This model will enable the customer success team to proactively contact high-risk customers, "
        f"resolving their concerns before they churn, while minimizing the cost of false alarms."
    )
    
    summary_data = {
        "selected_model_name": selected_model_name,
        "accuracy": float(selected_metrics['accuracy']),
        "precision": float(selected_metrics['precision']),
        "recall": float(selected_metrics['recall']),
        "f1_score": float(selected_metrics['f1']),
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "important_business_conclusion": conclusion
    }
    
    with open('outputs/evaluation_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=4, ensure_ascii=False)
    print("Evaluation summary saved to outputs/evaluation_summary.json")
    
    print("\nTraining and evaluation pipeline completed successfully!")

if __name__ == "__main__":
    main()
