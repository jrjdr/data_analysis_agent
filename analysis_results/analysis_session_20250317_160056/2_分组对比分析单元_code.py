import pandas as pd
import numpy as np
from pathlib import Path

def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def analyze_distribution(df):
    result = "Data Distribution Analysis:\n" + "="*30 + "\n\n"
    
    for col in df.columns:
        result += f"{col}:\n"
        if df[col].dtype in ['int64', 'float64']:
            result += f"  Mean: {df[col].mean():.2f}\n"
            result += f"  Median: {df[col].median():.2f}\n"
            result += f"  Std Dev: {df[col].std():.2f}\n"
        else:
            value_counts = df[col].value_counts()
            result += f"  Top 3 categories:\n"
            for i, (value, count) in enumerate(value_counts.head(3).items()):
                result += f"    {value}: {count} ({count/len(df)*100:.2f}%)\n"
        result += "\n"
    
    return result

def group_comparison(df):
    result = "Group Comparison Analysis:\n" + "="*30 + "\n\n"
    
    grouping_columns = ['Region', 'Service_Type', 'Priority']
    target_columns = ['Resolution_Time_Days', 'Customer_Satisfaction']
    
    for group_col in grouping_columns:
        result += f"Grouping by {group_col}:\n"
        grouped = df.groupby(group_col)
        
        for target_col in target_columns:
            result += f"  {target_col}:\n"
            agg_result = grouped[target_col].agg(['mean', 'median', 'std']).round(2)
            for index, row in agg_result.iterrows():
                result += f"    {index}: Mean={row['mean']}, Median={row['median']}, Std Dev={row['std']}\n"
        
        result += "\n"
    
    return result

def save_results(content, output_file):
    try:
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    file_path = "temp_csv/excel_data_20250317160056.csv"
    output_file = "pngs/group_comparison_results.txt"
    
    df = load_data(file_path)
    if df is None:
        return
    
    distribution_analysis = analyze_distribution(df)
    group_analysis = group_comparison(df)
    
    full_analysis = (
        "Customer Complaint Analysis Report\n"
        "==================================\n\n"
        f"{distribution_analysis}\n"
        f"{group_analysis}"
    )
    
    save_results(full_analysis, output_file)

if __name__ == "__main__":
    main()