import pandas as pd
import numpy as np
import json
import sys
import argparse
from datetime import datetime

def analyze_for_bar_charts(csv_path):
    """分析CSV数据并生成适合柱状图展示的数据"""
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 存储分析结果
        results = {}
        
        # 1. 基站对比分析
        # 各基站的成功率平均值
        station_success = df.groupby('base_station_name')['success_rate'].mean().reset_index()
        station_success = station_success.sort_values('success_rate', ascending=False)
        results['station_success_rate'] = {
            'title': '各基站平均成功率',
            'x_label': '基站名称',
            'y_label': '平均成功率',
            'data': station_success.to_dict('records')
        }
        
        # 2. 信号类型分析
        # 不同信号类型的数量统计
        signal_counts = df['signal_type'].value_counts().reset_index()
        signal_counts.columns = ['signal_type', 'count']
        results['signal_type_counts'] = {
            'title': '不同信号类型数量统计',
            'x_label': '信号类型',
            'y_label': '数量',
            'data': signal_counts.to_dict('records')
        }
        
        # 3. 状态分析
        # 不同状态的数量统计
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        results['status_counts'] = {
            'title': '不同状态数量统计',
            'x_label': '状态',
            'y_label': '数量',
            'data': status_counts.to_dict('records')
        }
        
        # 4. 信号类型与成功率的关系
        signal_success = df.groupby('signal_type')['success_rate'].mean().reset_index()
        signal_success = signal_success.sort_values('success_rate', ascending=False)
        results['signal_type_success_rate'] = {
            'title': '不同信号类型的平均成功率',
            'x_label': '信号类型',
            'y_label': '平均成功率',
            'data': signal_success.to_dict('records')
        }
        
        # 5. 基站资源使用情况对比
        resource_usage = df.groupby('base_station_name')['resource_block_usage_percent'].mean().reset_index()
        resource_usage = resource_usage.sort_values('resource_block_usage_percent', ascending=False)
        results['station_resource_usage'] = {
            'title': '各基站平均资源块使用率',
            'x_label': '基站名称',
            'y_label': '平均资源块使用率(%)',
            'data': resource_usage.to_dict('records')
        }
        
        # 6. 基站性能指标对比
        # 计算每个基站的平均下行吞吐量
        downlink = df.groupby('base_station_name')['downlink_throughput_mbps'].mean().reset_index()
        downlink = downlink.sort_values('downlink_throughput_mbps', ascending=False)
        results['station_downlink'] = {
            'title': '各基站平均下行吞吐量',
            'x_label': '基站名称',
            'y_label': '平均下行吞吐量(Mbps)',
            'data': downlink.to_dict('records')
        }
        
        # 7. 基站延迟对比
        latency = df.groupby('base_station_name')['latency_ms'].mean().reset_index()
        latency = latency.sort_values('latency_ms')
        results['station_latency'] = {
            'title': '各基站平均延迟',
            'x_label': '基站名称',
            'y_label': '平均延迟(ms)',
            'data': latency.to_dict('records')
        }
        
        # 8. 基站硬件状态对比
        # 计算每个基站的平均CPU和内存使用率
        hardware = df.groupby('base_station_name').agg({
            'cpu_usage_percent': 'mean',
            'memory_usage_percent': 'mean',
            'temperature_celsius': 'mean'
        }).reset_index()
        
        results['station_hardware'] = {
            'title': '各基站硬件状态',
            'x_label': '基站名称',
            'y_label': '使用率/温度',
            'data': hardware.to_dict('records')
        }
        
        return results
    
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return {"error": str(e)}

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='分析CSV数据并生成适合柱状图的数据')
    parser.add_argument('csv_path', help='CSV文件路径')
    parser.add_argument('--output', default='bar_chart_analysis_results.json', help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    try:
        # 执行分析
        results = analyze_for_bar_charts(args.csv_path)
        
        # 保存结果到JSON文件
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"分析完成，结果已保存到 {args.output}")
    
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()