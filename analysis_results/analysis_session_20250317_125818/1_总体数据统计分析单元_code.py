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
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 确保时间戳列是日期时间类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 2. 基本描述性统计分析
        print("正在进行基本统计分析...")
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # 基本统计信息
        numeric_stats = df[numeric_columns].describe().to_dict()
        categorical_stats = {col: df[col].value_counts().to_dict() for col in categorical_columns}
        
        # 3. 分析数值列和分类列的分布
        print("分析列分布...")
        
        # 创建保存图表的目录
        os.makedirs("pngs", exist_ok=True)
        
        # 4. 生成统计图表
        print("生成统计图表...")
        charts_info = []
        
        # 图表1: 服务器资源使用情况热力图
        plt.figure(figsize=(14, 10))
        resource_cols = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                         'network_traffic_percent', 'temperature_celsius']
        
        # 按服务器和时间聚合数据
        pivot_data = df.pivot_table(
            index='server_name', 
            values=resource_cols,
            aggfunc='mean'
        ).sort_values('cpu_usage_percent', ascending=False)
        
        # 绘制热力图
        sns.heatmap(pivot_data, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=.5)
        plt.title('Average Resource Usage by Server', fontsize=16)
        plt.tight_layout()
        
        chart1_path = "pngs/chart_stats_resource_usage_by_server.png"
        plt.savefig(chart1_path)
        plt.close()
        
        charts_info.append({
            "title": "Average Resource Usage by Server",
            "description": "Heatmap showing average resource utilization across different servers. "
                          "Higher values (darker colors) indicate higher resource consumption.",
            "path": chart1_path
        })
        
        # 图表2: 数据库性能指标时间序列
        plt.figure(figsize=(14, 8))
        
        # 按时间聚合数据库性能指标
        db_metrics = df[df['resource_type'] == 'database'].groupby(pd.Grouper(key='timestamp', freq='1H')).agg({
            'query_rate_per_sec': 'mean',
            'avg_query_time_ms': 'mean',
            'cache_hit_rate_percent': 'mean'
        })
        
        # 创建三个子图
        fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
        
        # 绘制查询率
        axes[0].plot(db_metrics.index, db_metrics['query_rate_per_sec'], 'b-', linewidth=2)
        axes[0].set_ylabel('Queries/sec')
        axes[0].set_title('Database Performance Metrics Over Time')
        axes[0].grid(True)
        
        # 绘制平均查询时间
        axes[1].plot(db_metrics.index, db_metrics['avg_query_time_ms'], 'r-', linewidth=2)
        axes[1].set_ylabel('Avg Query Time (ms)')
        axes[1].grid(True)
        
        # 绘制缓存命中率
        axes[2].plot(db_metrics.index, db_metrics['cache_hit_rate_percent'], 'g-', linewidth=2)
        axes[2].set_ylabel('Cache Hit Rate (%)')
        axes[2].set_xlabel('Time')
        axes[2].grid(True)
        
        plt.tight_layout()
        chart2_path = "pngs/chart_stats_db_performance_time_series.png"
        plt.savefig(chart2_path)
        plt.close()
        
        charts_info.append({
            "title": "Database Performance Metrics Over Time",
            "description": "Time series showing query rate, average query time, and cache hit rate. "
                          "Patterns indicate performance fluctuations throughout the monitoring period.",
            "path": chart2_path
        })
        
        # 图表3: 事件类型分布饼图
        plt.figure(figsize=(10, 8))
        event_counts = df['event_type'].value_counts()
        plt.pie(event_counts, labels=event_counts.index, autopct='%1.1f%%', 
                startangle=90, shadow=True, explode=[0.05]*len(event_counts))
        plt.axis('equal')
        plt.title('Distribution of Event Types', fontsize=16)
        
        chart3_path = "pngs/chart_stats_event_distribution.png"
        plt.savefig(chart3_path)
        plt.close()
        
        charts_info.append({
            "title": "Distribution of Event Types",
            "description": "Pie chart showing the distribution of different event types. "
                          "Normal events dominate, with critical and warning events requiring attention.",
            "path": chart3_path
        })
        
        # 5. 将分析结果保存为JSON格式
        print("保存分析结果...")
        result = {
            "file_analyzed": file_path,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "row_count": len(df),
            "column_count": len(df.columns),
            "numeric_statistics": numeric_stats,
            "categorical_statistics": categorical_stats,
            "charts": charts_info,
            "key_findings": [
                "服务器资源使用情况存在显著差异，部分服务器CPU和内存使用率较高",
                f"数据库查询率平均为 {df['query_rate_per_sec'].mean():.2f} 每秒，最高达到 {df['query_rate_per_sec'].max():.2f} 每秒",
                f"缓存命中率平均为 {df['cache_hit_rate_percent'].mean():.2f}%，表明缓存配置总体良好",
                f"共有 {df[df['event_type'] != 'normal'].shape[0]} 条非正常事件记录，需要关注",
                f"平均查询时间为 {df['avg_query_time_ms'].mean():.2f} 毫秒，最高达到 {df['avg_query_time_ms'].max():.2f} 毫秒"
            ]
        }
        
        # 保存JSON结果
        with open("pngs/analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("分析完成！结果已保存到 pngs/analysis_results.json")
        return result
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317125818.csv"
    analyze_csv_data(file_path)