import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_csv_data(file_path):
    """加载CSV文件数据"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载CSV文件失败: {e}")
        return None

def analyze_columns(df):
    """分析数据列的基本统计信息"""
    results = []
    
    # 区分数值列和分类列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    results.append("数据列分析\n" + "="*50)
    
    # 分析分类列
    results.append("\n分类列分析:\n" + "-"*50)
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        unique_count = len(value_counts)
        most_common = value_counts.index[0]
        most_common_count = value_counts.iloc[0]
        results.append(f"\n列名: {col}")
        results.append(f"  唯一值数量: {unique_count}")
        results.append(f"  最常见值: {most_common} (出现{most_common_count}次)")
        if unique_count <= 10:  # 如果唯一值较少，显示所有值的分布
            results.append("  值分布:")
            for val, count in value_counts.items():
                results.append(f"    {val}: {count} ({count/len(df)*100:.2f}%)")
    
    # 分析数值列
    results.append("\n数值列分析:\n" + "-"*50)
    for col in numeric_cols:
        # 跳过缺失值过多的列
        missing = df[col].isna().sum()
        if missing == len(df):
            continue
            
        stats = df[col].describe()
        results.append(f"\n列名: {col}")
        results.append(f"  缺失值: {missing} ({missing/len(df)*100:.2f}%)")
        results.append(f"  均值: {stats['mean']:.2f}")
        results.append(f"  中位数: {stats['50%']:.2f}")
        results.append(f"  标准差: {stats['std']:.2f}")
        results.append(f"  最小值: {stats['min']:.2f}")
        results.append(f"  最大值: {stats['max']:.2f}")
        
    return "\n".join(results)

def group_comparison(df):
    """对数据进行分组比较分析"""
    results = []
    results.append("\n分组比较分析\n" + "="*50)
    
    # 按服务器类型分组分析
    if 'server_name' in df.columns:
        results.append("\n按服务器名称分组分析:\n" + "-"*50)
        server_groups = df.groupby('server_name')
        
        # 获取所有数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # 计算每个服务器的关键指标平均值
        server_stats = server_groups[numeric_cols].mean().round(2)
        
        # 格式化输出
        for server, stats in server_stats.iterrows():
            results.append(f"\n服务器: {server}")
            for col, val in stats.items():
                if not np.isnan(val):  # 跳过NaN值
                    results.append(f"  {col}: {val:.2f}")
    
    # 按资源类型分组分析
    if 'resource_type' in df.columns:
        results.append("\n按资源类型分组分析:\n" + "-"*50)
        resource_groups = df.groupby('resource_type')
        
        for resource_type, group in resource_groups:
            results.append(f"\n资源类型: {resource_type}")
            
            # 获取该资源类型的非NaN列
            valid_cols = [col for col in df.columns if group[col].notna().any() and 
                         df[col].dtype != 'object']
            
            for col in valid_cols[:10]:  # 限制显示的列数
                if group[col].notna().any():
                    results.append(f"  {col}: 均值={group[col].mean():.2f}, 中位数={group[col].median():.2f}")
    
    # 按事件类型分组分析
    if 'event_type' in df.columns:
        results.append("\n按事件类型分组分析:\n" + "-"*50)
        event_groups = df.groupby('event_type')
        
        # 计算每种事件类型的数量和百分比
        event_counts = df['event_type'].value_counts()
        for event_type, count in event_counts.items():
            results.append(f"\n事件类型: {event_type}")
            results.append(f"  数量: {count} ({count/len(df)*100:.2f}%)")
            
            # 获取该事件类型的关键性能指标
            event_data = df[df['event_type'] == event_type]
            perf_cols = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                        'network_traffic_percent']
            
            for col in perf_cols:
                if col in df.columns and event_data[col].notna().any():
                    results.append(f"  {col}: 均值={event_data[col].mean():.2f}, 最大值={event_data[col].max():.2f}")
    
    # 高负载时间段分析
    results.append("\n高负载时间段分析:\n" + "-"*50)
    if 'cpu_usage_percent' in df.columns and df['cpu_usage_percent'].notna().any():
        high_cpu = df[df['cpu_usage_percent'] > df['cpu_usage_percent'].quantile(0.9)]
        if 'timestamp' in df.columns and len(high_cpu) > 0:
            results.append(f"\n高CPU使用率时间段 (前5个):")
            for ts in high_cpu['timestamp'].head(5):
                results.append(f"  {ts}")
    
    return "\n".join(results)

def save_results(content, output_path):
    """保存分析结果到文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果失败: {e}")
        return False

def main():
    # 文件路径
    csv_path = "temp_csv/excel_data_20250317151146.csv"
    output_path = "pngs/group_comparison_results.txt"
    
    # 加载数据
    df = load_csv_data(csv_path)
    if df is None:
        return
    
    # 生成报告头部
    report = []
    report.append("服务器性能数据分析报告")
    report.append("=" * 50)
    report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"数据文件: {csv_path}")
    report.append(f"数据行数: {len(df)}")
    report.append(f"数据列数: {len(df.columns)}")
    report.append("\n")
    
    # 进行列分析
    column_analysis = analyze_columns(df)
    report.append(column_analysis)
    
    # 进行分组比较分析
    group_analysis = group_comparison(df)
    report.append(group_analysis)
    
    # 保存结果
    save_results("\n".join(report), output_path)

if __name__ == "__main__":
    main()