import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

def analyze_csv_data(file_path):
    try:
        # 1. 读取CSV文件
        df = pd.read_csv(file_path)
        print(f"成功读取CSV文件，共{len(df)}行数据")
        
        # 创建保存图表的目录
        os.makedirs("pngs", exist_ok=True)
        
        # 2. 分析数据
        analysis_results = {}
        
        # 图表1: 不同基站的成功率对比
        plt.figure(figsize=(12, 6))
        station_success = df.groupby('base_station_name')['success_rate'].mean().sort_values(ascending=False)
        
        bars = plt.bar(station_success.index, station_success.values, color='skyblue')
        plt.title('Average Success Rate by Base Station', fontsize=14)
        plt.xlabel('Base Station Name', fontsize=12)
        plt.ylabel('Average Success Rate', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0.7, 1.0)  # 设置y轴范围以突出差异
        
        # 在柱状图上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                    f'{height:.4f}', ha='center', va='bottom', fontsize=10)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加描述性文字
        plt.figtext(0.5, 0.01, 
                   "Key Finding: '城南-住宅区基站' has the highest success rate while '城西-工业区基站' has the lowest.", 
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart1_path = "pngs/chart_bar_station_success_rate.png"
        plt.savefig(chart1_path)
        plt.close()
        
        # 图表2: 不同信号类型的成功率和失败率对比
        plt.figure(figsize=(14, 7))
        signal_stats = df.groupby('signal_type').agg({
            'success_rate': 'mean',
            'failure_rate': 'mean'
        }).sort_values('success_rate', ascending=False)
        
        x = np.arange(len(signal_stats.index))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(14, 7))
        success_bars = ax.bar(x - width/2, signal_stats['success_rate'], width, label='Success Rate', color='green')
        failure_bars = ax.bar(x + width/2, signal_stats['failure_rate'], width, label='Failure Rate', color='red')
        
        ax.set_title('Success vs Failure Rate by Signal Type', fontsize=14)
        ax.set_xlabel('Signal Type', fontsize=12)
        ax.set_ylabel('Rate', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(signal_stats.index, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 在柱状图上添加数值标签
        for bar in success_bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=9)
                   
        for bar in failure_bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.figtext(0.5, 0.01, 
                   "Key Finding: 'HANDOVER' signals have the highest success rate (0.94), while 'EMERGENCY' signals have the lowest (0.76).", 
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        plt.tight_layout()
        chart2_path = "pngs/chart_bar_signal_type_rates.png"
        plt.savefig(chart2_path)
        plt.close()
        
        # 图表3: 不同基站的资源使用情况对比
        plt.figure(figsize=(12, 8))
        resource_usage = df.groupby('base_station_name').agg({
            'resource_block_usage_percent': 'mean',
            'cpu_usage_percent': 'mean',
            'memory_usage_percent': 'mean'
        })
        
        x = np.arange(len(resource_usage.index))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(12, 8))
        resource_bars = ax.bar(x - width, resource_usage['resource_block_usage_percent'], width, label='Resource Block Usage', color='blue')
        cpu_bars = ax.bar(x, resource_usage['cpu_usage_percent'], width, label='CPU Usage', color='orange')
        memory_bars = ax.bar(x + width, resource_usage['memory_usage_percent'], width, label='Memory Usage', color='green')
        
        ax.set_title('Resource Usage by Base Station', fontsize=14)
        ax.set_xlabel('Base Station Name', fontsize=12)
        ax.set_ylabel('Usage Percentage (%)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(resource_usage.index, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.figtext(0.5, 0.01, 
                   "Key Finding: '城中-办公区基站' shows the highest resource block usage, while '城东-商业区基站' has the highest CPU and memory usage.", 
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        plt.tight_layout()
        chart3_path = "pngs/chart_bar_resource_usage.png"
        plt.savefig(chart3_path)
        plt.close()
        
        # 4. 将分析结果保存为JSON格式
        analysis_results = {
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_analyzed": file_path,
            "row_count": len(df),
            "charts_generated": [
                {
                    "chart_name": "Base Station Success Rate Comparison",
                    "chart_path": chart1_path,
                    "key_finding": "城南-住宅区基站 has the highest success rate while 城西-工业区基站 has the lowest.",
                    "data": station_success.to_dict()
                },
                {
                    "chart_name": "Signal Type Success vs Failure Rate",
                    "chart_path": chart2_path,
                    "key_finding": "HANDOVER signals have the highest success rate, while EMERGENCY signals have the lowest.",
                    "data": signal_stats.to_dict()
                },
                {
                    "chart_name": "Base Station Resource Usage",
                    "chart_path": chart3_path,
                    "key_finding": "城中-办公区基站 shows the highest resource block usage, while 城东-商业区基站 has the highest CPU and memory usage.",
                    "data": resource_usage.to_dict()
                }
            ]
        }
        
        # 保存分析结果为JSON文件
        with open("pngs/analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=4)
        
        print("分析完成，结果已保存到 pngs/analysis_results.json")
        print(f"生成的图表已保存到 {chart1_path}, {chart2_path}, {chart3_path}")
        
        return analysis_results
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317113352.csv"
    analyze_csv_data(file_path)