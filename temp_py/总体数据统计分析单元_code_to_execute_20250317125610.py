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
        
        # 创建输出目录
        output_dir = "pngs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 3. 分析数值列和分类列的分布
        stats_result = {
            "file_info": {
                "file_path": file_path,
                "row_count": len(df),
                "column_count": len(df.columns)
            },
            "numeric_stats": {},
            "categorical_stats": {},
            "charts": []
        }
        
        # 数值列统计
        for col in numeric_columns:
            if df[col].notna().any():  # 确保列不是全部为NaN
                stats_result["numeric_stats"][col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "missing_values": int(df[col].isna().sum())
                }
        
        # 分类列统计
        for col in categorical_columns:
            value_counts = df[col].value_counts()
            stats_result["categorical_stats"][col] = {
                "unique_values": int(df[col].nunique()),
                "most_common": {
                    "value": value_counts.index[0],
                    "count": int(value_counts.iloc[0])
                },
                "missing_values": int(df[col].isna().sum())
            }
        
        # 4. 生成统计图表
        print("正在生成统计图表...")
        
        # 图表1: 服务器资源使用情况热力图
        plt.figure(figsize=(14, 10))
        resource_cols = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                         'network_traffic_percent', 'temperature_celsius']
        
        # 按服务器和时间聚合数据
        pivot_df = df.pivot_table(
            index='server_name', 
            values=resource_cols,
            aggfunc='mean'
        ).sort_values('cpu_usage_percent', ascending=False)
        
        # 绘制热力图
        sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=.5)
        plt.title('Average Resource Usage by Server')
        plt.tight_layout()
        
        chart1_path = os.path.join(output_dir, f"chart_stats_resource_heatmap_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        plt.savefig(chart1_path)
        plt.close()
        
        stats_result["charts"].append({
            "title": "Average Resource Usage by Server",
            "description": "Heatmap showing average resource utilization across different servers. Higher values (darker colors) indicate higher resource usage.",
            "path": chart1_path
        })
        
        # 图表2: 数据库性能指标时间序列
        plt.figure(figsize=(14, 8))
        
        # 选择数据库类型的记录
        db_df = df[df['resource_type'] == 'database'].copy()
        if not db_df.empty:
            # 按时间聚合数据
            db_df.set_index('timestamp', inplace=True)
            db_hourly = db_df.resample('H').mean()
            
            # 绘制多指标时间序列图
            ax = db_hourly['query_rate_per_sec'].plot(label='Query Rate (per sec)', color='blue')
            ax2 = ax.twinx()
            db_hourly['avg_query_time_ms'].plot(ax=ax2, label='Avg Query Time (ms)', color='red')
            
            ax.set_xlabel('Time')
            ax.set_ylabel('Queries per Second')
            ax2.set_ylabel('Average Query Time (ms)')
            
            # 合并图例
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.title('Database Performance Metrics Over Time')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            chart2_path = os.path.join(output_dir, f"chart_stats_db_performance_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
            plt.savefig(chart2_path)
            plt.close()
            
            stats_result["charts"].append({
                "title": "Database Performance Metrics Over Time",
                "description": "Time series showing query rate and average query time. Reveals performance patterns and potential bottlenecks over time.",
                "path": chart2_path
            })
        else:
            # 如果没有数据库记录，创建一个替代图表
            # 图表2(替代): 系统负载随时间变化
            plt.figure(figsize=(14, 8))
            
            # 按时间聚合数据
            df.set_index('timestamp', inplace=True)
            hourly_data = df.resample('H').mean()
            
            ax = hourly_data['load_avg_1min'].plot(label='1 min', color='blue')
            hourly_data['load_avg_5min'].plot(ax=ax, label='5 min', color='green')
            hourly_data['load_avg_15min'].plot(ax=ax, label='15 min', color='red')
            
            ax.set_xlabel('Time')
            ax.set_ylabel('System Load Average')
            ax.legend()
            
            plt.title('System Load Average Over Time')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            chart2_path = os.path.join(output_dir, f"chart_stats_system_load_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
            plt.savefig(chart2_path)
            plt.close()
            
            stats_result["charts"].append({
                "title": "System Load Average Over Time",
                "description": "Time series showing system load averages at different intervals (1, 5, and 15 minutes). Helps identify periods of high system stress.",
                "path": chart2_path
            })
        
        # 图表3: 事件类型分布饼图
        plt.figure(figsize=(10, 8))
        event_counts = df['event_type'].value_counts()
        plt.pie(event_counts, labels=event_counts.index, autopct='%1.1f%%', 
                startangle=90, shadow=True, explode=[0.05]*len(event_counts))
        plt.axis('equal')
        plt.title('Distribution of Event Types')
        
        chart3_path = os.path.join(output_dir, f"chart_stats_event_types_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        plt.savefig(chart3_path)
        plt.close()
        
        stats_result["charts"].append({
            "title": "Distribution of Event Types",
            "description": "Pie chart showing the distribution of different event types. Normal events dominate, with various alert types making up a small percentage.",
            "path": chart3_path
        })
        
        # 5. 将分析结果保存为JSON格式
        json_path = os.path.join(output_dir, f"stats_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats_result, f, ensure_ascii=False, indent=2)
        
        print(f"分析完成! 结果已保存到 {json_path}")
        print(f"生成的图表已保存到 {output_dir} 目录")
        
        return stats_result
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317125505.csv"
    analyze_csv_data(file_path)