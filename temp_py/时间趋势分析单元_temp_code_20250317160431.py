import pandas as pd
import numpy as np
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

def read_and_process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        df['Date_Reported'] = pd.to_datetime(df['Date_Reported'])
        df['Resolution_Date'] = pd.to_datetime(df['Resolution_Date'])
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def analyze_time_trends(df):
    daily_complaints = df.groupby('Date_Reported').size().resample('D').sum().fillna(0)
    weekly_complaints = daily_complaints.resample('W').sum()
    monthly_complaints = daily_complaints.resample('M').sum()

    result = seasonal_decompose(daily_complaints, model='additive', period=7)
    trend = result.trend
    seasonal = result.seasonal
    residual = result.resid

    anomalies = residual[abs(residual) > 2 * residual.std()]

    return daily_complaints, weekly_complaints, monthly_complaints, trend, seasonal, anomalies

def format_results(daily, weekly, monthly, trend, seasonal, anomalies):
    result = "Time Trend Analysis Results\n"
    result += "===========================\n\n"

    result += "1. Daily Complaint Trends\n"
    result += "--------------------------\n"
    result += f"Average daily complaints: {daily.mean():.2f}\n"
    result += f"Maximum daily complaints: {daily.max()} on {daily.idxmax().strftime('%Y-%m-%d')}\n"
    result += f"Minimum daily complaints: {daily.min()} on {daily.idxmin().strftime('%Y-%m-%d')}\n\n"

    result += "2. Weekly Complaint Trends\n"
    result += "---------------------------\n"
    result += f"Average weekly complaints: {weekly.mean():.2f}\n"
    result += f"Maximum weekly complaints: {weekly.max()} for week ending {weekly.idxmax().strftime('%Y-%m-%d')}\n"
    result += f"Minimum weekly complaints: {weekly.min()} for week ending {weekly.idxmin().strftime('%Y-%m-%d')}\n\n"

    result += "3. Monthly Complaint Trends\n"
    result += "----------------------------\n"
    result += f"Average monthly complaints: {monthly.mean():.2f}\n"
    result += f"Maximum monthly complaints: {monthly.max()} for {monthly.idxmax().strftime('%Y-%m')}\n"
    result += f"Minimum monthly complaints: {monthly.min()} for {monthly.idxmin().strftime('%Y-%m')}\n\n"

    result += "4. Trend Analysis\n"
    result += "-------------------\n"
    result += f"Trend start value: {trend.dropna().iloc[0]:.2f}\n"
    result += f"Trend end value: {trend.dropna().iloc[-1]:.2f}\n"
    result += f"Overall trend: {'Increasing' if trend.dropna().iloc[-1] > trend.dropna().iloc[0] else 'Decreasing'}\n\n"

    result += "5. Seasonal Patterns\n"
    result += "---------------------\n"
    result += f"Highest seasonal factor: {seasonal.max():.2f} (Day of week: {seasonal.idxmax().dayofweek})\n"
    result += f"Lowest seasonal factor: {seasonal.min():.2f} (Day of week: {seasonal.idxmin().dayofweek})\n\n"

    result += "6. Anomalies\n"
    result += "--------------\n"
    result += f"Number of anomalies detected: {len(anomalies)}\n"