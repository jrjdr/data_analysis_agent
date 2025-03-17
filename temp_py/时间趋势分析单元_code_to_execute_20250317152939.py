import pandas as pd
import numpy as np
from scipy import stats
import os

def read_and_process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def analyze_time_series(df):
    results = []
    
    # Overall trends
    results.append("Overall Trends:")
    for column in df.select_dtypes(include=[np.number]).columns:
        trend = stats.linregress(range(len(df)), df[column])
        trend_direction = "increasing" if trend.slope > 0 else "decreasing"
        results.append(f"  - {column}: {trend_direction} trend (slope: {trend.slope:.4f})")
    
    # Daily patterns
    results.append("\nDaily Patterns:")
    daily_avg = df.groupby(df.index.hour).mean()
    for column in daily_avg.columns:
        peak_hour = daily_avg[column].idxmax()
        trough_hour = daily_avg[column].idxmin()
        results.append(f"  - {column}: Peak at {peak_hour}:00, Trough at {trough_hour}:00")
    
    # Weekly patterns
    results.append("\nWeekly Patterns:")
    weekly_avg = df.groupby(df.index.dayofweek).mean()
    for column in weekly_avg.columns:
        peak_day = weekly_avg[column].idxmax()
        trough_day = weekly_avg[column].idxmin()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        results.append(f"  - {column}: Peak on {days[peak_day]}, Trough on {days[trough_day]}")
    
    # Anomalies
    results.append("\nAnomalies (Z-score > 3):")
    for column in df.select_dtypes(include=[np.number]).columns:
        z_scores = np.abs(stats.zscore(df[column]))
        anomalies = df[z_scores > 3]
        if not anomalies.empty:
            results.append(f"  - {column}:")
            for idx, value in anomalies[column].items():
                results.append(f"    {idx}: {value:.2f}")
    
    return "\n".join(results)

def save_results(results, output_file):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(results)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    input_file = "temp_csv/excel_data_20250317152243.csv"
    output_file = "pngs/time_trend_results.txt"
    
    df = read_and_process_csv(input_file)
    if df is not None:
        results = analyze_time_series(df)
        save_results(results, output_file)

if __name__ == "__main__":
    main()