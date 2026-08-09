# Customer Retention Prioritization Report

## Introduction

The main goal of this project is to help the company decide which customers should be contacted first before they leave the service. Since the company has limited employees and budget, it cannot contact every customer. Therefore, this system combines machine learning predictions with business information to identify the customers with the highest priority.

---

## Why Churn Probability Alone Is Not Enough

Predicting whether a customer will leave is useful, but it is not enough. Some customers have a very high chance of churning but generate only a small amount of revenue. Other customers may have a lower churn probability but are much more valuable to the company.

For this reason, the project combines churn probability with future customer value to make better business decisions.

---

## Future Customer Value

Future customer value is the estimated revenue that the company expects to receive from a customer during the next 12 months if that customer stays with the company.

To predict this value, regression models were trained using customer information. The following columns were not used as input features:

* customerID
* Churn
* future_12_month_revenue_if_retained

---

## Regression Models

Two regression models were tested:

* Linear Regression
* Random Forest Regressor

The models were evaluated using:

* MAE
* RMSE
* R² Score

The model with the best performance was selected and saved for later use. MAE was considered the most important metric because it shows the average prediction error in the same unit as customer revenue, making it easy to understand from a business perspective.

---

## Understanding Regression Errors

Regression models do not predict exact values, so some prediction error is expected.

For example:

* Actual Future Revenue = 1200
* Predicted Future Revenue = 900
* Prediction Error = 300

If customer value is underestimated, the company may ignore an important customer. If customer value is overestimated, the company may spend time and money on customers who are less valuable than expected.

---

## Reusing the Churn Model

Instead of training a new churn model, the classification model from Task 01 was reused.

The saved model generated a churn probability for every customer, representing the likelihood that the customer will leave the company.

---

## Revenue at Risk

Revenue at Risk was calculated using the following equation:

Revenue at Risk = Churn Probability × Predicted Future Revenue

This value combines customer risk with customer value. Customers with the highest Revenue at Risk are the customers that could cause the biggest financial loss if they leave.

---

## Customer Segmentation

Customers were divided into four business groups:

### Critical Priority

Customers with high churn probability and high predicted value.

**Recommended Action:** Immediate personal call.

### High Risk – Lower Value

Customers with high churn probability but lower predicted value.

**Recommended Action:** Automated retention campaign or special offer.

### Valuable but Stable

Customers with high predicted value but low churn probability.

**Recommended Action:** Maintain a good relationship and continue monitoring.

### Low Priority

Customers with low churn probability and low predicted value.

**Recommended Action:** No immediate action is required.

The segmentation thresholds were based on the median predicted customer value and the median churn probability.

---

## Campaign Strategy Comparison

Several campaign strategies were compared:

* Random Selection
* Highest Churn Probability
* Highest Predicted Future Value
* Highest Revenue at Risk

The results showed that selecting customers based on Revenue at Risk gives the best balance between customer value and churn risk. This strategy helps the company use its limited retention budget more effectively.

---

## Business Recommendation

The company should prioritize customers with the highest Revenue at Risk because they have both a high chance of leaving and a high expected business value.

This approach allows the customer success team to focus on the customers whose loss would have the greatest financial impact.

---

## Limitations

This system has some limitations:

* Future customer revenue is only an estimate.
* Prediction accuracy depends on data quality.
* Customer behavior may change over time, so the models should be updated regularly.
* More customer information could improve future predictions.

---

## Conclusion

This project combines classification and regression models to support better business decisions. Instead of using churn probability alone, the system predicts future customer value, calculates Revenue at Risk, prioritizes customers, and recommends suitable retention actions. This helps the company use its resources more efficiently and focus on the customers who have the greatest business impact.
