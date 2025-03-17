#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成后端大数据库服务器的指标监控模拟数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 设置随机种子以确保可重复性
np.random.seed(42)

# 定义服务器和数据库信息
servers = {
    'SRV001': '主应用服务器',
    'SRV002': '备份应用服务器',
    'SRV003': '数据处理服务器',
    'SRV004': '缓存服务器',
    'SRV005': '负载均衡服务器'
}

databases = {
    'DB001': 'MySQL主数据库',
    'DB002': 'MySQL从数据库',
    'DB003': 'Redis缓存数据库',
    'DB004': 'MongoDB文档数据库',
    'DB005': 'Elasticsearch搜索数据库'
}

# 生成时间序列 - 2025年2月28日的每分钟数据
start_time = datetime(2025, 2, 28, 0, 0, 0)
end_time = datetime(2025, 2, 28, 23, 59, 0)
time_range = pd.date_range(start=start_time, end=end_time, freq='1min')

# 创建数据框
data = []

# 模拟一些事件
events = [
    {'time': datetime(2025, 2, 28, 3, 15, 0), 'duration': 45, 'type': 'high_load', 'affected': ['SRV001', 'DB001']},
    {'time': datetime(2025, 2, 28, 10, 30, 0), 'duration': 20, 'type': 'memory_leak', 'affected': ['SRV003']},
    {'time': datetime(2025, 2, 28, 14, 0, 0), 'duration': 30, 'type': 'db_slowdown', 'affected': ['DB002', 'DB004']},
    {'time': datetime(2025, 2, 28, 19, 45, 0), 'duration': 60, 'type': 'network_issue', 'affected': ['SRV005', 'SRV002']}
]

# 检查时间点是否在事件影响范围内
def is_in_event(t, server_id=None, db_id=None):
    for event in events:
        event_end = event['time'] + timedelta(minutes=event['duration'])
        if event['time'] <= t <= event_end:
            if server_id and server_id in event['affected']:
                return event['type']
            if db_id and db_id in event['affected']:
                return event['type']
    return None

