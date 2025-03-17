import pandas as pd
import numpy as np
import json
import sys
from collections import defaultdict

def analyze_data(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        results = {}

        # 1. 基站信号类型分布
        signal_type_counts = df['signal_type'].value_counts().to_dict()
        results['signal_type_distribution'] = signal_type_counts

        # 2. 基站状态分布
        status_counts = df['status'].value_counts().to_dict()
        results['status_distribution'] = status_counts

        # 3. 基站平均成功率排名（Top 5）
        avg_success_rate = df.groupby('base_station_name')['success_rate'].mean().sort_values(ascending=False)
        results['top_5_base_stations_by_success_rate'] = avg_success_rate.head(5).to_dict()

        # 4. 信号类型平均吞吐量对比
        avg_throughput = df.groupby('signal_type')[['downlink_throughput_mbps', 'uplink_throughput_mbps']].mean()
        results['avg_throughput_by_signal_type'] = avg_throughput.to_dict()

        # 5. 基站资源块使用率分布
        resource_block_usage_bins = pd.cut(df['resource_block_usage_percent'], bins=5)
        resource_block_usage_counts = resource_block_usage_bins.value_counts().sort_index()
        results['resource_block_usage_distribution'] = {str(k): v for k, v in resource_block_usage_counts.items()}

        # 6. 活跃用户数量分布
        active_users_bins = pd.cut(df['active_users'], bins=5)
        active_users_counts = active_users_bins.value_counts().sort_index()
        results['active_users_distribution'] = {str(k): v for k, v in active_users_counts.items()}

        # 7. CPU使用率区间分布
        cpu_usage_bins = pd.cut(df['cpu_usage_percent'], bins=[0, 25, 50, 75, 100, float('inf')])
        cpu_usage_counts = cpu_usage_bins.value_counts().sort_index()
        results['cpu_usage_distribution'] = {str(k): v for k, v in cpu_usage_counts.items()}

        # 8. 内存使用率区间分布
        memory_usage_bins = pd.cut(df['memory_usage_percent'], bins=[0, 25, 50, 75, 100, float('inf')])
        memory_usage_counts = memory_usage_bins.value_counts().sort_index()
        results['memory_usage_distribution'] = {str(k): v for k, v in memory_usage_counts.items()}

        # 9. 温度区间分布
        temperature_bins = pd.cut(df['temperature_celsius'], bins=5)
        temperature_counts = temperature_bins.value_counts().sort_index()
        results['temperature_distribution'] = {str(k): v for k, v in temperature_counts.items()}

        # 10. 每小时平均调用尝试次数
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_call_attempts = df.groupby('hour')['call_attempts'].mean().round().astype(int)
        results['hourly_avg_call_attempts'] = hourly_call_attempts.to_dict()

        return results

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: