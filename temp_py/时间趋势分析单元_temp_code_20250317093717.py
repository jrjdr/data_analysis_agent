import pandas as pd
import numpy as np
import json
import sys
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import argparse
from typing import Dict, List, Any

def time_trend_analysis(file_path: str) -> Dict[str, Any]:
    """
    对CSV文件进行时间趋势分析
    
    Args:
        file_path: CSV文件路径
    
    Returns:
        包含时间趋势分析结果的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查是否存在时间列
        if 'timestamp' not in df.columns:
            raise ValueError("数据中没有timestamp列，无法进行时间趋势分析")
        
        # 将timestamp列转换为datetime类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 设置timestamp为索引
        df.set_index('timestamp', inplace=True)
        
        # 按基站和信号类型分组的结果字典
        results = {
            "hourly_trends": {},
            "daily_trends": {},
            "moving_averages": {},
            "seasonal_decomposition": {},
            "forecasts": {}
        }
        
        # 按小时重采样关键指标
        hourly_metrics = ['success_rate', 'active_users', 'downlink_throughput_mbps', 
                          'latency_ms', 'packet_loss_percent']
        
        hourly_data = {}
        for metric in hourly_metrics:
            # 按小时重采样并计算平均值
            hourly_series = df[metric].resample('H').mean()
            hourly_data[metric] = {
                "timestamps": hourly_series.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                "values": hourly_series.values.tolist()
            }
        
        results["hourly_trends"] = hourly_data
        
        # 按天重采样关键指标
        daily_data = {}
        for metric in hourly_metrics:
            # 按天重采样并计算平均值、最大值、最小值
            daily_series = df[metric].resample('D').agg(['mean', 'max', 'min'])
            daily_data[metric] = {
                "timestamps": daily_series.index.strftime('%Y-%m-%d').tolist(),
                "mean": daily_series['mean'].values.tolist(),
                "max": daily_series['max'].values.tolist(),
                "min": daily_series['min'].values.tolist()
            }
        
        results["daily_trends"] = daily_data
        
        # 计算移动平均
        moving_avg_data = {}
        for metric in ['success_rate', 'downlink_throughput_mbps', 'latency_ms']:
            # 按小时重采样后计算移动平均
            hourly_series = df[metric].resample('H').mean()
            
            # 计算6小时移动平均
            ma_6h = hourly_series.rolling(window=6).mean().dropna()
            # 计算12小时移动平均
            ma_12h = hourly_series.rolling(window=12).mean().dropna()
            
            moving_avg_data[metric] = {
                "timestamps": hourly_series.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                "original": hourly_series.values.tolist(),
                "ma_6h": {
                    "timestamps": ma_6h.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "values": ma_6h.values.tolist()
                },
                "ma_12h": {
                    "timestamps": ma_12h.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "values": ma_12h.values.tolist()
                }
            }
        
        results["moving_averages"] = moving_avg_data
        
        # 季节性分析
        seasonal_data = {}
        for metric in ['success_rate', 'active_users']:
            # 按小时重采样
            hourly_series = df[metric].resample('H').mean()
            
            # 确保数据长度足够进行季节性分析
            if len(hourly_series) >= 24:  # 至少需要一天的数据
                # 进行季节性分解
                decomposition = seasonal_decompose(hourly_series, model='additive', period=24)
                
                seasonal_data[metric] = {
                    "timestamps": hourly_series.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "trend": decomposition.trend.dropna().values.tolist(),
                    "seasonal": decomposition.seasonal.dropna().values.tolist(),
                    "residual": decomposition.resid.dropna().values.tolist()
                }
        
        results["seasonal_decomposition"] = seasonal_data
        
        # 简单预测
        forecast_data = {}
        for metric in ['success_rate', 'downlink_throughput_mbps']:
            hourly_series = df[metric].resample('H').mean()
            
            if len(hourly_series) >= 48:  # 至少需要两天的数据
                # 使用指数平滑模型进行预测
                train_data = hourly_series[:-12]  # 使用除最后12小时外的数据进行训练
                
                # 创建Holt-Winters模型
                model = ExponentialSmoothing(
                    train_data, 
                    trend='add', 
                    seasonal='add', 
                    seasonal_periods=24
                ).fit()
                
                # 预测未来12小时
                forecast = model.forecast(12)
                
                forecast_data[metric] = {
                    "historical_timestamps": train_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "historical_values": train_data.values.tolist(),
                    "forecast_timestamps": forecast.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "forecast_values": forecast.values.tolist()
                }
        
        results["forecasts"] = forecast_data
        
        # 按基站分析
        if 'base_station_id' in df.reset_index().columns:
            station_trends = {}
            for station in df.reset_index()['base_station_id'].unique():
                station_df = df[df.reset_index()['base_station_id'] == station]
                
                # 按小时重采样计算每个基站的成功率
                hourly_success = station_df['success_rate'].resample('H').mean()
                
                station_trends[station] = {
                    "timestamps": hourly_success.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "success_rate": hourly_success.values.tolist()
                }
            
            results["station_trends"] = station_trends
        
        return results
    
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='时间趋势分析')
    parser.add_argument('file_path', help='CSV文件路径')
    parser.add_argument('--output', default='time_trend_analysis_results.json', help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    results = time_trend_analysis(args.file_path)
    
    # 保存结果到JSON文件
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"分析结果已保存到 {args.output}")

if __name__ == "__main__":
    main()