import pandas as pd
import os
import numpy as np
from datetime import datetime

def load_csv(file_path):
    """加载CSV文件并返回DataFrame"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载CSV文件时出错: {e}")
        return None

def analyze_categorical_columns(df):
    """分析分类列的分布情况"""
    results = []
    
    # 识别分类列
    categorical_columns = ['base_station_id', 'base_station_name', 'signal_type', 'status']
    
    for col in categorical_columns:
        if col in df.columns:
            # 计算分布
            distribution = df[col].value_counts()
            total = len(df)
            
            # 格式化结果
            result = f"\n{'='*80}\n{col} 分布分析\n{'='*80}\n"
            result += f"总记录数: {total}\n\n"
            result += f"{'类别值':<30}{'数量':<10}{'占比':<10}\n"
            result += f"{'-'*50}\n"
            
            for value, count in distribution.items():
                percentage = count / total * 100
                result += f"{str(value):<30}{count:<10}{percentage:.2f}%\n"
            
            results.append(result)
    
    return results

def analyze_numerical_columns(df):
    """分析数值列的分布情况"""
    results = []
    
    # 数值列分析
    numerical_columns = [
        'success_rate', 'failure_rate', 'call_attempts', 'active_users',
        'signal_strength_dbm', 'signal_quality_db', 'downlink_throughput_mbps',
        'uplink_throughput_mbps', 'latency_ms', 'packet_loss_percent',
        'resource_block_usage_percent', 'cpu_usage_percent', 'memory_usage_percent',
        'temperature_celsius'
    ]
    
    for col in numerical_columns:
        if col in df.columns:
            # 创建范围分组
            if col in ['success_rate', 'failure_rate']:
                bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
            elif col in ['packet_loss_percent', 'resource_block_usage_percent', 'cpu_usage_percent', 'memory_usage_percent']:
                bins = [0, 20, 40, 60, 80, 100, float('inf')]
                labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%', '>100%']
            else:
                # 动态创建分组
                min_val = df[col].min()
                max_val = df[col].max()
                bins = np.linspace(min_val, max_val, 6)
                labels = [f'{bins[i]:.1f}-{bins[i+1]:.1f}' for i in range(len(bins)-1)]
            
            # 计算分布
            df['range'] = pd.cut(df[col], bins=bins, labels=labels, include_lowest=True)
            distribution = df['range'].value_counts().sort_index()
            total = len(df)
            
            # 格式化结果
            result = f"\n{'='*80}\n{col} 范围分布分析\n{'='*80}\n"
            result += f"总记录数: {total}\n"
            result += f"最小值: {df[col].min():.2f}, 最大值: {df[col].max():.2f}, 平均值: {df[col].mean():.2f}\n\n"
            result += f"{'范围':<20}{'数量':<10}{'占比':<10}\n"
            result += f"{'-'*40}\n"
            
            for value, count in distribution.items():
                percentage = count / total * 100
                result += f"{value:<20}{count:<10}{percentage:.2f}%\n"
            
            # 删除临时列
            df.drop('range', axis=1, inplace=True)
            
            results.append(result)
    
    return results

def save_results(results, output_path):
    """保存分析结果到文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 添加标题和时间戳
            f.write(f"CSV数据分布分析报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
            
            # 写入所有结果
            for result in results:
                f.write(result)
        
        print(f"分析结果已保存到 {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    # 文件路径
    csv_path = "temp_csv/excel_data_20250317152243.csv"
    output_path = "pngs/category_distribution_results.txt"
    
    # 加载数据
    df = load_csv(csv_path)
    if df is None:
        return
    
    # 分析分类列
    categorical_results = analyze_categorical_columns(df)
    
    # 分析数值列
    numerical_results = analyze_numerical_columns(df)
    
    # 合并结果
    all_results = categorical_results + numerical_results
    
    # 保存结果
    save_results(all_results, output_path)

if __name__ == "__main__":
    main()