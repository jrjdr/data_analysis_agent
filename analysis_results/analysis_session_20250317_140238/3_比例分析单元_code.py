import pandas as pd
import os
import numpy as np
from datetime import datetime

def read_csv_file(file_path):
    """读取CSV文件并处理可能的错误"""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        return None
    except pd.errors.EmptyDataError:
        print(f"错误: 文件 '{file_path}' 为空")
        return None
    except pd.errors.ParserError:
        print(f"错误: 文件 '{file_path}' 解析失败")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None

def analyze_categorical_columns(df):
    """分析分类数据列的分布情况"""
    results = []
    
    # 识别分类列（对象类型和唯一值较少的数值列）
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    # 分析每个分类列
    for col in categorical_columns:
        value_counts = df[col].value_counts()
        total = len(df)
        
        # 计算每个值的数量和百分比
        distribution = []
        for value, count in value_counts.items():
            percentage = (count / total) * 100
            distribution.append((value, count, percentage))
        
        results.append((col, distribution))
    
    return results

def analyze_numerical_columns(df):
    """分析数值列的基本统计信息"""
    results = []
    
    # 选择数值列
    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    # 对每个数值列，计算基本统计信息
    for col in numerical_columns:
        # 计算非空值的基本统计数据
        non_null_values = df[col].dropna()
        if len(non_null_values) > 0:
            stats = {
                "count": len(non_null_values),
                "missing": df[col].isna().sum(),
                "mean": non_null_values.mean(),
                "median": non_null_values.median(),
                "min": non_null_values.min(),
                "max": non_null_values.max(),
                "std": non_null_values.std()
            }
            results.append((col, stats))
    
    return results

def format_results(categorical_results, numerical_results):
    """将分析结果格式化为可读的文本"""
    output = "服务器监控数据分析报告\n"
    output += "=" * 50 + "\n"
    output += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # 分类数据分析结果
    output += "一、分类数据分布分析\n"
    output += "-" * 50 + "\n\n"
    
    for col, distribution in categorical_results:
        output += f"【{col}】分布情况:\n"
        output += "-" * 30 + "\n"
        
        # 按计数降序排序
        sorted_dist = sorted(distribution, key=lambda x: x[1], reverse=True)
        
        # 计算总数
        total = sum(item[1] for item in distribution)
        
        for value, count, percentage in sorted_dist:
            output += f"  {value}: {count} 条记录 ({percentage:.2f}%)\n"
        
        output += "\n"
    
    # 数值数据分析结果
    output += "二、数值数据基本统计分析\n"
    output += "-" * 50 + "\n\n"
    
    for col, stats in numerical_results:
        output += f"【{col}】统计数据:\n"
        output += "-" * 30 + "\n"
        output += f"  总记录数: {stats['count'] + stats['missing']}\n"
        output += f"  有效记录: {stats['count']} ({(stats['count'] / (stats['count'] + stats['missing']) * 100):.2f}%)\n"
        output += f"  缺失记录: {stats['missing']} ({(stats['missing'] / (stats['count'] + stats['missing']) * 100):.2f}%)\n"
        
        if stats['count'] > 0:
            output += f"  平均值: {stats['mean']:.2f}\n"
            output += f"  中位数: {stats['median']:.2f}\n"
            output += f"  最小值: {stats['min']:.2f}\n"
            output += f"  最大值: {stats['max']:.2f}\n"
            output += f"  标准差: {stats['std']:.2f}\n"
        
        output += "\n"
    
    return output

def save_results(content, output_path):
    """保存结果到文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时发生错误: {str(e)}")
        return False

def main():
    # 文件路径
    csv_file = "temp_csv/excel_data_20250317140237.csv"
    output_file = "pngs/category_distribution_results.txt"
    
    # 读取CSV文件
    df = read_csv_file(csv_file)
    if df is None:
        return
    
    # 分析分类列的分布情况
    categorical_results = analyze_categorical_columns(df)
    
    # 分析数值列的基本统计信息
    numerical_results = analyze_numerical_columns(df)
    
    # 格式化结果
    formatted_results = format_results(categorical_results, numerical_results)
    
    # 保存结果
    save_results(formatted_results, output_file)

if __name__ == "__main__":
    main()