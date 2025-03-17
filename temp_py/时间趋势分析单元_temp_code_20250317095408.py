import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import json
import sys
from datetime import datetime, timedelta

def time_trend_analysis(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查是否存在时间列
        if 'timestamp' not in df.columns:
            raise ValueError("No timestamp column found in the dataset.")
        
        # 将timestamp列转换为datetime类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # 选择需要分析的数值列
        numeric_columns = ['success_rate', 'active_users', 'downlink_throughput_mbps', 'latency_ms']
        
        results = {}
        
        for column in numeric_columns:
            # 重采样到小时级别
            hourly_data = df[column].resample('H').mean()
            
            # 计算日增长率
            daily_growth_rate = hourly_data.resample('D').last().pct_change()
            
            # 计算7天移动平均
            moving_average_7d = hourly_data.rolling(window=7*24).mean()
            
            # 季节性分解
            decomposition = seasonal_decompose(hourly_data, model='additive', period=24)
            
            # 简单预测（指数平滑）
            model = ExponentialSmoothing(hourly_data, trend='add', seasonal='add', seasonal_periods=24)
            fit_model = model.fit()
            forecast = fit_model.forecast(steps=24)  # 预测未来24小时
            
            results[column] = {
                'hourly_data': hourly_data.to_dict(),
                'daily_growth_rate': daily_growth_rate.to_dict(),
                'moving_average_7d': moving_average_7d.to_dict(),
                'trend': decomposition.trend.to_dict(),
                'seasonal': decomposition.seasonal.to_dict(),
                'forecast': forecast.to_dict()
            }
        
        # 保存结果到JSON文件
        with open('time_trend_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=4, default=str)
        
        print("Analysis completed. Results saved to 'time_trend_analysis_results.json'.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
    else:
        file_path = sys.argv[1]
        time_trend_analysis(file_path)