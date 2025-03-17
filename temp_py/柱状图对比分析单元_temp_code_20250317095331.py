import pandas as pd
import numpy as np
import json
import sys
from typing import Dict, Any

def analyze_data(file_path: str) -> Dict[str, Any]:
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        results = {}
        
        # 1. 分析不同基站的平均成功率
        base_station_success = df.groupby('base_station_name')['success_rate'].mean().sort_values(ascending=False)
        results['base_station_success'] = base_station_success.to_dict()
        
        # 2. 信号类型计数
        signal_type_counts = df['signal_type'].value_counts()
        results['signal_type_counts'] = signal_type_counts.to_dict()
        
        # 3. 状态分布
        status_distribution = df['status'].value_counts(normalize=True) * 100
        results['status_distribution'] = status_distribution.to_dict()
        
        # 4. 资源块使用率分布
        resource_block_bins = pd.cut(df['resource_block_usage_percent'], bins=5)
        resource_block_distribution = resource_block_bins.value_counts().sort_index()
        results['resource_block_distribution'] = {str(k): v for k, v in resource_block_distribution.to_dict().items()}
        
        # 5. 平均吞吐量（上行和下行）对比
        throughput_comparison = {
            'Downlink': df['downlink_throughput_mbps'].mean(),
            'Uplink': df['uplink_throughput_mbps'].mean()
        }
        results['throughput_comparison'] = throughput_comparison
        
        # 6. CPU和内存使用率分布
        usage_bins = pd.cut(df['cpu_usage_percent'], bins=5)
        cpu_usage_distribution = usage_bins.value_counts().sort_index()
        results['cpu_usage_distribution'] = {str(k): v for k, v in cpu_usage_distribution.to_dict().items()}
        
        usage_bins = pd.cut(df['memory_usage_percent'], bins=5)
        memory_usage_distribution = usage_bins.value_counts().sort_index()
        results['memory_usage_distribution'] = {str(k): v for k, v in memory_usage_distribution.to_dict().items()}
        
        # 7. 温度分布
        temp_bins = pd.cut(df['temperature_celsius'], bins=5)
        temp_distribution = temp_bins.value_counts().sort_index()
        results['temperature_distribution'] = {str(k): v for k, v in temp_distribution.to_dict().items()}
        
        # 8. 活跃用户数量最多的前5个时间段
        top_active_users = df.groupby('timestamp')['active_users'].sum().sort_values(ascending=False).head(5)
        results['top_active_users'] = top_active_users.to_dict()
        
        return results
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analysis_results = analyze_data(file_path)
    
    # 将结果保存为JSON文件
    with open('bar_chart_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=4)
    
    print("Analysis complete. Results saved to bar_chart_analysis_results.json")