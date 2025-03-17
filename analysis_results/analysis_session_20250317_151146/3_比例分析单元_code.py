import pandas as pd
import os
import numpy as np
from datetime import datetime

def read_csv_file(file_path):
    """读取CSV文件并返回DataFrame"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取CSV文件，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None

def analyze_categorical_columns(df):
    """分析分类列的分布情况"""
    results = []
    
    # 识别分类列（object类型和唯一值较少的数值列）
    categorical_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':
            categorical_columns.append(col)
        elif df[col].dtype in ['int64', 'float64'] and df[col].nunique() < 50:
            # 对于唯一值较少的数值列，也视为分类列
            categorical_columns.append(col)
    
    results.append(f"分类列分析结果 (共{len(categorical_columns)}列)")
    results.append("=" * 50)
    
    # 分析每个分类列
    for col in categorical_columns:
        results.append(f"\n列名: {col}")
        results.append("-" * 30)
        
        # 计算值分布
        value_counts = df[col].value_counts()
        total_count = len(df)
        
        # 添加分布情况
        results.append(f"总记录数: {total_count}")
        results.append(f"唯一值数量: {df[col].nunique()}")
        results.append(f"缺失值数量: {df[col].isna().sum()}")
        results.append("\n分布情况:")
        
        # 对于值较多的列，只显示前10个
        if len(value_counts) > 10:
            for value, count in value_counts.head(10).items():
                percentage = (count / total_count) * 100
                results.append(f"  {value}: {count} ({percentage:.2f}%)")
            results.append(f"  ... 以及其他 {len(value_counts) - 10} 个值")
        else:
            for value, count in value_counts.items():
                percentage = (count / total_count) * 100
                results.append(f"  {value}: {count} ({percentage:.2f}%)")
    
    return results

def analyze_numerical_columns(df):
    """分析数值列的统计信息"""
    results = []
    
    # 识别数值列
    numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    results.append(f"\n数值列分析结果 (共{len(numerical_columns)}列)")
    results.append("=" * 50)
    
    # 分析每个数值列
    for col in numerical_columns:
        # 跳过唯一值较少的列，因为它们已在分类列中分析
        if df[col].nunique() < 50:
            continue
            
        results.append(f"\n列名: {col}")
        results.append("-" * 30)
        
        # 计算基本统计量
        non_null_count = df[col].count()
        missing_count = df[col].isna().sum()
        
        results.append(f"非空值数量: {non_null_count}")
        results.append(f"缺失值数量: {missing_count} ({(missing_count/len(df))*100:.2f}%)")
        
        if non_null_count > 0:
            results.append(f"最小值: {df[col].min():.2f}")
            results.append(f"最大值: {df[col].max():.2f}")
            results.append(f"平均值: {df[col].mean():.2f}")
            results.append(f"中位数: {df[col].median():.2f}")
            results.append(f"标准差: {df[col].std():.2f}")
            
            # 计算分位数
            quantiles = df[col].quantile([0.25, 0.5, 0.75]).to_dict()
            results.append(f"25%分位数: {quantiles[0.25]:.2f}")
            results.append(f"75%分位数: {quantiles[0.75]:.2f}")
    
    return results

def analyze_resource_usage(df):
    """分析资源使用情况"""
    results = []
    
    results.append("\n资源使用情况分析")
    results.append("=" * 50)
    
    # 分析服务器资源使用情况
    resource_cols = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
                    'network_traffic_percent', 'temperature_celsius']
    
    for col in resource_cols:
        if col in df.columns:
            non_null_df = df[~df[col].isna()]
            if len(non_null_df) > 0:
                results.append(f"\n{col} 分析:")
                
                # 定义资源使用级别
                bins = [0, 50, 70, 85, 100]
                labels = ['正常 (0-50%)', '中等 (50-70%)', '较高 (70-85%)', '严重 (85-100%)']
                
                # 对温度使用不同的区间
                if col == 'temperature_celsius':
                    bins = [0, 40, 50, 60, 100]
                    labels = ['正常 (0-40°C)', '中等 (40-50°C)', '较高 (50-60°C)', '严重 (>60°C)']
                
                # 计算每个级别的数量
                non_null_df['level'] = pd.cut(non_null_df[col], bins=bins, labels=labels, right=True)
                level_counts = non_null_df['level'].value_counts().sort_index()
                
                for level, count in level_counts.items():
                    percentage = (count / len(non_null_df)) * 100
                    results.append(f"  {level}: {count} ({percentage:.2f}%)")
    
    return results

def analyze_event_distribution(df):
    """分析事件类型分布"""
    results = []
    
    if 'event_type' in df.columns:
        results.append("\n事件类型分布")
        results.append("=" * 50)
        
        event_counts = df['event_type'].value_counts()
        total_events = len(df)
        
        for event, count in event_counts.items():
            percentage = (count / total_events) * 100
            results.append(f"{event}: {count} ({percentage:.2f}%)")
    
    return results

def analyze_server_distribution(df):
    """分析服务器分布"""
    results = []
    
    if 'server_id' in df.columns and 'server_name' in df.columns:
        results.append("\n服务器分布")
        results.append("=" * 50)
        
        server_counts = df.groupby(['server_id', 'server_name']).size().reset_index(name='count')
        total_records = len(df)
        
        for _, row in server_counts.iterrows():
            percentage = (row['count'] / total_records) * 100
            results.append(f"{row['server_id']} ({row['server_name']}): {row['count']} ({percentage:.2f}%)")
    
    return results

def save_results_to_file(results, output_path):
    """将结果保存到文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"CSV数据分析报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for line in results:
                f.write(f"{line}\n")
                
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    # 文件路径
    csv_file = "temp_csv/excel_data_20250317151146.csv"
    output_file = "pngs/category_distribution_results.txt"
    
    # 读取CSV文件
    df = read_csv_file(csv_file)
    if df is None:
        return
    
    # 收集所有分析结果
    all_results = []
    
    # 分析分类列
    all_results.extend(analyze_categorical_columns(df))
    
    # 分析数值列
    all_results.extend(analyze_numerical_columns(df))
    
    # 分析资源使用情况
    all_results.extend(analyze_resource_usage(df))
    
    # 分析事件分布
    all_results.extend(analyze_event_distribution(df))
    
    # 分析服务器分布
    all_results.extend(analyze_server_distribution(df))
    
    # 保存结果
    save_results_to_file(all_results, output_file)

if __name__ == "__main__":
    main()