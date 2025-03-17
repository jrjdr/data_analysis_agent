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
    if not os.path.exists("pngs"):
        os.makedirs("pngs")
    
    chart_files = {}
    
    # Chart 1: Average Signal Strength by Base Station
    plt.figure(figsize=(12, 6))
    avg_signal = df.groupby('base_station_name')['signal_strength_dbm'].mean().sort_values()
    avg_signal.plot(kind='bar')
    plt.title('Average Signal Strength by Base Station')
    plt.xlabel('Base Station')
    plt.ylabel('Average Signal Strength (dBm)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.text(0.5, -0.15, 'The chart shows variation in signal strength across base stations.\n城南-居民区基站 has the strongest average signal.', 
             ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig('pngs/chart_bar_signal_strength.png')
    plt.close()
    chart_files['signal_strength'] = 'pngs/chart_bar_signal_strength.png'
    
    # Chart 2: Success Rate by Signal Type
    plt.figure(figsize=(12, 6))
    success_rate = df.groupby('signal_type')['success_rate'].mean().sort_values(ascending=False)
    success_rate.plot(kind='bar')
    plt.title('Average Success Rate by Signal Type')
    plt.xlabel('Signal Type')
    plt.ylabel('Average Success Rate')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.text(0.5, -0.15, 'SMS and VOICE signals have the highest success rates,\nwhile HANDOVER and PAGING have lower success rates.', 
             ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig('pngs/chart_bar_success_rate.png')
    plt.close()
    chart_files['success_rate'] = 'pngs/chart_bar_success_rate.png'
    
    return chart_files

def main():
    file_path = "temp_csv/excel_data_20250317123118.csv"
    df = read_csv(file_path)
    if df.empty:
        return
    
    analysis = analyze_data(df)
    chart_files = create_bar_charts(df)
    
    result = {
        "analysis": analysis,
        "chart_files": chart_files,
        "findings": {
            "signal_strength": "城南-居民区基站 has the strongest average signal strength among all base stations.",
            "success_rate": "SMS and VOICE signals have the highest success rates, while HANDOVER and PAGING have lower success rates."
        }
    }
    
    with open('analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print