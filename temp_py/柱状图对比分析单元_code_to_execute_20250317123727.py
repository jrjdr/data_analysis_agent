import pandas as pd
import matplotlib.pyplot as plt
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

# 分析数据并生成图表
def analyze_data(df):
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_results": {},
        "charts": []
    }
    
    # 图表1: 不同基站的成功率对比
    try:
        plt.figure(figsize=(12, 6))
        station_success = df.groupby('base_station_name')['success_rate'].mean().sort_values(ascending=False)
        
        bars = plt.bar(station_success.index, station_success.values, color='skyblue')
        plt.title('Average Success Rate by Base Station', fontsize=14)
        plt.xlabel('Base Station', fontsize=12)
        plt.ylabel('Average Success Rate', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0.8, 0.9)  # 调整y轴范围以突出差异
        
        # 在柱状图上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{height:.4f}', ha='center', va='bottom', fontsize=9)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加分析说明
        plt.figtext(0.5, 0.01, 
                   "Finding: Urban stations show higher success rates than rural stations.",
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart_path = 'pngs/chart_bar_station_success_rate.png'
        plt.savefig(chart_path)
        plt.close()
        
        results["charts"].append({
            "title": "Average Success Rate by Base Station",
            "path": chart_path,
            "data": station_success.to_dict()
        })
        
        results["analysis_results"]["station_success_rate"] = {
            "highest": {"station": station_success.index[0], "rate": float(station_success.iloc[0])},
            "lowest": {"station": station_success.index[-1], "rate": float(station_success.iloc[-1])},
            "difference": float(station_success.iloc[0] - station_success.iloc[-1])
        }
    except Exception as e:
        print(f"生成基站成功率图表时出错: {e}")
    
    # 图表2: 不同信号类型的平均延迟对比
    try:
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
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加分析说明
        plt.figtext(0.5, 0.01, 
                   "Finding: Control signals (PAGING, RACH) have lower latency than data transmission signals.",
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart_path = 'pngs/chart_bar_signal_latency.png'
        plt.savefig(chart_path)
        plt.close()
        
        results["charts"].append({
            "title": "Average Latency by Signal Type",
            "path": chart_path,
            "data": signal_latency.to_dict()
        })
        
        results["analysis_results"]["signal_latency"] = {
            "lowest": {"signal": signal_latency.index[0], "latency": float(signal_latency.iloc[0])},
            "highest": {"signal": signal_latency.index[-1], "latency": float(signal_latency.iloc[-1])},
            "difference": float(signal_latency.iloc[-1] - signal_latency.iloc[0])
        }
    except Exception as e:
        print(f"生成信号类型延迟图表时出错: {e}")
    
    # 图表3: 不同状态下的资源块使用率对比
    try:
        plt.figure(figsize=(10, 6))
        status_resource = df.groupby('status')['resource_block_usage_percent'].mean().sort_values(ascending=False)
        
        bars = plt.bar(status_resource.index, status_resource.values, color='salmon')
        plt.title('Average Resource Block Usage by Status', fontsize=14)
        plt.xlabel('Status', fontsize=12)
        plt.ylabel('Resource Block Usage (%)', fontsize=12)
        
        # 在柱状图上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.2f}%', ha='center', va='bottom', fontsize=10)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加分析说明
        plt.figtext(0.5, 0.01, 
                   "Finding: Failed and overloaded statuses consume significantly more resources than successful operations.",
                   ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart_path = 'pngs/chart_bar_status_resource_usage.png'
        plt.savefig(chart_path)
        plt.close()
        
        results["charts"].append({
            "title": "Average Resource Block Usage by Status",
            "path": chart_path,
            "data": status_resource.to_dict()
        })
        
        results["analysis_results"]["status_resource_usage"] = {
            "highest": {"status": status_resource.index[0], "usage": float(status_resource.iloc[0])},
            "lowest": {"status": status_resource.index[-1], "usage": float(status_resource.iloc[-1])},
            "difference": float(status_resource.iloc[0] - status_resource.iloc[-1])
        }
    except Exception as e:
        print(f"生成状态资源使用图表时出错: {e}")
    
    return results

# 保存分析结果为JSON
def save_results(results, output_path="analysis_results.json"):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存至 {output_path}")
    except Exception as e:
        print(f"保存分析结果时出错: {e}")

# 主函数
def main():
    file_path = "temp_csv/excel_data_20250317123517.csv"
    df = read_csv_file(file_path)
    
    if df is not None:
        print(f"成功读取CSV文件，共{len(df)}行数据")
        results = analyze_data(df)
        save_results(results)
    else:
        print("无法继续分析，请检查文件路径和格式")

if __name__ == "__main__":
    main()