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
        plt.xlabel('Base Station', fontsize=12)
        plt.ylabel('Average Success Rate', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0.7, 1.0)  # 设置y轴范围以突出差异
        
        # 在柱状图上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加描述性文字
        plt.figtext(0.5, 0.01, 
                   "The chart shows that success rates vary across base stations, with some stations consistently performing better.",
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart1_path = "pngs/chart_bar_success_rate_by_station.png"
        plt.savefig(chart1_path)
        plt.close()
        
        # 图表2: 不同信号类型的平均延迟对比
        plt.figure(figsize=(14, 7))
        signal_latency = df.groupby('signal_type')['latency_ms'].mean().sort_values(ascending=True)
        
        bars = plt.bar(signal_latency.index, signal_latency.values, color='lightgreen')
        plt.title('Average Latency by Signal Type', fontsize=14)
        plt.xlabel('Signal Type', fontsize=12)
        plt.ylabel('Average Latency (ms)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # 在柱状图上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加描述性文字
        plt.figtext(0.5, 0.01, 
                   "Different signal types exhibit varying latency characteristics, with some types consistently showing lower latency.",
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart2_path = "pngs/chart_bar_latency_by_signal_type.png"
        plt.savefig(chart2_path)
        plt.close()
        
        # 图表3: 不同状态下的资源块使用率对比
        plt.figure(figsize=(10, 6))
        status_resource = df.groupby('status')['resource_block_usage_percent'].mean().sort_values(ascending=False)
        
        bars = plt.bar(status_resource.index, status_resource.values, color='salmon')
        plt.title('Average Resource Block Usage by Status', fontsize=14)
        plt.xlabel('Status', fontsize=12)
        plt.ylabel('Resource Block Usage (%)', fontsize=12)
        
        # 在柱状图上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}%', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加描述性文字
        plt.figtext(0.5, 0.01, 
                   "Resource block usage varies significantly across different status types, with failure states generally showing higher resource consumption.",
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart3_path = "pngs/chart_bar_resource_usage_by_status.png"
        plt.savefig(chart3_path)
        plt.close()
        
        # 3. 保存分析结果为JSON
        analysis_results = {
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": file_path,
            "row_count": len(df),
            "charts": [
                {
                    "title": "Average Success Rate by Base Station",
                    "file_path": chart1_path,
                    "description": "Comparison of success rates across different base stations",
                    "data": station_success.to_dict()
                },
                {
                    "title": "Average Latency by Signal Type",
                    "file_path": chart2_path,
                    "description": "Comparison of average latency across different signal types",
                    "data": signal_latency.to_dict()
                },
                {
                    "title": "Average Resource Block Usage by Status",
                    "file_path": chart3_path,
                    "description": "Comparison of resource block usage across different status types",
                    "data": status_resource.to_dict()
                }
            ],
            "key_statistics": {
                "overall_success_rate": {
                    "mean": df['success_rate'].mean(),
                    "median": df['success_rate'].median(),
                    "min": df['success_rate'].min(),
                    "max": df['success_rate'].max()
                },
                "overall_latency_ms": {
                    "mean": df['latency_ms'].mean(),
                    "median": df['latency_ms'].median(),
                    "min": df['latency_ms'].min(),
                    "max": df['latency_ms'].max()
                }
            }
        }
        
        # 保存JSON结果
        json_path = "pngs/analysis_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=4)
        
        print(f"分析完成，结果已保存到 {json_path}")
        print(f"生成的图表已保存到 pngs 目录")
        
        return analysis_results
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317114210.csv"
    analyze_csv_data(file_path)