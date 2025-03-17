import pandas as pd
import numpy as np
import json
import sys
import os
from collections import defaultdict

def analyze_pie_chart_data(csv_path):
    """
    分析CSV数据，提取适合饼图展示的比例数据
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 初始化结果字典
        pie_chart_data = {}
        
        # 1. 分析信号类型分布
        signal_type_counts = df['signal_type'].value_counts()
        total_signals = signal_type_counts.sum()
        pie_chart_data['signal_type_distribution'] = {
            'title': '信号类型分布',
            'description': '各种信号类型在总信号中的占比',
            'data': {signal: count/total_signals for signal, count in signal_type_counts.items()}
        }
        
        # 2. 分析状态分布
        status_counts = df['status'].value_counts()
        total_status = status_counts.sum()
        pie_chart_data['status_distribution'] = {
            'title': '状态分布',
            'description': '各种状态在总记录中的占比',
            'data': {status: count/total_status for status, count in status_counts.items()}
        }
        
        # 3. 分析基站分布
        station_counts = df['base_station_name'].value_counts()
        total_stations = station_counts.sum()
        pie_chart_data['base_station_distribution'] = {
            'title': '基站分布',
            'description': '各基站数据记录在总记录中的占比',
            'data': {station: count/total_stations for station, count in station_counts.items()}
        }
        
        # 4. 分析成功率和失败率的平均分布
        avg_success_rate = df['success_rate'].mean()
        avg_failure_rate = df['failure_rate'].mean()
        pie_chart_data['avg_success_failure_rate'] = {
            'title': '平均成功/失败率',
            'description': '通信成功率与失败率的平均分布',
            'data': {
                '成功率': avg_success_rate,
                '失败率': avg_failure_rate
            }
        }
        
        # 5. 分析资源块使用率分布
        # 将资源块使用率分成几个区间
        resource_bins = [0, 25, 50, 75, 100]
        resource_labels = ['0-25%', '25-50%', '50-75%', '75-100%']
        resource_counts = pd.cut(df['resource_block_usage_percent'], bins=resource_bins, labels=resource_labels).value_counts()
        total_resource = resource_counts.sum()
        pie_chart_data['resource_usage_distribution'] = {
            'title': '资源块使用率分布',
            'description': '不同资源块使用率区间的分布',
            'data': {label: count/total_resource for label, count in resource_counts.items()}
        }
        
        # 6. 分析CPU使用率分布
        cpu_bins = [0, 25, 50, 75, 100, float('inf')]
        cpu_labels = ['0-25%', '25-50%', '50-75%', '75-100%', '>100%']
        cpu_counts = pd.cut(df['cpu_usage_percent'], bins=cpu_bins, labels=cpu_labels).value_counts()
        total_cpu = cpu_counts.sum()
        pie_chart_data['cpu_usage_distribution'] = {
            'title': 'CPU使用率分布',
            'description': '不同CPU使用率区间的分布',
            'data': {label: count/total_cpu for label, count in cpu_counts.items()}
        }
        
        # 7. 分析内存使用率分布
        memory_bins = [0, 25, 50, 75, 100, float('inf')]
        memory_labels = ['0-25%', '25-50%', '50-75%', '75-100%', '>100%']
        memory_counts = pd.cut(df['memory_usage_percent'], bins=memory_bins, labels=memory_labels).value_counts()
        total_memory = memory_counts.sum()
        pie_chart_data['memory_usage_distribution'] = {
            'title': '内存使用率分布',
            'description': '不同内存使用率区间的分布',
            'data': {label: count/total_memory for label, count in memory_counts.items()}
        }
        
        # 8. 分析温度分布
        temp_bins = [25, 30, 35, 40, 45]
        temp_labels = ['25-30°C', '30-35°C', '35-40°C', '40-45°C']
        temp_counts = pd.cut(df['temperature_celsius'], bins=temp_bins, labels=temp_labels).value_counts()
        total_temp = temp_counts.sum()
        pie_chart_data['temperature_distribution'] = {
            'title': '温度分布',
            'description': '不同温度区间的分布',
            'data': {label: count/total_temp for label, count in temp_counts.items()}
        }
        
        return pie_chart_data
        
    except Exception as e:
        print(f"分析数据时出错: {str(e)}")
        return None

def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        print(f"错误: 文件 '{csv_path}' 不存在")
        sys.exit(1)
    
    # 分析数据
    pie_chart_data = analyze_pie_chart_data(csv_path)
    
    if pie_chart_data:
        # 将结果保存为JSON
        output_file = 'pie_chart_analysis_results.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(pie_chart_data, f, ensure_ascii=False, indent=4)
            print(f"分析结果已保存到 {output_file}")
        except Exception as e:
            print(f"保存结果时出错: {str(e)}")
    else:
        print("分析失败，未生成结果")

if __name__ == "__main__":
    main()