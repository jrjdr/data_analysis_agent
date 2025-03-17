import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_data(file_path):
    """加载CSV文件数据"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共 {len(df)} 行，{len(df.columns)} 列")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def analyze_columns(df):
    """分析数值列和分类列的分布"""
    result = []
    result.append("=== 数据列分析 ===\n")
    
    # 分类数据列
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    result.append(f"分类列 ({len(categorical_cols)}): {', '.join(categorical_cols)}\n")
    
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        result.append(f"\n{col} 分布:")
        for val, count in value_counts.head(5).items():
            result.append(f"  - {val}: {count} ({count/len(df)*100:.2f}%)")
        if len(value_counts) > 5:
            result.append(f"  - ... 其他 {len(value_counts)-5} 个值")
    
    # 数值数据列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    result.append(f"\n\n数值列 ({len(numeric_cols)}): {', '.join(numeric_cols[:10])}...")
    
    for col in numeric_cols[:10]:  # 只显示前10个数值列的详细信息
        stats = df[col].describe()
        result.append(f"\n{col} 统计:")
        result.append(f"  - 均值: {stats['mean']:.2f}")
        result.append(f"  - 中位数: {stats['50%']:.2f}")
        result.append(f"  - 标准差: {stats['std']:.2f}")
        result.append(f"  - 最小值: {stats['min']:.2f}")
        result.append(f"  - 最大值: {stats['max']:.2f}")
        result.append(f"  - 缺失值: {df[col].isna().sum()} ({df[col].isna().sum()/len(df)*100:.2f}%)")
    
    return "\n".join(result)

def group_comparison(df):
    """对数据进行分组统计，比较不同组之间的差异"""
    result = []
    result.append("\n\n=== 分组对比分析 ===\n")
    
    # 按服务器类型分组
    result.append("1. 按服务器名称分组分析")
    server_groups = df.groupby('server_name')
    
    # 选择关键指标进行分析
    key_metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                  'network_traffic_percent', 'temperature_celsius']
    
    # 计算每组的平均值
    server_means = server_groups[key_metrics].mean().round(2)
    result.append("\n服务器性能指标平均值:")
    result.append(server_means.to_string())
    
    # 按资源类型分组
    result.append("\n\n2. 按资源类型分组分析")
    resource_groups = df.groupby('resource_type')
    resource_means = resource_groups[key_metrics].mean().round(2)
    result.append("\n资源类型性能指标平均值:")
    result.append(resource_means.to_string())
    
    # 按事件类型分组
    result.append("\n\n3. 按事件类型分组分析")
    event_groups = df.groupby('event_type')
    event_counts = df['event_type'].value_counts()
    result.append("\n事件类型分布:")
    for event, count in event_counts.items():
        result.append(f"  - {event}: {count} ({count/len(df)*100:.2f}%)")
    
    # 分析异常事件
    if 'error' in df['event_type'].values:
        error_data = df[df['event_type'] == 'error']
        result.append("\n错误事件分析:")
        result.append(f"  - 错误事件总数: {len(error_data)}")
        result.append(f"  - 错误事件服务器分布: {error_data['server_name'].value_counts().to_dict()}")
        
        # 错误事件时的平均指标
        error_means = error_data[key_metrics].mean().round(2)
        normal_means = df[df['event_type'] == 'normal'][key_metrics].mean().round(2)
        
        result.append("\n错误事件与正常事件指标对比:")
        comparison = pd.DataFrame({'错误事件': error_means, '正常事件': normal_means})
        result.append(comparison.to_string())
    
    # 高负载分析
    result.append("\n\n4. 高负载分析")
    high_cpu = df[df['cpu_usage_percent'] > 80]
    result.append(f"\n高CPU使用率 (>80%) 事件数: {len(high_cpu)}")
    if len(high_cpu) > 0:
        result.append(f"  - 服务器分布: {high_cpu['server_name'].value_counts().to_dict()}")
    
    high_memory = df[df['memory_usage_percent'] > 80]
    result.append(f"\n高内存使用率 (>80%) 事件数: {len(high_memory)}")
    if len(high_memory) > 0:
        result.append(f"  - 服务器分布: {high_memory['server_name'].value_counts().to_dict()}")
    
    return "\n".join(result)

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
    file_path = "temp_csv/excel_data_20250317142408.csv"
    output_path = "pngs/group_comparison_results.txt"
    
    # 加载数据
    df = load_data(file_path)
    if df is None:
        return
    
    # 数据预处理
    # 将timestamp列转换为datetime类型
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 生成分析结果
    results = []
    
    # 添加标题和基本信息
    results.append("=== 服务器性能数据分析报告 ===")
    results.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"数据文件: {file_path}")
    results.append(f"数据范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
    results.append(f"数据行数: {len(df)}")
    results.append(f"服务器数量: {df['server_id'].nunique()}")
    results.append("\n" + "="*50 + "\n")
    
    # 添加列分析结果
    results.append(analyze_columns(df))
    
    # 添加分组对比分析结果
    results.append(group_comparison(df))
    
    # 保存结果
    save_results("\n".join(results), output_path)

if __name__ == "__main__":
    main()