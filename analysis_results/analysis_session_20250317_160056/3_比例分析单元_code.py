import pandas as pd
import os
import numpy as np
from datetime import datetime

def read_csv_file(file_path):
    """读取CSV文件并返回DataFrame"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取CSV文件，共{len(df)}行数据")
        return df
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None

def analyze_categorical_columns(df):
    """分析分类列的分布情况"""
    results = []
    
    # 识别分类列（排除数值型列）
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    # 添加可能的分类数值列
    for col in df.select_dtypes(include=['number']).columns:
        if df[col].nunique() < 10:  # 如果唯一值少于10个，可能是分类变量
            categorical_columns.append(col)
    
    # 分析每个分类列
    for column in categorical_columns:
        # 计算分布
        value_counts = df[column].value_counts()
        total = len(df)
        
        # 计算占比
        percentages = (value_counts / total * 100).round(2)
        
        # 计算缺失值
        missing = df[column].isna().sum()
        missing_percentage = (missing / total * 100).round(2)
        
        # 存储结果
        column_result = {
            'column': column,
            'distribution': value_counts,
            'percentages': percentages,
            'missing': missing,
            'missing_percentage': missing_percentage
        }
        results.append(column_result)
    
    return results

def format_results_as_text(results):
    """将分析结果格式化为文本"""
    text = "数据分类分布分析报告\n"
    text += "=" * 50 + "\n"
    text += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += "=" * 50 + "\n\n"
    
    for result in results:
        column = result['column']
        distribution = result['distribution']
        percentages = result['percentages']
        missing = result['missing']
        missing_percentage = result['missing_percentage']
        
        text += f"列名: {column}\n"
        text += "-" * 50 + "\n"
        
        # 添加缺失值信息
        if missing > 0:
            text += f"缺失值: {missing} ({missing_percentage}%)\n\n"
        else:
            text += "缺失值: 0 (0.00%)\n\n"
        
        # 添加分布信息
        text += "类别分布:\n"
        for value, count in distribution.items():
            percentage = percentages[value]
            text += f"  {value}: {count} ({percentage}%)\n"
        
        text += "\n" + "=" * 50 + "\n\n"
    
    return text

def save_results_to_file(text, output_path):
    """保存结果到文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    # 文件路径
    csv_file_path = "temp_csv/excel_data_20250317160056.csv"
    output_file_path = "pngs/category_distribution_results.txt"
    
    # 读取CSV文件
    df = read_csv_file(csv_file_path)
    if df is None:
        return
    
    # 分析分类列
    analysis_results = analyze_categorical_columns(df)
    
    # 格式化结果为文本
    formatted_results = format_results_as_text(analysis_results)
    
    # 保存结果
    save_results_to_file(formatted_results, output_file_path)

if __name__ == "__main__":
    main()