import pandas as pd
import numpy as np
import json
import sys
from datetime import datetime

def analyze_bar_chart_data(file_path):
    """
    分析适合柱状图展示的数据并保存结果到JSON文件
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 初始化结果字典
        results = {}
        
        # 1. 基站性能对比分析
        station_performance = df.groupby('base_station_name').agg({
            'success_rate': 'mean',
            'downlink_throughput_mbps': 'mean',
            'uplink_throughput_mbps': 'mean',
            'latency_ms': 'mean',
            'active_users': 'mean'
        }).round(2)
        
        results['base_station_performance'] = station_performance.to_dict()
        
        # 2. 信号类型分布分析
        signal_type_counts = df['signal_type'].value_counts().to_dict()
        results['signal_type_distribution'] = signal_type_counts
        
        # 3. 状态分布分析
        status_counts = df['status'].value_counts().to_dict()
        results['status_distribution'] = status_counts
        
        # 4. 资源使用率分析 - 按基站分组
        resource_usage = df.groupby('base_station_name').agg({
            'resource_block_usage_percent': 'mean',
            'cpu_usage_percent': 'mean',
            'memory_usage_percent': 'mean'
        }).round(2)
        
        results['resource_usage_by_station'] = resource_usage.to_dict()
        
        # 5. 按小时分析流量和用户数
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_metrics = df.groupby('hour').agg({
            'active_users': 'mean',
            'call_attempts': 'mean',
            'downlink_throughput_mbps': 'mean',
            'uplink_throughput_mbps': 'mean'
        }).round(2)
        
        results['hourly_metrics'] = hourly_metrics.to_dict()
        
        # 6. 按信号类型分析成功率
        signal_success_rate = df.groupby('signal_type')['success_rate'].mean().round(4).to_dict()
        results['signal_type_success_rate'] = signal_success_rate
        
        # 7. 基站温度对比
        temperature_by_station = df.groupby('base_station_name')['temperature_celsius'].agg(['mean', 'min', 'max']).round(2)
        results['temperature_by_station'] = temperature_by_station.to_dict()
        
        # 8. 信号强度和质量对比
        signal_metrics = df.groupby('base_station_name').agg({
            'signal_strength_dbm': 'mean',
            'signal_quality_db': 'mean'
        }).round(2)
        
        results['signal_metrics_by_station'] = signal_metrics.to_dict()
        
        # 9. 资源块使用率分布
        resource_block_bins = [0, 20, 40, 60, 80, 100]
        resource_block_labels = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
        df['resource_block_bin'] = pd.cut(df['resource_block_usage_percent'], bins=resource_block_bins, labels=resource_block_labels)
        resource_block_dist = df['resource_block_bin'].value_counts().to_dict()
        results['resource_block_usage_distribution'] = resource_block_dist
        
        # 10. 延迟分布
        latency_bins = [0, 10, 20, 30, 40, 50]
        latency_labels = ['0-10ms', '11-20ms', '21-30ms', '31-40ms', '41-50ms']
        df['latency_bin'] = pd.cut(df['latency_ms'], bins=latency_bins, labels=latency_labels)
        latency_dist = df['latency_bin'].value_counts().to_dict()
        results['latency_distribution'] = latency_dist
        
        # 保存结果到JSON文件
        with open('bar_chart_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        return "分析完成，结果已保存到 bar_chart_analysis_results.json"
    
    except Exception as e:
        return f"分析过程中出错: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'temp_csv/excel_data_20250317093536.csv'  # 使用默认路径
    
    result = analyze_bar_chart_data(file_path)
    print(result)