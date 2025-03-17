#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成5G小区基站通话信令模拟数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 设置随机种子以确保可重复性
np.random.seed(42)

# 定义基站ID和名称
base_stations = {
    'BS001': '城东-商业区基站',
    'BS002': '城西-住宅区基站',
    'BS003': '城北-工业园区基站',
    'BS004': '城南-大学城基站',
    'BS005': '市中心-商业区基站'
}

# 定义可能的信令类型
signal_types = [
    'ATTACH_REQUEST', 'ATTACH_ACCEPT', 'ATTACH_COMPLETE',
    'DETACH_REQUEST', 'DETACH_ACCEPT',
    'SERVICE_REQUEST', 'SERVICE_ACCEPT',
    'HANDOVER_REQUEST', 'HANDOVER_COMMAND', 'HANDOVER_COMPLETE',
    'PAGING', 'RRC_CONNECTION_REQUEST', 'RRC_CONNECTION_SETUP',
    'RRC_CONNECTION_SETUP_COMPLETE', 'RRC_CONNECTION_RELEASE'
]

# 定义可能的信令状态
signal_status = ['SUCCESS', 'FAILED', 'TIMEOUT', 'REJECTED', 'PENDING']

# 生成时间序列 - 2025年3月1日的每分钟数据
start_time = datetime(2025, 3, 1, 0, 0, 0)
end_time = datetime(2025, 3, 1, 23, 59, 0)
time_range = pd.date_range(start=start_time, end=end_time, freq='1min')

# 创建数据框
data = []

for t in time_range:
    hour = t.hour
    
    # 模拟业务高峰期 (8-10点, 12-14点, 18-22点)
    is_peak_hour = (8 <= hour < 10) or (12 <= hour < 14) or (18 <= hour < 22)
    
    # 为每个基站生成数据
    for bs_id, bs_name in base_stations.items():
        # 根据时间段调整基础负载
        if is_peak_hour:
            base_load = np.random.randint(80, 100)  # 高峰期基础负载
            call_attempts = np.random.randint(50, 100)  # 高峰期呼叫尝试次数
            active_users = np.random.randint(200, 500)  # 高峰期活跃用户数
        else:
            base_load = np.random.randint(20, 60)  # 非高峰期基础负载
            call_attempts = np.random.randint(10, 40)  # 非高峰期呼叫尝试次数
            active_users = np.random.randint(50, 200)  # 非高峰期活跃用户数
        
        # 随机选择信令类型和状态
        signal_type = np.random.choice(signal_types)
        status = np.random.choice(signal_status, p=[0.85, 0.05, 0.04, 0.03, 0.03])  # 85%成功率
        
        # 计算成功率和失败率
        success_rate = np.random.uniform(0.8, 0.99) if status == 'SUCCESS' else np.random.uniform(0.5, 0.8)
        failure_rate = 1 - success_rate
        
        # 计算信号强度 (dBm) 和质量 (dB)
        signal_strength = np.random.uniform(-120, -70)  # dBm
        signal_quality = np.random.uniform(0, 30)  # dB
        
        # 计算吞吐量 (Mbps)
        downlink_throughput = np.random.uniform(50, 1000) if is_peak_hour else np.random.uniform(100, 1500)
        uplink_throughput = np.random.uniform(10, 100) if is_peak_hour else np.random.uniform(20, 200)
        
        # 计算延迟 (ms)
        latency = np.random.uniform(10, 50) if is_peak_hour else np.random.uniform(5, 30)
        
        # 计算资源块使用率
        resource_block_usage = base_load / 100.0
        
        # 添加随机波动
        jitter = np.random.uniform(-5, 5)
        packet_loss = np.random.uniform(0, 0.05)  # 0-5%的丢包率
        
        # 添加数据行
        data.append({
            'timestamp': t,
            'base_station_id': bs_id,
            'base_station_name': bs_name,
            'signal_type': signal_type,
            'status': status,
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'call_attempts': call_attempts,
            'active_users': active_users,
            'signal_strength_dbm': signal_strength,
            'signal_quality_db': signal_quality,
            'downlink_throughput_mbps': downlink_throughput,
            'uplink_throughput_mbps': uplink_throughput,
            'latency_ms': latency,
            'jitter_ms': jitter,
            'packet_loss_percent': packet_loss * 100,
            'resource_block_usage_percent': resource_block_usage * 100,
            'cpu_usage_percent': base_load + np.random.uniform(-10, 10),
            'memory_usage_percent': base_load + np.random.uniform(-15, 15),
            'temperature_celsius': np.random.uniform(25, 45)
        })

# 创建DataFrame
df = pd.DataFrame(data)

# 保存为Excel文件
output_file = 'sample_data/5g_station_data_2025_03_01.xlsx'
df.to_excel(output_file, index=False)

print(f"已生成5G基站数据并保存到 {output_file}")
print(f"数据记录总数: {len(df)}")
