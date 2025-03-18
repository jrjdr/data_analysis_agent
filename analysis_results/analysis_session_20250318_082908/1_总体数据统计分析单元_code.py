import pandas as pd
import os
import numpy as np
from datetime import datetime

def load_csv_data(file_path):
    """加载CSV文件数据"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载CSV文件: {file_path}")
        return df
    except Exception as e:
        print(f"加载CSV文件时出错: {e}")
        return None

def basic_statistics(df):
    """计算基本描述性统计"""
    result = []
    result.append("=" * 80)
    result.append("基本数据统计")
    result.append("=" * 80)
    
    result.append(f"数据集大小: {df.shape[0]} 行 x {df.shape[1]} 列")
    result.append(f"内存使用: {df.memory_usage().sum() / (1024 * 1024):.2f} MB")
    
    # 检查缺失值
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        result.append("\n缺失值统计:")
        for col, count in missing_values[missing_values > 0].items():
            result.append(f"  {col}: {count} 缺失值 ({count/len(df)*100:.2f}%)")
    else:
        result.append("\n数据集中没有缺失值")
    
    # 数据类型信息
    result.append("\n列数据类型:")
    for col, dtype in df.dtypes.items():
        result.append(f"  {col}: {dtype}")
    
    return "\n".join(result)

def analyze_numeric_columns(df):
    """分析数值型列"""
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    result = []
    result.append("\n" + "=" * 80)
    result.append("数值列分析")
    result.append("=" * 80)
    
    for col in numeric_cols:
        result.append(f"\n列: {col}")
        result.append("-" * 40)
        
        # 基本统计
        stats = df[col].describe()
        result.append(f"  计数: {stats['count']:.0f}")
        result.append(f"  均值: {stats['mean']:.2f}")
        result.append(f"  标准差: {stats['std']:.2f}")
        result.append(f"  最小值: {stats['min']:.2f}")
        result.append(f"  25%分位数: {stats['25%']:.2f}")
        result.append(f"  中位数: {stats['50%']:.2f}")
        result.append(f"  75%分位数: {stats['75%']:.2f}")
        result.append(f"  最大值: {stats['max']:.2f}")
        
        # 额外统计
        result.append(f"  偏度: {df[col].skew():.2f}")
        result.append(f"  峰度: {df[col].kurtosis():.2f}")
        
        # 分位数分析
        percentiles = [0.1, 0.9, 0.95, 0.99]
        result.append("\n  分位数分析:")
        for p in percentiles:
            result.append(f"    {int(p*100)}%分位数: {df[col].quantile(p):.2f}")
    
    return "\n".join(result)

def analyze_categorical_columns(df):
    """分析分类列"""
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    result = []
    result.append("\n" + "=" * 80)
    result.append("分类列分析")
    result.append("=" * 80)
    
    for col in cat_cols:
        result.append(f"\n列: {col}")
        result.append("-" * 40)
        
        # 唯一值计数
        unique_count = df[col].nunique()
        result.append(f"  唯一值数量: {unique_count}")
        
        # 频率分析
        value_counts = df[col].value_counts()
        result.append("\n  值分布:")
        
        for value, count in value_counts.head(10).items():
            result.append(f"    {value}: {count} ({count/len(df)*100:.2f}%)")
        
        if len(value_counts) > 10:
            result.append(f"    ... 以及 {len(value_counts)-10} 个其他值")
    
    return "\n".join(result)

def analyze_timestamp_column(df):
    """分析时间戳列"""
    result = []
    
    if 'Timestamp' in df.columns and pd.api.types.is_object_dtype(df['Timestamp']):
        result.append("\n" + "=" * 80)
        result.append("时间戳分析")
        result.append("=" * 80)
        
        try:
            # 转换时间戳列
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            
            # 时间范围
            min_time = df['Timestamp'].min()
            max_time = df['Timestamp'].max()
            time_range = max_time - min_time
            
            result.append(f"\n时间范围: {time_range}")
            result.append(f"开始时间: {min_time}")
            result.append(f"结束时间: {max_time}")
            
            # 按日期分组统计
            result.append("\n每日数据量:")
            daily_counts = df.groupby(df['Timestamp'].dt.date).size()
            for date, count in daily_counts.head(10).items():
                result.append(f"  {date}: {count} 条记录")
            
            if len(daily_counts) > 10:
                result.append(f"  ... 以及 {len(daily_counts)-10} 个其他日期")
            
        except Exception as e:
            result.append(f"时间戳分析出错: {e}")
    
    return "\n".join(result)

def cross_analysis(df):
    """交叉分析"""
    result = []
    result.append("\n" + "=" * 80)
    result.append("交叉分析")
    result.append("=" * 80)
    
    # 按区域和服务类型分析流量
    if all(col in df.columns for col in ['Region', 'Service_Type', 'Traffic_Volume_GB']):
        result.append("\n按区域和服务类型的平均流量(GB):")
        cross_table = df.pivot_table(
            values='Traffic_Volume_GB', 
            index='Region', 
            columns='Service_Type', 
            aggfunc='mean'
        )
        
        # 格式化输出
        result.append("\n" + " " * 15 + "".join([f"{col:>15}" for col in cross_table.columns]))
        for idx, row in cross_table.iterrows():
            result.append(f"{idx:15}" + "".join([f"{val:15.2f}" for val in row]))
    
    # 按网络类型分析速度
    if all(col in df.columns for col in ['Network_Type', 'Average_Speed_Mbps']):
        result.append("\n按网络类型的平均速度(Mbps):")
        network_speed = df.groupby('Network_Type')['Average_Speed_Mbps'].agg(['mean', 'min', 'max'])
        
        result.append("\n" + " " * 10 + "".join([f"{col:>15}" for col in network_speed.columns]))
        for idx, row in network_speed.iterrows():
            result.append(f"{idx:10}" + "".join([f"{val:15.2f}" for val in row]))
    
    return "\n".join(result)

def save_analysis_results(results, output_path):
    """保存分析结果到文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(results)
        
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存分析结果时出错: {e}")
        return False

def main():
    # 文件路径
    csv_path = "temp_csv/excel_data_20250318082908.csv"
    output_path = "pngs/analysis_results.txt"
    
    # 加载数据
    df = load_csv_data(csv_path)
    if df is None:
        return
    
    # 执行分析
    results = []
    results.append(f"CSV数据分析报告")
    results.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"文件: {csv_path}")
    results.append("")
    
    results.append(basic_statistics(df))
    results.append(analyze_numeric_columns(df))
    results.append(analyze_categorical_columns(df))
    results.append(analyze_timestamp_column(df))
    results.append(cross_analysis(df))
    
    # 保存结果
    save_analysis_results("\n".join(results), output_path)

if __name__ == "__main__":
    main()