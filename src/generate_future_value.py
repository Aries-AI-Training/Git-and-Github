import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_future_revenue(df, seed=42):#عشان اضمن الارقام العشوائية يلي رح تنتج تضلها تتكرر كل ما نشغل الكود 
    # Set seed for reproducibility of noise
    np.random.seed(seed)
    
    # 1. Start with baseline annual charges
    # اي ايراد مستقبلي هو دفع هالشهر الحالي ضرب 12 
    #لو بدفع 50 بالشهر ف 50*12 بالسنة
    base_annual = df['MonthlyCharges'] * 12
    
    # 2. Map Contract Factors (longer contracts = more stable/committed revenue)
    #هاد فكرتو نعدل ال renew المتوقع يعني لو العميل بيدفع 100 ف بالسنة 1200 ف بنحكي انو هاد رح يكن اكتر استقرار ف بنتوقع قيمته المستقبلية اعلى : مثلا
    # 1200*1.10=1320
    # يلي بوقع سنتين بتوقع منو اعلى ب 10%
    contract_map = {
        'Month-to-month': 1.00,
        'One year': 1.05,
        'Two year': 1.10
    }
    #روح على عمود Contract وكل قيمة فيه استبدلها بالرقم الموجود بال contract_map
    contract_factor = df['Contract'].map(contract_map).fillna(1.00)
    
    # 3. Map Internet Service Factors (fiber optic premium tier = higher future value potential)
   #نوع الانترنت
    service_map = {
        'Fiber optic': 1.08, # الفايبر اغلى فالكوستمر قيمته المستقبلية اعلى
        'DSL': 1.02, #زيادة بسيطة يا دوبك 
        'No': 0.95# يلي ما عنده نت قللناه
    }
    service_factor = df['InternetService'].map(service_map).fillna(1.00)
    
#مدة البقاء بالشركة
#اذا عدد الاشهر اقل من 12 شهر يعني سنى فالعميل جديد وممكن يلغي بسهولة بنخفض قيمته2 المية
#يين سنة و 4 سنوات عميل مستقر طبيعي 1 
# اكتر من 4 سنوات (48 شهر ) ف هو قديم ومضمون فبنزيده ب 3 بالمية  
#np.where نفس if-else بس اسرع بالعمود الكامل 
    tenure_factor = np.where(df['tenure'] <= 12, 0.98,
                             np.where(df['tenure'] <= 48, 1.00, 1.03))

    # 5. Map Security & Support Add-on Factors (high commitment to product ecosystem)
    #خدمات اضافية الحماية والدعم الفني
    security_factor = np.where(df['OnlineSecurity'] == 'Yes', 1.02, 1.00)
    support_factor = np.where(df['TechSupport'] == 'Yes', 1.02, 1.00)
    
    # 6. Apply factors and controlled noise (5% standard deviation)
    noise = np.random.normal(loc=0.0, scale=0.05, size=len(df))
    #loc=0.0 : يعني افريج الراندوم صفر , احيانا بتزيد القيمة شوي واحيانا بتنقص , فش انحياز لاشي معين
    #scale=0.05 : يعني ال std = 5% , التغيير بكون+-5% 
    # يعني التغيير بسيط بحدود الطبيعي
    #size=len(df)=بننشئ أرقام عشوائية بنفس عدد صفوف العملاء

#هاد عشان اعطي الشركة العمود المطلوب يلي مش  موجود اصلا  
# انا بدي احسبو
    future_revenue = (base_annual * 
                      contract_factor * 
                      service_factor * 
                      tenure_factor * 
                      security_factor * 
                      support_factor * 
                      (1.0 + noise))
    
    # Ensure no negative or zero values (minimum future revenue is MonthlyCharges * 6)
    min_allowable = df['MonthlyCharges'] * 6
#لو عميل بيدفع 20 دينار بالشهر 
#ب 6 اشهر =120 , ف مستحيل نتوقع منه اقل من 120

    future_revenue = np.maximum(future_revenue, min_allowable)
    #هون انا بدي اضمن انو ولا عميل رح تطلع قيمتو المستقبلية صفر او سالب او رقم مش منطقي 
    #ي عميل قيمته بتنزل تحت حد الأمان، np.maximum بترفعها فوراً لـ min_allowable
    
    # Round to 2 decimal places (standard currency format)
    return np.round(future_revenue, 2)

