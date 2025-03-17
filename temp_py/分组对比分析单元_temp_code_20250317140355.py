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
        results.append(f"    Most Common: {df[col].mode().values[0]}")
    
    return "\n".join(results)

def group_comparison(df):
    results = []
    results.append("Group Comparison:")
    
    # Compare servers
    results.append("  Server Comparison:")
    server_stats = df.groupby('server_name')['cpu_usage_percent', 'memory_usage_percent'].mean()
    for server, stats in server_stats.iterrows():
        results.append(f"    {server}:")
        results.append(f"      Avg CPU Usage: {stats['cpu_usage_percent']:.2f}%")
        results.append(f"      Avg Memory Usage: {stats['memory_usage_percent']:.2f}%")
    
    # Compare resource types
    results.append("\n  Resource Type Comparison:")
    resource_stats = df.groupby('resource_type')['query_rate_per_sec', 'active_connections'].mean()
    for resource, stats in resource_stats.iterrows():
        results.append(f"    {resource}:")
        results.append(f"      Avg Query Rate: {stats['query_rate_per_sec']:.2f}/sec")
        results.append(f"      Avg Active Connections: {stats['active_connections']:.2f}")
    
    # Compare event types
    results.append("\n  Event Type Comparison:")
    event_stats = df.groupby('event_type')['cpu_usage_percent', 'memory_usage_percent'].mean()
    for event, stats in event_stats.iterrows():
        results.append(f"    {event}:")
        results.append(f"      Avg CPU Usage: {stats['cpu_usage_percent']:.2f}%")
        results.append(f"      Avg Memory Usage: {stats['memory_usage_percent']:.2f}%")
    
    return "\n".join(results)

def save_results(content, output_file):
    try:
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
    
    column_analysis = analyze_columns(df)
    group_analysis = group_comparison(df)
    
    results = f"Data Analysis Results\n{'='*20}\n\n{column_analysis}\n\n{group_analysis}"
    save_results(results, output_file)

if __name__ == "__main__":
    main()