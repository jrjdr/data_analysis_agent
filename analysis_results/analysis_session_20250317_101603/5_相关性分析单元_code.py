#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import f_oneway
import json
import sys
import os
from typing import Dict, List, Any, Tuple

def load_data(file_path: str) -> pd.DataFrame:
    """加载CSV数据文件"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"加载数据文件时出错: {e}")
        sys.exit(1)

def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """获取数据框中的数值型列"""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """获取数据框中的分类列"""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def calculate_correlations(df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
    """计算数值变量之间的相关系数"""
    if len(numeric_cols) < 2:
        return {"error": "没有足够的数值列进行相关性分析"}
    
    # 计算Pearson相关系数
    pearson_corr = df[numeric_cols].corr(method='pearson').round(4)
    
    # 计算Spearman相关系数
    spearman_corr = df[numeric_cols].corr(method='spearman').round(4)
    
    # 提取强相关变量对(|r| > 0.7)
    strong_correlations = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            corr_value = pearson_corr.iloc[i, j]
            if abs(corr_value) > 0.7:
                strong_correlations.append({
                    "variable1": numeric_cols[i],
                    "variable2": numeric_cols[j],
                    "pearson_correlation": float(corr_value),
                    "correlation_type": "强正相关" if corr_value > 0 else "强负相关"
                })
    
    return {
        "pearson_correlation_matrix": pearson_corr.to_dict(),
        "spearman_correlation_matrix": spearman_corr.to_dict(),
        "strong_correlations": strong_correlations
    }

def analyze_categorical_vs_numeric(df: pd.DataFrame, cat_cols: List[str], 
                                  num_cols: List[str]) -> Dict[str, Any]:
    """分析分类变量与数值变量之间的关系"""
    results = []
    
    for cat_col in cat_cols:
        if len(df[cat_col].unique()) > 30:  # 跳过唯一值过多的分类变量
            continue
            
        for num_col in num_cols:
            try:
                # 按分类变量分组
                groups = [df[df[cat_col] == val][num_col].dropna() for val in df[cat_col].unique()]
                
                # 只有当每组至少有2个值时才进行ANOVA分析
                if all(len(group) >= 2 for group in groups):
                    f_stat, p_value = f_oneway(*groups)
                    
                    if p_value < 0.05:
                        results.append({
                            "categorical_variable": cat_col,
                            "numeric_variable": num_col,
                            "f_statistic": float(f_stat),
                            "p_value": float(p_value),
                            "significant": True
                        })
            except Exception as e:
                continue  # 跳过出错的分析
    
    return {"categorical_vs_numeric_analysis": results}

def analyze_correlations(file_path: str) -> Dict[str, Any]:
    """执行相关性分析并返回结果"""
    # 加载数据
    df = load_data(file_path)
    
    # 获取数值列和分类列
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    
    if len(numeric_cols) < 2:
        return {"error": "数据中没有足够的数值列进行相关性分析"}
    
    # 数值变量之间的相关性分析
    correlation_results = calculate_correlations(df, numeric_cols)
    
    # 分类变量与数值变量之间的关系分析
    cat_num_results = analyze_categorical_vs_numeric(df, categorical_cols, numeric_cols)
    
    # 合并结果
    results = {
        "file_analyzed": file_path,
        "total_rows": len(df),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        **correlation_results,
        **cat_num_results
    }
    
    return results

def save_results(results: Dict[str, Any], output_file: str = 'correlation_analysis_results.json') -> None:
    """将分析结果保存为JSON文件"""
    try:
        # 将NumPy类型转换为Python原生类型
        def convert_numpy_types(obj):
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(i) for i in obj]
            else:
                return obj
        
        results = convert_numpy_types(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存结果时出错: {e}")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    results = analyze_correlations(file_path)
    save_results(results)

if __name__ == "__main__":
    main()