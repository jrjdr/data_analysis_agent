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
            raise ValueError("数据中没有timestamp列，无法进行时间趋势分析")
        
        # 将timestamp转换为datetime类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 设置timestamp为索引
        df_time = df.set_index('timestamp')
        
        # 选择需要分析的指标列
        metrics = ['success_rate', 'active_users', 'signal_strength_dbm', 
                  'downlink_throughput_mbps', 'latency_ms', 'packet_loss_percent']
        
        results = {}
        
        # 按基站分组进行分析
        for station_id in df['base_station_id'].unique():
            station_data = df[df['base_station_id'] == station_id]
            station_results = {}
            
            # 1. 按小时聚合数据
            hourly_data = station_data.set_index('timestamp').resample('H').mean()
            
            # 2. 按天聚合数据
            daily_data = station_data.set_index('timestamp').resample('D').mean()
            
            for metric in metrics:
                metric_results = {}
                
                # 跳过缺失值过多的指标
                if hourly_data[metric].isna().sum() > len(hourly_data) * 0.3:
                    continue
                
                # 1. 时间序列趋势分析
                hourly_trend = hourly_data[metric].fillna(method='ffill').to_dict()
                hourly_trend = {k.strftime('%Y-%m-%d %H:%M:%S'): float(v) for k, v in hourly_trend.items()}
                metric_results['hourly_trend'] = hourly_trend
                
                # 2. 计算小时级别的移动平均线 (3小时)
                if len(hourly_data) >= 3:
                    ma_3h = hourly_data[metric].rolling(window=3).mean().fillna(method='bfill').to_dict()
                    ma_3h = {k.strftime('%Y-%m-%d %H:%M:%S'): float(v) for k, v in ma_3h.items()}
                    metric_results['moving_average_3h'] = ma_3h
                
                # 3. 日趋势
                if len(daily_data) >= 1:
                    daily_trend = daily_data[metric].fillna(method='ffill').to_dict()
                    daily_trend = {k.strftime('%Y-%m-%d'): float(v) for k, v in daily_trend.items()}
                    metric_results['daily_trend'] = daily_trend
                
                # 4. 季节性分析 (如果有足够的数据)
                if len(hourly_data) >= 24:
                    try:
                        # 对小时数据进行季节性分解
                        decomposition = seasonal_decompose(
                            hourly_data[metric].fillna(hourly_data[metric].mean()), 
                            model='additive', 
                            period=24  # 假设24小时为一个周期
                        )
                        
                        # 提取趋势和季节性成分
                        trend = decomposition.trend.dropna().to_dict()
                        trend = {k.strftime('%Y-%m-%d %H:%M:%S'): float(v) for k, v in trend.items()}
                        
                        seasonal = decomposition.seasonal.dropna().to_dict()
                        seasonal = {k.strftime('%Y-%m-%d %H:%M:%S'): float(v) for k, v in seasonal.items()}
                        
                        metric_results['trend_component'] = trend
                        metric_results['seasonal_component'] = seasonal
                    except:
                        # 季节性分解可能失败，忽略错误
                        pass
                
                # 5. 简单预测 (如果有足够的数据)
                if len(hourly_data) >= 24:
                    try:
                        # 使用指数平滑模型进行简单预测
                        model = ExponentialSmoothing(
                            hourly_data[metric].fillna(method='ffill'),
                            trend='add',
                            seasonal='add',
                            seasonal_periods=24
                        ).fit()
                        
                        # 预测未来12小时
                        forecast = model.forecast(12)
                        forecast_dict = forecast.to_dict()
                        forecast_dict = {k.strftime('%Y-%m-%d %H:%M:%S'): float(v) for k, v in forecast_dict.items()}
                        
                        metric_results['forecast_next_12h'] = forecast_dict
                    except:
                        # 预测可能失败，忽略错误
                        pass
                
                # 6. 计算环比变化率 (相邻小时)
                if len(hourly_data) >= 2:
                    hourly_data['pct_change'] = hourly_data[metric].pct_change() * 100
                    pct_change = hourly_data['pct_change'].dropna().to_dict()
                    pct_change = {k.strftime('%Y-%m-%d %H:%M:%S'): float(v) for k, v in pct_change.items()}
                    metric_results['hourly_change_rate'] = pct_change
                
                station_results[metric] = metric_results
            
            results[station_id] = station_results
        
        # 保存结果到JSON文件
        with open('time_trend_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "message": "时间趋势分析完成，结果已保存到time_trend_analysis_results.json"}
    
    except Exception as e:
        return {"status": "error", "message": f"分析过程中出错: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供CSV文件路径作为参数")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"文件不存在: {csv_path}")
        sys.exit(1)
    
    result = time_trend_analysis(csv_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))