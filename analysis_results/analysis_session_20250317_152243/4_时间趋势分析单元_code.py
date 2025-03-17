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
    
    # 获取数值型列
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_columns) == 0:
        return "No numeric columns found for analysis."
    
    # Overall trends
    results.append("Overall Trends:")
    for column in numeric_columns:
        # 确保没有NaN值
        valid_data = df[column].dropna()
        if len(valid_data) > 1:  # 至少需要两个点来计算趋势
            trend = stats.linregress(range(len(valid_data)), valid_data.values)
            trend_direction = "increasing" if trend.slope > 0 else "decreasing"
            results.append(f"  - {column}: {trend_direction} trend (slope: {trend.slope:.4f})")
        else:
            results.append(f"  - {column}: Insufficient data for trend analysis")
    
    # Daily patterns
    results.append("\nDaily Patterns:")
    try:
        daily_avg = df[numeric_columns].groupby(df.index.hour).mean()
        for column in daily_avg.columns:
            if not daily_avg[column].isna().all():  # 确保不全是NaN
                peak_hour = daily_avg[column].idxmax()
                trough_hour = daily_avg[column].idxmin()
                results.append(f"  - {column}: Peak at {peak_hour}:00, Trough at {trough_hour}:00")
            else:
                results.append(f"  - {column}: No valid data for daily pattern analysis")
    except Exception as e:
        results.append(f"  Error analyzing daily patterns: {e}")
    
    # Weekly patterns
    results.append("\nWeekly Patterns:")
    try:
        weekly_avg = df[numeric_columns].groupby(df.index.dayofweek).mean()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for column in weekly_avg.columns:
            if not weekly_avg[column].isna().all():  # 确保不全是NaN
                peak_day = weekly_avg[column].idxmax()
                trough_day = weekly_avg[column].idxmin()
                results.append(f"  - {column}: Peak on {days[peak_day]}, Trough on {days[trough_day]}")
            else:
                results.append(f"  - {column}: No valid data for weekly pattern analysis")
    except Exception as e:
        results.append(f"  Error analyzing weekly patterns: {e}")
    
    # Anomalies
    results.append("\nAnomalies (Z-score > 3):")
    for column in numeric_columns:
        try:
            # 确保没有NaN值
            valid_data = df[column].dropna()
            if len(valid_data) > 1:  # 需要至少两个点来计算z-score
                z_scores = np.abs(stats.zscore(valid_data))
                anomalies = valid_data[z_scores > 3]
                if not anomalies.empty:
                    results.append(f"  - {column}:")
                    for idx, value in anomalies.items():
                        results.append(f"    {idx}: {value:.2f}")
                else:
                    results.append(f"  - {column}: No anomalies detected")
            else:
                results.append(f"  - {column}: Insufficient data for anomaly detection")
        except Exception as e:
            results.append(f"  - {column}: Error detecting anomalies: {e}")
    
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
        # 打印数据集信息，帮助调试
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"DataFrame dtypes:\n{df.dtypes}")
        
        # 只保留数值型列进行分析
        results = analyze_time_series(df)
        save_results(results, output_file)
    else:
        print("Failed to read data file.")

if __name__ == "__main__":
    main()