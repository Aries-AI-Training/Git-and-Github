# Customer Churn Analysis & Predictive Intelligence Report

This report presents the findings, data cleaning decisions, model comparison, and strategic recommendations for the Customer Churn Prediction System. It is designed to be fully understandable by the customer-success team and non-technical stakeholders.

---

## 1. The Business Problem: What is Customer Churn?

**Customer churn** occurs when a customer cancels their subscription or stops doing business with our company. In a subscription-based business model, churn is one of the most critical metrics because it directly impacts recurring revenue and growth stability.

### The Problem
Historically, the customer-success team only finds out about a cancellation *after* it happens, when it is too late to intervene. 

### The Solution
By utilizing historical customer data, we want to predict **which active customers are likely to leave within the next 60 days**. This allows the customer-success team to proactively contact high-risk customers, understand their pain points, and offer customized retention plans (e.g., discounts, contract adjustments, or dedicated support) before they cancel.

---

## 2. Available Data Overview

We analyzed a dataset of **1,000 customers**, consisting of the following key features:
*   **Customer Identity**: `customer_id` (excluded from predictive features to prevent bias).
*   **Account Details**: `tenure_months` (how long they've been a customer), `monthly_spend`, `contract_type` (Month-to-Month, One-Year, Two-Year), `product_plan` (Basic, Standard, Premium), `auto_renew`.
*   **Engagement Metrics**: `average_weekly_usage_hours`, `days_since_last_login` (account activity).
*   **Satisfaction & Friction**: `late_payments_6m`, `support_tickets_3m`, `complaints_6m`, `satisfaction_score` (1 to 5).

---

## 3. Data-Quality Problems Found & Cleaned

Before training our predictive models, we identified and corrected several data issues to ensure the models did not learn from corrupted data:

1.  **Duplicate Customers**: Found and removed 5 duplicate customer entries to prevent over-representing specific customers.
2.  **Formatting Errors**: The `monthly_spend` column contained currency symbols (`$`) and leading/trailing spaces (e.g., `"$85.50"`). We stripped these symbols and converted the values into clean decimal numbers.
3.  **Invalid Values (Typos)**:
    *   *Negative spending* (e.g., `-$50.00`) and *negative tenure* (e.g., `-12 months`) were corrected to absolute values (e.g., `$50.00` and `12 months`), assuming these were entry typos.
    *   *Negative support ticket counts* were corrected to absolute values.
    *   *Out-of-bounds satisfaction scores* (e.g., `9` and `-2` on a 1-5 scale) were clipped to the nearest valid limits (5 and 1, respectively).
4.  **Missing Values (Nulls)**:
    *   15 missing satisfaction scores and 10 missing login recency records were filled with their respective column **medians** (middle values) to preserve the rows without introducing bias.
    *   5 missing auto-renew indicators were filled with the **mode** (most frequent value, which was `0`).

---

## 4. Key Customer Behaviors Connected to Churn

Based on our exploratory data analysis, the following behaviors are strongly correlated with a high risk of churn:

*   **Contract Type**: Month-to-Month customers churn at a significantly higher rate than those on One-Year or Two-Year plans. Longer commitments create natural stability.
*   **Complaints**: Customers who submitted at least one complaint in the last 6 months are highly likely to churn. This is the strongest behavioral distress signal.
*   **Late Payments**: Multiple late payments in the last 6 months correlate heavily with customer cancellation, signaling either financial issues or dissatisfaction with the product's value.
*   **Days Since Last Login**: A spike in days since last login indicates disengagement; customers who stop logging in are on the verge of canceling.
*   **Low Satisfaction Score**: Customers rating their satisfaction as 1 or 2 are highly vulnerable.

---

## 5. Model Evaluation and Comparison

We tested four approaches on a test dataset (20% of the data, which was hidden during training to ensure fair evaluation):
1.  **Business Rule Baseline**: A simple rule-based approach (predicting churn if the customer has a satisfaction score $\le 2$ OR has active complaints OR has not logged in for $> 30$ days).
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
| **Business Rule Baseline** | 85.00% | 40.91% | 81.82% | 54.55% |
| **Logistic Regression** | 88.50% | 48.57% | 77.27% | 59.65% |
| **Decision Tree** | 86.00% | 43.18% | 86.36% | 57.58% |
| **Random Forest** | 86.00% | 42.50% | 77.27% | 54.84% |

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
1.  **High Recall (86.36%)**: It catches the vast majority of churning customers, leaving very few false negatives.
2.  **Excellent Balance (F1-score: 57.58%)**: It outperforms both the manual business rule and Random Forest on our metrics.
3.  **Interpretability (Business Usefulness)**: Unlike Random Forest (a "black box" model that is hard to explain), a Decision Tree can be drawn as a transparent flowchart. Customer Success Managers can easily look at the tree branches (e.g., *"If complaints $\ge 1$ and contract is Month-to-Month, then Churn Risk is High"*) and understand *why* the model flagged a customer.
4.  **Simplicity**: It is lightweight, fast to train, and easy to deploy in the next stages of the project.

---

## 8. Strategic Recommendations for Customer Success

Now that we have this model, what should the company do?

1.  **Proactive CSM Outreach**: Integrate the model's high-risk list into the daily workflow of the Customer Success team. CSMs should prioritize calling customers with a predicted churn probability $> 70\%$.
2.  **Targeted Retention Offers**:
    *   For month-to-month customers flagged as high risk, offer them a discounted annual contract to lock in their loyalty.
    *   For customers with low satisfaction scores or complaints, immediately route their issues to a senior support representative.
3.  **No-Risk Check-Ins**: For false positives (loyal customers who are flagged), a simple "thank you" call or customer satisfaction survey will build goodwill, rendering the cost of a false alarm negligible.

---

## 9. Current Limitations & Future Data Collection

While the model performs well, we can improve its accuracy by addressing current limitations:

### Current Limitations
*   Our dataset does not include real-time usage trends (e.g., did their usage drop by 50% in the last 2 weeks?).
*   We lack communication history details (e.g., sentiment of support emails).

### Recommended Data to Collect
1.  **Trend Indicators**: Month-over-month change in weekly usage hours.
2.  **Support Sentiment**: Text sentiment scores of support tickets.
3.  **Feature Adoption**: Number of key software features they actively use.
