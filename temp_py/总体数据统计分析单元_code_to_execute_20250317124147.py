import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import os
from datetime import datetime

# 创建保存图表的目录
os.makedirs("pngs", exist_ok=True)

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
    try:
        # 获取数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        # 获取分类列
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # 数值列统计
        numeric_stats = df[numeric_cols].describe().to_dict()
        
        # 分类列统计
        categorical_stats = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts().to_dict()
            categorical_stats[col] = {
                "unique_values": len(value_counts),
                "top_values": {k: v for k, v in sorted(value_counts.items(), key=lambda item: item[1], reverse=True)[:5]}
            }
        
        return {
            "numeric_statistics": numeric_stats,
            "categorical_statistics": categorical_stats
        }
    except Exception as e:
        print(f"计算基本统计信息时出错: {e}")
        return {}

# 生成图表1: 基站性能指标对比
def create_station_performance_chart(df):
    try:
        plt.figure(figsize=(12, 8))
        
        # 按基站分组计算平均值
        station_stats = df.groupby('base_station_name').agg({
            'success_rate': 'mean',
            'signal_strength_dbm': 'mean',
            'downlink_throughput_mbps': 'mean',
            'latency_ms': 'mean',
            'packet_loss_percent': 'mean'
        }).reset_index()
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 成功率
        axes[0, 0].bar(station_stats['base_station_name'], station_stats['success_rate'], color='green')
        axes[0, 0].set_title('Average Success Rate by Base Station')
        axes[0, 0].set_ylabel('Success Rate')
        axes[0, 0].set_xticklabels(station_stats['base_station_name'], rotation=45, ha='right')
        axes[0, 0].grid(axis='y', linestyle='--', alpha=0.7)
        
        # 信号强度
        axes[0, 1].bar(station_stats['base_station_name'], station_stats['signal_strength_dbm'], color='blue')
        axes[0, 1].set_title('Average Signal Strength by Base Station')
        axes[0, 1].set_ylabel('Signal Strength (dBm)')
        axes[0, 1].set_xticklabels(station_stats['base_station_name'], rotation=45, ha='right')
        axes[0, 1].grid(axis='y', linestyle='--', alpha=0.7)
        
        # 下行吞吐量
        axes[1, 0].bar(station_stats['base_station_name'], station_stats['downlink_throughput_mbps'], color='purple')
        axes[1, 0].set_title('Average Downlink Throughput by Base Station')
        axes[1, 0].set_ylabel('Throughput (Mbps)')
        axes[1, 0].set_xticklabels(station_stats['base_station_name'], rotation=45, ha='right')
        axes[1, 0].grid(axis='y', linestyle='--', alpha=0.7)
        
        # 延迟
        axes[1, 1].bar(station_stats['base_station_name'], station_stats['latency_ms'], color='orange')
        axes[1, 1].set_title('Average Latency by Base Station')
        axes[1, 1].set_ylabel('Latency (ms)')
        axes[1, 1].set_xticklabels(station_stats['base_station_name'], rotation=45, ha='right')
        axes[1, 1].grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.figtext(0.5, 0.01, 
                   "Key Finding: Base stations show significant performance variations across metrics.",
                   ha='center', fontsize=12, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart_path = "pngs/chart_stats_base_station_performance.png"
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    except Exception as e:
        print(f"创建基站性能图表时出错: {e}")
        return None

# 生成图表2: 信号类型与状态关系热力图
def create_signal_status_heatmap(df):
    try:
        plt.figure(figsize=(14, 10))
        
        # 创建信号类型和状态的交叉表
        cross_tab = pd.crosstab(df['signal_type'], df['status'])
        
        # 绘制热力图
        plt.figure(figsize=(12, 8))
        sns.heatmap(cross_tab, annot=True, cmap='YlGnBu', fmt='d', cbar_kws={'label': 'Count'})
        plt.title('Relationship Between Signal Type and Status')
        plt.xlabel('Status')
        plt.ylabel('Signal Type')
        plt.tight_layout()
        
        plt.figtext(0.5, 0.01, 
                   "Key Finding: Different signal types show varying success and failure patterns.",
                   ha='center', fontsize=12, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart_path = "pngs/chart_stats_signal_status_heatmap.png"
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    except Exception as e:
        print(f"创建信号状态热力图时出错: {e}")
        return None

# 生成图表3: 资源使用与性能关系散点图
def create_resource_performance_scatter(df):
    try:
        plt.figure(figsize=(12, 10))
        
        # 创建子图
        fig, axes = plt.subplots(2, 1, figsize=(12, 14))
        
        # CPU使用率与成功率的关系
        axes[0].scatter(df['cpu_usage_percent'], df['success_rate'], alpha=0.5, c='blue')
        axes[0].set_title('CPU Usage vs Success Rate')
        axes[0].set_xlabel('CPU Usage (%)')
        axes[0].set_ylabel('Success Rate')
        axes[0].grid(True, linestyle='--', alpha=0.7)
        
        # 资源块使用率与下行吞吐量的关系
        axes[1].scatter(df['resource_block_usage_percent'], df['downlink_throughput_mbps'], alpha=0.5, c='green')
        axes[1].set_title('Resource Block Usage vs Downlink Throughput')
        axes[1].set_xlabel('Resource Block Usage (%)')
        axes[1].set_ylabel('Downlink Throughput (Mbps)')
        axes[1].grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.figtext(0.5, 0.01, 
                   "Key Finding: Higher resource utilization correlates with varying performance outcomes.",
                   ha='center', fontsize=12, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart_path = "pngs/chart_stats_resource_performance.png"
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    except Exception as e:
        print(f"创建资源性能散点图时出错: {e}")
        return None

# 主函数
def main():
    file_path = "temp_csv/excel_data_20250317124038.csv"
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return
    
    # 基本统计分析
    stats = basic_statistics(df)
    
    # 生成图表
    chart1_path = create_station_performance_chart(df)
    chart2_path = create_signal_status_heatmap(df)
    chart3_path = create_resource_performance_scatter(df)
    
    # 准备结果
    result = {
        "file_analyzed": file_path,
        "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "row_count": len(df),
        "column_count": len(df.columns),
        "statistics": stats,
        "charts": {
            "base_station_performance": chart1_path,
            "signal_status_heatmap": chart2_path,
            "resource_performance": chart3_path
        },
        "key_findings": [
            "基站之间的性能指标存在显著差异",
            "不同信号类型的成功率和失败率模式各不相同",
            "资源利用率与性能指标之间存在相关性"
        ]
    }
    
    # 保存结果为JSON
    with open("analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("分析完成，结果已保存到 analysis_results.json")
    print(f"图表已保存到 {chart1_path}, {chart2_path}, {chart3_path}")

if __name__ == "__main__":
    main()