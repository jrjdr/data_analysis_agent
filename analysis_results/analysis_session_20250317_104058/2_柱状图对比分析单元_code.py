import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def analyze_for_bar_charts(csv_path):
    """分析CSV数据并生成适合柱状图展示的数据"""
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 存储所有分析结果
        analysis_results = {}
        
        # 1. 基站对比分析
        # 各基站的成功率平均值
        station_success_rate = df.groupby('base_station_name')['success_rate'].mean().reset_index()
        station_success_rate = station_success_rate.sort_values('success_rate', ascending=False)
        analysis_results['station_success_rate'] = station_success_rate.to_dict('records')
        
        # 2. 信号类型分析
        # 不同信号类型的数量统计
        signal_type_counts = df['signal_type'].value_counts().reset_index()
        signal_type_counts.columns = ['signal_type', 'count']
        analysis_results['signal_type_counts'] = signal_type_counts.to_dict('records')
        
        # 3. 状态分析
        # 不同状态的数量统计
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        analysis_results['status_counts'] = status_counts.to_dict('records')
        
        # 4. 基站资源使用情况对比
        # 各基站的资源块使用率平均值
        station_resource_usage = df.groupby('base_station_name')['resource_block_usage_percent'].mean().reset_index()
        station_resource_usage = station_resource_usage.sort_values('resource_block_usage_percent', ascending=False)
        analysis_results['station_resource_usage'] = station_resource_usage.to_dict('records')
        
        # 5. 基站性能指标对比
        # 各基站的下行吞吐量平均值
        station_downlink = df.groupby('base_station_name')['downlink_throughput_mbps'].mean().reset_index()
        station_downlink = station_downlink.sort_values('downlink_throughput_mbps', ascending=False)
        analysis_results['station_downlink_throughput'] = station_downlink.to_dict('records')
        
        # 6. 基站延迟对比
        station_latency = df.groupby('base_station_name')['latency_ms'].mean().reset_index()
        station_latency = station_latency.sort_values('latency_ms')
        analysis_results['station_latency'] = station_latency.to_dict('records')
        
        # 7. 信号类型与成功率的关系
        signal_success_rate = df.groupby('signal_type')['success_rate'].mean().reset_index()
        signal_success_rate = signal_success_rate.sort_values('success_rate', ascending=False)
        analysis_results['signal_type_success_rate'] = signal_success_rate.to_dict('records')
        
        # 8. 基站硬件状态对比
        # CPU使用率
        station_cpu = df.groupby('base_station_name')['cpu_usage_percent'].mean().reset_index()
        station_cpu = station_cpu.sort_values('cpu_usage_percent', ascending=False)
        analysis_results['station_cpu_usage'] = station_cpu.to_dict('records')
        
        # 内存使用率
        station_memory = df.groupby('base_station_name')['memory_usage_percent'].mean().reset_index()
        station_memory = station_memory.sort_values('memory_usage_percent', ascending=False)
        analysis_results['station_memory_usage'] = station_memory.to_dict('records')
        
        # 温度
        station_temp = df.groupby('base_station_name')['temperature_celsius'].mean().reset_index()
        station_temp = station_temp.sort_values('temperature_celsius', ascending=False)
        analysis_results['station_temperature'] = station_temp.to_dict('records')
        
        # 9. 按小时统计活跃用户数
        # 提取小时信息
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_users = df.groupby('hour')['active_users'].mean().reset_index()
        analysis_results['hourly_active_users'] = hourly_users.to_dict('records')
        
        # 10. 信号强度分布
        # 将信号强度分为几个区间
        bins = [-120, -110, -100, -90, -80, -70]
        labels = ['-120 to -110', '-110 to -100', '-100 to -90', '-90 to -80', '-80 to -70']
        df['signal_strength_range'] = pd.cut(df['signal_strength_dbm'], bins=bins, labels=labels)
        signal_strength_dist = df['signal_strength_range'].value_counts().reset_index()
        signal_strength_dist.columns = ['signal_strength_range', 'count']
        signal_strength_dist = signal_strength_dist.sort_values('signal_strength_range')
        analysis_results['signal_strength_distribution'] = signal_strength_dist.to_dict('records')
        
        return analysis_results
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return {"error": str(e)}

def main():
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"错误: 文件 '{csv_path}' 不存在")
        sys.exit(1)
    
    try:
        # 执行分析
        results = analyze_for_bar_charts(csv_path)
        
        # 保存结果到JSON文件
        with open('bar_chart_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        print(f"分析完成，结果已保存到 'bar_chart_analysis_results.json'")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()