for t in time_range:
    hour = t.hour
    
    # 模拟业务高峰期 (9-12点, 14-18点)
    is_peak_hour = (9 <= hour < 12) or (14 <= hour < 18)
    
    # 为每个服务器生成数据
    for srv_id, srv_name in servers.items():
        # 检查是否在事件影响范围内
        event_type = is_in_event(t, server_id=srv_id)
        
        # 根据时间段和事件调整基础负载
        if event_type == 'high_load':
            cpu_base = np.random.uniform(85, 98)
            memory_base = np.random.uniform(80, 95)
            disk_io_base = np.random.uniform(70, 90)
            network_base = np.random.uniform(80, 95)
        elif event_type == 'memory_leak':
            cpu_base = np.random.uniform(60, 80)
            memory_base = np.random.uniform(90, 99)
            disk_io_base = np.random.uniform(40, 60)
            network_base = np.random.uniform(30, 50)
        elif event_type == 'network_issue':
            cpu_base = np.random.uniform(40, 60)
            memory_base = np.random.uniform(50, 70)
            disk_io_base = np.random.uniform(30, 50)
            network_base = np.random.uniform(90, 99)
        elif is_peak_hour:
            cpu_base = np.random.uniform(50, 80)
            memory_base = np.random.uniform(60, 85)
            disk_io_base = np.random.uniform(40, 70)
            network_base = np.random.uniform(50, 80)
        else:
            cpu_base = np.random.uniform(10, 40)
            memory_base = np.random.uniform(30, 60)
            disk_io_base = np.random.uniform(5, 30)
            network_base = np.random.uniform(10, 40)
        
        # 添加随机波动
        cpu_usage = min(100, max(0, cpu_base + np.random.uniform(-5, 5)))
        memory_usage = min(100, max(0, memory_base + np.random.uniform(-3, 3)))
        disk_io = min(100, max(0, disk_io_base + np.random.uniform(-5, 5)))
        network_traffic = min(100, max(0, network_base + np.random.uniform(-5, 5)))
        
        # 计算其他指标
        load_avg_1min = cpu_usage / 25  # 模拟1分钟平均负载
        load_avg_5min = (cpu_usage / 25) * np.random.uniform(0.8, 1.2)  # 模拟5分钟平均负载
        load_avg_15min = (cpu_usage / 25) * np.random.uniform(0.7, 1.3)  # 模拟15分钟平均负载
        
        # 计算磁盘使用情况
        disk_usage = min(95, max(50, memory_usage * 0.8 + np.random.uniform(-10, 10)))
        disk_read_mbps = disk_io * np.random.uniform(0.5, 2.0)
        disk_write_mbps = disk_io * np.random.uniform(0.3, 1.5)
        
        # 计算网络流量
        network_in_mbps = network_traffic * np.random.uniform(0.5, 3.0)
        network_out_mbps = network_traffic * np.random.uniform(0.3, 2.0)
        
        # 计算进程数和线程数
        process_count = int(100 + cpu_usage * 2 + np.random.uniform(-10, 10))
        thread_count = int(process_count * np.random.uniform(3, 8))
        
        # 添加服务器数据行
        data.append({
            'timestamp': t,
            'server_id': srv_id,
            'server_name': srv_name,
            'resource_type': 'server',
            'cpu_usage_percent': cpu_usage,
            'memory_usage_percent': memory_usage,
            'disk_usage_percent': disk_usage,
            'disk_io_percent': disk_io,
            'disk_read_mbps': disk_read_mbps,
            'disk_write_mbps': disk_write_mbps,
            'network_traffic_percent': network_traffic,
            'network_in_mbps': network_in_mbps,
            'network_out_mbps': network_out_mbps,
            'load_avg_1min': load_avg_1min,
            'load_avg_5min': load_avg_5min,
            'load_avg_15min': load_avg_15min,
            'process_count': process_count,
            'thread_count': thread_count,
            'open_file_count': int(thread_count * np.random.uniform(2, 5)),
            'temperature_celsius': np.random.uniform(35, 65),
            'event_type': event_type if event_type else 'normal'
        })
    
    # 为每个数据库生成数据
    for db_id, db_name in databases.items():
        # 检查是否在事件影响范围内
        event_type = is_in_event(t, db_id=db_id)
        
        # 根据时间段和事件调整基础负载
        if event_type == 'high_load':
            query_rate_base = np.random.uniform(800, 1200)
            active_connections_base = np.random.uniform(80, 150)
            cache_hit_rate_base = np.random.uniform(50, 70)
        elif event_type == 'db_slowdown':
            query_rate_base = np.random.uniform(200, 400)
            active_connections_base = np.random.uniform(100, 200)
            cache_hit_rate_base = np.random.uniform(30, 50)
        elif is_peak_hour:
            query_rate_base = np.random.uniform(500, 900)
            active_connections_base = np.random.uniform(50, 100)
            cache_hit_rate_base = np.random.uniform(70, 90)
        else:
            query_rate_base = np.random.uniform(100, 300)
            active_connections_base = np.random.uniform(10, 40)
            cache_hit_rate_base = np.random.uniform(80, 95)
        
        # 添加随机波动
        query_rate = max(0, query_rate_base + np.random.uniform(-50, 50))
        active_connections = max(1, active_connections_base + np.random.uniform(-5, 5))
        cache_hit_rate = min(100, max(0, cache_hit_rate_base + np.random.uniform(-5, 5)))
        
        # 计算其他指标
        avg_query_time_ms = 10 + (100 - cache_hit_rate) / 5 + np.random.uniform(-2, 10)
        if event_type == 'db_slowdown':
            avg_query_time_ms *= np.random.uniform(3, 8)
        
        # 计算事务数
        transactions_per_sec = query_rate / np.random.uniform(5, 15)
        
        # 计算读写比例
        read_write_ratio = np.random.uniform(2, 8)  # 读/写比例
        read_percent = (read_write_ratio / (1 + read_write_ratio)) * 100
        write_percent = 100 - read_percent
        
        # 计算锁等待和死锁
        lock_wait_count = int(active_connections * np.random.uniform(0, 0.2))
        deadlock_count = int(lock_wait_count * np.random.uniform(0, 0.1))
        
        # 添加数据库数据行
        data.append({
            'timestamp': t,
            'server_id': db_id,
            'server_name': db_name,
            'resource_type': 'database',
            'query_rate_per_sec': query_rate,
            'active_connections': active_connections,
            'cache_hit_rate_percent': cache_hit_rate,
            'avg_query_time_ms': avg_query_time_ms,
            'transactions_per_sec': transactions_per_sec,
            'read_percent': read_percent,
            'write_percent': write_percent,
            'lock_wait_count': lock_wait_count,
            'deadlock_count': deadlock_count,
            'buffer_pool_usage_percent': np.random.uniform(50, 95),
            'table_scans_per_sec': np.random.uniform(0, 50),
            'index_usage_percent': np.random.uniform(60, 99),
            'temp_tables_created_per_sec': np.random.uniform(0, 20),
            'slow_queries_count': int(query_rate * np.random.uniform(0, 0.05)),
            'aborted_connections': int(active_connections * np.random.uniform(0, 0.03)),
            'event_type': event_type if event_type else 'normal'
        })

# 创建DataFrame
df = pd.DataFrame(data)

# 保存为Excel文件
output_file = 'sample_data/server_monitoring_data_2025_02_28.xlsx'
df.to_excel(output_file, index=False)

print(f"已生成服务器监控数据并保存到 {output_file}")
print(f"数据记录总数: {len(df)}")
