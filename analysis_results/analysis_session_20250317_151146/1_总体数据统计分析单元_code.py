import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    try:
        # 1. 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入分析标题和时间戳
            f.write("=" * 80 + "\n")
            f.write(f"服务器性能数据分析报告\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据文件: {file_path}\n")
            f.write("=" * 80 + "\n\n")
            
            # 2. 基本数据概览
            f.write("1. 基本数据概览\n")
            f.write("-" * 80 + "\n")
            f.write(f"记录总数: {len(df)}\n")
            f.write(f"列数量: {len(df.columns)}\n")
            f.write(f"数据时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}\n")
            f.write(f"服务器数量: {df['server_id'].nunique()}\n")
            f.write(f"资源类型: {', '.join(df['resource_type'].unique())}\n")
            f.write(f"事件类型分布:\n")
            event_counts = df['event_type'].value_counts()
            for event, count in event_counts.items():
                f.write(f"  - {event}: {count} ({count/len(df)*100:.2f}%)\n")
            f.write("\n")
            
            # 3. 服务器分布
            f.write("2. 服务器分布\n")
            f.write("-" * 80 + "\n")
            server_info = df[['server_id', 'server_name']].drop_duplicates()
            for _, row in server_info.iterrows():
                f.write(f"  - {row['server_id']}: {row['server_name']}\n")
            f.write("\n")
            
            # 4. 数值列统计分析
            f.write("3. 关键性能指标统计\n")
            f.write("-" * 80 + "\n")
            
            # 选择关键性能指标
            key_metrics = [
                'cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent',
                'network_traffic_percent', 'load_avg_1min', 'temperature_celsius',
                'query_rate_per_sec', 'active_connections', 'cache_hit_rate_percent',
                'avg_query_time_ms', 'transactions_per_sec'
            ]
            
            # 处理每个指标
            for metric in key_metrics:
                if metric in df.columns:
                    metric_data = df[metric].dropna()
                    if len(metric_data) > 0:
                        f.write(f"{metric}:\n")
                        f.write(f"  - 数据点数: {len(metric_data)}\n")
                        f.write(f"  - 最小值: {metric_data.min():.2f}\n")
                        f.write(f"  - 最大值: {metric_data.max():.2f}\n")
                        f.write(f"  - 平均值: {metric_data.mean():.2f}\n")
                        f.write(f"  - 中位数: {metric_data.median():.2f}\n")
                        f.write(f"  - 标准差: {metric_data.std():.2f}\n")
                        
                        # 计算分位数
                        percentiles = [25, 50, 75, 90, 95, 99]
                        percentile_values = np.percentile(metric_data, percentiles)
                        for p, val in zip(percentiles, percentile_values):
                            f.write(f"  - {p}%分位数: {val:.2f}\n")
                        f.write("\n")
            
            # 5. 异常事件分析
            f.write("4. 异常事件分析\n")
            f.write("-" * 80 + "\n")
            
            abnormal_events = df[df['event_type'] != 'normal']
            if len(abnormal_events) > 0:
                event_types = abnormal_events['event_type'].value_counts()
                f.write(f"异常事件总数: {len(abnormal_events)}\n")
                f.write("异常事件类型分布:\n")
                for event, count in event_types.items():
                    f.write(f"  - {event}: {count}\n")
                
                # 分析每种异常事件的关键指标
                for event in abnormal_events['event_type'].unique():
                    if event != 'normal':
                        event_df = abnormal_events[abnormal_events['event_type'] == event]
                        f.write(f"\n{event}事件分析 (共{len(event_df)}条):\n")
                        for metric in ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent']:
                            if metric in event_df.columns:
                                metric_data = event_df[metric].dropna()
                                if len(metric_data) > 0:
                                    f.write(f"  - {metric}: 平均值={metric_data.mean():.2f}, 最大值={metric_data.max():.2f}\n")
            else:
                f.write("未发现异常事件。\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("分析报告结束\n")
            
        print(f"分析完成，结果已保存至: {output_path}")
        return True
        
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
        return False

# 执行分析
file_path = "temp_csv/excel_data_20250317151146.csv"
output_path = "pngs/analysis_results.txt"
analyze_csv_data(file_path, output_path)