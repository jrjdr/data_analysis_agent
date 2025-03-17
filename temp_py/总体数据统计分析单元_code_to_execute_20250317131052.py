import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    try:
        # 1. 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 2. 基本描述性统计分析
        # 获取基本信息
        basic_info = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "timestamp_range": {
                "start": df['timestamp'].min(),
                "end": df['timestamp'].max()
            }
        }
        
        # 3. 分析数值列和分类列的分布
        column_analysis = {}
        
        # 分类所有列
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # 分析分类列
        for col in categorical_columns:
            value_counts = df[col].value_counts()
            column_analysis[col] = {
                "type": "categorical",
                "missing_values": df[col].isna().sum(),
                "unique_values": df[col].nunique(),
                "most_common": {
                    "value": value_counts.index[0],
                    "count": value_counts.iloc[0]
                },
                "distribution": value_counts.head(5).to_dict()
            }
        
        # 分析数值列
        for col in numeric_columns:
            stats = df[col].describe()
            column_analysis[col] = {
                "type": "numeric",
                "missing_values": df[col].isna().sum(),
                "unique_values": df[col].nunique(),
                "min": stats['min'],
                "max": stats['max'],
                "mean": stats['mean'],
                "median": stats['50%'],
                "std": stats['std'],
                "quartiles": {
                    "25%": stats['25%'],
                    "50%": stats['50%'],
                    "75%": stats['75%']
                }
            }
        
        # 4. 分析服务器资源使用情况
        server_analysis = {}
        for server_id in df['server_id'].unique():
            server_df = df[df['server_id'] == server_id]
            server_analysis[server_id] = {
                "server_name": server_df['server_name'].iloc[0],
                "avg_cpu_usage": server_df['cpu_usage_percent'].mean(),
                "avg_memory_usage": server_df['memory_usage_percent'].mean(),
                "avg_disk_usage": server_df['disk_usage_percent'].mean(),
                "avg_network_traffic": server_df['network_traffic_percent'].mean(),
                "event_counts": server_df['event_type'].value_counts().to_dict()
            }
        
        # 5. 分析异常事件
        event_analysis = {
            "total_events": df['event_type'].value_counts().to_dict(),
            "critical_events": len(df[df['event_type'] == 'critical']),
            "warning_events": len(df[df['event_type'] == 'warning']),
            "servers_with_most_critical": df[df['event_type'] == 'critical']['server_id'].value_counts().head(3).to_dict()
        }
        
        # 6. 数据库性能分析 (针对resource_type为'database'的记录)
        db_df = df[df['resource_type'] == 'database']
        db_analysis = {}
        if not db_df.empty:
            db_analysis = {
                "avg_query_rate": db_df['query_rate_per_sec'].mean(),
                "avg_query_time": db_df['avg_query_time_ms'].mean(),
                "avg_cache_hit_rate": db_df['cache_hit_rate_percent'].mean(),
                "total_slow_queries": db_df['slow_queries_count'].sum(),
                "total_deadlocks": db_df['deadlock_count'].sum()
            }
        
        # 汇总分析结果
        analysis_results = {
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "basic_info": basic_info,
            "column_analysis": column_analysis,
            "server_analysis": server_analysis,
            "event_analysis": event_analysis,
            "database_analysis": db_analysis
        }
        
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存为JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        return f"分析完成，结果已保存到 {output_path}"
    
    except FileNotFoundError:
        return f"错误：找不到文件 {file_path}"
    except Exception as e:
        return f"分析过程中发生错误: {str(e)}"

# 执行分析
result = analyze_csv_data("temp_csv/excel_data_20250317131028.csv", "pngs/analysis_results.json")
print(result)