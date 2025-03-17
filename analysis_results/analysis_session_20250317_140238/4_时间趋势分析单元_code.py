import pandas as pd
import numpy as np
from datetime import datetime
import os
from scipy import stats

def load_and_preprocess_data(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 将timestamp列转换为datetime格式
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 按时间戳排序
        df = df.sort_values('timestamp')
        
        return df
    except Exception as e:
        print(f"错误: 无法加载或预处理数据: {e}")
        return None

def analyze_time_series(df):
    results = []
    
    # 基本时间信息
    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()
    duration = end_time - start_time
    time_interval = (df['timestamp'].iloc[1] - df['timestamp'].iloc[0]).seconds / 60  # 时间间隔(分钟)
    
    results.append("===== 基本时间信息 =====")
    results.append(f"记录开始时间: {start_time}")
    results.append(f"记录结束时间: {end_time}")
    results.append(f"总监控时长: {duration}")
    results.append(f"采样频率: {time_interval}分钟")
    
    # 主要资源指标分析
    results.append("\n===== 资源使用趋势分析 =====")
    
    # 筛选服务器类型数据(resource_type为server的数据)
    server_df = df[df['resource_type'] == 'server']
    
    # 分析主要指标
    metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
               'network_traffic_percent', 'query_rate_per_sec', 'active_connections']
    
    for metric in metrics:
        if metric in server_df.columns:
            valid_data = server_df[metric].dropna()
            if len(valid_data) > 0:
                results.append(f"\n-- {metric} 趋势分析 --")
                
                # 计算平均值
                hourly_avg = server_df.set_index('timestamp').resample('H')[metric].mean()
                
                # 计算高峰时段
                peak_hour = hourly_avg.idxmax().hour if not hourly_avg.empty else "无数据"
                
                # 计算趋势
                if len(valid_data) > 2:
                    # 使用简单线性回归估计趋势
                    x = np.arange(len(valid_data))
                    slope, _, _, _, _ = stats.linregress(x, valid_data)
                    trend = "上升" if slope > 0.01 else "下降" if slope < -0.01 else "稳定"
                else:
                    trend = "数据不足"
                
                # 计算异常值
                if len(valid_data) > 10:
                    q1 = valid_data.quantile(0.25)
                    q3 = valid_data.quantile(0.75)
                    iqr = q3 - q1
                    upper_bound = q3 + 1.5 * iqr
                    outliers = valid_data[valid_data > upper_bound]
                    outlier_pct = (len(outliers) / len(valid_data)) * 100
                else:
                    outlier_pct = 0
                
                results.append(f"平均值: {valid_data.mean():.2f}")
                results.append(f"最大值: {valid_data.max():.2f}")
                results.append(f"最小值: {valid_data.min():.2f}")
                results.append(f"标准差: {valid_data.std():.2f}")
                results.append(f"高峰时段: {peak_hour}时")
                results.append(f"总体趋势: {trend}")
                results.append(f"异常值比例: {outlier_pct:.2f}%")
    
    # 事件分析
    results.append("\n===== 系统事件分析 =====")
    event_counts = df['event_type'].value_counts()
    for event, count in event_counts.items():
        results.append(f"{event}: {count}次 ({count/len(df)*100:.2f}%)")
    
    # 服务器负载分析
    results.append("\n===== 服务器负载分析 =====")
    for server_name in df['server_name'].unique():
        server_data = df[df['server_name'] == server_name]
        results.append(f"\n服务器: {server_name}")
        
        # 计算平均CPU和内存
        avg_cpu = server_data['cpu_usage_percent'].mean() if 'cpu_usage_percent' in server_data else "N/A"
        avg_mem = server_data['memory_usage_percent'].mean() if 'memory_usage_percent' in server_data else "N/A"
        
        if avg_cpu != "N/A":
            results.append(f"平均CPU使用率: {avg_cpu:.2f}%")
        if avg_mem != "N/A":
            results.append(f"平均内存使用率: {avg_mem:.2f}%")
    
    # 性能相关指标周期性分析
    results.append("\n===== 数据库性能周期性分析 =====")
    db_metrics = ['query_rate_per_sec', 'active_connections', 'avg_query_time_ms', 'transactions_per_sec']
    
    # 只分析数据库类型数据
    db_df = df[df['resource_type'] == 'database']
    
    for metric in db_metrics:
        if metric in db_df.columns and not db_df[metric].isna().all():
            hourly_data = db_df.set_index('timestamp').resample('H')[metric].mean()
            if not hourly_data.empty:
                peak_hour = hourly_data.idxmax().hour
                results.append(f"{metric} 高峰时段: {peak_hour}时")
    
    return results

def save_results(results, output_path):
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
        
        print(f"分析结果已保存到 {output_path}")
    except Exception as e:
        print(f"保存结果时出错: {e}")

def main():
    file_path = "temp_csv/excel_data_20250317140237.csv"
    output_path = "pngs/time_trend_results.txt"
    
    # 加载数据
    df = load_and_preprocess_data(file_path)
    
    if df is not None:
        # 分析时间序列
        results = analyze_time_series(df)
        
        # 保存结果
        save_results(results, output_path)
    else:
        print("由于数据加载错误，无法进行分析")

if __name__ == "__main__":
    main()