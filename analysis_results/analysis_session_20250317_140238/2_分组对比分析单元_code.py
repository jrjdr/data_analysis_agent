import pandas as pd
import numpy as np
from pathlib import Path

def read_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def analyze_columns(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    results = []
    results.append("Numeric Columns Analysis:")
    for col in numeric_cols:
        results.append(f"  {col}:")
        results.append(f"    Mean: {df[col].mean():.2f}")
        results.append(f"    Median: {df[col].median():.2f}")
        results.append(f"    Std Dev: {df[col].std():.2f}")
    
    results.append("\nCategorical Columns Analysis:")
    for col in categorical_cols:
        results.append(f"  {col}:")
        results.append(f"    Unique Values: {df[col].nunique()}")
        # 添加错误处理，防止没有众数或众数为NaN的情况
        if not df[col].mode().empty:
            mode_value = df[col].mode().values[0]
            if pd.notna(mode_value):
                results.append(f"    Most Common: {mode_value}")
            else:
                results.append(f"    Most Common: N/A (NaN values)")
        else:
            results.append(f"    Most Common: N/A (No mode found)")
    
    return "\n".join(results)

def group_comparison(df):
    results = []
    results.append("Group Comparison:")
    
    # 修复：使用列表而不是元组来选择多个列
    # Compare servers
    if 'server_name' in df.columns:
        results.append("  Server Comparison:")
        # 使用列表 [] 而不是元组 () 来选择多列
        server_stats = df.groupby('server_name')[['cpu_usage_percent', 'memory_usage_percent']].mean()
        for server, stats in server_stats.iterrows():
            results.append(f"    {server}:")
            results.append(f"      Avg CPU Usage: {stats['cpu_usage_percent']:.2f}%")
            results.append(f"      Avg Memory Usage: {stats['memory_usage_percent']:.2f}%")
    else:
        results.append("  Server Comparison: 'server_name' column not found in dataset")
    
    # Compare resource types
    if 'resource_type' in df.columns and 'query_rate_per_sec' in df.columns and 'active_connections' in df.columns:
        results.append("\n  Resource Type Comparison:")
        # 使用列表选择多列
        resource_stats = df.groupby('resource_type')[['query_rate_per_sec', 'active_connections']].mean()
        for resource, stats in resource_stats.iterrows():
            results.append(f"    {resource}:")
            results.append(f"      Avg Query Rate: {stats['query_rate_per_sec']:.2f}/sec")
            results.append(f"      Avg Active Connections: {stats['active_connections']:.2f}")
    else:
        results.append("\n  Resource Type Comparison: Required columns not found in dataset")
    
    # Compare event types
    if 'event_type' in df.columns:
        results.append("\n  Event Type Comparison:")
        # 使用列表选择多列
        event_stats = df.groupby('event_type')[['cpu_usage_percent', 'memory_usage_percent']].mean()
        for event, stats in event_stats.iterrows():
            results.append(f"    {event}:")
            results.append(f"      Avg CPU Usage: {stats['cpu_usage_percent']:.2f}%")
            results.append(f"      Avg Memory Usage: {stats['memory_usage_percent']:.2f}%")
    else:
        results.append("\n  Event Type Comparison: 'event_type' column not found in dataset")
    
    return "\n".join(results)

def save_results(content, output_file):
    try:
        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    input_file = "temp_csv/excel_data_20250317140237.csv"
    output_file = "pngs/group_comparison_results.txt"
    
    df = read_csv(input_file)
    if df is None:
        return
    
    # 检查数据框是否为空
    if df.empty:
        print("Warning: The dataframe is empty.")
        save_results("Data Analysis Results\n====================\n\nThe dataset is empty.", output_file)
        return
    
    column_analysis = analyze_columns(df)
    group_analysis = group_comparison(df)
    
    results = f"Data Analysis Results\n{'='*20}\n\n{column_analysis}\n\n{group_analysis}"
    save_results(results, output_file)

if __name__ == "__main__":
    main()