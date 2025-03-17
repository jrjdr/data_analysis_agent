import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def time_trend_analysis(csv_path):
    """
    对CSV文件进行时间趋势分析
    
    参数:
        csv_path: CSV文件路径
    
    返回:
        分析结果字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 检查是否存在时间列
        if 'timestamp' not in df.columns:
            raise ValueError("数据中没有timestamp列，无法进行时间趋势分析")
        
        # 将timestamp转换为datetime类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 设置timestamp为索引
        df_time = df.set_index('timestamp')
        
        # 选择需要分析的指标列
        metrics = ['success_rate', 'active_users', 'signal_strength_dbm', 
                  'downlink_throughput_mbps', 'latency_ms', 'packet_loss_percent']
        
        results = {
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_file": os.path.basename(csv_path),
            "time_range": {
                "start": df['timestamp'].min().strftime("%Y-%m-%d %H:%M:%S"),
                "end": df['timestamp'].max().strftime("%Y-%m-%d %H:%M:%S"),
                "duration_days": (df['timestamp'].max() - df['timestamp'].min()).days
            },
            "metrics": {}
        }
        
        # 按基站分组进行分析
        for station_id in df['base_station_id'].unique():
            station_data = df[df['base_station_id'] == station_id]
            station_name = station_data['base_station_name'].iloc[0]
            
            results["metrics"][station_id] = {
                "station_name": station_name,
                "metrics_analysis": {}
            }
            
            # 对每个指标进行分析
            for metric in metrics:
                # 重采样为小时数据
                hourly_data = station_data.set_index('timestamp')[metric].resample('H').mean()
                
                # 计算每日平均值
                daily_data = station_data.set_index('timestamp')[metric].resample('D').mean()
                
                # 计算移动平均
                if len(hourly_data) >= 24:
                    ma_24h = hourly_data.rolling(window=24).mean()
                else:
                    ma_24h = None
                
                # 计算增长率（环比）
                if len(daily_data) >= 2:
                    growth_rate = daily_data.pct_change().dropna()
                    avg_growth_rate = growth_rate.mean()
                else:
                    avg_growth_rate = None
                
                # 进行时间序列分解（如果有足够的数据点）
                seasonal_result = None
                if len(daily_data) >= 14:  # 至少需要两周的数据
                    try:
                        decomposition = seasonal_decompose(daily_data, model='additive', period=7)
                        seasonal_result = {
                            "trend": decomposition.trend.dropna().tolist(),
                            "seasonal": decomposition.seasonal.dropna().tolist(),
                            "timestamps": daily_data.index[decomposition.seasonal.dropna().index].strftime("%Y-%m-%d").tolist()
                        }
                    except:
                        seasonal_result = None
                
                # 简单预测（如果有足够的数据点）
                forecast = None
                if len(daily_data) >= 7:
                    try:
                        model = ExponentialSmoothing(
                            daily_data, 
                            trend='add', 
                            seasonal='add' if len(daily_data) >= 14 else None,
                            seasonal_periods=7 if len(daily_data) >= 14 else None
                        ).fit()
                        
                        # 预测未来7天
                        forecast_horizon = 7
                        forecast_values = model.forecast(forecast_horizon)
                        forecast = {
                            "dates": pd.date_range(
                                start=daily_data.index[-1] + pd.Timedelta(days=1), 
                                periods=forecast_horizon
                            ).strftime("%Y-%m-%d").tolist(),
                            "values": forecast_values.tolist()
                        }
                    except:
                        forecast = None
                
                # 保存分析结果
                results["metrics"][station_id]["metrics_analysis"][metric] = {
                    "hourly_data": {
                        "timestamps": hourly_data.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                        "values": hourly_data.tolist()
                    },
                    "daily_data": {
                        "timestamps": daily_data.index.strftime("%Y-%m-%d").tolist(),
                        "values": daily_data.tolist()
                    },
                    "moving_average_24h": None if ma_24h is None else {
                        "timestamps": ma_24h.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                        "values": ma_24h.dropna().tolist()
                    },
                    "average_daily_growth_rate": None if avg_growth_rate is None else float(avg_growth_rate),
                    "seasonal_decomposition": seasonal_result,
                    "forecast": forecast,
                    "statistics": {
                        "min": float(station_data[metric].min()),
                        "max": float(station_data[metric].max()),
                        "mean": float(station_data[metric].mean()),
                        "median": float(station_data[metric].median()),
                        "std": float(station_data[metric].std())
                    }
                }
        
        return results
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python script.py <csv文件路径>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    results = time_trend_analysis(csv_path)
    
    # 将结果保存为JSON文件
    with open('time_trend_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成，结果已保存到 time_trend_analysis_results.json")