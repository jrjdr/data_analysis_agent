import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

def read_and_process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def analyze_time_series(df):
    results = []
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    results.append("Time Series Analysis Results")
    results.append("=" * 30)
    
    for column in numeric_columns:
        results.append(f"\nAnalysis for {column}")
        results.append("-" * 20)
        
        # Overall trend
        trend = np.polyfit(range(len(df)), df[column], 1)
        results.append(f"Overall trend: {'Increasing' if trend[0] > 0 else 'Decreasing'}")
        
        # Daily pattern
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')[column].mean()
        peak_hour = hourly_avg.idxmax()
        trough_hour = hourly_avg.idxmin()
        results.append(f"Daily pattern: Peak at {peak_hour}:00, Trough at {trough_hour}:00")
        
        # Weekly pattern
        df['dayofweek'] = df['timestamp'].dt.dayofweek
        daily_avg = df.groupby('dayofweek')[column].mean()
        peak_day = daily_avg.idxmax()
        trough_day = daily_avg.idxmin()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        results.append(f"Weekly pattern: Peak on {days[peak_day]}, Trough on {days[trough_day]}")
        
        # Anomalies
        z_scores = np.abs(stats.zscore(df[column]))
        anomalies = df[z_scores > 3]
        if not anomalies.empty:
            results.append(f"Anomalies detected: {len(anomalies)} points")
            results.append(f"First anomaly: {anomalies['timestamp'].iloc[0]}, Value: {anomalies[column].iloc[0]:.2f}")
        else:
            results.append("No significant anomalies detected")
    
    return "\n".join(results)

def save_results(results, output_file):
    try:
        with open(output_file, 'w') as f:
            f.write(results)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    input_file = "temp_csv/excel_data_20250317141159.csv"
    output_file = "pngs/time_trend_results.txt"
    
    df = read_and_process_csv(input_file)
    if df is not None:
        results = analyze_time_series(df)
        save_results(results, output_file)

if __name__ == "__main__":
    main()