import os
import pandas as pd
import numpy as np
import joblib

def load_models_and_data():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    data_path = os.path.join(project_dir, 'data', 'joined_customer_data.csv')
    
    churn_model_path = os.path.join(project_dir, 'outputs', 'selected_model.joblib')
    value_model_path = os.path.join(project_dir, 'outputs', 'selected_value_model.joblib')
    
    # Load dataset
    df = pd.read_csv(data_path)
    
    # Clean features to ensure they match model preprocessing requirements
    df['TotalCharges'] = df['TotalCharges'].replace(r'^\s*$', np.nan, regex=True)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0.0)
    df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce').fillna(0)
    df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce').fillna(0.0)
    
    # Load models
    print("Loading Churn Classification model...")
    churn_model = joblib.load(churn_model_path)
    
    print("Loading Value Regression model...")
    value_model = joblib.load(value_model_path)
    
    return df, churn_model, value_model

def get_predictions(df, churn_model, value_model):
    print("Generating predictions for all customers...")
    
    # Separate the features (matching what both models expect)
    # The models expect features excluding customerID and Churn target
    features_to_drop = ['customerID', 'Churn', 'future_12_month_revenue_if_retained']
    X = df.drop(columns=[col for col in features_to_drop if col in df.columns])
    
    # Generate Churn Probabilities
    # predict_proba returns [prob_class_0, prob_class_1]
    df['churn_probability'] = np.round(churn_model.predict_proba(X)[:, 1], 4)
    
    # Generate Predicted Future Revenue
    df['predicted_future_12_month_revenue'] = np.round(value_model.predict(X), 2)
    
    # Calculate Expected Revenue at Risk
    df['revenue_at_risk'] = np.round(df['churn_probability'] * df['predicted_future_12_month_revenue'], 2)
    
    return df

def segment_customers(df):
    print("Segmenting customers into retention priority groups...")
    
    # Define thresholds dynamically based on distribution analysis
    # Churn probability threshold: 
    # Let's check the churn probability distribution. Instead of hardcoding 0.5, 
    # we choose a threshold that represents high risk. 
    # The baseline churn rate is ~26.5%, so we choose the 70th percentile of probabilities.
    churn_threshold = round(df['churn_probability'].quantile(0.70), 2)
    
    # Value threshold: Top 25% of predicted revenue (75th percentile)
    value_threshold = round(df['predicted_future_12_month_revenue'].quantile(0.75), 2)
    
    print(f"Dynamic Churn Probability Threshold (70th percentile): {churn_threshold}")
    print(f"Dynamic Predicted Future Revenue Threshold (75th percentile): {value_threshold}")
    
    segments = []
    actions = []
    
    for idx, row in df.iterrows():
        p_churn = row['churn_probability']
        pred_rev = row['predicted_future_12_month_revenue']
        
        if p_churn >= churn_threshold and pred_rev >= value_threshold:
            segments.append("Critical Priority")
            actions.append("Immediate personal call from customer-success team")
        elif p_churn >= churn_threshold and pred_rev < value_threshold:
            segments.append("High Risk, Lower Value")
            actions.append("Automated retention campaign or targeted offer")
        elif p_churn < churn_threshold and pred_rev >= value_threshold:
            segments.append("Valuable but Stable")
            actions.append("Monitor and maintain relationship")
        else:
            segments.append("Low Priority")
            actions.append("No immediate intervention")
            
    df['retention_segment'] = segments
    df['recommended_action'] = actions
    
    # Sort by revenue at risk (highest business priority)
    df = df.sort_values(by='revenue_at_risk', ascending=False).reset_index(drop=True)
    df['priority_rank'] = range(1, len(df) + 1)
    
    return df, churn_threshold, value_threshold

def run_budget_simulation(df, seed=42):
    print("Running limited-budget simulation (capacity = 100 customers)...")
    np.random.seed(seed)
    
    # Ensure Churn target is binary integer (robust mapping for string/object dtypes)
    df['actual_churn_numeric'] = df['Churn'].apply(lambda x: 1 if str(x).strip().lower() in ['yes', '1', 'true'] else 0)
    #بدي اعمل هيك عشان عندي SUM كمان شوي ف بحاجة يكونو ارقام
        
    strategies = {}
    
    # 1. Random strategy
    random_sel = df.sample(n=100)
    strategies['Random Selection'] = random_sel
    
    # 2. Highest Churn Probability strategy
    churn_sel = df.nlargest(100, 'churn_probability')
    strategies['Highest Churn Probability'] = churn_sel
    #بنختار أعلى 100 عميل متوقع يتركوا الشركة بناءً على Task 01 بس (بدون ما نهتم كم بيدفعوا).
    
    # 3. Highest Predicted Value strategy
    value_sel = df.nlargest(100, 'predicted_future_12_month_revenue')
    strategies['Highest Predicted Value'] = value_sel
    #بنختار أغنى 100 عميل بيدفعوا فلوس، حتى لو كانت احتمالية إنهم يتركوا الشركة واطية جداً ومستقرين
    
    # 4. Highest Revenue at Risk strategy (Our proposed system)
    risk_sel = df.nlargest(100, 'revenue_at_risk')
    strategies['Highest Revenue at Risk'] = risk_sel
    
    comparison_results = []
    
    for name, sel_df in strategies.items():
        total_val = sel_df['predicted_future_12_month_revenue'].sum()
        total_risk = sel_df['revenue_at_risk'].sum()
        avg_churn_prob = sel_df['churn_probability'].mean()
        actual_churned_saved = sel_df['actual_churn_numeric'].sum()
        
        comparison_results.append({
            'Strategy': name,
            'Total Selected Value ($)': round(total_val, 2),
            'Total Revenue at Risk ($)': round(total_risk, 2),
            'Avg Churn Probability': round(avg_churn_prob, 4),
            'Actual Churners Contacted': int(actual_churned_saved)
        })
        
    comparison_df = pd.DataFrame(comparison_results)
    return comparison_df

def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    outputs_dir = os.path.join(project_dir, 'outputs')
    
    # 1. Load data and models
    df, churn_model, value_model = load_models_and_data()
    
    # 2. Predict churn probability, future revenue, and revenue at risk
    df = get_predictions(df, churn_model, value_model)
    
    # 3. Segment customers based on dynamic thresholds
    df, churn_threshold, value_threshold = segment_customers(df)
    
    # 4. Save Customer Priority List CSV
    priority_cols = [
        'customerID', 'churn_probability', 
        'predicted_future_12_month_revenue',
        'revenue_at_risk', 'priority_rank',
          'retention_segment', 'recommended_action'
    ]
    priority_list_df = df[priority_cols]
    priority_path = os.path.join(outputs_dir, 'customer_priority_list.csv')
    priority_list_df.to_csv(priority_path, index=False)
    print(f"Saved customer priority list to: {priority_path}")
    print(priority_list_df.head(10))
    
    # 5. Run campaign budget simulation
    sim_df = run_budget_simulation(df)
    sim_path = os.path.join(outputs_dir, 'campaign_strategy_comparison.csv')
    sim_df.to_csv(sim_path, index=False)
    print(f"\nSaved strategy comparison to: {sim_path}")
    print(sim_df.to_string(index=False))

if __name__ == "__main__":
    main()

