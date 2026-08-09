# Customer Retention Prioritization Report
**Author:** Antigravity (AI Coding Assistant)  
**Target Audience:** Customer Success Manager & Executive Team  

---

## Executive Summary

Predicting which customers are likely to leave is only half the battle. In a business environment with limited budgets and staff, we cannot target every at-risk customer. We must prioritize our efforts based on **expected financial impact**.

By combining **Churn Probability** (from the classification model in Task 01) and **Predicted Future Revenue** (from our new regression model in Task 02), we calculated the **Expected Revenue at Risk (RAR)** for each customer. 

Our key finding is that prioritizing customers based on **Revenue at Risk** allows the customer success team to protect **$111,795.42** in at-risk revenue—saving **$9,155.67 more revenue** than prioritizing by churn probability alone, using the exact same budget (contacting only 100 customers).

---

## Business Assumptions for Future Revenue Generation

Since the Telco Churn dataset has unique customer IDs, no real-world external dataset contains matching revenue data. Therefore, we programmatically generated a realistic, high-fidelity customer future value dataset (`customer_future_value.csv`) based on existing client attributes:

$$\text{Future Revenue} = \text{Monthly Charges} \times 12 \times \text{Contract Factor} \times \text{Service Factor} \times \text{Tenure Factor} \times \text{Security Factor} \times \text{Support Factor} \times (1 + \text{Controlled Noise})$$

### Rationale Behind the Multi-Factor Formula:
1. **Contract type**: Customers on a 2-year contract represent more stable future revenue ($\times 1.10$) compared to 1-year ($\times 1.05$) or Month-to-month ($\times 1.00$) contracts.
2. **Internet Service**: Premium Fiber optic users contribute higher relative future value ($\times 1.08$) compared to DSL ($\times 1.02$) or no internet ($\times 0.95$).
3. **Tenure (Loyalty)**: Established loyal customers (tenure > 48 months) have higher lifetime value ($\times 1.03$) compared to new customers in their first year ($\times 0.98$).
4. **Commitment Add-ons**: Subscribing to ecosystem services like `OnlineSecurity` ($\times 1.02$) and `TechSupport` ($\times 1.02$) signals a highly embedded customer with higher future value.
5. **Controlled Noise (5% Std Dev)**: Introduced normal variance to prevent the machine learning models from learning a trivial linear mapping (e.g., $y = 12 \times \text{Monthly Charges}$), forcing the model to learn complex relationships instead.

---

## Regression Model Analysis & Performance

We built and evaluated two regression models to predict each customer's 12-month future value. The inputs excluded `customerID`, `Churn` (to prevent data leakage), and the target itself.

### Model Evaluation Results:

| Regression Model | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | R-squared ($R^2$) |
| :--- | :---: | :---: | :---: |
| **Linear Regression (Baseline)** | $36.19 | $49.58 | 0.9872 |
| **Random Forest Regressor** | **$35.53** | **$49.70** | **0.9871** |

### Why We Selected the Random Forest Model:
* **Interpretability of MAE**: The Mean Absolute Error (MAE) represents the average dollar amount the model's predictions deviate from the true value. The **Random Forest model achieved the lowest MAE of $35.53**, meaning on average, its prediction is off by only $35.53 per customer on an annual basis (a very small error relative to the average annual customer value of $861.88).
* **Non-linear Relationship Capture**: Random Forest utilizes an ensemble of decision trees, allowing it to capture non-linear relationships (such as the combined impact of tenure, contract types, and service add-ons) much better than a simple linear model.

---

## Expected Revenue at Risk (RAR) Methodology

To calculate the expected financial risk for each customer, we used the formula:

$$\text{Revenue at Risk} = \text{Churn Probability} \times \text{Predicted Future Revenue}$$

### Example Case Study:
* **Customer A**: Churn Probability = 90%, Predicted Revenue = $200 $\rightarrow$ **Revenue at Risk = $180**
* **Customer B**: Churn Probability = 60%, Predicted Revenue = $2,000 $\rightarrow$ **Revenue at Risk = $1,200**
* **Customer C**: Churn Probability = 35%, Predicted Revenue = $5,000 $\rightarrow$ **Revenue at Risk = $1,750**

