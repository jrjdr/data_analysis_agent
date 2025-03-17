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
        
        # 1. 分析基站分布情况
        station_counts = df['base_station_name'].value_counts()
        pie_chart_data['基站分布'] = {
            'data': station_counts.to_dict(),
            'description': '各基站数据记录占比'
        }
        
        # 2. 分析信号类型分布
        signal_type_counts = df['signal_type'].value_counts()
        pie_chart_data['信号类型分布'] = {
            'data': signal_type_counts.to_dict(),
            'description': '不同信号类型的占比'
        }
        
        # 3. 分析状态分布
        status_counts = df['status'].value_counts()
        pie_chart_data['状态分布'] = {
            'data': status_counts.to_dict(),
            'description': '不同状态的占比'
        }
        
        # 4. 成功率与失败率的平均分布
        success_failure_avg = {
            '成功率': df['success_rate'].mean(),
            '失败率': df['failure_rate'].mean()
        }
        pie_chart_data['平均成功失败率'] = {
            'data': success_failure_avg,
            'description': '平均成功率与失败率分布'
        }
        
        # 5. 资源块使用率分布（分段）
        resource_bins = [0, 25, 50, 75, 100]
        resource_labels = ['0-25%', '25-50%', '50-75%', '75-100%']
        resource_usage_dist = pd.cut(df['resource_block_usage_percent'], bins=resource_bins, labels=resource_labels).value_counts()
        pie_chart_data['资源块使用率分布'] = {
            'data': resource_usage_dist.to_dict(),
            'description': '资源块使用率的区间分布'
        }
        
        # 6. CPU使用率分布（分段）
        cpu_bins = [0, 25, 50, 75, 100, float('inf')]
        cpu_labels = ['0-25%', '25-50%', '50-75%', '75-100%', '>100%']
        cpu_usage_dist = pd.cut(df['cpu_usage_percent'], bins=cpu_bins, labels=cpu_labels).value_counts()
        pie_chart_data['CPU使用率分布'] = {
            'data': cpu_usage_dist.to_dict(),
            'description': 'CPU使用率的区间分布'
        }
        
        # 7. 内存使用率分布（分段）
        memory_bins = [0, 25, 50, 75, 100, float('inf')]
        memory_labels = ['0-25%', '25-50%', '50-75%', '75-100%', '>100%']
        memory_usage_dist = pd.cut(df['memory_usage_percent'], bins=memory_bins, labels=memory_labels).value_counts()
        pie_chart_data['内存使用率分布'] = {
            'data': memory_usage_dist.to_dict(),
            'description': '内存使用率的区间分布'
        }
        
        # 8. 温度分布（分段）
        temp_bins = [25, 30, 35, 40, 45]
        temp_labels = ['25-30°C', '30-35°C', '35-40°C', '40-45°C']
        temp_dist = pd.cut(df['temperature_celsius'], bins=temp_bins, labels=temp_labels).value_counts()
        pie_chart_data['温度分布'] = {
            'data': temp_dist.to_dict(),
            'description': '基站温度的区间分布'
        }
        
        # 9. 按基站分析平均信号强度
        signal_strength_by_station = df.groupby('base_station_name')['signal_strength_dbm'].mean().to_dict()
        # 将负值转为正值以便于饼图展示
        signal_strength_by_station = {k: abs(v) for k, v in signal_strength_by_station.items()}
        pie_chart_data['各基站平均信号强度'] = {
            'data': signal_strength_by_station,
            'description': '各基站的平均信号强度分布（绝对值）'
        }
        
        # 10. 按基站分析平均吞吐量
        throughput_by_station = df.groupby('base_station_name')['downlink_throughput_mbps'].mean().to_dict()
        pie_chart_data['各基站平均下行吞吐量'] = {
            'data': throughput_by_station,
            'description': '各基站的平均下行吞吐量分布'
        }
        
        return pie_chart_data
        
    except Exception as e:
        print(f"分析数据时出错: {str(e)}")
        return None

def save_to_json(data, output_path='pie_chart_analysis_results.json'):
    """
    将分析结果保存为JSON文件
    """
    try:
        # 将numpy数据类型转换为Python原生类型
        def convert_to_native_types(obj):
            if isinstance(obj, dict):
                return {k: convert_to_native_types(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_native_types(i) for i in obj]
            elif isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            else:
                return obj
        
        data = convert_to_native_types(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"分析结果已保存到 {output_path}")
        return True
    except Exception as e:
        print(f"保存JSON文件时出错: {str(e)}")
        return False

def main():
    """
    主函数，处理命令行参数并执行分析
    """
    if len(sys.argv) < 2:
        print("用法: python script.py <csv文件路径> [输出json文件路径]")
        return
    
    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'pie_chart_analysis_results.json'
    
    if not os.path.exists(csv_path):
        print(f"错误: 文件 '{csv_path}' 不存在")
        return
    
    # 执行分析
    pie_chart_data = analyze_pie_chart_data(csv_path)
    if pie_chart_data:
        save_to_json(pie_chart_data, output_path)

if __name__ == "__main__":
    main()