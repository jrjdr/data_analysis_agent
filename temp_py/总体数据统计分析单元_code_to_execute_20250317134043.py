#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from datetime import datetime
import traceback


def analyze_server_data(csv_path):
    """Analyze server performance data from CSV file and save results as text."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs('pngs', exist_ok=True)
        
        # Read CSV file
        print(f"Reading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Start building analysis results
        result = []
        result.append("=" * 80)
        result.append("服务器性能数据分析报告")
        result.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append(f"数据文件: {csv_path}")
        result.append("=" * 80)
        
        # Basic dataset info
        result.append("\n1. 基本数据信息")
        result.append("-" * 50)
        result.append(f"记录数量: {len(df)}")
        result.append(f"列数量: {len(df.columns)}")
        result.append(f"数据时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
        result.append(f"覆盖天数: {(df['timestamp'].max() - df['timestamp'].min()).days + 1}")
        
        # Server info
        result.append("\n2. 服务器信息")
        result.append("-" * 50)
        servers = df[['server_id', 'server_name']].drop_duplicates()
        result.append(f"服务器数量: {len(servers)}")
        result.append("\n服务器列表:")
        for _, row in servers.iterrows():
            result.append(f"  - {row['server_id']}: {row['server_name']}")
        
        # Resource types
        result.append("\n3. 资源类型分布")
        result.append("-" * 50)
        resource_counts = df['resource_type'].value_counts()
        for resource_type, count in resource_counts.items():
            result.append(f"  - {resource_type}: {count} 条记录 ({count/len(df)*100:.2f}%)")
        
        # Event types analysis
        result.append("\n4. 事件类型分析")
        result.append("-" * 50)
        event_counts = df['event_type'].value_counts()
        result.append("事件类型分布:")
        for event_type, count in event_counts.items():
            result.append(f"  - {event_type}: {count} 条记录 ({count/len(df)*100:.2f}%)")
        
        # Performance metrics analysis
        result.append("\n5. 性能指标统计分析")
        result.append("-" * 50)
        
        # Define key metrics categories
        system_metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                          'disk_io_percent', 'network_traffic_percent', 'temperature_celsius']
        
        io_metrics = ['disk_read_mbps', 'disk_write_mbps', 'network_in_mbps', 'network_out_mbps']
        
        db_metrics = ['query_rate_per_sec', 'active_connections', 'cache_hit_rate_percent', 
                      'avg_query_time_ms', 'transactions_per_sec', 'read_percent', 'write_percent',
                      'lock_wait_count', 'deadlock_count', 'buffer_pool_usage_percent',
                      'table_scans_per_sec', 'index_usage_percent', 'temp_tables_created_per_sec',
                      'slow_queries_count', 'aborted_connections']
        
        # Helper function for metric analysis
        def analyze_metrics(metrics_list, title):
            result.append(f"\n{title}:")
            result.append("-" * 40)
            
            for col in metrics_list:
                # Skip if all values are missing
                if df[col].isna().all():
                    continue
                    
                # Calculate statistics (handling missing values)
                data = df[col].dropna()
                if len(data) == 0:
                    continue
                    
                stats = {
                    '最小值': data.min(),
                    '最大值': data.max(),
                    '平均值': data.mean(),
                    '中位数': data.median(),
                    '标准差': data.std(),
                    '25%分位数': data.quantile(0.25),
                    '75%分位数': data.quantile(0.75),
                    '缺失值': df[col].isna().sum(),
                    '缺失率': df[col].isna().sum() / len(df) * 100
                }
                
                result.append(f"  {col}:")
                for stat_name, stat_value in stats.items():
                    # Format floating point values
                    if isinstance(stat_value, (float, np.float64)):
                        result.append(f"    {stat_name}: {stat_value:.2f}")
                    else:
                        result.append(f"    {stat_name}: {stat_value}")
        
        analyze_metrics(system_metrics, "系统资源指标")
        analyze_metrics(io_metrics, "IO指标")
        analyze_metrics(db_metrics, "数据库指标")
        
        # Critical events analysis
        result.append("\n6. 关键事件分析")
        result.append("-" * 50)
        
        critical_events = df[df['event_type'] != 'normal']
        if len(critical_events) > 0:
            result.append(f"发现 {len(critical_events)} 条非正常事件记录:")
            for event_type in critical_events['event_type'].unique():
                event_count = len(critical_events[critical_events['event_type'] == event_type])
                result.append(f"  - {event_type}: {event_count} 条记录")
            
            # Find critical events with high resource usage
            high_cpu_events = critical_events[critical_events['cpu_usage_percent'] > 90].shape[0]
            high_mem_events = critical_events[critical_events['memory_usage_percent'] > 90].shape[0]
            high_disk_events = critical_events[critical_events['disk_usage_percent'] > 85].shape[0]
            
            result.append("\n高资源占用的关键事件:")
            result.append(f"  - 高CPU使用率 (>90%): {high_cpu_events} 条记录")
            result.append(f"  - 高内存使用率 (>90%): {high_mem_events} 条记录")
            result.append(f"  - 高磁盘使用率 (>85%): {high_disk_events} 条记录")
        else:
            result.append("未发现关键事件。")
        
        # Database performance analysis
        result.append("\n7. 数据库性能分析")
        result.append("-" * 50)
        
        db_records = df[df['resource_type'] == 'database'].dropna(subset=['query_rate_per_sec'])
        if len(db_records) > 0:
            result.append(f"数据库记录数: {len(db_records)}")
            
            # Calculate average performance metrics
            avg_query_rate = db_records['query_rate_per_sec'].mean()
            avg_query_time = db_records['avg_query_time_ms'].mean()
            avg_transactions = db_records['transactions_per_sec'].mean()
            avg_slow_queries = db_records['slow_queries_count'].mean()
            
            result.append(f"平均查询率: {avg_query_rate:.2f} 每秒")
            result.append(f"平均查询时间: {avg_query_time:.2f} 毫秒")
            result.append(f"平均事务数: {avg_transactions:.2f} 每秒")
            result.append(f"平均慢查询数: {avg_slow_queries:.2f}")
            
            # Deadlock analysis
            total_deadlocks = db_records['deadlock_count'].sum()
            result.append(f"总死锁数: {total_deadlocks}")
            
            # Cache hit rate analysis
            avg_cache_hit = db_records['cache_hit_rate_percent'].mean()
            result.append(f"平均缓存命中率: {avg_cache_hit:.2f}%")
        else:
            result.append("未找到数据库性能记录。")
        
        # Write results to file
        output_path = "pngs/analysis_results.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))
        
        print(f"Analysis completed successfully. Results saved to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error analyzing server data: {str(e)}")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    csv_path = "temp_csv/excel_data_20250317133847.csv"
    analyze_server_data(csv_path)