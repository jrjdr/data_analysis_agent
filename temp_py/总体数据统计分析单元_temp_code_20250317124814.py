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
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # 基本统计信息
        numeric_stats = df[numeric_columns].describe().to_dict()
        categorical_stats = {col: df[col].value_counts().to_dict() for col in categorical_columns}
        
        # 3. 分析数值列和分类列的分布
        print("分析数据分布...")
        
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
        
        # 绘制多轴图表
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        color1, color2, color3 = 'tab:blue', 'tab:red', 'tab:green'
        
        # 查询率
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Queries per Second', color=color1)
        ax1.plot(db_metrics.index, db_metrics['query_rate_per_sec'], color=color1, label='Query Rate')
        ax1.tick_params(axis='y', labelcolor=color1)
        
        # 查询时间
        ax2 = ax1.twinx()
        ax2.set_ylabel('Query Time (ms)', color=color2)
        ax2.plot(db_metrics.index, db_metrics['avg_query_time_ms'], color=color2, label='Avg Query Time')
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # 缓存命中率
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        ax3.set_ylabel('Cache Hit Rate (%)', color=color3)
        ax3.plot(db_metrics.index, db_metrics['cache_hit_rate_percent'], color=color3, label='Cache Hit Rate')
        ax3.tick_params(axis='y', labelcolor=color3)
        
        # 添加图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()
        ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper left')
        
        plt.title('Database Performance Metrics Over Time', fontsize=16)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        chart2_path = "pngs/chart_stats_db_performance_time_series.png"
        plt.savefig(chart2_path)
        plt.close()
        
        charts_info.append({
            "title": "Database Performance Metrics Over Time",
            "description": "Time series showing key database performance indicators: query rate, "
                          "average query time, and cache hit rate. Periods of high query rates "
                          "often correlate with increased query times and varying cache efficiency.",
            "path": chart2_path
        })
        
        # 图表3: 事件类型分布饼图
        plt.figure(figsize=(10, 8))
        event_counts = df['event_type'].value_counts()
        plt.pie(event_counts, labels=event_counts.index, autopct='%1.1f%%', 
                startangle=90, shadow=True, explode=[0.05]*len(event_counts))
        plt.title('Distribution of Event Types', fontsize=16)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        chart3_path = "pngs/chart_stats_event_distribution.png"
        plt.savefig(chart3_path)
        plt.close()
        
        charts_info.append({
            "title": "Distribution of Event Types",
            "description": "Pie chart showing the distribution of different event types in the system. "
                          "Normal events dominate, with various alert types making up a small percentage.",
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
            "summary": {
                "avg_cpu_usage": df['cpu_usage_percent'].mean(),
                "avg_memory_usage": df['memory_usage_percent'].mean(),
                "avg_disk_usage": df['disk_usage_percent'].mean(),
                "avg_query_rate": df['query_rate_per_sec'].mean(),
                "total_slow_queries": df['slow_queries_count'].sum(),
                "total_deadlocks": df['deadlock_count'].sum(),
                "event_distribution": df['event_type'].value_counts().to_dict()
            }
        }
        
        # 保存JSON结果
        json_path = "pngs/analysis_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"分析完成! 结果已保存到 {json_path}")
        print(f"图表已保存到 pngs/ 目录")
        
        return result
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return {"error": str(e)}

# 执行分析
if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317124712.csv"
    analyze_csv_data(file_path)