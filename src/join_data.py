import os
import pandas as pd

def validate_join(churn_df, value_df):
    print("--- DATA QUALITY & JOIN VALIDATION CHECKS ---")
    
    # 1. Shape Checks
    #بدي اطبع عدد الكوستمرز بكل داتا سيت 
    print(f"Total customers in Churn Dataset (Dataset 1): {len(churn_df)}")
    print(f"Total customers in Future Value Dataset (Dataset 2): {len(value_df)}")
    
    # 2. Duplicate Check in both datasets
    #لو في customerID مكرر، الموديل رح يحسب أرباح هاد العميل مرتين
    churn_dupes = churn_df.duplicated(subset=['customerID']).sum()
    value_dupes = value_df.duplicated(subset=['customerID']).sum()
    print(f"Duplicate customer IDs in Churn Dataset: {churn_dupes}")
    print(f"Duplicate customer IDs in Future Value Dataset: {value_dupes}")
    
    # 3. Perform Outer Join to check for mismatching IDs on either side
    outer_merged = pd.merge(churn_df, value_df, on='customerID', how='outer', indicator=True)
#الاوتر بجيب كل العملاء من داتا 1 وداتا 2 حتى لو ما كانو موجودين بالتنين 
#left_only: العميل موجود بملف الـ Churn بس مش موجود بملف الـ Future Value.
# right_only: العميل موجود بملف الـ Future Value بس مش موجود بملف الـ Churn.
# both: العميل موجود بالملفين ومطابق $100\%$.
    churn_only = (outer_merged['_merge'] == 'left_only').sum()
    value_only = (outer_merged['_merge'] == 'right_only').sum()
    both_matched = (outer_merged['_merge'] == 'both').sum()
    
    print(f"Customers appearing ONLY in Churn Dataset (unmatched): {churn_only}")
    print(f"Customers appearing ONLY in Future Value Dataset (unmatched): {value_only}")
    print(f"Successfully matched customers (appearing in both): {both_matched}")
    
    # 4. Check for Missing (NaN) values in future revenue after join
    # We perform an inner join for final usage
    joined_df = pd.merge(churn_df, value_df, on='customerID', how='inner')
#how='inner': بياخد فقط العملاء المطابقين بالطرفين وبيضمن عدم وجود خانات فارغة.

    missing_revenue = joined_df['future_12_month_revenue_if_retained'].isna().sum()
    print(f"Missing (NaN) future revenue values after join: {missing_revenue}")
    
    # 5. Check for Invalid or Negative Revenue Values
    negative_revenue = (joined_df['future_12_month_revenue_if_retained'] <= 0).sum()
    print(f"Negative or zero revenue values after join: {negative_revenue}")
    
    # Summary of Business Importance of correct joins
    print("\n--- BUSINESS EXPLANATION: WHY CORRECT JOINING IS IMPORTANT ---")

    explanation = (
        "In a real-world business setting, database joins are the foundation of decision making.\n"
        "If the join is performed incorrectly:\n"
        "1. Mismatched customerIDs would lead to targeting the wrong customers for retention campaigns, wasting budget.\n"
        "2. Duplicate customer records would double-count revenues, artificially inflating projected budgets and ROI.\n"#والأرباح المتوقعة (ROI).
        "3. Missing revenue values or zero values would cause the system to ignore high-value customers, risking massive revenue loss.\n"
        "Ensuring 100% data integrity during this join guarantees that resources are allocated efficiently."
    )
    print(explanation)
    
    # Return the clean joined dataset if valid
    if churn_only == 0 and value_only == 0 and missing_revenue == 0 and negative_revenue == 0:
        print("\n[SUCCESS] Data join validation passed successfully! No anomalies found.")
        return joined_df
    else:
        print("\n[WARNING] Anomalies detected during data validation. Please inspect output logs.")
        return joined_df

def main():
    # Setup paths relative to project root
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    data_dir = os.path.join(project_dir, 'data')
    
    churn_path = os.path.join(data_dir, 'customer_churn.csv')
    value_path = os.path.join(data_dir, 'customer_future_value.csv')
    joined_output_path = os.path.join(data_dir, 'joined_customer_data.csv')
    
    # Check if files exist
    if not os.path.exists(churn_path):
        print(f"Error: {churn_path} does not exist.")
        return
    if not os.path.exists(value_path):
        print(f"Error: {value_path} does not exist.")
        return
        
    print("Loading datasets...")
    churn_df = pd.read_csv(churn_path)
    value_df = pd.read_csv(value_path)
    
    # Run the join validation
    joined_df = validate_join(churn_df, value_df)#افحص البيانات واربطها
    
    # Save the clean joined dataset for modeling in the next steps
    #index=False:بدون ما تضيف عمود أرقام أسطر زوائد .
    
    joined_df.to_csv(joined_output_path, index=False)
    print(f"Saved joined dataset to: {joined_output_path}")

if __name__ == "__main__":
    main()
