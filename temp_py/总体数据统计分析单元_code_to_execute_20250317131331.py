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
        # 获取数据基本信息
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
        # 分离数值列和分类列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # 数值列分析
        numeric_analysis = {}
        for col in numeric_cols:
            # 跳过缺失值过多的列
            if df[col].isna().sum() > len(df) / 2:
                continue
                
            stats = df[col].describe().to_dict()
            # 添加额外统计信息
            stats["missing_values"] = df[col].isna().sum()
            stats["unique_values"] = df[col].nunique()
            
            # 检查异常值 (使用IQR方法)
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            stats["outliers_count"] = int(outliers)
            stats["outliers_percent"] = round(outliers / len(df) * 100, 2)
            
            numeric_analysis[col] = stats
        
        # 分类列分析
        categorical_analysis = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            stats = {
                "unique_values": df[col].nunique(),
                "missing_values": df[col].isna().sum(),
                "most_common": {
                    "value": value_counts.index[0],
                    "count": int(value_counts.iloc[0]),
                    "percent": round(value_counts.iloc[0] / len(df) * 100, 2)
                }
            }
            # 添加所有类别的分布
            if df[col].nunique() <= 10:  # 只对少量类别的列显示完整分布
                distribution = {}
                for val, count in value_counts.items():
                    distribution[val] = {
                        "count": int(count),
                        "percent": round(count / len(df) * 100, 2)
                    }
                stats["distribution"] = distribution
            
            categorical_analysis[col] = stats
        
        # 4. 特殊分析：服务器性能指标
        server_performance = {}
        if 'server_id' in df.columns and 'cpu_usage_percent' in df.columns:
            # 按服务器分组计算平均性能指标
            perf_metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                           'network_traffic_percent']
            perf_metrics = [m for m in perf_metrics if m in df.columns]
            
            if perf_metrics:
                server_perf = df.groupby('server_id')[perf_metrics].mean().to_dict('index')
                server_performance["avg_by_server"] = server_perf
        
        # 5. 事件分析
        event_analysis = {}
        if 'event_type' in df.columns:
            event_counts = df['event_type'].value_counts().to_dict()
            event_analysis["event_distribution"] = event_counts
            
            # 如果有警告或错误事件，提取相关信息
            if 'warning' in df['event_type'].values or 'error' in df['event_type'].values:
                critical_events = df[df['event_type'].isin(['warning', 'error', 'critical'])]
                if not critical_events.empty:
                    event_analysis["critical_events_count"] = len(critical_events)
                    event_analysis["critical_events_percent"] = round(len(critical_events) / len(df) * 100, 2)
        
        # 组合所有分析结果
        analysis_results = {
            "basic_info": basic_info,
            "numeric_analysis": numeric_analysis,
            "categorical_analysis": categorical_analysis,
            "server_performance": server_performance,
            "event_analysis": event_analysis,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存为JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            
        return True, "分析完成，结果已保存到 " + output_path
        
    except Exception as e:
        return False, f"分析过程中出错: {str(e)}"

# 执行分析
success, message = analyze_csv_data("temp_csv/excel_data_20250317131305.csv", "pngs/analysis_results.json")
print(message)