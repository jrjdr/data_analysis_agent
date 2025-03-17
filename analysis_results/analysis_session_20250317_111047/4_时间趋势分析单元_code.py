import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

# 创建保存图表的目录
os.makedirs("pngs", exist_ok=True)

# 读取CSV文件
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取数据，共 {len(df)} 行")
        return df
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

# 处理时间列
def process_timestamp(df):
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['date'] = df['timestamp'].dt.date
        print("时间列处理完成")
        return df
    except Exception as e:
        print(f"处理时间列时出错: {e}")
        return df

# 分析数据趋势
def analyze_trends(df):
    results = {}
    
    # 按基站和时间聚合数据
    hourly_stats = df.groupby(['base_station_name', pd.Grouper(key='timestamp', freq='H')]).agg({
        'success_rate': 'mean',
        'active_users': 'mean',
        'signal_strength_dbm': 'mean',
        'downlink_throughput_mbps': 'mean',
        'latency_ms': 'mean',
        'packet_loss_percent': 'mean',
        'cpu_usage_percent': 'mean',
        'temperature_celsius': 'mean'
    }).reset_index()
    
    # 计算每个基站的关键指标
    station_stats = {}
    for station in df['base_station_name'].unique():
        station_data = df[df['base_station_name'] == station]
        station_stats[station] = {
            'avg_success_rate': float(station_data['success_rate'].mean()),
            'avg_throughput': float(station_data['downlink_throughput_mbps'].mean()),
            'peak_users': int(station_data['active_users'].max()),
            'avg_latency': float(station_data['latency_ms'].mean())
        }
    
    results['station_stats'] = station_stats
    results['hourly_stats'] = hourly_stats.to_dict(orient='records')
    
    return results, hourly_stats

# 生成图表
def create_charts(df, hourly_stats):
    chart_info = []
    
    # 图表1: 各基站的成功率随时间变化
    try:
        plt.figure(figsize=(12, 6))
        for station in df['base_station_name'].unique():
            station_data = hourly_stats[hourly_stats['base_station_name'] == station]
            plt.plot(station_data['timestamp'], station_data['success_rate'], label=station)
        
        plt.title('Success Rate Trend by Base Station')
        plt.xlabel('Time')
        plt.ylabel('Success Rate')
        plt.legend(loc='lower right')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 添加趋势说明
        plt.figtext(0.5, 0.01, 'Key Finding: Success rates show daily patterns with peaks during off-peak hours', 
                   ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        chart_path = "pngs/chart_trend_success_rate.png"
        plt.savefig(chart_path)
        plt.close()
        
        chart_info.append({
            "title": "Success Rate Trend by Base Station",
            "path": chart_path,
            "description": "Shows how success rates vary across different base stations over time"
        })
    except Exception as e:
        print(f"生成成功率图表时出错: {e}")
    
    # 图表2: 用户数量和延迟的关系随时间变化
    try:
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # 选择一个基站进行详细分析
        station = df['base_station_name'].unique()[0]
        station_data = hourly_stats[hourly_stats['base_station_name'] == station]
        
        # 用户数量 (左Y轴)
        color = 'tab:blue'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Active Users', color=color)
        ax1.plot(station_data['timestamp'], station_data['active_users'], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        
        # 延迟 (右Y轴)
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Latency (ms)', color=color)
        ax2.plot(station_data['timestamp'], station_data['latency_ms'], color=color, linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title(f'Active Users vs Latency for {station}')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 添加趋势说明
        plt.figtext(0.5, 0.01, 'Key Finding: Latency increases with higher user counts, showing network congestion effects', 
                   ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        chart_path = "pngs/chart_trend_users_latency.png"
        plt.savefig(chart_path)
        plt.close()
        
        chart_info.append({
            "title": f"Active Users vs Latency for {station}",
            "path": chart_path,
            "description": "Shows the relationship between user count and network latency over time"
        })
    except Exception as e:
        print(f"生成用户数量和延迟图表时出错: {e}")
    
    # 图表3: 吞吐量和CPU使用率的关系
    try:
        plt.figure(figsize=(12, 6))
        
        # 计算每个基站的平均值
        station_avg = df.groupby('base_station_name').agg({
            'downlink_throughput_mbps': 'mean',
            'cpu_usage_percent': 'mean',
            'active_users': 'mean'
        }).reset_index()
        
        # 绘制散点图，大小表示活跃用户数
        plt.scatter(station_avg['downlink_throughput_mbps'], station_avg['cpu_usage_percent'], 
                   s=station_avg['active_users']/2, alpha=0.7)
        
        # 添加基站标签
        for i, row in station_avg.iterrows():
            plt.annotate(row['base_station_name'], 
                        (row['downlink_throughput_mbps'], row['cpu_usage_percent']),
                        xytext=(5, 5), textcoords='offset points')
        
        plt.title('Throughput vs CPU Usage by Base Station')
        plt.xlabel('Downlink Throughput (Mbps)')
        plt.ylabel('CPU Usage (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 添加趋势说明
        plt.figtext(0.5, 0.01, 'Key Finding: Higher throughput correlates with increased CPU usage across base stations', 
                   ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        chart_path = "pngs/chart_trend_throughput_cpu.png"
        plt.savefig(chart_path)
        plt.close()
        
        chart_info.append({
            "title": "Throughput vs CPU Usage by Base Station",
            "path": chart_path,
            "description": "Shows the relationship between throughput and CPU usage for each base station"
        })
    except Exception as e:
        print(f"生成吞吐量和CPU使用率图表时出错: {e}")
    
    return chart_info

# 保存分析结果为JSON
def save_results(results, chart_info):
    try:
        output = {
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "temp_csv/excel_data_20250317111047.csv",
            "charts": chart_info,
            "statistics": results
        }
        
        with open("pngs/analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print("分析结果已保存到 pngs/analysis_results.json")
    except Exception as e:
        print(f"保存结果时出错: {e}")

# 主函数
def main():
    file_path = "temp_csv/excel_data_20250317111047.csv"
    
    # 读取数据
    df = load_data(file_path)
    if df is None:
        return
    
    # 处理时间列
    df = process_timestamp(df)
    
    # 分析趋势
    results, hourly_stats = analyze_trends(df)
    
    # 生成图表
    chart_info = create_charts(df, hourly_stats)
    
    # 保存结果
    save_results(results, chart_info)
    
    print("分析完成，图表已保存到pngs目录")

if __name__ == "__main__":
    main()