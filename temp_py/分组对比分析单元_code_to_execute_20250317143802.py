import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_csv_data(file_path):
    """加载CSV文件数据"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载CSV文件失败: {e}")
        return None

def analyze_column_distributions(df):
    """分析数值列和分类列的分布"""
    results = []
    
    # 分类数据列
    categorical_cols = df.select_dtypes(include=['object']).columns
    results.append("=== 分类列分布 ===")
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        results.append(f"\n{col} 分布:")
        for val, count in value_counts.items():
            results.append(f"  {val}: {count} ({count/len(df)*100:.2f}%)")
    
    # 数值数据列
    numeric_cols = df.select_dtypes(include=['number']).columns
    results.append("\n\n=== 数值列统计 ===")
    for col in numeric_cols:
        if df[col].notna().sum() > 0:  # 只处理有数据的列
            results.append(f"\n{col} 统计:")
            results.append(f"  非空值数: {df[col].notna().sum()}")
            results.append(f"  最小值: {df[col].min():.2f}")
            results.append(f"  最大值: {df[col].max():.2f}")
            results.append(f"  平均值: {df[col].mean():.2f}")
            results.append(f"  中位数: {df[col].median():.2f}")
            results.append(f"  标准差: {df[col].std():.2f}")
    
    return "\n".join(results)

def group_comparison(df):
    """对数据进行分组统计，比较不同组之间的差异"""
    results = []
    
    # 按服务器类型分组比较
    results.append("=== 按服务器名称分组比较 ===")
    server_groups = df.groupby('server_name')
    
    # 选择一些关键指标进行比较
    key_metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                  'network_traffic_percent', 'temperature_celsius']
    
    for metric in key_metrics:
        if metric in df.columns:
            results.append(f"\n{metric} 按服务器比较:")
            group_stats = server_groups[metric].agg(['mean', 'median', 'std']).round(2)
            for server, stats in group_stats.iterrows():
                results.append(f"  {server}: 平均值={stats['mean']}, 中位数={stats['median']}, 标准差={stats['std']}")
    
    # 按资源类型分组比较
    if 'resource_type' in df.columns:
        results.append("\n\n=== 按资源类型分组比较 ===")
        resource_groups = df.groupby('resource_type')
        
        for metric in key_metrics:
            if metric in df.columns:
                results.append(f"\n{metric} 按资源类型比较:")
                group_stats = resource_groups[metric].agg(['mean', 'median', 'std', 'count']).round(2)
                for resource, stats in group_stats.iterrows():
                    results.append(f"  {resource}: 平均值={stats['mean']}, 中位数={stats['median']}, 标准差={stats['std']}, 计数={stats['count']}")
    
    # 按事件类型分组比较
    if 'event_type' in df.columns:
        results.append("\n\n=== 按事件类型分组比较 ===")
        event_groups = df.groupby('event_type')
        
        for metric in key_metrics:
            if metric in df.columns:
                results.append(f"\n{metric} 按事件类型比较:")
                group_stats = event_groups[metric].agg(['mean', 'median', 'std', 'count']).round(2)
                for event, stats in group_stats.iterrows():
                    results.append(f"  {event}: 平均值={stats['mean']}, 中位数={stats['median']}, 标准差={stats['std']}, 计数={stats['count']}")
    
    # 数据库性能指标比较（如果存在）
    db_metrics = ['query_rate_per_sec', 'active_connections', 'cache_hit_rate_percent', 
                 'avg_query_time_ms', 'transactions_per_sec']
    
    has_db_metrics = any(metric in df.columns for metric in db_metrics)
    if has_db_metrics:
        results.append("\n\n=== 数据库性能指标按服务器比较 ===")
        for metric in db_metrics:
            if metric in df.columns:
                results.append(f"\n{metric} 按服务器比较:")
                group_stats = server_groups[metric].agg(['mean', 'median', 'max']).round(2)
                for server, stats in group_stats.iterrows():
                    results.append(f"  {server}: 平均值={stats['mean']}, 中位数={stats['median']}, 最大值={stats['max']}")
    
    return "\n".join(results)

def find_anomalies(df):
    """查找异常值和模式"""
    results = []
    results.append("=== 异常值分析 ===")
    
    # 检查高CPU使用率事件
    if 'cpu_usage_percent' in df.columns:
        high_cpu = df[df['cpu_usage_percent'] > 90]
        if len(high_cpu) > 0:
            results.append(f"\n高CPU使用率事件 (>90%): {len(high_cpu)}次")
            by_server = high_cpu['server_name'].value_counts()
            for server, count in by_server.items():
                results.append(f"  {server}: {count}次")
    
    # 检查高内存使用率事件
    if 'memory_usage_percent' in df.columns:
        high_mem = df[df['memory_usage_percent'] > 90]
        if len(high_mem) > 0:
            results.append(f"\n高内存使用率事件 (>90%): {len(high_mem)}次")
            by_server = high_mem['server_name'].value_counts()
            for server, count in by_server.items():
                results.append(f"  {server}: {count}次")
    
    # 检查非正常事件
    if 'event_type' in df.columns:
        abnormal_events = df[df['event_type'] != 'normal']
        if len(abnormal_events) > 0:
            results.append(f"\n非正常事件: {len(abnormal_events)}次")
            by_type = abnormal_events['event_type'].value_counts()
            for event_type, count in by_type.items():
                results.append(f"  {event_type}: {count}次")
            
            # 按服务器统计非正常事件
            by_server = abnormal_events['server_name'].value_counts()
            results.append("\n非正常事件按服务器统计:")
            for server, count in by_server.items():
                results.append(f"  {server}: {count}次")
    
    # 检查死锁事件
    if 'deadlock_count' in df.columns:
        deadlocks = df[df['deadlock_count'] > 0]
        if len(deadlocks) > 0:
            results.append(f"\n死锁事件: {len(deadlocks)}次")
            by_server = deadlocks.groupby('server_name')['deadlock_count'].sum()
            for server, count in by_server.items():
                results.append(f"  {server}: {int(count)}次")
    
    return "\n".join(results)

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
    # 文件路径
    file_path = "temp_csv/excel_data_20250317143557.csv"
    output_path = "pngs/group_comparison_results.txt"
    
    # 加载数据
    df = load_csv_data(file_path)
    if df is None:
        return
    
    # 生成报告
    report = []
    report.append("=" * 80)
    report.append(f"服务器性能数据分析报告")
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"数据文件: {file_path}")
    report.append(f"数据行数: {len(df)}")
    report.append("=" * 80)
    
    # 添加各部分分析结果
    report.append("\n\n" + analyze_column_distributions(df))
    report.append("\n\n" + group_comparison(df))
    report.append("\n\n" + find_anomalies(df))
    
    # 保存结果
    save_results("\n".join(report), output_path)

if __name__ == "__main__":
    main()