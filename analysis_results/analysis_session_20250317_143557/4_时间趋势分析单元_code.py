import pandas as pd
import numpy as np
from datetime import datetime
import os
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose

def load_csv_data(file_path):
    """加载CSV文件并处理时间列"""
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 将timestamp列转换为datetime格式
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"成功加载数据: {len(df)}行, {len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载CSV文件时出错: {e}")
        return None

def analyze_time_trends(df):
    """分析时间序列数据的趋势和模式"""
    results = []
    
    # 确保数据按时间排序
    df = df.sort_values('timestamp')
    
    # 基本时间信息
    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()
    time_span = end_time - start_time
    
    results.append("=== 基本时间信息 ===")
    results.append(f"数据起始时间: {start_time}")
    results.append(f"数据结束时间: {end_time}")
    results.append(f"数据时间跨度: {time_span}")
    results.append(f"数据点数量: {len(df)}")
    
    # 分析不同服务器和资源类型
    server_counts = df['server_name'].value_counts()
    resource_counts = df['resource_type'].value_counts()
    
    results.append("\n=== 服务器和资源类型分布 ===")
    results.append("服务器分布:")
    for server, count in server_counts.items():
        results.append(f"  {server}: {count}条记录")
    
    results.append("资源类型分布:")
    for resource, count in resource_counts.items():
        results.append(f"  {resource}: {count}条记录")
    
    # 分析事件类型
    event_counts = df['event_type'].value_counts()
    results.append("\n=== 事件类型分布 ===")
    for event, count in event_counts.items():
        results.append(f"  {event}: {count}条记录 ({count/len(df)*100:.2f}%)")
    
    # 选择关键指标进行时间趋势分析
    key_metrics = [
        'cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent',
        'network_traffic_percent', 'query_rate_per_sec', 'active_connections',
        'avg_query_time_ms', 'cache_hit_rate_percent'
    ]
    
    # 对每个服务器分别分析
    for server_name in df['server_name'].unique():
        server_df = df[df['server_name'] == server_name]
        
        results.append(f"\n=== 服务器 {server_name} 的时间趋势分析 ===")
        
        for metric in key_metrics:
            # 跳过缺失值过多的指标
            if server_df[metric].isna().sum() > len(server_df) * 0.5:
                continue
                
            metric_df = server_df.dropna(subset=[metric])
            if len(metric_df) < 10:  # 数据点太少，跳过
                continue
                
            # 计算基本统计信息
            mean_val = metric_df[metric].mean()
            median_val = metric_df[metric].median()
            std_val = metric_df[metric].std()
            min_val = metric_df[metric].min()
            max_val = metric_df[metric].max()
            
            results.append(f"\n指标: {metric}")
            results.append(f"  平均值: {mean_val:.2f}")
            results.append(f"  中位数: {median_val:.2f}")
            results.append(f"  标准差: {std_val:.2f}")
            results.append(f"  最小值: {min_val:.2f}")
            results.append(f"  最大值: {max_val:.2f}")
            
            # 检测异常值
            z_scores = np.abs(stats.zscore(metric_df[metric].fillna(metric_df[metric].median())))
            outliers = metric_df[z_scores > 3]
            if len(outliers) > 0:
                results.append(f"  检测到 {len(outliers)} 个异常值 (Z分数 > 3)")
                results.append(f"  异常时间点示例: {', '.join(outliers['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').head(3).tolist())}")
            
            # 尝试进行时间序列分解（如果数据点足够）
            if len(metric_df) >= 24:  # 假设至少需要24个点进行分解
                try:
                    # 设置时间索引并重采样为均匀时间序列
                    ts_df = metric_df.set_index('timestamp')
                    # 检查时间间隔
                    time_diff = (ts_df.index[1] - ts_df.index[0]).total_seconds() / 60
                    results.append(f"  时间间隔: {time_diff:.1f}分钟")
                    
                    # 检测趋势
                    # 简单线性回归
                    x = np.arange(len(metric_df))
                    y = metric_df[metric].values
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                    
                    trend_direction = "上升" if slope > 0 else "下降"
                    trend_strength = abs(r_value)
                    
                    results.append(f"  趋势: {trend_direction}趋势 (斜率: {slope:.4f}, R²: {r_value**2:.4f})")
                    
                    if trend_strength > 0.7:
                        results.append(f"  强{trend_direction}趋势")
                    elif trend_strength > 0.3:
                        results.append(f"  中等{trend_direction}趋势")
                    else:
                        results.append(f"  弱{trend_direction}趋势或无明显趋势")
                        
                except Exception as e:
                    results.append(f"  时间序列分解失败: {e}")
    
    # 分析事件类型随时间的变化
    if 'event_type' in df.columns:
        results.append("\n=== 事件类型随时间变化分析 ===")
        # 按小时统计事件
        df['hour'] = df['timestamp'].dt.hour
        hourly_events = df.groupby(['hour', 'event_type']).size().unstack(fill_value=0)
        
        results.append("每小时事件分布:")
        for hour in sorted(df['hour'].unique()):
            hour_data = hourly_events.loc[hour]
            total = hour_data.sum()
            results.append(f"  {hour}时: 总计{total}事件")
            for event_type in hour_data.index:
                if hour_data[event_type] > 0:
                    results.append(f"    - {event_type}: {hour_data[event_type]}次 ({hour_data[event_type]/total*100:.1f}%)")
    
    return results

def save_results(results, output_path):
    """将分析结果保存为纯文本格式"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("时间趋势分析结果\n")
            f.write("=" * 50 + "\n\n")
            f.write("\n".join(results))
            
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    # 文件路径
    csv_path = "temp_csv/excel_data_20250317143557.csv"
    output_path = "pngs/time_trend_results.txt"
    
    # 加载数据
    df = load_csv_data(csv_path)
    if df is None:
        return
    
    # 分析时间趋势
    results = analyze_time_trends(df)
    
    # 保存结果
    save_results(results, output_path)

if __name__ == "__main__":
    main()