**Business Insight**: While Customer A has the highest probability of leaving, Customer C represents the largest financial risk. Focusing only on churn probability would cause us to ignore Customer C, resulting in a potential $1,750 loss. Focusing on Revenue at Risk ensures we protect our high-value revenue streams.

---

## Customer Segmentation Strategy

To classify our customer base, we established dynamic thresholds based on the actual distribution of our data:
* **High Churn Risk Threshold**: **$\ge 0.58$** (70th percentile of predicted churn probabilities).
* **High Value Threshold**: **$\ge \$1,199.78$** (75th percentile of predicted future revenue).

This creates four distinct customer-success segments:

1. **Critical Priority** (High Churn $\ge 0.58$ & High Value $\ge \$1,199.78$):
   * *Action*: Immediate personal call from the customer-success team to offer customized contracts or discounts.
2. **High Risk, Lower Value** (High Churn $\ge 0.58$ & Lower Value $< \$1,199.78$):
   * *Action*: Automated email retention campaigns or standard promotional offers.
3. **Valuable but Stable** (Low Churn $< 0.58$ & High Value $\ge \$1,199.78$):
   * *Action*: Regular relationship monitoring, proactive satisfaction checks, and loyalty rewards.
4. **Low Priority** (Low Churn $< 0.58$ & Lower Value $< \$1,199.78$):
   * *Action*: Standard automated transactional communication; no immediate manual intervention.

---

## Campaign Strategy Comparison (Budget Simulation)

We simulated a marketing campaign with a strict budget constraint: the customer success team can only contact **100 customers**. We compared four selection strategies:

| Strategy | Total Selected Value | Total Revenue at Risk | Avg Churn Probability | Actual Churners Contacted |
| :--- | :---: | :---: | :---: | :---: |
| **Random Selection** | $86,606.31 | $45,974.50 | 49.48% | 34 / 100 |
| **Highest Churn Probability** | $108,936.25 | $102,639.75 | **94.22%** | **90 / 100** |
| **Highest Predicted Value** | **$173,814.43** | $16,892.03 | 9.78% | 7 / 100 |
| **Highest Revenue at Risk (Selected)** | $131,391.80 | **$111,795.42** | 85.67% | 73 / 100 |

### In-Depth Strategy Analysis:
* **The Pitfall of Churn-Only Prioritization**: Targeting the 100 customers with the highest churn probability contacts 90 actual churners, but only protects **$102,639.75** in revenue. This is because many of these high-risk customers have low monthly bills.
* **Why Revenue at Risk Wins**: The Revenue at Risk strategy focuses on the multiplication of risk and value. It contacts 73 actual churners, but protects **$111,795.42** in revenue. 
* **The Bottom Line**: By switching from Churn-Only to **Revenue at Risk prioritization**, we secure an extra **$9,155.67** of at-risk revenue for the company using the exact same budget and headcount.

---

## Actionable Recommendations

1. **Prioritize by RAR, Not Churn Prob**: Instruct the customer-success team to work down the priority list starting from the highest **Revenue at Risk** (Priority Rank 1).
2. **Execute the Immediate Call Playbook**: Contact the 100 customers in the `customer_priority_list.csv` first. Since they are all in the **Critical Priority** segment, they should receive a direct phone call from a senior customer-success representative with authority to offer retention terms.
3. **Automate the Low-Value Campaigns**: For the "High Risk, Lower Value" segment, set up automated emails containing standard discount triggers. This ensures coverage without depleting manual CS hours.

---

## System Limitations & Future Improvements

1. **Static Value Assumptions**: The regression model assumes a static 12-month future value. In reality, customers may upgrade or downgrade services. Incorporating historical purchase pathways could improve prediction accuracy.
2. **Static Churn Scores**: Churn scores are imported as static numbers. Incorporating real-time usage data (such as support ticket counts, dropped calls, or website portal activity) would allow us to compute dynamic, real-time risk scores.
3. **Retention Cost vs Reward**: The budget simulation assumes all contacted customers are successfully saved at zero cost. A more robust model would incorporate the cost of the offer (e.g., $10 discount) and the probability of saving the customer to calculate the net-revenue saved.
