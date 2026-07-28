import os
import shutil
import urllib.request

def download_or_copy_dataset():
    os.makedirs('data', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    csv_path = 'data/customer_churn.csv'
    url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
    
    print("Preparing the Kaggle Telco Customer Churn dataset...")
    
    # 1. Try to download the dataset from GitHub first
    try:
        print(f"Downloading from public source: {url}")
        with urllib.request.urlopen(url, timeout=10) as response, open(csv_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Successfully downloaded and saved dataset to {csv_path}")
        return
    except Exception as e:
        print(f"Web download failed ({e}). Checking for local files...")
        
    # 2. Try to copy from local student_intelligence_system repository if available
    local_source = r"D:\student_intelligence_system\Git-and-Github\data\customer_churn.csv"
    if os.path.exists(local_source):
        try:
            shutil.copy(local_source, csv_path)
            print(f"Successfully copied dataset from local path {local_source} to {csv_path}")
            return
        except Exception as e:
            print(f"Failed to copy local file: {e}")
            
    # 3. Try searching in Hp Downloads folder
    downloads_source = r"C:\Users\Hp\Downloads\archive\WA_Fn-UseC_-Telco-Customer-Churn.csv"
    if os.path.exists(downloads_source):
        try:
            shutil.copy(downloads_source, csv_path)
            print(f"Successfully copied dataset from Downloads archive {downloads_source} to {csv_path}")
            return
        except Exception as e:
            print(f"Failed to copy from Downloads: {e}")
            
    print("Error: Could not obtain the Kaggle Telco Customer Churn dataset.")

if __name__ == "__main__":
    download_or_copy_dataset()
