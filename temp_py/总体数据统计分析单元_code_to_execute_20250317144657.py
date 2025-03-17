#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_csv(file_path):
    """
    分析CSV文件并生成统计报告
    """
    try:
        # 读取CSV文件
        print(f"正在读取CSV文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 创建结果文本
        results = []
        
        # 基本文件信息
        results.append("=" * 80)
        results.append("服务器监控数据分析报告")
        results.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results.append("=" * 80)
        
        # 数据概览
        results.append("\n1. 数据概览")
        results.append("-" * 40)
        results.append(f"文件路径: {file_path}")
        results.append(f"总行数: {len(df)}")
        results.append(f"总列数: {len(df.columns)}")
        
        # 将timestamp列转换为datetime类型
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            results.append(f"数据时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
        
        # 服务器信息
        if 'server_id' in df.columns and 'server_name' in df.columns:
            results.append("\n2. 服务器信息")
            results.append("-" * 40)
            server_info = df[['server_id', 'server_name']].drop_duplicates()
            for _, row in server_info.iterrows():
                results.append(f"服务器ID: {row['server_id']}, 名称: {row['server_name']}")
        
        # 数据完整性检查
        results.append("\n3. 数据完整性检查")
        results.append("-" * 40)
        missing_data = df.isnull().sum()
        results.append("列缺失值统计:")
        for col, missing in missing_data.items():
            if missing > 0:
                results.append(f"  {col}: {missing}个缺失值 ({missing/len(df)*100:.2f}%)")
        
        # 分析数值列
        results.append("\n4. 数值列统计分析")
        results.append("-" * 40)
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                results.append(f"\n4.1 {col}:")
                results.append(f"  数据类型: {df[col].dtype}")
                results.append(f"  非空值数量: {len(col_data)}")
                results.append(f"  最小值: {col_data.min():.2f}")
                results.append(f"  最大值: {col_data.max():.2f}")
                results.append(f"  平均值: {col_data.mean():.2f}")
                results.append(f"  中位数: {col_data.median():.2f}")
                results.append(f"  标准差: {col_data.std():.2f}")
                
                # 计算主要百分位数
                percentiles = col_data.quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).to_dict()
                results.append("  百分位数:")
                for p, val in percentiles.items():
                    results.append(f"    {int(p*100)}%: {val:.2f}")
        
        # 分析分类列
        results.append("\n5. 分类列统计分析")
        results.append("-" * 40)
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if col != 'timestamp':  # 跳过时间戳列
                results.append(f"\n5.1 {col}:")
                value_counts = df[col].value_counts()
                results.append(f"  唯一值数量: {len(value_counts)}")
                results.append("  最常见值:")
                for val, count in value_counts.head(5).items():
                    results.append(f"    {val}: {count}次 ({count/len(df)*100:.2f}%)")
        
        # 分析事件类型
        if 'event_type' in df.columns:
            results.append("\n6. 事件类型分析")
            results.append("-" * 40)
            event_counts = df['event_type'].value_counts()
            for event, count in event_counts.items():
                results.append(f"  {event}: {count}次 ({count/len(df)*100:.2f}%)")
        
        # 数据库性能指标分析
        db_cols = ['query_rate_per_sec', 'active_connections', 'cache_hit_rate_percent', 
                   'avg_query_time_ms', 'transactions_per_sec', 'slow_queries_count']
        
        if all(col in df.columns for col in db_cols):
            results.append("\n7. 数据库性能指标分析")
            results.append("-" * 40)
            
            # 计算缓存命中率
            cache_hit = df['cache_hit_rate_percent'].dropna()
            if len(cache_hit) > 0:
                results.append(f"  缓存命中率: 平均值={cache_hit.mean():.2f}%, 最小值={cache_hit.min():.2f}%")
            
            # 计算慢查询信息
            slow_queries = df['slow_queries_count'].dropna()
            if len(slow_queries) > 0 and slow_queries.sum() > 0:
                results.append(f"  慢查询总数: {int(slow_queries.sum())}")
                results.append(f"  慢查询平均数: {slow_queries.mean():.2f}")
                results.append(f"  慢查询最大数: {slow_queries.max():.2f}")
            
            # 死锁信息
            if 'deadlock_count' in df.columns:
                deadlocks = df['deadlock_count'].dropna()
                if len(deadlocks) > 0 and deadlocks.sum() > 0:
                    results.append(f"  死锁总数: {int(deadlocks.sum())}")
                    results.append(f"  死锁发生率: {(deadlocks > 0).mean()*100:.2f}%")
        
        # 系统负载分析
        load_cols = ['load_avg_1min', 'load_avg_5min', 'load_avg_15min']
        if all(col in df.columns for col in load_cols):
            results.append("\n8. 系统负载分析")
            results.append("-" * 40)
            
            for col in load_cols:
                load_data = df[col].dropna()
                if len(load_data) > 0:
                    results.append(f"  {col}: 平均值={load_data.mean():.2f}, 最大值={load_data.max():.2f}")
                    results.append(f"    负载超过1的比例: {(load_data > 1).mean()*100:.2f}%")
                    results.append(f"    负载超过2的比例: {(load_data > 2).mean()*100:.2f}%")
                    results.append(f"    负载超过3的比例: {(load_data > 3).mean()*100:.2f}%")
        
        # 结论
        results.append("\n9. 主要发现")
        results.append("-" * 40)
        
        # CPU使用率分析
        if 'cpu_usage_percent' in df.columns:
            cpu_data = df['cpu_usage_percent'].dropna()
            if len(cpu_data) > 0:
                high_cpu = (cpu_data > 80).mean() * 100
                results.append(f"  CPU使用率超过80%的情况: {high_cpu:.2f}%")
        
        # 内存使用分析
        if 'memory_usage_percent' in df.columns:
            mem_data = df['memory_usage_percent'].dropna()
            if len(mem_data) > 0:
                high_mem = (mem_data > 80).mean() * 100
                results.append(f"  内存使用率超过80%的情况: {high_mem:.2f}%")
        
        # 磁盘使用分析
        if 'disk_usage_percent' in df.columns:
            disk_data = df['disk_usage_percent'].dropna()
            if len(disk_data) > 0:
                high_disk = (disk_data > 80).mean() * 100
                results.append(f"  磁盘使用率超过80%的情况: {high_disk:.2f}%")
        
        # 页脚
        results.append("\n" + "=" * 80)
        results.append("分析完成")
        results.append("=" * 80)
        
        return "\n".join(results)
    
    except Exception as e:
        return f"分析过程中发生错误: {str(e)}"

def save_analysis(content, output_path):
    """
    保存分析结果到指定路径
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {str(e)}")
        return False

def main():
    # 文件路径
    csv_file = "temp_csv/excel_data_20250317144534.csv"
    output_file = "pngs/analysis_results.txt"
    
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"错误: 文件 {csv_file} 不存在")
        return
    
    # 分析数据
    analysis_results = analyze_csv(csv_file)
    
    # 保存结果
    save_analysis(analysis_results, output_file)

if __name__ == "__main__":
    main()