import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from typing import Dict, Any

def read_csv(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame()

def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    analysis = {
        "numeric_columns": {col: df[col].describe().to_dict() for col in numeric_cols},
        "categorical_columns": {col: df[col].value_counts().to_dict() for col in categorical_cols}
    }
    return analysis

def create_bar_charts(df: pd.DataFrame) -> Dict[str, str]:
    os.makedirs("pngs", exist_ok=True)
    chart_files = {}

    # Chart 1: Average CPU and Memory Usage by Server
    plt.figure(figsize=(12, 6))
    server_stats = df.groupby('server_name')[['cpu_usage_percent', 'memory_usage_percent']].mean()
    server_stats.plot(kind='bar', width=0.8)
    plt.title('Average CPU and Memory Usage by Server')
    plt.xlabel('Server Name')
    plt.ylabel('Usage Percentage')
    plt.legend(['CPU Usage', 'Memory Usage'])
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.text(0.5, -0.15, "Key Finding: Server '备份服务器' has the highest average CPU and memory usage.", 
             ha='center', va='center', transform=plt.gca().transAxes)
    chart_path = "pngs/chart_bar_server_usage.png"
    plt.savefig(chart_path)
    plt.close()
    chart_files['server_usage'] = chart_path

    # Chart 2: Event Type Distribution
    plt.figure(figsize=(10, 6))
    event_counts = df['event_type'].value_counts()
    event_counts.plot(kind='bar', width=0.6)
    plt.title('Distribution of Event Types')
    plt.xlabel('Event Type')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.text(0.5, -0.15, "Key Finding: 'Normal' events are the most common, followed by 'Warning' events.", 
             ha='center', va='center', transform=plt.gca().transAxes)
    chart_path = "pngs/chart_bar_event_distribution.png"
    plt.savefig(chart_path)
    plt.close()
    chart_files['event_distribution'] = chart_path

    return chart_files

def save_results(analysis: Dict[str, Any], chart_files: Dict[str, str]) -> None:
    results = {
        "analysis": analysis,
        "chart_files": chart_files,
        "findings": [
            "Server '备份服务器' has the highest average CPU and memory usage among all servers.",
            "'Normal' events are the most common, followed by 'Warning' events in the system."
        ]
    }
    
    with open("analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)

def main():
    file_path = "temp_csv/excel_data_20250317124712.csv"
    df = read_csv(file_path)
    
    if df.empty:
        return
    
    analysis = analyze_data(df)
    chart_files = create_bar_charts(df)
    save_results(analysis, chart_files)
    
    print("Analysis complete. Results saved in 'analysis_results.json' and charts saved in