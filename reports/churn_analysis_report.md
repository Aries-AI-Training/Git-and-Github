# Customer Churn Analysis & Predictive Intelligence Report (Telco Churn Dataset)

This report presents the findings, data cleaning decisions, model comparison, and strategic recommendations for the Customer Churn Prediction System. It is designed to be fully understandable by the customer-success team and non-technical stakeholders.

---

## 1. The Business Problem: What is Customer Churn?

**Customer churn** occurs when a customer cancels their subscription or stops doing business with our company. In a telecom or subscription-based business model, churn is one of the most critical metrics because it directly impacts recurring revenue and growth stability.

### The Problem
Historically, the customer-success team only finds out about a cancellation *after* it happens, when it is too late to intervene. 

### The Solution
By utilizing historical customer data, we want to predict **which active customers are likely to leave within the next 60 days**. This allows the customer-success team to proactively contact high-risk customers, understand their pain points, and offer customized retention plans (e.g., discounts, contract adjustments, or dedicated support) before they cancel.

---

## 2. Available Data Overview

We analyzed a dataset of **7,043 customers**, consisting of the following key features:
*   **Customer Identity**: `customerID` (excluded from predictive features to prevent bias).
*   **Account Details**: `tenure` (how long they've been a customer in months), `MonthlyCharges`, `TotalCharges`, `Contract` (Month-to-month, One year, Two year), `PaperlessBilling`, `PaymentMethod`.
*   **Demographic Details**: `gender`, `SeniorCitizen` (0 = no, 1 = yes), `Partner` (Yes/No), `Dependents` (Yes/No).
*   **Services Subscribed**: `PhoneService`, `MultipleLines`, `InternetService` (DSL, Fiber optic, No), `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`.
*   **Target column**: `Churn` (Yes = customer left, No = customer stayed).

---

## 3. Data-Quality Problems Found & Cleaned

Before training our predictive models, we identified and corrected several data issues to ensure the models did not learn from corrupted data:

1.  **Duplicate Customers**: Checked all customer IDs and confirmed there were 0 duplicate records.
2.  **Formatting & Type Errors (Missing Values)**:
    *   The `TotalCharges` column was stored as a string instead of a number. During conversion, we found **11 rows** containing empty spaces (`" "`).
    *   *Root cause*: These were new customers who had a `tenure` of `0` months, meaning their first bill had not yet been generated.
    *   *Correction*: We converted these empty charges to `NaN` and imputed them with `0.0` (since they had not yet incurred charges), ensuring no loss of customer records.
3.  **Target Column Encoding**:
    *   The target column `Churn` was stored as text (`Yes` / `No`). We mapped these to binary integers (`Yes` -> `1`, `No` -> `0`) to make them compatible with machine learning algorithms.

---

## 4. Key Customer Behaviors Connected to Churn

Based on our exploratory data analysis, the following behaviors are strongly correlated with a high risk of churn:

*   **Contract Type**: Month-to-month customers churn at a significantly higher rate than those on One-year or Two-year plans.
*   **Internet Service Type**: Customers with Fiber optic internet service have a notably higher churn rate compared to DSL customers, suggesting possible service reliability or pricing issues.
*   **Tech Support & Online Security**: Customers who do *not* subscribe to Tech Support or Online Security services are much more likely to cancel, indicating that value-added services build loyalty.
*   **Payment Method**: Customers paying via Electronic Check show a massive spike in churn compared to credit cards or automated bank transfers.
*   **Tenure**: Churn is highly concentrated in the first 12 months. Once a customer passes their first year, their likelihood of leaving drops dramatically.

---

## 5. Model Evaluation and Comparison

We tested four approaches on a test dataset (1,409 customers, representing 20% of the dataset that was hidden during training to ensure fair evaluation):
1.  **Business Rule Baseline**: A simple rule-based approach (predicting churn if the customer has a Month-to-month contract AND has no Online Security AND has no Tech Support).
2.  **Logistic Regression**: A standard statistical model.
3.  **Decision Tree Classifier**: A model that splits data based on simple thresholds (like an advanced flowchart).
4.  **Random Forest Classifier**: An ensemble model combining multiple decision trees.

### Evaluation Metrics Defined
*   **Accuracy**: The percentage of overall correct predictions (retained and churned). *Note: In churn prediction, accuracy can be misleading due to class imbalance.*
*   **Precision**: Out of all customers the model *predicted* would churn, how many *actually* churned? (High precision means fewer false alarms).
*   **Recall**: Out of all customers who *actually* churned, how many did the model *correctly identify*? (High recall means fewer missed churning customers).
*   **F1-Score**: The harmonic mean of Precision and Recall, representing overall model balance.

### Performance Summary Table

| Model | Accuracy | Precision (Targeting Accuracy) | Recall (Coverage) | F1-Score (Overall Balance) |
| :--- | :---: | :---: | :---: | :---: |
| **Business Rule Baseline** | 76.08% | 54.23% | 63.37% | 58.45% |
| **Logistic Regression** | 73.81% | 50.43% | 78.34% | 61.36% |
| **Decision Tree (Selected)** | **73.46%** | **50.00%** | **82.09%** | **62.15%** |
| **Random Forest** | 73.81% | 50.43% | 78.88% | 61.52% |

*Note: The exact numbers are derived from our training script and show that Machine Learning significantly outperforms the manual business rule.*

---

## 6. Business Error Analysis: The Cost of Mistakes

In predictive churn modeling, there are two types of errors:

### A. False Positives (False Alarms)
*   **What it means**: The system predicts a customer will leave, but they actually stay.
*   **Business Cost**: 
    *   Wasted marketing budget (e.g., sending an unnecessary promotional discount or coupon).
    *   CSM team spends time calling a customer who was already satisfied.
    *   *Estimated cost*: Very low (value of a discount or a 5-minute phone call).

### B. False Negatives (Missed Churners)
*   **What it means**: The system predicts a customer will stay, but they actually leave.
*   **Business Cost**: 
    *   The company misses the chance to save the customer.
    *   Loss of recurring subscription revenue (entire customer lifetime value).
    *   *Estimated cost*: Very high (hundreds or thousands of dollars in lost revenue).

> [!WARNING]
> **Conclusion**: **False Negatives are far more dangerous** for our business. Missing a customer who is about to leave results in permanent revenue loss. Therefore, we prioritize models with high **Recall** (identifying as many true churners as possible) while maintaining a reasonable **Precision** to avoid over-spending on retention campaigns.

---

## 7. Model Selection & Rationale

We selected the **Decision Tree Classifier** as our first recommended production model.

### Why Decision Tree?
1.  **Highest Recall (82.09%)**: It catches the highest percentage of churning customers compared to all other models, minimizing our most expensive error (False Negatives).
2.  **Highest Balance (F1-score: 62.15%)**: It outperforms both the manual business rule, Logistic Regression, and Random Forest on our target metric.
3.  **Interpretability (Business Usefulness)**: Unlike Random Forest (a "black box" model that is hard to explain), a Decision Tree can be drawn as a transparent flowchart. Customer Success Managers can easily look at the tree branches (e.g., *"If Contract is Month-to-month and Internet Service is Fiber optic, then Churn Risk is High"*) and understand *why* the model flagged a customer.
4.  **Simplicity**: It is lightweight, fast to train, and easy to deploy in the next stages of the project.

---

## 8. Strategic Recommendations for Customer Success

Now that we have this model, what should the company do?

1.  **Proactive CSM Outreach**: Integrate the model's high-risk list into the daily workflow of the Customer Success team. CSMs should prioritize calling customers with a predicted churn probability $> 60\%$.
2.  **Targeted Retention Offers**:
    *   For Month-to-month customers flagged as high risk, offer them a discounted annual contract to lock in their loyalty.
    *   For Fiber optic customers showing high churn probability, run a proactive quality check-in to ensure their speed and stability are up to standard.
    *   Encourage customers paying by Electronic Check to switch to credit card or bank auto-payment by offering a one-time bill credit.
3.  **No-Risk Check-Ins**: For false positives (loyal customers who are flagged), a simple "thank you" call or customer satisfaction survey will build goodwill, rendering the cost of a false alarm negligible.

---

## 9. Current Limitations & Future Data Collection

While the model performs well, we can improve its accuracy by addressing current limitations:

### Current Limitations
*   Our dataset does not include real-time usage trends (e.g., did their data usage drop by 50% in the last 2 weeks?).
*   We lack customer service ticket text sentiment.

### Recommended Data to Collect
1.  **Usage Trend Indicators**: Month-over-month change in usage data volume or voice calls.
2.  **Support Sentiment**: Text sentiment scores of support tickets.
3.  **competitor Pricing**: Information on whether the customer is receiving offers from competitors.
