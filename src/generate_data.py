import os
import csv
import random
import math

def generate_dataset():
    random.seed(42)
    os.makedirs('data', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Schema columns
    columns = [
        "customer_id", "tenure_months", "monthly_spend", "contract_type", 
        "product_plan", "payment_method", "late_payments_6m", "support_tickets_3m", 
        "complaints_6m", "average_weekly_usage_hours", "days_since_last_login", 
        "satisfaction_score", "auto_renew", "churned"
    ]
    
    contract_types = ["Month-to-Month", "One-Year", "Two-Year"]
    product_plans = ["Basic", "Standard", "Premium"]
    payment_methods = ["Credit Card", "Bank Transfer", "Electronic Check", "Mailed Check"]
    
    rows = []
    num_records = 1000
    
    for i in range(1, num_records + 1):
        cust_id = f"CUST-{1000 + i}"
        
        # Numeric base features
        tenure = random.randint(1, 72)
        monthly_spend = round(random.uniform(20.0, 150.0), 2)
        
        # Categorical
        if tenure > 36:
            contract = random.choice(["One-Year", "Two-Year", "Two-Year"])
        elif tenure > 12:
            contract = random.choice(["Month-to-Month", "One-Year", "One-Year"])
        else:
            contract = random.choice(["Month-to-Month", "Month-to-Month", "One-Year"])
            
        plan = random.choice(product_plans)
        pay_method = random.choice(payment_methods)
        
        # Behavioral features
        complaint_prob = 0.05
        if contract == "Month-to-Month":
            complaint_prob += 0.1
        complaints = 1 if random.random() < complaint_prob else 0
        if complaints == 1 and random.random() < 0.3:
            complaints = random.randint(1, 3)
            
        # Support tickets
        support_tickets = random.randint(0, 5)
        if complaints > 0:
            support_tickets += random.randint(1, 4)
            
        # Late payments
        late_payments = 0
        if random.random() < 0.15:
            late_payments = random.randint(1, 6)
            
        usage_hours = round(random.uniform(2.0, 40.0) + (10.0 if plan == "Premium" else 0.0), 1)
        
        days_last_login = random.randint(0, 30)
        if random.random() < 0.05:
            days_last_login = random.randint(31, 60) # inactive
            
        satisfaction = random.randint(1, 5)
        if complaints > 0:
            satisfaction = random.choice([1, 2, 2, 3])
        elif late_payments > 2:
            satisfaction = random.choice([2, 3, 3, 4])
        elif tenure > 24:
            satisfaction = random.choice([4, 5, 5])
            
        auto_renew = 1 if random.random() < 0.6 else 0
        if contract == "Month-to-Month":
            auto_renew = 1 if random.random() < 0.3 else 0
            
        # Churn probability logic
        score = 0.0
        score -= 0.04 * tenure
        score += 0.005 * monthly_spend
        score += 1.5 * complaints
        score += 0.4 * late_payments
        score -= 0.8 * satisfaction
        score += 0.03 * days_last_login
        score -= 1.0 * auto_renew
        
        if contract == "Month-to-Month":
            score += 0.8
        elif contract == "Two-Year":
            score -= 1.0
            
        # Sigmoid function for probability
        prob = 1.0 / (1.0 + math.exp(-score))
        churned = 1 if random.random() < prob else 0
        
        row = {
            "customer_id": cust_id,
            "tenure_months": tenure,
            "monthly_spend": monthly_spend,
            "contract_type": contract,
            "product_plan": plan,
            "payment_method": pay_method,
            "late_payments_6m": late_payments,
            "support_tickets_3m": support_tickets,
            "complaints_6m": complaints,
            "average_weekly_usage_hours": usage_hours,
            "days_since_last_login": days_last_login,
            "satisfaction_score": satisfaction,
            "auto_renew": auto_renew,
            "churned": churned
        }
        rows.append(row)
        
    # Inject anomalies:
    # 1. Duplicates: duplicate 5 rows
    dup_indices = [12, 115, 234, 567, 888]
    for idx in dup_indices:
        rows.append(rows[idx].copy())
        
    # 2. Missing values (empty strings)
    null_sat_indices = [5, 45, 92, 150, 222, 305, 412, 550, 601, 715, 800, 899, 912, 945, 980]
    for idx in null_sat_indices:
        rows[idx]["satisfaction_score"] = ""
        
    # days_since_last_login: 10 rows set to empty string
    null_login_indices = [15, 122, 280, 399, 444, 580, 690, 770, 850, 930]
    for idx in null_login_indices:
        rows[idx]["days_since_last_login"] = ""
        
    # auto_renew: 5 rows set to empty string
    null_renew_indices = [25, 250, 480, 710, 990]
    for idx in null_renew_indices:
        rows[idx]["auto_renew"] = ""
        
    # 3. Incorrect Data Types (monthly_spend with '$')
    type_spend_indices = [10, 80, 140, 210, 320, 430, 520, 610, 740, 830, 905, 915, 925, 935, 945, 955, 965, 975, 985, 995]
    for idx in type_spend_indices:
        rows[idx]["monthly_spend"] = f"${rows[idx]['monthly_spend']}"
        
    # 4. Impossible/Invalid values
    # Negative monthly spend
    rows[3]["monthly_spend"] = -50.0
    rows[154]["monthly_spend"] = -120.5
    
    # Negative tenure
    rows[17]["tenure_months"] = -12
    rows[320]["tenure_months"] = -1
    
    # Out of range satisfaction score
    rows[88]["satisfaction_score"] = 9
    rows[470]["satisfaction_score"] = -2
    
    # Negative support tickets
    rows[102]["support_tickets_3m"] = -3
    rows[680]["support_tickets_3m"] = -1
    
    # Shuffle list
    random.shuffle(rows)
    
    # Write to CSV
    csv_path = 'data/customer_churn.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} customer records (with anomalies) in {csv_path}")

if __name__ == "__main__":
    generate_dataset()
