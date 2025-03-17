import pandas as pd
import os
import numpy as np
from datetime import datetime

def read_data_safely(file_path):
    """安全读取CSV文件"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取文件 {file_path}，共 {len(df)} 行数据")
        return df
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None

def analyze_distribution(df):
    """分析数值列和分类列的分布"""
    results = []
    
    results.append("1. 数据分布分析\n" + "="*50)
    
    # 分析分类列
    cat_columns = ['base_station_id', 'base_station_name', 'signal_type', 'status']
    results.append("\n1.1 分类列分布\n" + "-"*50)
    
    for col in cat_columns:
        dist = df[col].value_counts().reset_index()
        dist.columns = [col, '计数']
        dist['百分比'] = (dist['计数'] / dist['计数'].sum() * 100).round(2)
        
        results.append(f"\n{col} 分布:")
        table_rows = []
        for _, row in dist.iterrows():
            table_rows.append(f"{row[col]:<20} {row['计数']:<6} {row['百分比']}%")
        results.append("\n".join(table_rows))
    
    # 分析数值列
    num_columns = ['success_rate', 'failure_rate', 'call_attempts', 'active_users', 
                  'signal_strength_dbm', 'signal_quality_db', 'downlink_throughput_mbps',
                  'uplink_throughput_mbps', 'latency_ms', 'jitter_ms', 'packet_loss_percent',
                  'resource_block_usage_percent', 'cpu_usage_percent', 'memory_usage_percent',
                  'temperature_celsius']
    
    results.append("\n\n1.2 数值列统计\n" + "-"*50)
    
    # 创建一个表格形式的输出
    headers = ["列名", "最小值", "最大值", "平均值", "中位数", "标准差"]
    results.append(f"{headers[0]:<30} {headers[1]:<10} {headers[2]:<10} {headers[3]:<10} {headers[4]:<10} {headers[5]:<10}")
    results.append("-"*80)
    
    for col in num_columns:
        min_val = df[col].min().round(2)
        max_val = df[col].max().round(2)
        mean_val = df[col].mean().round(2)
        median_val = df[col].median().round(2)
        std_val = df[col].std().round(2)
        
        results.append(f"{col:<30} {min_val:<10} {max_val:<10} {mean_val:<10} {median_val:<10} {std_val:<10}")
    
    return "\n".join(results)

def group_analysis(df):
    """对数据进行分组统计，比较不同组之间的差异"""
    results = []
    
    results.append("\n\n2. 分组对比分析\n" + "="*50)
    
    # 2.1 按基站分组
    results.append("\n2.1 按基站分组分析\n" + "-"*50)
    station_group = df.groupby('base_station_name').agg({
        'success_rate': ['mean', 'min', 'max'],
        'active_users': ['mean', 'max'],
        'signal_strength_dbm': 'mean',
        'downlink_throughput_mbps': 'mean',
        'uplink_throughput_mbps': 'mean',
        'latency_ms': 'mean',
        'packet_loss_percent': 'mean',
        'cpu_usage_percent': 'mean',
        'temperature_celsius': 'mean'
    }).round(2)
    
    results.append(station_group.to_string())
    
    # 2.2 按信号类型分组
    results.append("\n\n2.2 按信号类型分组分析\n" + "-"*50)
    signal_group = df.groupby('signal_type').agg({
        'success_rate': ['mean', 'min', 'max'],
        'failure_rate': 'mean',
        'call_attempts': 'mean',
        'latency_ms': 'mean',
        'packet_loss_percent': 'mean'
    }).round(2)
    
    results.append(signal_group.to_string())
    
    # 2.3 按状态分组
    results.append("\n\n2.3 按状态分组分析\n" + "-"*50)
    status_group = df.groupby('status').agg({
        'call_attempts': 'mean',
        'signal_strength_dbm': 'mean',
        'downlink_throughput_mbps': 'mean',
        'latency_ms': 'mean',
        'resource_block_usage_percent': 'mean'
    }).round(2)
    
    results.append(status_group.to_string())
    
    # 2.4 按时间段分组（每小时）
    results.append("\n\n2.4 按时间段分组分析（每小时）\n" + "-"*50)
    # 转换时间戳列为日期时间格式
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    time_group = df.groupby('hour').agg({
        'success_rate': 'mean',
        'active_users': 'mean',
        'downlink_throughput_mbps': 'mean',
        'latency_ms': 'mean',
        'cpu_usage_percent': 'mean'
    }).round(2)
    
    results.append(time_group.to_string())
    
    return "\n".join(results)

def comparative_analysis(df):
    """执行比较性分析，寻找显著差异"""
    results = []
    
    results.append("\n\n3. 比较性分析\n" + "="*50)
    
    # 3.1 不同基站之间的成功率差异
    results.append("\n3.1 不同基站之间的关键性能指标对比\n" + "-"*50)
    
    # 计算各基站的关键指标并进行排名
    station_perf = df.groupby('base_station_name').agg({
        'success_rate': 'mean',
        'latency_ms': 'mean',
        'downlink_throughput_mbps': 'mean',
        'packet_loss_percent': 'mean'
    }).round(2)
    
    # 添加排名
    station_perf['成功率_排名'] = station_perf['success_rate'].rank(ascending=False).astype(int)
    station_perf['延迟_排名'] = station_perf['latency_ms'].rank().astype(int)  # 延迟越低越好
    station_perf['下行吞吐量_排名'] = station_perf['downlink_throughput_mbps'].rank(ascending=False).astype(int)
    station_perf['丢包率_排名'] = station_perf['packet_loss_percent'].rank().astype(int)  # 丢包率越低越好
    
    results.append(station_perf.to_string())
    
    # 3.2 高负载与低负载条件下的性能差异
    results.append("\n\n3.2 高负载与低负载条件下的性能差异\n" + "-"*50)
    
    # 基于活跃用户数定义高负载和低负载
    median_users = df['active_users'].median()
    high_load = df[df['active_users'] > median_users]
    low_load = df[df['active_users'] <= median_users]
    
    metrics = ['success_rate', 'latency_ms', 'downlink_throughput_mbps', 
               'uplink_throughput_mbps', 'packet_loss_percent']
    
    load_comparison = pd.DataFrame({
        '高负载_平均值': high_load[metrics].mean(),
        '低负载_平均值': low_load[metrics].mean(),
        '差异_百分比': ((high_load[metrics].mean() - low_load[metrics].mean()) / low_load[metrics].mean() * 100).round(2)
    })
    
    results.append(load_comparison.to_string())
    
    # 3.3 信号强度与性能关系
    results.append("\n\n3.3 信号强度与成功率关系\n" + "-"*50)
    
    # 将信号强度分成几个区间
    df['signal_strength_group'] = pd.cut(
        df['signal_strength_dbm'],
        bins=[-120, -110, -100, -90, -80, -70],
        labels=['极弱 (-120~-110)', '较弱 (-110~-100)', '中等 (-100~-90)', '较强 (-90~-80)', '强 (-80~-70)']
    )
    
    signal_perf = df.groupby('signal_strength_group').agg({
        'success_rate': 'mean',
        'downlink_throughput_mbps': 'mean',
        'latency_ms': 'mean',
        'packet_loss_percent': 'mean',
        'base_station_id': 'count'
    })
    
    signal_perf.rename(columns={'base_station_id': '样本数'}, inplace=True)
    signal_perf = signal_perf.round(2)
    
    results.append(signal_perf.to_string())
    
    return "\n".join(results)

def identify_anomalies(df):
    """识别异常值和异常模式"""
    results = []
    
    results.append("\n\n4. 异常检测与模式识别\n" + "="*50)
    
    # 4.1 识别异常高的延迟
    results.append("\n4.1 高延迟异常\n" + "-"*50)
    latency_threshold = df['latency_ms'].mean() + 2 * df['latency_ms'].std()
    high_latency = df[df['latency_ms'] > latency_threshold]
    
    results.append(f"高延迟阈值: {latency_threshold:.2f} ms")
    results.append(f"高延迟记录数: {len(high_latency)} ({len(high_latency)/len(df)*100:.2f}%)")
    
    if len(high_latency) > 0:
        # 按基站和信号类型统计高延迟记录
        high_latency_by_station = high_latency['base_station_name'].value_counts()
        high_latency_by_signal = high_latency['signal_type'].value_counts()
        
        results.append("\n按基站统计高延迟记录:")
        results.append(high_latency_by_station.to_string())
        
        results.append("\n按信号类型统计高延迟记录:")
        results.append(high_latency_by_signal.to_string())
    
    # 4.2 识别异常低的成功率
    results.append("\n\n4.2 低成功率异常\n" + "-"*50)
    success_threshold = df['success_rate'].mean() - 2 * df['success_rate'].std()
    low_success = df[df['success_rate'] < success_threshold]
    
    results.append(f"低成功率阈值: {success_threshold:.2f}")
    results.append(f"低成功率记录数: {len(low_success)} ({len(low_success)/len(df)*100:.2f}%)")
    
    if len(low_success) > 0:
        # 按基站和信号类型统计低成功率记录
        low_success_by_station = low_success['base_station_name'].value_counts()
        low_success_by_signal = low_success['signal_type'].value_counts()
        
        results.append("\n按基站统计低成功率记录:")
        results.append(low_success_by_station.to_string())
        
        results.append("\n按信号类型统计低成功率记录:")
        results.append(low_success_by_signal.to_string())
    
    return "\n".join(results)

def main():
    """主函数，执行所有分析并保存结果"""
    file_path = "temp_csv/excel_data_20250317152243.csv"
    output_path = "pngs/group_comparison_results.txt"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 读取数据
    df = read_data_safely(file_path)
    if df is None:
        return
    
    # 生成分析结果
    results = []
    
    # 添加标题和执行时间
    results.append("基站数据分析报告")
    results.append("=" * 50)
    results.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"数据文件: {file_path}")
    results.append(f"记录数: {len(df)}")
    
    # 执行各项分析
    results.append(analyze_distribution(df))
    results.append(group_analysis(df))
    results.append(comparative_analysis(df))
    results.append(identify_anomalies(df))
    
    # 添加结论
    results.append("\n\n5. 分析结论\n" + "="*50)
    results.append("\n这里是自动生成的结论，基于数据分析结果。具体结论将取决于实际数据内容。")
    
    # 保存结果
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(results))
        print(f"分析结果已保存至 {output_path}")
    except Exception as e:
        print(f"保存结果时发生错误: {str(e)}")

if __name__ == "__main__":
    main()