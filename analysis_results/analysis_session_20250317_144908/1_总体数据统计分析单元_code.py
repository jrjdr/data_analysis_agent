#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
from datetime import datetime

def read_csv_file(file_path):
    """读取CSV文件并处理基本错误"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取CSV文件，包含{df.shape[0]}行和{df.shape[1]}列数据")
        return df
    except FileNotFoundError:
        print(f"错误: 文件'{file_path}'不存在")
        return None
    except pd.errors.EmptyDataError:
        print(f"错误: 文件'{file_path}'为空或格式不正确")
        return None
    except Exception as e:
        print(f"读取CSV文件时发生错误: {str(e)}")
        return None

def basic_statistics(df):
    """计算基本描述性统计"""
    result = []
    result.append("=== 基本数据统计 ===")
    result.append(f"数据行数: {df.shape[0]}")
    result.append(f"数据列数: {df.shape[1]}")
    result.append(f"时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
    
    # 计算数据完整性
    missing_data = df.isnull().sum()
    missing_pct = (missing_data / len(df)) * 100
    result.append("\n=== 数据完整性 ===")
    result.append("列名\t缺失值数量\t缺失百分比")
    result.append("-" * 40)
    for col, missing in missing_data.items():
        if missing > 0:
            result.append(f"{col}\t{missing}\t{missing_pct[col]:.2f}%")
    
    return result

def analyze_numerical_columns(df):
    """分析数值型列的分布"""
    result = []
    result.append("\n=== 数值型数据分析 ===")
    
    # 选择数值型列
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        # 跳过缺失值过多的列(超过50%)
        if df[col].isnull().sum() / len(df) > 0.5:
            continue
            
        result.append(f"\n--- {col} 分析 ---")
        data = df[col].dropna()
        
        # 基本统计量
        result.append(f"最小值: {data.min():.2f}")
        result.append(f"最大值: {data.max():.2f}")
        result.append(f"平均值: {data.mean():.2f}")
        result.append(f"中位数: {data.median():.2f}")
        result.append(f"标准差: {data.std():.2f}")
        
        # 分位数
        q1, q3 = data.quantile(0.25), data.quantile(0.75)
        result.append(f"25%分位数: {q1:.2f}")
        result.append(f"75%分位数: {q3:.2f}")
        result.append(f"IQR(四分位距): {(q3-q1):.2f}")
        
        # 异常值检测
        lower_bound = q1 - 1.5 * (q3 - q1)
        upper_bound = q3 + 1.5 * (q3 - q1)
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        result.append(f"潜在异常值数量: {len(outliers)}, 占比: {(len(outliers)/len(data)*100):.2f}%")
    
    return result

def analyze_categorical_columns(df):
    """分析分类型列的分布"""
    result = []
    result.append("\n=== 分类型数据分析 ===")
    
    # 选择对象类型列
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    for col in categorical_cols:
        result.append(f"\n--- {col} 分析 ---")
        value_counts = df[col].value_counts()
        unique_values = len(value_counts)
        result.append(f"唯一值数量: {unique_values}")
        
        # 显示前5个最常见的值
        result.append("\n最常见的值:")
        for val, count in value_counts.head(5).items():
            result.append(f"{val}: {count}次 ({count/len(df)*100:.2f}%)")
    
    return result

def analyze_server_metrics(df):
    """分析服务器特定指标"""
    result = []
    result.append("\n=== 服务器性能指标分析 ===")
    
    # 获取不同的服务器
    servers = df['server_name'].unique()
    
    # 资源使用率阈值
    cpu_threshold = 80
    memory_threshold = 90
    disk_threshold = 85
    
    for server in servers:
        server_data = df[df['server_name'] == server]
        result.append(f"\n--- 服务器: {server} 分析 ---")
        
        # CPU使用率分析
        if 'cpu_usage_percent' in df.columns and not server_data['cpu_usage_percent'].isnull().all():
            cpu_data = server_data['cpu_usage_percent'].dropna()
            high_cpu = cpu_data[cpu_data > cpu_threshold]
            result.append(f"CPU使用率 > {cpu_threshold}% 的时间点数量: {len(high_cpu)}, 占比: {len(high_cpu)/len(cpu_data)*100:.2f}%")
            if len(high_cpu) > 0:
                result.append(f"CPU使用率最高值: {cpu_data.max():.2f}%")
        
        # 内存使用率分析
        if 'memory_usage_percent' in df.columns and not server_data['memory_usage_percent'].isnull().all():
            mem_data = server_data['memory_usage_percent'].dropna()
            high_mem = mem_data[mem_data > memory_threshold]
            result.append(f"内存使用率 > {memory_threshold}% 的时间点数量: {len(high_mem)}, 占比: {len(high_mem)/len(mem_data)*100:.2f}%")
            if len(high_mem) > 0:
                result.append(f"内存使用率最高值: {mem_data.max():.2f}%")
        
        # 磁盘使用率分析
        if 'disk_usage_percent' in df.columns and not server_data['disk_usage_percent'].isnull().all():
            disk_data = server_data['disk_usage_percent'].dropna()
            high_disk = disk_data[disk_data > disk_threshold]
            result.append(f"磁盘使用率 > {disk_threshold}% 的时间点数量: {len(high_disk)}, 占比: {len(high_disk)/len(disk_data)*100:.2f}%")
            if len(high_disk) > 0:
                result.append(f"磁盘使用率最高值: {disk_data.max():.2f}%")
    
    # 分析事件类型
    if 'event_type' in df.columns:
        result.append("\n--- 事件分析 ---")
        event_counts = df['event_type'].value_counts()
        for event, count in event_counts.items():
            result.append(f"{event}: {count}次 ({count/len(df)*100:.2f}%)")
    
    # 分析数据库相关指标
    result.append("\n--- 数据库性能指标 ---")
    if 'slow_queries_count' in df.columns and not df['slow_queries_count'].isnull().all():
        slow_queries = df['slow_queries_count'].dropna()
        result.append(f"慢查询总数: {slow_queries.sum():.0f}")
        result.append(f"平均慢查询数: {slow_queries.mean():.2f}")
        result.append(f"最多慢查询数: {slow_queries.max():.0f}")
    
    if 'deadlock_count' in df.columns and not df['deadlock_count'].isnull().all():
        deadlocks = df['deadlock_count'].dropna()
        result.append(f"死锁总数: {deadlocks.sum():.0f}")
        if deadlocks.sum() > 0:
            result.append(f"平均死锁数: {deadlocks.mean():.4f}")
            result.append(f"最多死锁数: {deadlocks.max():.0f}")
    
    return result

def save_results(results, output_path):
    """保存分析结果到文本文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 添加文件头
    header = [
        "===================================================",
        "             服务器数据分析报告                      ",
        "===================================================",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # 合并所有结果
    all_results = header + results
    
    # 写入文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_results))
        print(f"分析结果已保存至: {output_path}")
        return True
    except Exception as e:
        print(f"保存分析结果时发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    file_path = "temp_csv/excel_data_20250317144907.csv"
    output_path = "pngs/analysis_results.txt"
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return
    
    # 转换时间戳列
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        print(f"转换时间戳时发生错误: {str(e)}")
    
    # 执行各种分析
    results = []
    results.extend(basic_statistics(df))
    results.extend(analyze_numerical_columns(df))
    results.extend(analyze_categorical_columns(df))
    results.extend(analyze_server_metrics(df))
    
    # 保存结果
    save_results(results, output_path)

if __name__ == "__main__":
    main()