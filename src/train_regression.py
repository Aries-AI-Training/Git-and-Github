import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def clean_and_prepare_data(filepath):
    print("Loading joined dataset for regression training...")
    #عشان إذا كان الملف كبير، يعرف انو البرنامج شغال ما يضلو يستنى ويفكرو معلق
    df = pd.read_csv(filepath)#بتقرا الملف وبتحوله لداتا فريم
    
    # Clean TotalCharges (in case of empty spaces or string formatting)
    df['TotalCharges'] = df['TotalCharges'].replace(r'^\s*$', np.nan, regex=True)
    #كل القيم اافاضي "" حولها لنان
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0.0)
    #اذا لقيت قيم مش رقمية حولها لنان وبعدين عبيها بصفر                                     
    # Ensure tenure and MonthlyCharges are correct numeric types
    df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce').fillna(0)
    df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce').fillna(0.0)
    
    return df

def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    data_path = os.path.join(project_dir, 'data', 'joined_customer_data.csv')
    outputs_dir = os.path.join(project_dir, 'outputs')
    
    os.makedirs(outputs_dir, exist_ok=True)
    
    # 1. Load and clean data
    df = clean_and_prepare_data(data_path)
    
    # 2. Separate Features (X) and Target (y)
    # CRITICAL: We drop customerID, Churn (classification label), and the target itself.
    drop_cols = ['customerID', 'Churn', 'future_12_month_revenue_if_retained']
    X = df.drop(columns=drop_cols)
    y = df['future_12_month_revenue_if_retained']
    
    # 3. Train-Test Split (80/20 train/test split, random_state=42)
    # Note: We do not stratify continuous variables.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Features list: {list(X.columns)}")
    print(f"Training set size: {len(X_train)} samples")
    print(f"Testing set size: {len(X_test)} samples")
    
    # 4. Preprocessing Pipeline
    numeric_features = ['tenure', 'MonthlyCharges', 'TotalCharges']
    categorical_features = [
        'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 
        'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
        'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 
        'Contract', 'PaperlessBilling', 'PaymentMethod'
    ]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),#بخلي كل الارقام بنفس المقياس 
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)#بحول الاعمدة ل 0 و 1
        ]
    )
    
    # 5. Define Models
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(random_state=42, n_estimators=150, max_depth=10, min_samples_leaf=4)
    }
    
    results = []
    trained_pipelines = {}
    
    # 6. Train and Evaluate each model
    for name, regressor in models.items():
        print(f"\nTraining {name} Model...")
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])
        
        # Fit model on training data
        pipeline.fit(X_train, y_train)
        trained_pipelines[name] = pipeline
        
        # Predict on test data
        y_pred = pipeline.predict(X_test)
        
        # Compute metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results.append({
            'Model': name,
            'MAE': round(mae, 4),
            'RMSE': round(rmse, 4),
            'R2': round(r2, 4)
        })
        
        print(f"{name} Evaluation -> MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.4f}")
        
    # 7. Save model comparison results
    comparison_df = pd.DataFrame(results)
    comparison_path = os.path.join(outputs_dir, 'regression_model_comparison.csv')
    comparison_df.to_csv(comparison_path, index=False)
    print(f"\nSaved regression model comparison table to: {comparison_path}")
    print(comparison_df.to_string(index=False))
    
    # 8. Model Selection: Select the model with the lowest MAE
    # (MAE is highly interpretable representing the average dollar error per customer)
    best_model_name = min(results, key=lambda x: x['MAE'])['Model']
    best_pipeline = trained_pipelines[best_model_name]
    #بقدر اعملها هيك برضو :
    #def get_mae(x):
    #return x['MAE']
    #best_model = min(results, key=get_mae)
    print(f"\nSelected Model: {best_model_name} (Lowest MAE)")
    
    # Save the selected model
    model_output_path = os.path.join(outputs_dir, 'selected_value_model.joblib')
    joblib.dump(best_pipeline, model_output_path)
    print(f"Saved selected regression model to: {model_output_path}")

if __name__ == "__main__":
    main()
