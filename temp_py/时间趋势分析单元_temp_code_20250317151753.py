import pandas as pd
import numpy as np
import os
from datetime import datetime
from scipy import stats

def load_csv_data(file_path):
    """加载CSV文件并处理时间列"""
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查是否存在timestamp列
        if 'timestamp' not in df.columns:
            raise ValueError("CSV文件中缺少timestamp列")
        
        # 将timestamp列转换为datetime格式
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"成功加载数据: {len(df)}行, {len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载CSV文件时出错: {str(e)}")
        raise

def analyze_time_trends(df):
    """分析时间序列数据的趋势和模式"""
    results = []
    
    # 基本信息
    results.append("=== 数据基本信息 ===")
    results.append(f"数据时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
    results.append(f"数据点数量: {len(df)}")
    results.append(f"服务器数量: {df['server_id'].nunique()}")
    results.append(f"资源类型: {', '.join(df['resource_type'].unique())}")
    results.append("")
    
    # 按小时聚合数据以分析趋势
    df['hour'] = df['timestamp'].dt.hour
    hourly_stats = df.groupby('hour').agg({
        'cpu_usage_percent': ['mean', 'max'],
        'memory_usage_percent': ['mean', 'max'],
        'disk_usage_percent': ['mean', 'max'],
        'network_traffic_percent': ['mean', 'max'],
        'temperature_celsius': ['mean', 'max'],
        'query_rate_per_sec': ['mean', 'max'],
        'active_connections': ['mean', 'max']
    })
    
    # 分析每日高峰时段
    results.append("=== 每日高峰时段分析 ===")
    peak_hour_cpu = hourly_stats[('cpu_usage_percent', 'mean')].idxmax()
    peak_hour_memory = hourly_stats[('memory_usage_percent', 'mean')].idxmax()
    peak_hour_network = hourly_stats[('network_traffic_percent', 'mean')].idxmax()
    peak_hour_queries = hourly_stats[('query_rate_per_sec', 'mean')].idxmax()
    
    results.append(f"CPU使用率高峰时段: {peak_hour_cpu}:00 (平均: {hourly_stats[('cpu_usage_percent', 'mean')][peak_hour_cpu]:.2f}%)")
    results.append(f"内存使用率高峰时段: {peak_hour_memory}:00 (平均: {hourly_stats[('memory_usage_percent', 'mean')][peak_hour_memory]:.2f}%)")
    results.append(f"网络流量高峰时段: {peak_hour_network}:00 (平均: {hourly_stats[('network_traffic_percent', 'mean')][peak_hour_network]:.2f}%)")
    results.append(f"查询率高峰时段: {peak_hour_queries}:00 (平均: {hourly_stats[('query_rate_per_sec', 'mean')][peak_hour_queries]:.2f}次/秒)")
    results.append("")
    
    # 按天聚合数据以分析日趋势
    df['date'] = df['timestamp'].dt.date
    daily_stats = df.groupby('date').agg({
        'cpu_usage_percent': ['mean', 'max'],
        'memory_usage_percent': ['mean', 'max'],
        'disk_usage_percent': ['mean', 'max'],
        'network_traffic_percent': ['mean', 'max'],
        'query_rate_per_sec': ['mean', 'max'],
        'slow_queries_count': 'sum',
        'deadlock_count': 'sum'
    })
    
    # 分析日趋势
    results.append("=== 日趋势分析 ===")
    
    # 计算趋势斜率
    days = np.arange(len(daily_stats))
    cpu_trend = stats.linregress(days, daily_stats[('cpu_usage_percent', 'mean')])
    memory_trend = stats.linregress(days, daily_stats[('memory_usage_percent', 'mean')])
    disk_trend = stats.linregress(days, daily_stats[('disk_usage_percent', 'mean')])
    
    results.append(f"CPU使用率趋势: {'上升' if cpu_trend.slope > 0 else '下降'} (斜率: {cpu_trend.slope:.4f}/天)")
    results.append(f"内存使用率趋势: {'上升' if memory_trend.slope > 0 else '下降'} (斜率: {memory_trend.slope:.4f}/天)")
    results.append(f"磁盘使用率趋势: {'上升' if disk_trend.slope > 0 else '下降'} (斜率: {disk_trend.slope:.4f}/天)")
    results.append("")
    
    # 分析异常事件
    results.append("=== 异常事件分析 ===")
    event_counts = df['event_type'].value_counts()
    for event, count in event_counts.items():
        if event != 'normal':
            results.append(f"{event}事件: {count}次")
    
    # 查找CPU使用率异常高的时间点
    high_cpu = df[df['cpu_usage_percent'] > 90]
    if not high_cpu.empty:
        results.append(f"\n高CPU使用率事件 (>90%): {len(high_cpu)}次")
        for _, row in high_cpu.head(5).iterrows():
            results.append(f"  - {row['timestamp']}: {row['server_name']} ({row['cpu_usage_percent']:.2f}%)")
        if len(high_cpu) > 5:
            results.append(f"  - ... 以及其他 {len(high_cpu) - 5} 次事件")
    
    # 查找内存使用率异常高的时间点
    high_memory = df[df['memory_usage_percent'] > 90]
    if not high_memory.empty:
        results.append(f"\n高内存使用率事件 (>90%): {len(high_memory)}次")
        for _, row in high_memory.head(5).iterrows():
            results.append(f"  - {row['timestamp']}: {row['server_name']} ({row['memory_usage_percent']:.2f}%)")
        if len(high_memory) > 5:
            results.append(f"  - ... 以及其他 {len(high_memory) - 5} 次事件")
    
    # 查找死锁事件
    deadlocks = df[df['deadlock_count'] > 0]
    if not deadlocks.empty:
        results.append(f"\n死锁事件: {len(deadlocks)}次")
        for _, row in deadlocks.head(5).iterrows():
            results.append(f"  - {row['timestamp']}: {row['server_name']} ({int(row['deadlock_count'])}次)")
        if len(deadlocks) > 5:
            results.append(f"  - ... 以及其他 {len(deadlocks) - 5} 次事件")
    
    # 按服务器分析性能
    results.append("\n=== 服务器性能比较 ===")
    server_stats = df.groupby('server_name').agg({
        'cpu_usage_percent': 'mean',
        'memory_usage_percent': 'mean',
        'disk_usage_percent': 'mean',
        'network_traffic_percent': 'mean',
        'query_rate_per_sec': 'mean',
        'slow_queries_count': 'sum'
    }).sort_values('cpu_usage_percent', ascending=False)
    
    for server, row in server_stats.iterrows():
        results.append(f"{server}:")
        results.append(f"  - 平均CPU使用率: {row['cpu_usage_percent']:.2f}%")
        results.append(f"  - 平均内存使用率: {row['memory_usage_percent']:.2f}%")
        results.append(f"  - 平均磁盘使用率: {row['disk_usage_percent']:.2f}%")
        results.append(f"  - 平均网络流量: {row['network_traffic_percent']:.2f}%")
        results.append(f"  - 平均查询率: {row['query_rate_per_sec']:.2f}次/秒")
        results.append(f"  - 慢查询总数: {row['slow_queries_count']:.0f}")
    
    return results

def save_results(results, output_path):
    """将分析结果保存为纯文本文件"""
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("时间趋势分析结果\n")
            f.write("=" * 50 + "\n\n")
            f.write("生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            f.write("\n".join(results))
        
        print(f"分析结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存结果时出错: {str(e)}")

def main():
    try:
        file_path = "temp_csv/excel_data_20250317151146.csv"
        output_path = "pngs/time_trend_results.txt"
        
        # 加载数据
        df = load_csv_data(file_path)
        
        # 分析时间趋势
        results = analyze_time_trends(df)
        
        # 保存结果
        save_results(results, output_path)
        
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")

if __name__ == "__main__":
    main()