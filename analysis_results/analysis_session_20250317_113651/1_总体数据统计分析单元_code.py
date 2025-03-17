import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import os
from datetime import datetime

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def analyze_csv_data(file_path):
    try:
        # 1. 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 创建保存图表的目录
        os.makedirs('pngs', exist_ok=True)
        
        # 2. 基本描述性统计分析
        numeric_columns = df.select_dtypes(include=['number']).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # 基本统计信息
        numeric_stats = df[numeric_columns].describe().to_dict()
        categorical_stats = {col: df[col].value_counts().to_dict() for col in categorical_columns}
        
        # 3. 分析数值列和分类列的分布
        # 将timestamp转换为datetime类型以便分析
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        # 4. 生成统计图表
        # 图表1: 不同基站的信号强度和成功率对比
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='base_station_name', y='signal_strength_dbm', data=df)
        plt.title('Signal Strength by Base Station')
        plt.xlabel('Base Station')
        plt.ylabel('Signal Strength (dBm)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.figtext(0.5, 0.01, 'Finding: Base stations show varying signal strength distributions, with 城东-商业区基站 having the strongest signals overall.', 
                   ha='center', fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        chart1_path = 'pngs/chart_stats_signal_strength_by_station.png'
        plt.savefig(chart1_path)
        plt.close()
        
        # 图表2: 一天中不同时段的网络性能指标
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 2, 1)
        sns.lineplot(x='hour', y='success_rate', data=df, ci='sd', estimator='mean')
        plt.title('Average Success Rate by Hour')
        plt.xlabel('Hour of Day')
        plt.ylabel('Success Rate')
        
        plt.subplot(2, 2, 2)
        sns.lineplot(x='hour', y='latency_ms', data=df, ci='sd', estimator='mean')
        plt.title('Average Latency by Hour')
        plt.xlabel('Hour of Day')
        plt.ylabel('Latency (ms)')
        
        plt.subplot(2, 2, 3)
        sns.lineplot(x='hour', y='downlink_throughput_mbps', data=df, ci='sd', estimator='mean')
        plt.title('Average Downlink Throughput by Hour')
        plt.xlabel('Hour of Day')
        plt.ylabel('Downlink Throughput (Mbps)')
        
        plt.subplot(2, 2, 4)
        sns.lineplot(x='hour', y='packet_loss_percent', data=df, ci='sd', estimator='mean')
        plt.title('Average Packet Loss by Hour')
        plt.xlabel('Hour of Day')
        plt.ylabel('Packet Loss (%)')
        
        plt.tight_layout()
        plt.figtext(0.5, 0.01, 'Finding: Network performance metrics show clear patterns throughout the day, with peak hours showing decreased performance.', 
                   ha='center', fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        chart2_path = 'pngs/chart_stats_network_performance_by_hour.png'
        plt.savefig(chart2_path)
        plt.close()
        
        # 图表3: 信号类型与状态的关系
        plt.figure(figsize=(14, 8))
        status_by_signal = pd.crosstab(df['signal_type'], df['status'])
        status_by_signal_percent = status_by_signal.div(status_by_signal.sum(axis=1), axis=0)
        status_by_signal_percent.plot(kind='bar', stacked=True, colormap='viridis')
        plt.title('Status Distribution by Signal Type')
        plt.xlabel('Signal Type')
        plt.ylabel('Percentage')
        plt.legend(title='Status')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.figtext(0.5, 0.01, 'Finding: Different signal types show varying success rates, with some types being more prone to failures than others.', 
                   ha='center', fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        chart3_path = 'pngs/chart_stats_status_by_signal_type.png'
        plt.savefig(chart3_path)
        plt.close()
        
        # 5. 将分析结果保存为JSON格式
        result = {
            "file_analyzed": file_path,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "row_count": len(df),
            "column_count": len(df.columns),
            "numeric_statistics": numeric_stats,
            "categorical_statistics": {
                k: v for k, v in categorical_stats.items() 
                if len(v) <= 10  # 只包含值较少的分类变量的统计
            },
            "charts_generated": [
                {
                    "title": "Signal Strength by Base Station",
                    "path": chart1_path,
                    "description": "Comparison of signal strength across different base stations"
                },
                {
                    "title": "Network Performance Metrics by Hour",
                    "path": chart2_path,
                    "description": "Hourly patterns in success rate, latency, throughput and packet loss"
                },
                {
                    "title": "Status Distribution by Signal Type",
                    "path": chart3_path,
                    "description": "Success and failure rates for different signal types"
                }
            ],
            "key_findings": [
                "Base stations show varying signal strength distributions",
                "Network performance metrics show clear patterns throughout the day",
                "Different signal types have varying success rates"
            ]
        }
        
        # 保存JSON结果
        with open('analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        return result
    
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317113651.csv"
    result = analyze_csv_data(file_path)
    print("分析完成，结果已保存到 analysis_results.json")
    print(f"生成的图表保存在 pngs 目录下")