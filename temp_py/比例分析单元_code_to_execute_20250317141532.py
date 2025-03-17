import pandas as pd
import os
import numpy as np
from datetime import datetime

def read_csv_file(file_path):
    """读取CSV文件并返回DataFrame"""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None

def analyze_categorical_columns(df):
    """分析分类列的分布情况"""
    results = []
    
    # 识别分类列(object类型和唯一值较少的数值列)
    categorical_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':
            categorical_columns.append(col)
        elif df[col].dtype in ['int64', 'float64'] and df[col].nunique() < 50:
            categorical_columns.append(col)
    
    # 分析每个分类列
    for col in categorical_columns:
        # 计算分布
        value_counts = df[col].value_counts(dropna=False)
        total = len(df)
        
        # 格式化结果
        section = f"列: {col}\n"
        section += "-" * 50 + "\n"
        section += f"总记录数: {total}\n"
        section += f"唯一值数量: {df[col].nunique()}\n\n"
        section += "分布情况:\n"
        
        # 对于值较多的列，只显示前15个
        if len(value_counts) > 15:
            top_values = value_counts.head(15)
            section += "（仅显示前15个最常见值）\n"
        else:
            top_values = value_counts
        
        # 添加每个值的计数和百分比
        for value, count in top_values.items():
            percentage = (count / total) * 100
            value_str = str(value) if pd.notna(value) else "缺失值"
            section += f"  {value_str}: {count} ({percentage:.2f}%)\n"
        
        results.append(section)
    
    return results

def save_results_to_text(results, output_path):
    """将结果保存为文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("数据分类分布分析报告\n")
            f.write("=" * 60 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for section in results:
                f.write(section)
                f.write("\n" + "=" * 60 + "\n\n")
            
            f.write("分析完成\n")
        
        print(f"结果已保存到 {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    # 文件路径
    file_path = "temp_csv/excel_data_20250317141159.csv"
    output_path = "pngs/category_distribution_results.txt"
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return
    
    # 分析分类列
    results = analyze_categorical_columns(df)
    
    # 保存结果
    save_results_to_text(results, output_path)

if __name__ == "__main__":
    main()