def main():
    # Setup paths relative to project root
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(src_dir)
    data_dir = os.path.join(project_dir, 'data')
    outputs_dir = os.path.join(project_dir, 'outputs')
    charts_dir = os.path.join(outputs_dir, 'charts')
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)
    
    input_path = os.path.join(data_dir, 'customer_churn.csv')
    output_path = os.path.join(data_dir, 'customer_future_value.csv')
    eda_chart_path = os.path.join(charts_dir, '07_future_revenue_eda.png')
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    print(f"Reading dataset: {input_path}")
    df = pd.read_csv(input_path)
    
    # Pre-clean just in case MonthlyCharges is non-numeric
    df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce').fillna(0.0)
    df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce').fillna(0)
    
    print("Generating customer future value dataset...")

 # Save Dataset 2
    df['future_12_month_revenue_if_retained'] = generate_future_revenue(df)
    value_df = df[['customerID', 'future_12_month_revenue_if_retained']]
    value_df.to_csv(output_path, index=False)
    print(f"Successfully generated and saved dataset to: {output_path}")
    print(f"Dataset preview:\n{value_df.head()}")
    
    # ------------------ Target EDA ------------------

    print("Generating EDA charts for the target variable...")
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    #plt.subplots(1, 2): بتجهز لوحة رسم مقسومة لعمودين (شارت يسار وشارت يمين).
    
    
    # Chart 1: Distribution of Future Revenue
    sns.histplot(df['future_12_month_revenue_if_retained'], kde=True, ax=axes[0], color='#1e3a8a')
    #يرسم خط ناعم فوق الأعمدة حتى يبين شكل التوزيع.
    axes[0].set_title('Distribution of Future 12-Month Revenue', fontsize=12, pad=10)
    axes[0].set_xlabel('Predicted Revenue if Retained ($)', fontsize=10)
    axes[0].set_ylabel('Customer Count', fontsize=10)
    
    # Chart 2: Correlation between Monthly Charges and Future Revenue
    sns.scatterplot(x='MonthlyCharges', y='future_12_month_revenue_if_retained', data=df, 
                    alpha=0.6, ax=axes[1], color='#3b82f6', edgecolor='none')
    #بيقاطِع الدفع الشهري الحالي للعميل مع قيمته المستقبيلة المتوقعة.
    # Add a reference line showing direct 12x MonthlyCharges to visual the deviation
    min_x, max_x = df['MonthlyCharges'].min(), df['MonthlyCharges'].max()
    axes[1].plot([min_x, max_x], [min_x * 12, max_x * 12], color='#b91c1c', linestyle='--', label='Trivial 12x MonthlyCharges')
    
    axes[1].set_title('Monthly Charges vs Future 12-Month Revenue', fontsize=12, pad=10)
    axes[1].set_xlabel('Monthly Charges ($)', fontsize=10)
    axes[1].set_ylabel('Future 12-Month Revenue ($)', fontsize=10)
    axes[1].legend(frameon=True)#يعرض اسم الخط الأحمر.
    
    plt.tight_layout() #هاي بتعمل ترتيب تلقائي للرسم حتى ما تتداخل العناوين.
    plt.savefig(eda_chart_path, dpi=150)
    plt.close()
    print(f"Saved EDA chart to: {eda_chart_path}")
    
    # Calculate some brief stats for sanity check
    correlation = df['MonthlyCharges'].corr(df['future_12_month_revenue_if_retained'])
    print(f"Correlation between MonthlyCharges and Future Revenue: {correlation:.4f}")
    print(f"Summary Statistics:\n{df['future_12_month_revenue_if_retained'].describe()}")
#corr(): حساب معامل الارتباط لمعرفة قوة العلاقة خطياً بين الدفع الشهري والدخل المتوقع مستقبلاً.describe(): طباعة المتوسط ($Mean$)، الحد الأدنى والني الأدنى، والـ Percentiles لضمان سلامة الأرقام.
if __name__ == "__main__":
    main()
