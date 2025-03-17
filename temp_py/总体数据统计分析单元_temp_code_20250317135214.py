import pandas as pd
import numpy as np
from datetime import datetime

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def analyze_data(df):
    results = []
    results.append("数据分析报告")
    results.append("=" * 40)
    results.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"数据集大小: {df.shape[0]} 行, {df.shape[1]} 列")
    results.append("")

    results.append("基本统计信息")
    results.append("-" * 40)
    for column in df.columns:
        results.append(f"{column}:")
        if pd.api.types.is_numeric_dtype(df[column]):
            stats = df[column].describe()
            results.append(f"  类型: {df[column].dtype}")
            results.append(f"  非空值数: {stats['count']:.0f}")
            results.append(f"  平均值: {stats['mean']:.2f}")
            results.append(f"  标准差: {stats['std']:.2f}")
            results.append(f"  最小值: {stats['min']:.2f}")
            results.append(f"  25%分位数: {stats['25%']:.2f}")
            results.append(f"  中位数: {stats['50%']:.2f}")
            results.append(f"  75%分位数: {stats['75%']:.2f}")
            results.append(f"  最大值: {stats['max']:.2f}")
        elif pd.api.types.is_object_dtype(df[column]):
            results.append(f"  类型: {df[column].dtype}")
            results.append(f"  非空值数: {df[column].count()}")
            results.append(f"  唯一值数: {df[column].nunique()}")
            top_values = df[column].value_counts().head(5)
            results.append("  前5个最常见值:")
            for value, count in top_values.items():
                results.append(f"    {value}: {count}")
        results.append("")

    results.append("数值列分布分析")
    results.append("-" * 40)
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    for column in numeric_columns:
        results.append(f"{column}:")
        results.append(f"  偏度: {df[column].skew():.2f}")
        results.append(f"  峰度: {df[column].kurtosis():.2f}")
        results.append("")

    results.append("分类列分布分析")
    results.append("-" * 40)
    categorical_columns = df.select_dtypes(include=['object']).columns
    for column in categorical_columns:
        results.append(f"{column}:")
        value_counts = df[column].value_counts(normalize=True) * 100
        for value, percentage in value_counts.head(5).items():
            results.append(f"  {value}: {percentage:.2f}%")
        results.append("")

    return "\n".join(results)

def save_results(results, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(results)
        print(f"Analysis results saved to {output_file}")
    except Exception as e:
        print(f"Error saving analysis results: {e}")

def main():
    file_path = "temp_csv/excel_data_20250317135141.csv"