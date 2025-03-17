import pandas as pd
import numpy as np
from datetime import datetime
import os
from scipy import stats
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

def load_csv_data(file_path):
    """加载CSV文件数据"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共 {len(df)} 行")
        return df
    except Exception as e:
        print(f"加载CSV文件时出错: {e}")
        return None

def preprocess_data(df):
    """预处理数据，转换时间格式"""
    try:
        # 转换时间戳列为日期时间格式
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 添加额外的时间特征
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day
        df['weekday'] = df['timestamp'].dt.weekday
        
        print("数据预处理完成")
        return df
    except Exception as e:
        print(f"预处理数据时出错: {e}")
        return None

def analyze_time_trends(df):
    """分析时间趋势"""
    results = []
    
    # 获取数值型列
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # 排除我们添加的时间特征列
    exclude_cols = ['hour', 'day', 'weekday']
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    results.append("=== 时间趋势分析 ===\n")
    
    # 1. 按小时聚合数据，分析每小时的趋势
    hourly_stats = df.groupby('hour')[numeric_cols].mean()
    
    # 找出每个指标的高峰时段和低谷时段
    for col in numeric_cols:
        if col in df.columns and not df[col].isna().all():
            max_hour = hourly_stats[col].idxmax()
            min_hour = hourly_stats[col].idxmin()
            results.append(f"{col} 指标:")
            results.append(f"  - 高峰时段: {max_hour}时 (平均值: {hourly_stats[col].max():.2f})")
            results.append(f"  - 低谷时段: {min_hour}时 (平均值: {hourly_stats[col].min():.2f})")
            results.append("")
    
    # 2. 分析每个服务器的性能指标
    results.append("\n=== 服务器性能分析 ===\n")
    server_stats = df.groupby('server_name')[numeric_cols].agg(['mean', 'max', 'min', 'std'])
    
    for server in df['server_name'].unique():
        results.append(f"服务器: {server}")
        for col in ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 'network_traffic_percent']:
            if col in server_stats.columns and not pd.isna(server_stats.loc[server, (col, 'mean')]):
                mean_val = server_stats.loc[server, (col, 'mean')]
                max_val = server_stats.loc[server, (col, 'max')]
                results.append(f"  - {col}: 平均 {mean_val:.2f}%, 最大 {max_val:.2f}%")
        results.append("")
    
    # 3. 检测异常值
    results.append("\n=== 异常值检测 ===\n")
    
    for col in ['cpu_usage_percent', 'memory_usage_percent', 'disk_io_percent', 'network_traffic_percent']:
        if col in df.columns and not df[col].isna().all():
            # 使用Z分数检测异常值
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers = df[z_scores > 3]  # 3个标准差以外的值视为异常
            
            if len(outliers) > 0:
                results.append(f"{col} 异常值:")
                results.append(f"  - 检测到 {len(outliers)} 个异常点")
                
                # 获取异常发生的时间段
                if len(outliers) > 0:
                    outlier_times = df.loc[outliers.index, 'timestamp']
                    outlier_servers = df.loc[outliers.index, 'server_name']
                    
                    # 只显示前5个异常
                    for i in range(min(5, len(outlier_times))):
                        results.append(f"  - 时间: {outlier_times.iloc[i]}, 服务器: {outlier_servers.iloc[i]}, 值: {outliers[col].iloc[i]:.2f}")
                results.append("")
    
    # 4. 分析事件类型分布
    results.append("\n=== 事件类型分析 ===\n")
    event_counts = df['event_type'].value_counts()
    total_events = len(df)
    
    for event, count in event_counts.items():
        percentage = (count / total_events) * 100
        results.append(f"{event}: {count} 次 ({percentage:.2f}%)")
    
    # 5. 分析数据库性能指标
    results.append("\n=== 数据库性能指标 ===\n")
    
    db_metrics = ['query_rate_per_sec', 'active_connections', 'cache_hit_rate_percent', 
                 'avg_query_time_ms', 'transactions_per_sec', 'slow_queries_count']
    
    for metric in db_metrics:
        if metric in df.columns and not df[metric].isna().all():
            mean_val = df[metric].mean()
            max_val = df[metric].max()
            min_val = df[metric].min()
            results.append(f"{metric}:")
            results.append(f"  - 平均值: {mean_val:.2f}")
            results.append(f"  - 最大值: {max_val:.2f}")
            results.append(f"  - 最小值: {min_val:.2f}")
            
            # 分析趋势
            if len(df) > 1:
                # 按时间排序
                time_series = df.sort_values('timestamp')
                first_val = time_series[metric].iloc[0]
                last_val = time_series[metric].iloc[-1]
                change = ((last_val - first_val) / first_val) * 100 if first_val != 0 else 0
                
                if abs(change) > 10:  # 变化超过10%才报告
                    trend = "上升" if change > 0 else "下降"
                    results.append(f"  - 趋势: 在监测期间{trend}了 {abs(change):.2f}%")
            
            results.append("")
    
    return "\n".join(results)

def save_results(results, output_path):
    """保存分析结果到文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(results)
        
        print(f"分析结果已保存到 {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    """主函数"""
    file_path = "temp_csv/excel_data_20250317142408.csv"
    output_path = "pngs/time_trend_results.txt"
    
    # 1. 加载数据
    df = load_csv_data(file_path)
    if df is None:
        return
    
    # 2. 预处理数据
    df = preprocess_data(df)
    if df is None:
        return
    
    # 3. 分析时间趋势
    results = analyze_time_trends(df)
    
    # 4. 保存结果
    save_results(results, output_path)

if __name__ == "__main__":
    main()