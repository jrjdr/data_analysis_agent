import pandas as pd
import numpy as np
from datetime import datetime

def analyze_csv(file_path, output_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 准备输出结果
        results = []
        
        # 基本信息
        results.append("=== 基本信息 ===")
        results.append(f"行数: {df.shape[0]}")
        results.append(f"列数: {df.shape[1]}")
        results.append(f"列名: {', '.join(df.columns)}")
        results.append("")
        
        # 数值列分析
        results.append("=== 数值列分析 ===")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            results.append(f"列: {col}")
            results.append(f"  最小值: {df[col].min():.2f}")
            results.append(f"  最大值: {df[col].max():.2f}")
            results.append(f"  平均值: {df[col].mean():.2f}")
            results.append(f"  中位数: {df[col].median():.2f}")
            results.append(f"  标准差: {df[col].std():.2f}")
            results.append(f"  缺失值: {df[col].isnull().sum()}")
            results.append("")
        
        # 分类列分析
        results.append("=== 分类列分析 ===")
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            results.append(f"列: {col}")
            value_counts = df[col].value_counts()
            results.append(f"  唯一值数量: {len(value_counts)}")
            results.append(f"  最常见值: {value_counts.index[0]} (出现 {value_counts.iloc[0]} 次)")
            results.append(f"  缺失值: {df[col].isnull().sum()}")
            results.append("")
        
        # 时间序列分析 (假设timestamp列为时间戳)
        if 'timestamp' in df.columns:
            results.append("=== 时间序列分析 ===")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            results.append(f"开始时间: {df['timestamp'].min()}")
            results.append(f"结束时间: {df['timestamp'].max()}")
            results.append(f"时间跨度: {df['timestamp'].max() - df['timestamp'].min()}")
            results.append("")
        
        # 相关性分析
        results.append("=== 相关性分析 ===")
        corr_matrix = df[numeric_cols].corr()
        high_corr = corr_matrix[abs(corr_matrix) > 0.8].stack()
        high_corr = high_corr[high_corr != 1]  # 移除自相关
        for idx, value in high_corr.items():
            results.append(f"高相关性: {idx[0]} 和 {idx[1]}, 相关系数: {value:.2f}")
        
        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(results))
        
        print(f"分析结果已保存到 {output_path}")
    
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")

# 执行分析
csv