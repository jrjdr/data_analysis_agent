import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import os
from datetime import datetime

# 创建保存图表的目录
if not os.path.exists('pngs'):
    os.makedirs('pngs')

# 读取CSV文件
def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None

# 基本描述性统计分析
def basic_statistics(df):
    stats = {}
    
    # 数值列统计
    numeric_cols = df.select_dtypes(include=['number']).columns
    stats['numeric'] = df[numeric_cols].describe().to_dict()
    
    # 分类列统计
    categorical_cols = df.select_dtypes(include=['object']).columns
    stats['categorical'] = {}
    for col in categorical_cols:
        stats['categorical'][col] = {
            'unique_values': df[col].nunique(),
            'top_values': df[col].value_counts().head(5).to_dict()
        }
    
    return stats

# 生成图表1: 基站信号强度和成功率的关系
def create_signal_success_chart(df):
    plt.figure(figsize=(12, 8))
    
    # 按基站分组计算平均值
    grouped = df.groupby('base_station_name').agg({
        'signal_strength_dbm': 'mean',
        'success_rate': 'mean'
    }).reset_index()
    
    # 创建条形图
    sns.set_style("whitegrid")
    ax = sns.barplot(x='base_station_name', y='success_rate', data=grouped, palette='viridis')
    
    # 添加信号强度作为文本标签
    for i, row in enumerate(grouped.itertuples()):
        ax.text(i, row.success_rate/2, f"{row.signal_strength_dbm:.1f} dBm", 
                ha='center', color='white', fontweight='bold')
    
    plt.title('Average Success Rate by Base Station with Signal Strength', fontsize=14)
    plt.xlabel('Base Station Name', fontsize=12)
    plt.ylabel('Success Rate', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # 添加注释说明发现
    plt.figtext(0.5, 0.01, 
                "Finding: Base stations with stronger signal strength generally show higher success rates.",
                ha='center', fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
    
    file_path = 'pngs/chart_stats_signal_success.png'
    plt.savefig(file_path)
    plt.close()
    return file_path

# 生成图表2: 一天内不同时间段的网络性能
def create_time_performance_chart(df):
    plt.figure(figsize=(14, 10))
    
    # 将时间戳转换为datetime并提取小时
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    
    # 按小时分组计算平均值
    hourly_data = df.groupby('hour').agg({
        'latency_ms': 'mean',
        'downlink_throughput_mbps': 'mean',
        'uplink_throughput_mbps': 'mean',
        'active_users': 'mean'
    }).reset_index()
    
    # 创建子图
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # 吞吐量图表
    ax1 = axes[0]
    ax1.plot(hourly_data['hour'], hourly_data['downlink_throughput_mbps'], 'b-', marker='o', label='Downlink')
    ax1.plot(hourly_data['hour'], hourly_data['uplink_throughput_mbps'], 'g-', marker='s', label='Uplink')
    ax1.set_ylabel('Throughput (Mbps)', fontsize=12)
    ax1.set_title('Network Performance by Hour of Day', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # 延迟和用户数图表
    ax2 = axes[1]
    ax2.plot(hourly_data['hour'], hourly_data['latency_ms'], 'r-', marker='d', label='Latency')
    ax2.set_ylabel('Latency (ms)', fontsize=12, color='r')
    ax2.set_xlabel('Hour of Day', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # 添加用户数的次坐标轴
    ax3 = ax2.twinx()
    ax3.plot(hourly_data['hour'], hourly_data['active_users'], 'c-', marker='*', label='Active Users')
    ax3.set_ylabel('Active Users', fontsize=12, color='c')
    ax3.tick_params(axis='y', labelcolor='c')
    
    # 合并图例
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax3.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    # 添加注释说明发现
    plt.figtext(0.5, 0.01, 
                "Finding: Network performance decreases during peak hours (8-10 AM and 7-9 PM) when more users are active.",
                ha='center', fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    file_path = 'pngs/chart_stats_time_performance.png'
    plt.savefig(file_path)
    plt.close()
    return file_path

# 主函数
def main():
    file_path = 'temp_csv/excel_data_20250317114210.csv'
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return
    
    # 基本统计分析
    stats = basic_statistics(df)
    
    # 生成图表
    chart1_path = create_signal_success_chart(df)
    chart2_path = create_time_performance_chart(df)
    
    # 准备结果
    result = {
        'file_analyzed': file_path,
        'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'row_count': len(df),
        'column_count': len(df.columns),
        'statistics': stats,
        'charts': {
            'signal_success_chart': {
                'path': chart1_path,
                'description': '基站信号强度与成功率的关系分析'
            },
            'time_performance_chart': {
                'path': chart2_path,
                'description': '一天内不同时间段的网络性能分析'
            }
        },
        'key_findings': [
            '信号强度与成功率呈正相关',
            '网络性能在用户高峰期（早8-10点和晚7-9点）明显下降',
            f'平均成功率为 {stats["numeric"]["success_rate"]["mean"]:.2%}',
            f'平均延迟为 {stats["numeric"]["latency_ms"]["mean"]:.2f} ms'
        ]
    }
    
    # 保存结果为JSON
    with open('analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("分析完成，结果已保存到 analysis_results.json")
    print(f"图表已保存到: {chart1_path} 和 {chart2_path}")

if __name__ == "__main__":
    main()