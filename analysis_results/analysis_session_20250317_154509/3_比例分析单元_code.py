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
    
    # 确定哪些列是分类列
    categorical_columns = [
        'Region', 'Complaint_Type', 'Service_Type', 
        'Priority', 'Status', 'Customer_Satisfaction'
    ]
    
    for column in categorical_columns:
        if column in df.columns:
            # 处理可能的缺失值
            valid_count = df[column].count()
            missing_count = df[column].isna().sum()
            
            # 计算分布和占比
            value_counts = df[column].value_counts()
            percentages = df[column].value_counts(normalize=True) * 100
            
            # 将结果添加到列表中
            results.append({
                'column': column,
                'valid_count': valid_count,
                'missing_count': missing_count,
                'distribution': {
                    'counts': value_counts,
                    'percentages': percentages
                }
            })
    
    return results

def format_results_as_text(results):
    """将分析结果格式化为纯文本"""
    text = "客户投诉数据分类分析报告\n"
    text += "=" * 50 + "\n"
    text += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += "=" * 50 + "\n\n"
    
    for result in results:
        column = result['column']
        valid_count = result['valid_count']
        missing_count = result['missing_count']
        
        text += f"{column} 分布分析\n"
        text += "-" * 30 + "\n"
        text += f"有效数据: {valid_count} 条\n"
        text += f"缺失数据: {missing_count} 条\n\n"
        
        text += "类别分布:\n"
        
        # 获取计数和百分比
        counts = result['distribution']['counts']
        percentages = result['distribution']['percentages']
        
        # 确保索引对齐
        for category in counts.index:
            count = counts[category]
            percentage = percentages[category]
            text += f"  {category}: {count} 条 ({percentage:.2f}%)\n"
        
        text += "\n" + "=" * 50 + "\n\n"
    
    return text

def save_results_to_file(text, output_path):
    """将结果保存到文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"分析结果已保存到 {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    # 文件路径
    csv_file_path = "temp_csv/excel_data_20250317154509.csv"
    output_path = "pngs/category_distribution_results.txt"
    
    # 读取CSV文件
    df = read_csv_file(csv_file_path)
    if df is None:
        return
    
    # 分析分类列
    results = analyze_categorical_columns(df)
    
    # 格式化结果为文本
    text_results = format_results_as_text(results)
    
    # 保存结果
    save_results_to_file(text_results, output_path)

if __name__ == "__main__":
    main()