import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
import numpy as np
import joblib


# Load prepared dataset
data = pd.read_csv("data/customer_retention_dataset.csv")


print(data.head())
print(data.shape)

# Target column
target = "future_12_month_revenue_if_retained"


# Features
X = data.drop(columns=[target, "customerID", "Churn"])

# Target values
y = data[target]


print(X.head())
print(y.head())

# Separate column types

numeric_features = X.select_dtypes(
    include=["int64", "float64"]
).columns

categorical_features = X.select_dtypes(
    include=["object"]
).columns


print("Numeric features:")
print(numeric_features)

print("Categorical features:")
print(categorical_features)

# Numeric preprocessing pipeline

numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)

# Categorical preprocessing pipeline

categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ]
)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_pipeline, numeric_features),
        ("cat", categorical_pipeline, categorical_features)
    ]
)
# Train/Test Split  👈 هون
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print("Training samples:", X_train.shape)
print("Testing samples:", X_test.shape)

# Linear Regression model

linear_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", LinearRegression())
    ]
)


linear_model.fit(
    X_train,
    y_train
)


linear_predictions = linear_model.predict(X_test)


print("Linear Regression predictions:")
print(linear_predictions[:5])

# Evaluate Linear Regression
linear_mae = mean_absolute_error(
    y_test,
    linear_predictions
)

linear_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        linear_predictions
    )
)

linear_r2 = r2_score(
    y_test,
    linear_predictions
)

print("\nLinear Regression Results")
print("MAE :", linear_mae)
print("RMSE:", linear_rmse)
print("R²  :", linear_r2)

# Random Forest model
rf_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
        )
    ]
)

rf_model.fit(
    X_train,
    y_train
)
rf_predictions = rf_model.predict(X_test)

rf_mae = mean_absolute_error(
    y_test,
    rf_predictions
)

rf_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        rf_predictions
    )
)

rf_r2 = r2_score(
    y_test,
    rf_predictions
)

print("\nRandom Forest Results")
print("MAE :", rf_mae)
print("RMSE:", rf_rmse)
print("R²  :", rf_r2)

comparison = pd.DataFrame(
    {
        "Model": [
            "Linear Regression",
            "Random Forest"
        ],
        "MAE": [
            linear_mae,
            rf_mae
        ],
        "RMSE": [
            linear_rmse,
            rf_rmse
        ],
        "R2": [
            linear_r2,
            rf_r2
        ]
    }
)

print(comparison)
comparison.to_csv(
    "outputs/regression_model_comparison.csv",
    index=False
)
print("Regression comparison saved successfully!")

#Best regression model
if rf_mae < linear_mae:
    best_model = rf_model
    best_model_name = "Random Forest"
else:
    best_model = linear_model
    best_model_name = "Linear Regression"

print(f"\nBest model: {best_model_name}")

joblib.dump(
    best_model,
    "outputs/selected_value_model.joblib"
)

print("Best regression model saved successfully!")
