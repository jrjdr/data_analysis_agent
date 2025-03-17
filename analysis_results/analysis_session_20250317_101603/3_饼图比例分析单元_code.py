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
        
        # 存储所有饼图分析结果
        pie_chart_data = {}
        
        # 1. 分析信号类型(signal_type)分布
        signal_type_counts = df['signal_type'].value_counts()
        pie_chart_data['signal_type_distribution'] = {
            'title': '信号类型分布',
            'description': '各种信号类型的占比分析',
            'data': signal_type_counts.apply(lambda x: round(x / signal_type_counts.sum() * 100, 2)).to_dict()
        }
        
        # 2. 分析状态(status)分布
        status_counts = df['status'].value_counts()
        pie_chart_data['status_distribution'] = {
            'title': '状态分布',
            'description': '各种状态的占比分析',
            'data': status_counts.apply(lambda x: round(x / status_counts.sum() * 100, 2)).to_dict()
        }
        
        # 3. 分析基站分布
        station_counts = df['base_station_name'].value_counts()
        pie_chart_data['base_station_distribution'] = {
            'title': '基站分布',
            'description': '各基站数据记录的占比分析',
            'data': station_counts.apply(lambda x: round(x / station_counts.sum() * 100, 2)).to_dict()
        }
        
        # 4. 成功率与失败率的平均分布
        success_failure_avg = {
            '成功率': round(df['success_rate'].mean() * 100, 2),
            '失败率': round(df['failure_rate'].mean() * 100, 2)
        }
        pie_chart_data['success_failure_distribution'] = {
            'title': '成功率与失败率分布',
            'description': '平均成功率与失败率的占比',
            'data': success_failure_avg
        }
        
        # 5. 资源块使用率分布（分段）
        resource_bins = [0, 25, 50, 75, 100]
        resource_labels = ['0-25%', '26-50%', '51-75%', '76-100%']
        resource_cut = pd.cut(df['resource_block_usage_percent'], bins=resource_bins, labels=resource_labels, right=True)
        resource_dist = resource_cut.value_counts()
        pie_chart_data['resource_usage_distribution'] = {
            'title': '资源块使用率分布',
            'description': '不同资源块使用率范围的占比',
            'data': resource_dist.apply(lambda x: round(x / resource_dist.sum() * 100, 2)).to_dict()
        }
        
        # 6. CPU使用率分布（分段）
        cpu_bins = [0, 25, 50, 75, 100, float('inf')]
        cpu_labels = ['0-25%', '26-50%', '51-75%', '76-100%', '>100%']
        cpu_cut = pd.cut(df['cpu_usage_percent'], bins=cpu_bins, labels=cpu_labels, right=True)
        cpu_dist = cpu_cut.value_counts()
        pie_chart_data['cpu_usage_distribution'] = {
            'title': 'CPU使用率分布',
            'description': '不同CPU使用率范围的占比',
            'data': cpu_dist.apply(lambda x: round(x / cpu_dist.sum() * 100, 2)).to_dict()
        }
        
        # 7. 内存使用率分布（分段）
        memory_bins = [0, 25, 50, 75, 100, float('inf')]
        memory_labels = ['0-25%', '26-50%', '51-75%', '76-100%', '>100%']
        memory_cut = pd.cut(df['memory_usage_percent'], bins=memory_bins, labels=memory_labels, right=True)
        memory_dist = memory_cut.value_counts()
        pie_chart_data['memory_usage_distribution'] = {
            'title': '内存使用率分布',
            'description': '不同内存使用率范围的占比',
            'data': memory_dist.apply(lambda x: round(x / memory_dist.sum() * 100, 2)).to_dict()
        }
        
        # 8. 温度分布（分段）
        temp_bins = [25, 30, 35, 40, 45]
        temp_labels = ['25-30°C', '30-35°C', '35-40°C', '40-45°C']
        temp_cut = pd.cut(df['temperature_celsius'], bins=temp_bins, labels=temp_labels, right=True)
        temp_dist = temp_cut.value_counts()
        pie_chart_data['temperature_distribution'] = {
            'title': '温度分布',
            'description': '不同温度范围的占比',
            'data': temp_dist.apply(lambda x: round(x / temp_dist.sum() * 100, 2)).to_dict()
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
        # 将结果保存为JSON文件
        output_file = 'pie_chart_analysis_results.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(pie_chart_data, f, ensure_ascii=False, indent=4)
            print(f"分析结果已保存到 {output_file}")
        except Exception as e:
            print(f"保存结果时出错: {str(e)}")
    else:
        print("无法生成分析结果")

if __name__ == "__main__":
    main()