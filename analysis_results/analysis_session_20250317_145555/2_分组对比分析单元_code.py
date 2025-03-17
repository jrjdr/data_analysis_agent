#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
import numpy as np
from datetime import datetime

def load_data(file_path):
    """加载CSV文件并处理可能的错误"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共 {len(df)} 行，{len(df.columns)} 列")
        return df
    except FileNotFoundError:
        print(f"错误: 未找到文件 '{file_path}'")
        return None
    except Exception as e:
        print(f"加载数据时出错: {str(e)}")
        return None

def analyze_column_distributions(df):
    """分析数据列的分布情况"""
    results = []
    results.append("=== 数据列分布分析 ===\n")
    
    # 区分数值列和分类列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # 分析分类列
    results.append("== 分类列分析 ==\n")
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        unique_count = len(value_counts)
        top_values = value_counts.head(3)
        
        results.append(f"列: {col}")
        results.append(f"  唯一值数量: {unique_count}")
        results.append(f"  最常见值: ")
        for value, count in top_values.items():
            results.append(f"    - {value}: {count} ({count/len(df)*100:.2f}%)")
        results.append("")
    
    # 分析数值列
    results.append("== 数值列分析 ==\n")
    for col in numeric_cols:
        # 跳过缺失值太多的列
        if df[col].isna().sum() > len(df) / 2:
            results.append(f"列: {col} (大部分为空，跳过分析)")
            continue
            
        results.append(f"列: {col}")
        results.append(f"  缺失值: {df[col].isna().sum()} ({df[col].isna().sum()/len(df)*100:.2f}%)")
        results.append(f"  最小值: {df[col].min():.2f}")
        results.append(f"  最大值: {df[col].max():.2f}")
        results.append(f"  平均值: {df[col].mean():.2f}")
        results.append(f"  中位数: {df[col].median():.2f}")
        results.append(f"  标准差: {df[col].std():.2f}")
        
        # 计算分位数
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        results.append(f"  25% 分位数: {q1:.2f}")
        results.append(f"  75% 分位数: {q3:.2f}")
        results.append("")
    
    return "\n".join(results)

def group_comparison_analysis(df):
    """对数据进行分组统计和对比分析"""
    results = []
    results.append("=== 分组对比分析 ===\n")
    
    # 按服务器类型分组分析
    results.append("== 按资源类型 (resource_type) 分组 ==\n")
    if 'resource_type' in df.columns:
        group_stats = df.groupby('resource_type').agg({
            col: ['mean', 'median', 'std'] for col in df.select_dtypes(include=['number']).columns
            if df[col].notna().sum() > len(df) / 2  # 只分析有足够非空值的列
        })
        
        # 使用flatten的多级索引便于输出
        group_stats.columns = [f"{col}_{stat}" for col, stat in group_stats.columns]
        
        for group in group_stats.index:
            results.append(f"资源类型: {group}")
            for col in group_stats.columns:
                orig_col, stat = col.rsplit('_', 1)
                results.append(f"  {orig_col} ({stat}): {group_stats.loc[group, col]:.2f}")
            results.append("")
    
    # 按服务器名称分组分析
    results.append("== 按服务器名称 (server_name) 分组 ==\n")
    if 'server_name' in df.columns:
        # 选择几个关键指标进行服务器间对比
        key_metrics = [
            'cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent',
            'network_traffic_percent', 'query_rate_per_sec', 'avg_query_time_ms'
        ]
        
        # 仅选择存在的指标
        key_metrics = [col for col in key_metrics if col in df.columns]
        
        if key_metrics:
            server_stats = df.groupby('server_name')[key_metrics].agg(['mean', 'max'])
            server_stats.columns = [f"{col}_{stat}" for col, stat in server_stats.columns]
            
            for server in server_stats.index:
                results.append(f"服务器: {server}")
                for col in server_stats.columns:
                    orig_col, stat = col.rsplit('_', 1)
                    results.append(f"  {orig_col} ({stat}): {server_stats.loc[server, col]:.2f}")
                results.append("")
    
    # 按事件类型分组分析
    results.append("== 按事件类型 (event_type) 分组 ==\n")
    if 'event_type' in df.columns:
        event_counts = df['event_type'].value_counts()
        results.append(f"事件类型分布:")
        for event, count in event_counts.items():
            results.append(f"  {event}: {count} ({count/len(df)*100:.2f}%)")
        results.append("")
        
        if len(event_counts) > 1:  # 如果有多个事件类型才进行比较
            # 选择关键指标进行比较
            event_metrics = [
                'cpu_usage_percent', 'memory_usage_percent', 'query_rate_per_sec', 
                'avg_query_time_ms', 'slow_queries_count'
            ]
            event_metrics = [col for col in event_metrics if col in df.columns]
            
            if event_metrics:
                event_stats = df.groupby('event_type')[event_metrics].agg(['mean'])
                event_stats.columns = [f"{col}_{stat}" for col, stat in event_stats.columns]
                
                for event in event_stats.index:
                    results.append(f"事件类型: {event}")
                    for col in event_stats.columns:
                        orig_col, stat = col.rsplit('_', 1)
                        results.append(f"  {orig_col} ({stat}): {event_stats.loc[event, col]:.2f}")
                    results.append("")
    
    # 时间模式分析 (按小时分组)
    results.append("== 按时间分组 (小时) ==\n")
    if 'timestamp' in df.columns:
        try:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            
            hourly_metrics = [
                'cpu_usage_percent', 'memory_usage_percent', 'query_rate_per_sec', 
                'active_connections', 'avg_query_time_ms'
            ]
            hourly_metrics = [col for col in hourly_metrics if col in df.columns]
            
            if hourly_metrics:
                hour_stats = df.groupby('hour')[hourly_metrics].agg(['mean'])
                hour_stats.columns = [f"{col}_{stat}" for col, stat in hour_stats.columns]
                
                busiest_hour = hour_stats['cpu_usage_percent_mean'].idxmax() if 'cpu_usage_percent_mean' in hour_stats.columns else None
                quietest_hour = hour_stats['cpu_usage_percent_mean'].idxmin() if 'cpu_usage_percent_mean' in hour_stats.columns else None
                
                results.append(f"时间模式分析:")
                if busiest_hour is not None:
                    results.append(f"  最繁忙时段: {busiest_hour}时")
                if quietest_hour is not None:
                    results.append(f"  最空闲时段: {quietest_hour}时")
                results.append("")
                
                # 只输出典型时段的详细数据
                typical_hours = [8, 12, 16, 20, 0, 4]
                typical_hours = [h for h in typical_hours if h in hour_stats.index]
                
                if typical_hours:
                    results.append("典型时段指标:")
                    for hour in typical_hours:
                        results.append(f"  时段: {hour}时")
                        for col in hour_stats.columns:
                            orig_col, stat = col.rsplit('_', 1)
                            results.append(f"    {orig_col} ({stat}): {hour_stats.loc[hour, col]:.2f}")
                        results.append("")
        
        except Exception as e:
            results.append(f"时间分析出错: {str(e)}")
    
    return "\n".join(results)

def find_anomalies(df):
    """查找异常值和模式"""
    results = []
    results.append("=== 异常检测分析 ===\n")
    
    # 选择关键指标进行异常值检测
    key_metrics = [
        'cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent',
        'query_rate_per_sec', 'avg_query_time_ms', 'slow_queries_count'
    ]
    key_metrics = [col for col in key_metrics if col in df.columns]
    
    for col in key_metrics:
        # 跳过大部分为空的列
        if df[col].isna().sum() > len(df) / 2:
            continue
            
        # 计算IQR和异常阈值
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # 计算异常值
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_count = len(outliers)
        
        results.append(f"指标: {col}")
        results.append(f"  异常值数量: {outlier_count} ({outlier_count/len(df)*100:.2f}%)")
        
        if outlier_count > 0:
            # 找出异常值的最大和最小值
            min_outlier = outliers[col].min()
            max_outlier = outliers[col].max()
            results.append(f"  异常值范围: {min_outlier:.2f} 至 {max_outlier:.2f}")
            
            # 如果存在事件类型，分析异常值与事件类型的关系
            if 'event_type' in df.columns:
                event_counts = outliers['event_type'].value_counts()
                results.append(f"  异常值事件类型分布:")
                for event, count in event_counts.items():
                    results.append(f"    - {event}: {count} ({count/outlier_count*100:.2f}%)")
        
        results.append("")
    
    # 检查是否存在异常的性能模式
    if 'event_type' in df.columns and df['event_type'].nunique() > 1:
        abnormal_events = df[df['event_type'] != 'normal']
        if len(abnormal_events) > 0:
            results.append("非正常事件分析:")
            event_types = abnormal_events['event_type'].unique()
            
            for event in event_types:
                event_data = abnormal_events[abnormal_events['event_type'] == event]
                results.append(f"  事件类型: {event}")
                results.append(f"  发生次数: {len(event_data)}")
                
                if 'server_name' in df.columns:
                    server_counts = event_data['server_name'].value_counts()
                    most_affected = server_counts.index[0] if len(server_counts) > 0 else "未知"
                    results.append(f"  最常受影响的服务器: {most_affected} ({server_counts.iloc[0]} 次)")
                
                results.append("")
    
    return "\n".join(results)

def main():
    file_path = "temp_csv/excel_data_20250317145554.csv"
    output_path = "pngs/group_comparison_results.txt"
    
    # 创建输出目录（如果不存在）
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 加载数据
    df = load_data(file_path)
    if df is None:
        print("数据加载失败，程序终止")
        return
    
    # 执行分析
    try:
        results = []
        results.append(f"=== 服务器数据分析报告 ===")
        results.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results.append(f"数据文件: {file_path}")
        results.append(f"记录数量: {len(df)}")
        results.append("\n")
        
        # 分析列分布
        results.append(analyze_column_distributions(df))
        
        # 分组对比分析
        results.append(group_comparison_analysis(df))
        
        # 异常检测
        results.append(find_anomalies(df))
        
        # 保存结果
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        
        print(f"分析完成! 结果已保存至 {output_path}")
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")

if __name__ == "__main__":
    main()