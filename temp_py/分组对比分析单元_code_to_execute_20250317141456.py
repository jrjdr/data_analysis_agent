import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_data(file_path):
    """加载CSV数据文件"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def analyze_columns(df):
    """分析数据列类型和基本统计信息"""
    result = []
    result.append("数据列分析\n" + "="*50)
    
    # 区分数值列和分类列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    result.append(f"\n数值列 ({len(numeric_cols)}): {', '.join(numeric_cols)}")
    result.append(f"分类列 ({len(categorical_cols)}): {', '.join(categorical_cols)}")
    
    # 分析分类列
    result.append("\n分类列分析:\n" + "-"*50)
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        unique_count = len(value_counts)
        result.append(f"\n{col} (唯一值: {unique_count}):")
        if unique_count <= 10:  # 如果唯一值较少，显示所有值的分布
            for val, count in value_counts.items():
                result.append(f"  {val}: {count} ({count/len(df):.2%})")
        else:  # 否则只显示前5个
            for val, count in value_counts.head(5).items():
                result.append(f"  {val}: {count} ({count/len(df):.2%})")
            result.append(f"  ... 及其他 {unique_count-5} 个值")
    
    # 分析数值列
    result.append("\n数值列分析:\n" + "-"*50)
    for col in numeric_cols:
        if df[col].notna().sum() > 0:  # 确保列有非空值
            stats = df[col].describe()
            result.append(f"\n{col}:")
            result.append(f"  缺失值: {df[col].isna().sum()} ({df[col].isna().sum()/len(df):.2%})")
            result.append(f"  均值: {stats['mean']:.2f}")
            result.append(f"  中位数: {stats['50%']:.2f}")
            result.append(f"  标准差: {stats['std']:.2f}")
            result.append(f"  最小值: {stats['min']:.2f}")
            result.append(f"  最大值: {stats['max']:.2f}")
    
    return "\n".join(result)

def group_comparison(df):
    """对数据进行分组比较分析"""
    result = []
    result.append("\n分组比较分析\n" + "="*50)
    
    # 按服务器类型分组比较
    if 'server_name' in df.columns:
        result.append("\n按服务器名称分组比较:\n" + "-"*50)
        server_groups = df.groupby('server_name')
        
        # 选择关键指标进行比较
        key_metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                      'network_traffic_percent', 'load_avg_1min']
        
        # 确保只选择存在的列
        key_metrics = [col for col in key_metrics if col in df.columns]
        
        if key_metrics:
            comparison = server_groups[key_metrics].mean().round(2)
            result.append("\n各服务器平均资源使用情况:")
            result.append(comparison.to_string())
            
            # 找出每个指标的最高和最低服务器
            result.append("\n各指标最高/最低的服务器:")
            for metric in key_metrics:
                if pd.notna(comparison[metric]).any():
                    max_server = comparison[metric].idxmax()
                    min_server = comparison[metric].idxmin()
                    max_val = comparison.loc[max_server, metric]
                    min_val = comparison.loc[min_server, metric]
                    result.append(f"  {metric}:")
                    result.append(f"    最高: {max_server} ({max_val:.2f})")
                    result.append(f"    最低: {min_server} ({min_val:.2f})")
    
    # 按资源类型分组比较
    if 'resource_type' in df.columns:
        result.append("\n按资源类型分组比较:\n" + "-"*50)
        resource_groups = df.groupby('resource_type')
        
        # 选择数据库相关指标
        db_metrics = ['query_rate_per_sec', 'active_connections', 'cache_hit_rate_percent',
                     'avg_query_time_ms', 'transactions_per_sec']
        
        # 确保只选择存在的列
        db_metrics = [col for col in db_metrics if col in df.columns]
        
        if db_metrics:
            db_comparison = resource_groups[db_metrics].mean().round(2)
            result.append("\n不同资源类型的数据库性能指标:")
            result.append(db_comparison.to_string())
    
    # 按事件类型分组比较
    if 'event_type' in df.columns:
        result.append("\n按事件类型分组比较:\n" + "-"*50)
        event_groups = df.groupby('event_type')
        
        # 选择系统负载指标
        system_metrics = ['cpu_usage_percent', 'memory_usage_percent', 
                         'load_avg_1min', 'process_count']
        
        # 确保只选择存在的列
        system_metrics = [col for col in system_metrics if col in df.columns]
        
        if system_metrics:
            event_comparison = event_groups[system_metrics].mean().round(2)
            result.append("\n不同事件类型的系统负载情况:")
            result.append(event_comparison.to_string())
    
    # 时间段分析
    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            result.append("\n按时间段分组比较:\n" + "-"*50)
            time_groups = df.groupby('hour')
            
            # 选择性能指标
            perf_metrics = ['cpu_usage_percent', 'memory_usage_percent', 
                           'network_traffic_percent', 'query_rate_per_sec']
            
            # 确保只选择存在的列
            perf_metrics = [col for col in perf_metrics if col in df.columns]
            
            if perf_metrics:
                time_comparison = time_groups[perf_metrics].mean().round(2)
                
                # 找出高峰和低谷时段
                peak_hours = {}
                valley_hours = {}
                for metric in perf_metrics:
                    if pd.notna(time_comparison[metric]).any():
                        peak_hours[metric] = time_comparison[metric].idxmax()
                        valley_hours[metric] = time_comparison[metric].idxmin()
                
                result.append("\n各指标的高峰和低谷时段:")
                for metric in perf_metrics:
                    if metric in peak_hours:
                        result.append(f"  {metric}:")
                        result.append(f"    高峰时段: {peak_hours[metric]}时 ({time_comparison.loc[peak_hours[metric], metric]:.2f})")
                        result.append(f"    低谷时段: {valley_hours[metric]}时 ({time_comparison.loc[valley_hours[metric], metric]:.2f})")
        except Exception as e:
            result.append(f"时间分析出错: {e}")
    
    return "\n".join(result)

def save_results(content, output_path):
    """保存分析结果到文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果失败: {e}")
        return False

def main():
    file_path = "temp_csv/excel_data_20250317141159.csv"
    output_path = "pngs/group_comparison_results.txt"
    
    # 加载数据
    df = load_data(file_path)
    if df is None:
        return
    
    # 生成报告内容
    report = []
    report.append(f"数据分析报告\n{'='*50}")
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"数据文件: {file_path}")
    report.append(f"数据行数: {len(df)}")
    
    # 添加列分析
    report.append(analyze_columns(df))
    
    # 添加分组比较
    report.append(group_comparison(df))
    
    # 保存结果
    save_results("\n".join(report), output_path)

if __name__ == "__main__":
    main()