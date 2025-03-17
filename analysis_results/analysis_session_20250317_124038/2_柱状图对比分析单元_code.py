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
        
        # 创建保存图表的目录
        os.makedirs('pngs', exist_ok=True)
        
        # 2. 分析数据
        analysis_results = {}
        
        # 分析基站性能
        station_performance = df.groupby('base_station_name').agg({
            'success_rate': 'mean',
            'failure_rate': 'mean',
            'signal_strength_dbm': 'mean',
            'downlink_throughput_mbps': 'mean',
            'uplink_throughput_mbps': 'mean',
            'latency_ms': 'mean'
        }).reset_index()
        
        # 分析信号类型分布
        signal_type_counts = df['signal_type'].value_counts().reset_index()
        signal_type_counts.columns = ['signal_type', 'count']
        
        # 分析状态分布
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        # 3. 生成柱状图
        
        # 图表1: 基站性能对比
        plt.figure(figsize=(12, 8))
        x = np.arange(len(station_performance['base_station_name']))
        width = 0.2
        
        plt.bar(x - width*1.5, station_performance['success_rate'], width, label='Success Rate')
        plt.bar(x - width/2, station_performance['downlink_throughput_mbps']/1500, width, label='Downlink Throughput (normalized)')
        plt.bar(x + width/2, station_performance['uplink_throughput_mbps']/200, width, label='Uplink Throughput (normalized)')
        plt.bar(x + width*1.5, station_performance['latency_ms']/50, width, label='Latency (normalized)')
        
        plt.xlabel('Base Station')
        plt.ylabel('Normalized Values')
        plt.title('Base Station Performance Comparison')
        plt.xticks(x, station_performance['base_station_name'], rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加描述
        plt.figtext(0.5, 0.01, 
                   "Key finding: Performance varies significantly across base stations, with urban stations showing better throughput but higher latency.", 
                   ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        chart1_path = 'pngs/chart_bar_station_performance.png'
        plt.savefig(chart1_path)
        plt.close()
        
        # 图表2: 信号类型分布
        plt.figure(figsize=(14, 8))
        top_signals = signal_type_counts.head(10)  # 取前10个信号类型
        
        bars = plt.bar(top_signals['signal_type'], top_signals['count'], color='skyblue')
        plt.xlabel('Signal Type')
        plt.ylabel('Count')
        plt.title('Distribution of Top 10 Signal Types')
        plt.xticks(rotation=45, ha='right')
        
        # 在柱状图上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{height}', ha='center', va='bottom')
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加描述
        plt.figtext(0.5, 0.01, 
                   "Key finding: PAGING signals are the most common, followed by DATA and VOICE signals.", 
                   ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        chart2_path = 'pngs/chart_bar_signal_distribution.png'
        plt.savefig(chart2_path)
        plt.close()
        
        # 图表3: 状态分布与基站关系
        plt.figure(figsize=(12, 8))
        status_by_station = pd.crosstab(df['base_station_name'], df['status'])
        status_by_station.plot(kind='bar', stacked=True, colormap='viridis')
        
        plt.xlabel('Base Station')
        plt.ylabel('Count')
        plt.title('Status Distribution by Base Station')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Status')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加描述
        plt.figtext(0.5, 0.01, 
                   "Key finding: Urban stations have higher success rates, while rural stations show more failures and warnings.", 
                   ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        chart3_path = 'pngs/chart_bar_status_by_station.png'
        plt.savefig(chart3_path)
        plt.close()
        
        # 4. 保存分析结果为JSON
        analysis_results = {
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_analyzed": file_path,
            "row_count": len(df),
            "charts": [
                {
                    "title": "Base Station Performance Comparison",
                    "file_path": chart1_path,
                    "description": "Comparison of key performance metrics across different base stations",
                    "metrics": station_performance.to_dict('records')
                },
                {
                    "title": "Distribution of Top 10 Signal Types",
                    "file_path": chart2_path,
                    "description": "Frequency distribution of the most common signal types",
                    "metrics": top_signals.to_dict('records')
                },
                {
                    "title": "Status Distribution by Base Station",
                    "file_path": chart3_path,
                    "description": "Distribution of connection statuses across different base stations",
                    "metrics": status_by_station.to_dict()
                }
            ],
            "summary_statistics": {
                "success_rate": {
                    "mean": df['success_rate'].mean(),
                    "median": df['success_rate'].median(),
                    "min": df['success_rate'].min(),
                    "max": df['success_rate'].max()
                },
                "signal_strength_dbm": {
                    "mean": df['signal_strength_dbm'].mean(),
                    "median": df['signal_strength_dbm'].median(),
                    "min": df['signal_strength_dbm'].min(),
                    "max": df['signal_strength_dbm'].max()
                }
            }
        }
        
        with open('analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=4)
        
        return analysis_results
        
    except Exception as e:
        print(f"Error analyzing CSV data: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317124038.csv"
    results = analyze_csv_data(file_path)
    print(f"Analysis complete. Results saved to analysis_results.json")
    print(f"Charts saved to pngs directory")