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
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 检查是否存在时间列
        if 'timestamp' not in df.columns:
            raise ValueError("数据中没有找到timestamp列，无法进行时间趋势分析")
        
        # 将timestamp转换为datetime类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 设置timestamp为索引
        df.set_index('timestamp', inplace=True)
        
        # 按基站分组进行分析
        results = {}
        
        # 获取所有基站ID
        base_stations = df['base_station_id'].unique()
        
        for station in base_stations:
            station_data = df[df['base_station_id'] == station]
            station_name = station_data['base_station_name'].iloc[0]
            
            # 按小时重采样数据
            hourly_data = station_data.resample('H').mean()
            
            # 计算关键指标的时间趋势
            metrics = ['success_rate', 'active_users', 'signal_strength_dbm', 
                      'downlink_throughput_mbps', 'latency_ms', 'packet_loss_percent']
            
            station_results = {
                'station_name': station_name,
                'metrics': {}
            }
            
            for metric in metrics:
                if metric in hourly_data.columns:
                    # 获取时间序列数据
                    ts_data = hourly_data[metric].dropna()
                    
                    if len(ts_data) < 24:  # 确保有足够的数据点
                        continue
                    
                    # 计算移动平均
                    ts_data_ma = ts_data.rolling(window=3).mean().dropna()
                    
                    # 计算环比增长率
                    growth_rate = ts_data.pct_change().dropna() * 100
                    
                    # 尝试进行时间序列分解
                    try:
                        # 季节性分解
                        decomposition = seasonal_decompose(ts_data, model='additive', period=24)
                        trend = decomposition.trend.dropna()
                        seasonal = decomposition.seasonal.dropna()
                        residual = decomposition.resid.dropna()
                        
                        # 简单预测（使用Holt-Winters方法）
                        if len(ts_data) >= 48:  # 确保有足够的数据进行预测
                            model = ExponentialSmoothing(
                                ts_data, 
                                trend='add', 
                                seasonal='add', 
                                seasonal_periods=24
                            ).fit()
                            forecast = model.forecast(6)  # 预测未来6小时
                        else:
                            forecast = None
                    except:
                        trend = seasonal = residual = forecast = None
                    
                    # 存储结果
                    station_results['metrics'][metric] = {
                        'raw_data': {
                            'timestamps': ts_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                            'values': ts_data.tolist()
                        },
                        'moving_average': {
                            'timestamps': ts_data_ma.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                            'values': ts_data_ma.tolist()
                        },
                        'growth_rate': {
                            'timestamps': growth_rate.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                            'values': growth_rate.tolist()
                        }
                    }
                    
                    # 添加时间序列分解结果
                    if trend is not None:
                        station_results['metrics'][metric]['decomposition'] = {
                            'trend': {
                                'timestamps': trend.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                                'values': trend.tolist()
                            },
                            'seasonal': {
                                'timestamps': seasonal.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                                'values': seasonal.tolist()
                            },
                            'residual': {
                                'timestamps': residual.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                                'values': residual.tolist()
                            }
                        }
                    
                    # 添加预测结果
                    if forecast is not None:
                        station_results['metrics'][metric]['forecast'] = {
                            'timestamps': forecast.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                            'values': forecast.tolist()
                        }
            
            results[station] = station_results
        
        # 保存结果到JSON文件
        with open('time_trend_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return "分析完成，结果已保存到time_trend_analysis_results.json"
    
    except Exception as e:
        return f"分析过程中出现错误: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供CSV文件路径作为参数")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"文件不存在: {csv_path}")
        sys.exit(1)
    
    result = time_trend_analysis(csv_path)
    print(result)